import tests

import unittest
from backend.data_versioning.version_control import DataVersionControl

class TestDataVersionControl(unittest.TestCase):
    def setUp(self):
        self.vcs = DataVersionControl(project_id=888) # unique project id

    def test_create_version(self):
        data = {"tasks": [1, 2, 3]}
        version = self.vcs.create_version(data=data, description="Initial")
        self.assertIsNotNone(version.version_id)
        self.assertEqual(version.description, "Initial")

    def test_get_history(self):
        v1 = self.vcs.create_version(data={"tasks": [1]}, description="A")
        v2 = self.vcs.create_version(data={"tasks": [1, 2]}, description="B")

        history = self.vcs.get_history()
        self.assertGreaterEqual(len(history), 2)
        descriptions = [h.description for h in history]
        self.assertIn("A", descriptions)
        self.assertIn("B", descriptions)
