"""
Base class for active learning strategies.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """Base class for all active learning strategies."""

    def __init__(self, **kwargs):
        """
        Initialize strategy with parameters.

        Args:
            **kwargs: Strategy-specific parameters
        """
        self.params = kwargs

    @abstractmethod
    def compute_scores(
        self, tasks: List[Dict[str, Any]], predictions: Dict[int, List[Dict]], **kwargs
    ) -> Dict[int, float]:
        """
        Compute selection scores for tasks.

        Args:
            tasks: List of task data dictionaries
            predictions: Dictionary mapping task_id to predictions
            **kwargs: Additional parameters

        Returns:
            Dictionary mapping task_id to score (higher = more informative)
        """
        raise NotImplementedError

    @abstractmethod
    def select(
        self,
        tasks: List[Dict[str, Any]],
        predictions: Dict[int, List[Dict]],
        batch_size: int,
        **kwargs
    ) -> Tuple[List[int], Dict[int, float]]:
        """
        Select tasks for annotation.

        Args:
            tasks: List of task data dictionaries
            predictions: Dictionary mapping task_id to predictions
            batch_size: Number of tasks to select
            **kwargs: Additional parameters

        Returns:
            Tuple of (selected_task_ids, all_scores)
        """
        raise NotImplementedError

    def _extract_probabilities(self, prediction: Dict) -> Optional[np.ndarray]:
        """
        Extract probability distribution from prediction.

        Args:
            prediction: Prediction dictionary

        Returns:
            numpy array of probabilities or None
        """
        result = prediction.get("result", [])

        for item in result:
            value = item.get("value", {})

            # Handle choices with scores
            if "choices" in value:
                choices = value["choices"]
                if isinstance(choices, dict):
                    return np.array(list(choices.values()))
                elif isinstance(choices, list):
                    # Uniform probability for each choice
                    return np.ones(len(choices)) / len(choices)

            # Handle numeric scores
            if "score" in value:
                return np.array([value["score"], 1 - value["score"]])

        return None

    def _get_prediction_for_task(
        self, task_id: int, predictions: Dict[int, List[Dict]]
    ) -> List[Dict]:
        """
        Get predictions for a specific task.

        Args:
            task_id: Task ID
            predictions: All predictions

        Returns:
            List of predictions for the task
        """
        return predictions.get(task_id, [])

    def _normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """
        Normalize scores to [0, 1] range.

        Args:
            scores: Dictionary of task_id to score

        Returns:
            Normalized scores
        """
        if not scores:
            return scores

        values = list(scores.values())
        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return {k: 0.5 for k in scores}

        return {k: (v - min_val) / (max_val - min_val) for k, v in scores.items()}
