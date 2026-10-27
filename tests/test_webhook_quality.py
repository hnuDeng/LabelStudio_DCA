import tests

import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from backend import database, server


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}", connect_args={"check_same_thread": False})
    database.Base.metadata.create_all(engine)
    monkeypatch.setattr(database, "SessionLocal", database.sessionmaker(bind=engine))
    monkeypatch.setattr(server, "LABEL_STUDIO_WEBHOOK_SECRET", "secret")
    monkeypatch.setattr(server, "dq_api", server.DataQualityAPI())
    with TestClient(server.app) as test_client:
        yield test_client
    engine.dispose()


def event(project=7):
    return {"action": "ANNOTATION_CREATED", "project": {"id": project},
            "task": {"id": 10}, "annotation": {"id": 20, "result": [{"value": {"choices": ["yes"]}}]}}


def send(client, payload):
    return client.post("/api/webhooks/label-studio", json=payload, headers={"Authorization": "Bearer secret"})


def test_event_assesses_and_persists_project_scoped_report(client):
    response = send(client, event())
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    report = client.get("/api/projects/7/quality-report").json()
    assert report["has_data"] is True
    assert report["completeness_score"] == 1.0
    assert report["tasks_analyzed"] == 1
    assert report["annotations_analyzed"] == 1
    assert client.get("/api/projects/8/quality-report").json()["has_data"] is False
    server.dq_api = server.DataQualityAPI()
    assert client.get("/api/projects/7/quality-report").json() == report


def test_repeated_event_returns_original_report_after_reinitialization(client):
    first = send(client, event()).json()
    server.dq_api = server.DataQualityAPI()
    second = send(client, event()).json()
    assert second["status"] == "duplicate"
    assert second["report_id"] == first["report_id"]
    with database.SessionLocal() as db:
        assert db.query(database.DBQualityReport).count() == 1


