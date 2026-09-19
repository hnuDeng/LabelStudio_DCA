import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple, Any


class BaseAnomalyDetector(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        pass


class IsolationForestDetector(BaseAnomalyDetector):
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        # Mock logic
        scores = np.random.uniform(0, 1, size=len(data))
        is_anomaly = scores > 0.8
        return scores, is_anomaly


class LocalOutlierFactorDetector(BaseAnomalyDetector):
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        scores = np.random.uniform(0, 1, size=len(data))
        is_anomaly = scores > 0.9
        return scores, is_anomaly


class StatisticalDetector(BaseAnomalyDetector):
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if len(data) == 0:
            return np.array([]), np.array([], dtype=bool)
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0) + 1e-6
        z_scores = (
            np.max(np.abs((data - mean) / std), axis=1)
            if len(data.shape) > 1
            else np.abs((data - mean) / std)
        )
        is_anomaly = z_scores > 3.0
        return z_scores, is_anomaly
