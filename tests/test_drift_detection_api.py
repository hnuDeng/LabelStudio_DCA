import unittest
from backend.drift_detection.api import DriftDetectionAPI
import numpy as np

class TestDriftDetectionAPI(unittest.TestCase):
    def setUp(self):
        self.api = DriftDetectionAPI()

    def test_create_baseline(self):
        # We need mock task data that the FeatureDriftDetector can parse
        tasks = [{"data": {"feat1": 0.0, "feat2": 1.0}} for _ in range(10)]
        annotations = [{"result": [{"value": {"choices": ["A"]}}]} for _ in range(10)]

        baseline = self.api.create_baseline(
            project_id=1,
            name="test_baseline",
            tasks=tasks,
            annotations=annotations
        )
        self.assertEqual(baseline.project_id, 1)
        self.assertEqual(baseline.name, "test_baseline")
        self.assertEqual(baseline.sample_count, 10)

    def test_run_detection(self):
        tasks = [{"data": {"feat1": 0.0}} for _ in range(10)]
        annotations = [{"result": [{"value": {"choices": ["A"]}}]} for _ in range(10)]

        baseline = self.api.create_baseline(1, "test", tasks, annotations)

        # Test drift detection
        shifted_tasks = [{"data": {"feat1": 100.0}} for _ in range(10)]
        shifted_annotations = [{"result": [{"value": {"choices": ["B"]}}]} for _ in range(10)]

        report = self.api.run_detection(1, baseline.id, shifted_tasks, shifted_annotations)
        self.assertIsNotNone(report)
        self.assertTrue(hasattr(report, "drift_level"))
        self.assertTrue(hasattr(report, "overall_drift_score"))

    def test_get_alerts(self):
        alerts = self.api.get_alerts(1)
        self.assertEqual(len(alerts), 0)

        # Acknowledge logic
        # We can just manually create an alert
        alert = self.api.create_alert(1, 1, "feature", "Test alert")
        alerts_active = self.api.get_alerts(1, status="active")
        self.assertEqual(len(alerts_active), 1)

        self.api.acknowledge_alert(alert.id, user_id=10)
        alerts_after = self.api.get_alerts(1, status="acknowledged")
        self.assertEqual(len(alerts_after), 1)
