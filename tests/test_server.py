import tests

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from backend.server import app

class TestServer(unittest.TestCase):
    def setUp(self):
        secret_patch = patch("backend.server.LABEL_STUDIO_WEBHOOK_SECRET", "test-webhook-secret")
        secret_patch.start()
        self.addCleanup(secret_patch.stop)
        environment_patch = patch.dict(os.environ, {"LABEL_STUDIO_ALLOW_UNSIGNED_WEBHOOKS": "false"})
        environment_patch.start()
        self.addCleanup(environment_patch.stop)
        self.client = TestClient(app)
        self.headers = {"Authorization": "Bearer test-webhook-secret"}

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "DCA Server is running"})

    def test_label_studio_webhook_rejects_missing_token(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={"action": "ANNOTATION_CREATED", "project": {"id": 1}},
        )
        self.assertEqual(response.status_code, 403)

    def test_label_studio_webhook_rejects_wrong_token(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={"action": "TASKS_CREATED", "project": {"id": 1}},
            headers={"Authorization": "Bearer wrong-secret"},
        )
        self.assertEqual(response.status_code, 403)

    def test_label_studio_webhook_rejects_malformed_authorization(self):
        for authorization in (
            "", "test-webhook-secret", "Basic test-webhook-secret",
            "Bearer", "Bearer ", "Bearer  test-webhook-secret",
        ):
            with self.subTest(authorization=authorization):
                response = self.client.post(
                    "/api/webhooks/label-studio",
                    json={"action": "TASKS_CREATED", "project": {"id": 1}},
                    headers={"Authorization": authorization},
                )
                self.assertEqual(response.status_code, 403)

    def test_label_studio_webhook_rejects_non_ascii_token(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={"action": "TASKS_CREATED", "project": {"id": 1}},
            headers={b"Authorization": b"Bearer \xff"},
        )
        self.assertEqual(response.status_code, 403)

    def test_label_studio_webhook_rejects_placeholder_signature(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={"action": "TASKS_CREATED", "project": {"id": 1}},
            headers={"x-label-studio-signature": "anything-except-invalid_signature"},
        )
        self.assertEqual(response.status_code, 403)

    def test_label_studio_webhook_fails_closed_without_secret(self):
        with patch("backend.server.LABEL_STUDIO_WEBHOOK_SECRET", ""):
            response = self.client.post(
                "/api/webhooks/label-studio",
                json={"action": "TASKS_CREATED", "project": {"id": 1}},
                headers=self.headers,
            )
        self.assertEqual(response.status_code, 503)

    def test_health_check_without_webhook_configuration(self):
        with patch("backend.server.LABEL_STUDIO_WEBHOOK_SECRET", ""):
            response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_label_studio_webhook_allows_explicit_unsigned_demo(self):
        with patch("backend.server.LABEL_STUDIO_WEBHOOK_SECRET", ""), patch.dict(
            os.environ, {"LABEL_STUDIO_ALLOW_UNSIGNED_WEBHOOKS": "true"}
        ):
            response = self.client.post(
                "/api/webhooks/label-studio",
                json={"action": "TASKS_CREATED", "project": {"id": 1}},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "unsupported")

    def test_label_studio_webhook_secret_overrides_unsigned_demo(self):
        with patch.dict(os.environ, {"LABEL_STUDIO_ALLOW_UNSIGNED_WEBHOOKS": "true"}):
            response = self.client.post(
                "/api/webhooks/label-studio",
                json={"action": "TASKS_CREATED", "project": {"id": 1}},
            )
        self.assertEqual(response.status_code, 403)

    def test_label_studio_webhook_valid(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={"action": "TASKS_CREATED", "project": {"id": 1}, "tasks": [{"id": 100}]},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["action"], "TASKS_CREATED")
        self.assertEqual(response.json()["status"], "unsupported")

    def test_label_studio_webhook_annotation(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={
                "action": "ANNOTATION_CREATED",
                "project": {"id": 1},
                "task": {"id": 100},
                "annotation": {"id": 200, "result": []}
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["action"], "ANNOTATION_CREATED")
        self.assertEqual(response.json()["status"], "insufficient_data")
