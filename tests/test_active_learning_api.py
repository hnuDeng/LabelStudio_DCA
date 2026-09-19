import unittest
from backend.active_learning.api import ActiveLearningAPI

class TestActiveLearningAPI(unittest.TestCase):
    def setUp(self):
        self.api = ActiveLearningAPI()

    def test_create_config(self):
        config = self.api.create_config(
            project_id=1,
            strategy="uncertainty",
            batch_size=5
        )
        self.assertEqual(config.project_id, 1)
        self.assertEqual(config.strategy.value, "uncertainty")

    def test_update_config(self):
        # Must create first
        config = self.api.create_config(1, "uncertainty", 5)
        updated = self.api.update_config(config.id, batch_size=10)
        self.assertEqual(updated.batch_size, 10)
        
    def test_get_status(self):
        config = self.api.create_config(1, "uncertainty", 5)
        status = self.api.get_status(1)
        self.assertTrue(status["configured"])
        self.assertEqual(status["strategy"], "uncertainty")
        
    def test_select_tasks(self):
        from backend.active_learning.models import TaskData
        config = self.api.create_config(1, "uncertainty", 2)
        self.api.toggle_config(config.id) # enable it
        tasks = [
            TaskData(id=1, data={"text": "A"}), 
            TaskData(id=2, data={"text": "B"}), 
            TaskData(id=3, data={"text": "C"})
        ]
        res = self.api.select_tasks(config.id, tasks)
        self.assertIsNotNone(res)