def test_duplicate_is_detected_after_process_restart(client, tmp_path):
    first = send(client, event()).json()
    script = """
from fastapi.testclient import TestClient
from backend.server import app
import json, sys
response = TestClient(app).post('/api/webhooks/label-studio', json=json.loads(sys.stdin.read()), headers={'Authorization': 'Bearer secret'})
print(json.dumps(response.json()))
"""
    env = dict(os.environ, DCA_DATABASE_URL=f"sqlite:///{(tmp_path / 'test.db').as_posix()}", LABEL_STUDIO_WEBHOOK_SECRET="secret", PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    env.pop("TESTING", None)
    process = subprocess.run([sys.executable, "-c", script], input=json.dumps(event()), text=True, capture_output=True, env=env, cwd=tmp_path, check=True)
    assert json.loads(process.stdout) == {"status": "duplicate", "action": "ANNOTATION_CREATED", "report_id": first["report_id"]}


def test_testing_memory_database_is_shared_with_testclient_thread(tmp_path):
    script = """
from fastapi.testclient import TestClient
from backend.server import app
import json, sys
client = TestClient(app)
response = client.post('/api/webhooks/label-studio', json=json.loads(sys.stdin.read()), headers={'Authorization': 'Bearer secret'})
report = client.get('/api/projects/7/quality-report').json() if response.status_code == 200 else None
print(json.dumps({'http_status': response.status_code, 'webhook': response.json(), 'report': report}))
"""
    env = dict(os.environ, TESTING="1", LABEL_STUDIO_WEBHOOK_SECRET="secret", PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    env.pop("DCA_DATABASE_URL", None)
    process = subprocess.run([sys.executable, "-c", script], input=json.dumps(event()), text=True, capture_output=True, env=env, cwd=tmp_path, check=True)
    result = json.loads(process.stdout)
    assert result["http_status"] == 200
    assert result["webhook"]["status"] == "processed"
    assert result["report"]["has_data"] is True
    assert not (tmp_path / "dca_data.db").exists()


@pytest.mark.parametrize("payload,expected", [
    ({"action": "TASKS_CREATED", "project": {"id": 7}}, "unsupported"),
    ({"action": "ANNOTATION_CREATED", "project": {"id": 7}}, "insufficient_data"),
    ({"action": "ANNOTATION_CREATED", "project": {"id": 7}, "task": {"id": 10}, "annotation": {"id": 20, "result": []}}, "insufficient_data"),
    ({"action": "ANNOTATION_CREATED", "project": {}, "task": {"id": 10}, "annotation": {"id": 20, "result": [{}]}}, "invalid"),
])
def test_unprocessable_events_do_not_create_report(client, payload, expected):
    response = send(client, payload)
    assert response.json()["status"] == expected
    with database.SessionLocal() as db:
        assert db.query(database.DBQualityReport).count() == 0


def test_assessor_failure_is_not_reported_as_processed(client):
    with patch("backend.data_quality.assessors.completeness.CompletenessAssessor.assess", side_effect=RuntimeError("assessment failed")):
        response = send(client, event())
    assert response.status_code == 500
    assert response.json()["status"] == "failed"
    with database.SessionLocal() as db:
        assert db.query(database.DBQualityReport).count() == 0
    assert send(client, event()).json()["status"] == "processed"


def test_database_failure_returns_failed_instead_of_success(client):
    with patch("backend.database.SessionLocal", side_effect=RuntimeError("database unavailable")):
        response = send(client, event())
    assert response.status_code == 500
    assert response.json()["status"] == "failed"


def test_changed_annotation_is_a_new_event(client):
    first = send(client, event()).json()
    updated = event()
    updated["action"] = "ANNOTATION_UPDATED"
    updated["annotation"]["result"][0]["value"]["choices"] = ["no"]
    second = send(client, updated).json()
    assert second["status"] == "processed"
    assert second["report_id"] != first["report_id"]
    assert client.get('/api/projects/7/quality-report').json()["report_id"] == second["report_id"]


def test_reports_remain_separate_when_both_projects_have_data(client):
    first = send(client, event(7)).json()
    second = send(client, event(8)).json()
    assert client.get('/api/projects/7/quality-report').json()["report_id"] == first["report_id"]
    assert client.get('/api/projects/8/quality-report').json()["report_id"] == second["report_id"]


@pytest.mark.parametrize("task_project", [8, {"id": 8}, {"id": True}, {}, None, "7"])
def test_rejects_task_from_another_or_invalid_project_without_persisting(client, task_project):
    payload = event()
    payload["task"]["project"] = task_project
    response = send(client, payload)
    assert response.status_code == 422
    assert response.json()["status"] == "invalid"
    with database.SessionLocal() as db:
        assert db.query(database.DBQualityReport).count() == 0
        assert db.query(database.DBWebhookQualityEvent).count() == 0


@pytest.mark.parametrize("task_project", [7, {"id": 7}])
def test_accepts_matching_task_project_id_or_object(client, task_project):
    payload = event()
    payload["task"]["project"] = task_project
    assert send(client, payload).json()["status"] == "processed"
    assert client.get('/api/projects/7/quality-report').json()["has_data"] is True


@pytest.mark.parametrize("value", ["not an annotation value", ["yes"], 1, True, None, {}])
def test_rejects_non_object_or_empty_annotation_value_without_persisting(client, value):
    payload = event()
    payload["annotation"]["result"][0]["value"] = value
    response = send(client, payload)
    assert response.status_code == 422
    assert response.json()["status"] == "invalid"
    with database.SessionLocal() as db:
        assert db.query(database.DBQualityReport).count() == 0
        assert db.query(database.DBWebhookQualityEvent).count() == 0


@pytest.mark.parametrize('field,value', [('project', 8), ('project', {'id': 8}), ('project', True), ('project', None), ('task', True), ('task', 0), ('task', 11), ('task', None)])
def test_rejects_inconsistent_annotation_references(client, field, value):
    payload = event()
    payload['annotation'][field] = value
    response = send(client, payload)
    assert response.status_code == 422
    assert response.json()['status'] == 'invalid'
    with database.SessionLocal() as db:
        assert db.query(database.DBQualityReport).count() == 0
        assert db.query(database.DBWebhookQualityEvent).count() == 0


@pytest.mark.parametrize('value', [{'choices': []}, {'choices': ['']}, {'text': []}, {'labels': []}])
def test_rejects_annotation_values_with_only_empty_selections(client, value):
    payload = event()
    payload['annotation']['result'][0]['value'] = value
    assert send(client, payload).json()['status'] == 'invalid'
    with database.SessionLocal() as db:
        assert db.query(database.DBQualityReport).count() == 0


@pytest.mark.parametrize('value', [{'choices': ['yes']}, {'text': ['hello']}, {'x': 0, 'y': 0, 'width': 10, 'height': 10, 'rectanglelabels': ['box']}, {'rating': 0}, {'number': 0}])
def test_accepts_meaningful_values_for_different_controls(client, value):
    payload = event()
    payload['annotation']['result'][0]['value'] = value
    payload['annotation'].update(project={'id': 7}, task=10)
    assert send(client, payload).json()['status'] == 'processed'


def test_unittest_discovery_isolates_database_before_backend_import(tmp_path):
    root = Path(__file__).resolve().parents[1]
    trap = tmp_path / 'must-not-be-created.db'
    env = dict(os.environ, DCA_DATABASE_URL=f"sqlite:///{trap.as_posix()}", PYTHONPATH=str(root))
    env.pop('TESTING', None)
    process = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(root / 'tests'), '-p', 'test_data_quality_api.py'], cwd=tmp_path, env=env, capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    assert not trap.exists()
    assert not (tmp_path / 'dca_data.db').exists()
