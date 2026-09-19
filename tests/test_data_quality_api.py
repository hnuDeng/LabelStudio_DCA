import unittest
from backend.data_quality.api import DataQualityAPI

class TestDataQualityAPI(unittest.TestCase):
    def setUp(self):
        self.api = DataQualityAPI()

    def test_run_assessment(self):
        tasks = [{"id": 1}, {"id": 2}]
        annotations = [
            {"task_id": 1, "annotator_id": 1, "result": []},
            {"task_id": 2, "annotator_id": 1, "result": []}
        ]
        
        report = self.api.run_assessment(project_id=1, tasks=tasks, annotations=annotations)
        self.assertIsNotNone(report.id)
        self.assertEqual(report.project_id, 1)
        self.assertTrue(hasattr(report, "overall_score"))
        self.assertTrue(hasattr(report, "issues"))
        
    def test_get_dashboard_data(self):
        data = self.api.get_dashboard_data(999) # DB might have data for 1
        print("DEBUG DATA:", data)
        self.assertFalse(data["has_data"])
        
        tasks = [{"id": 1}]
        annotations = [{"task_id": 1, "annotator_id": 1, "result": []}]
        self.api.run_assessment(999, tasks, annotations)
        
        data = self.api.get_dashboard_data(999)
        self.assertTrue(data["has_data"])
        self.assertEqual(data["project_id"], 999)
