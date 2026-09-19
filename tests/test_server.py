import unittest
from fastapi.testclient import TestClient
from backend.server import app

class TestServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "message": "DCA Server is running"})

    def test_label_studio_webhook_invalid_signature(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={"action": "ANNOTATION_CREATED", "project": {"id": 1}},
            headers={"x-label-studio-signature": "invalid_signature"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {"detail": "Invalid signature"})

    def test_label_studio_webhook_valid(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={"action": "TASKS_CREATED", "project": {"id": 1, "tasks": [{"id": 100}]}},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["action"], "TASKS_CREATED")

    def test_label_studio_webhook_annotation(self):
        response = self.client.post(
            "/api/webhooks/label-studio",
            json={
                "action": "ANNOTATION_CREATED",
                "project": {"id": 1},
                "task": {"id": 100},
                "annotation": {"id": 200, "result": []}
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["action"], "ANNOTATION_CREATED")
        self.assertEqual(response.json()["message"], "Processed annotation via DCA pipeline")
