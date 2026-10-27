import tests

import unittest
import numpy as np
from backend.anomaly_detection.engine import AnomalyDetectionEngine

class TestAnomalyDetectionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AnomalyDetectionEngine(project_id=1)

    def test_detect_anomalies(self):
        # Generate random data
        data = np.random.normal(0, 1, size=(100, 5))

        # Inject an anomaly (large z-score)
        data[0] = np.array([10.0, 10.0, 10.0, 10.0, 10.0])

        results = self.engine.detect_anomalies(data)
        self.assertIn("statistical", results["detector_results"])
        self.assertIn("isolation_forest", results["detector_results"])
        self.assertEqual(results["total_samples"], 100)
        self.assertGreaterEqual(results["total_anomalies"], 1)

    def test_invalid_detector(self):
        data = np.random.normal(0, 1, size=(10, 5))
        results = self.engine.detect_anomalies(data, detectors=["unknown_detector"])
        self.assertIn("unknown_detector", results["detector_results"])
        self.assertIn("error", results["detector_results"]["unknown_detector"])
