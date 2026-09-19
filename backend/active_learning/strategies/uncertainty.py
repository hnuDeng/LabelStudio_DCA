"""
Uncertainty sampling strategies for active learning.
"""

import logging
from typing import Any, Dict, List, Tuple

import numpy as np

from backend.active_learning.strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


class UncertaintySampling(BaseStrategy):
    """
    Uncertainty sampling strategy.

    Selects tasks where the model is most uncertain about its predictions.
    """

    METHODS = ["least_confidence", "margin_sampling", "entropy"]

    def __init__(self, method: str = "entropy", **kwargs):
        """
        Initialize uncertainty sampling.

        Args:
            method: Uncertainty calculation method
                - 'least_confidence': 1 - max(probability)
                - 'margin_sampling': 1 - (p1 - p2) where p1, p2 are top-2 probabilities
                - 'entropy': Shannon entropy of probability distribution
        """
        super().__init__(**kwargs)

        if method not in self.METHODS:
            raise ValueError(f"Unknown method: {method}. Available: {self.METHODS}")

        self.method = method

    def compute_uncertainty(self, probabilities: np.ndarray) -> float:
        """
        Compute uncertainty score for a probability distribution.

        Args:
            probabilities: Probability distribution

        Returns:
            Uncertainty score (higher = more uncertain)
        """
        if probabilities is None or len(probabilities) == 0:
            return 1.0  # Maximum uncertainty for no predictions

        # Ensure probabilities sum to 1
        probabilities = probabilities / probabilities.sum()

        if self.method == "least_confidence":
            # 1 - maximum probability
            return 1.0 - np.max(probabilities)

        elif self.method == "margin_sampling":
            # 1 - margin between top-2 probabilities
            sorted_probs = np.sort(probabilities)[::-1]
            if len(sorted_probs) >= 2:
                return 1.0 - (sorted_probs[0] - sorted_probs[1])
            return 1.0 - sorted_probs[0]

        elif self.method == "entropy":
            # Shannon entropy
            # Add small epsilon to avoid log(0)
            probs = np.clip(probabilities, 1e-10, 1.0)
            entropy = -np.sum(probs * np.log(probs))
            # Normalize by max entropy
            max_entropy = np.log(len(probabilities))
            if max_entropy > 0:
                return entropy / max_entropy
            return 0.0

        else:
            raise ValueError(f"Unknown method: {self.method}")

    def compute_task_uncertainty(self, predictions: List[Dict]) -> float:
        """
        Compute uncertainty for a task based on its predictions.

        Args:
            predictions: List of predictions for the task

        Returns:
            Average uncertainty score
        """
        if not predictions:
            return 1.0  # Maximum uncertainty for no predictions

        uncertainties = []

        for pred in predictions:
            probabilities = self._extract_probabilities(pred)
            if probabilities is not None:
                uncertainty = self.compute_uncertainty(probabilities)
                uncertainties.append(uncertainty)

        if not uncertainties:
            return 1.0

        return float(np.mean(uncertainties))

    def compute_scores(
        self, tasks: List[Dict[str, Any]], predictions: Dict[int, List[Dict]], **kwargs
    ) -> Dict[int, float]:
        """
        Compute uncertainty scores for all tasks.

        Args:
            tasks: List of task data dictionaries
            predictions: Dictionary mapping task_id to predictions

        Returns:
            Dictionary mapping task_id to uncertainty score
        """
        scores = {}

        for task in tasks:
            task_id = task["id"]
            task_predictions = self._get_prediction_for_task(task_id, predictions)
            uncertainty = self.compute_task_uncertainty(task_predictions)
            scores[task_id] = uncertainty

        # Normalize scores
        scores = self._normalize_scores(scores)

        logger.debug(
            f"Computed uncertainty scores for {len(tasks)} tasks "
            f"(method: {self.method}, avg: {np.mean(list(scores.values())):.3f})"
        )

        return scores

    def select(
        self,
        tasks: List[Dict[str, Any]],
        predictions: Dict[int, List[Dict]],
        batch_size: int,
        **kwargs,
    ) -> Tuple[List[int], Dict[int, float]]:
        """
        Select most uncertain tasks.

        Args:
            tasks: List of task data dictionaries
            predictions: Dictionary mapping task_id to predictions
            batch_size: Number of tasks to select

        Returns:
            Tuple of (selected_task_ids, all_scores)
        """
        # Compute scores
        scores = self.compute_scores(tasks, predictions)

        # Sort by score (descending) and select top-k
        sorted_tasks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        selected_ids = [task_id for task_id, _ in sorted_tasks[:batch_size]]

        logger.info(
            f"Selected {len(selected_ids)} tasks using uncertainty sampling "
            f"(method: {self.method})"
        )

        return selected_ids, scores


class LeastConfidence(UncertaintySampling):
    """Least confidence sampling strategy."""

    def __init__(self, **kwargs):
        super().__init__(method="least_confidence", **kwargs)


class MarginSampling(UncertaintySampling):
    """Margin sampling strategy."""

    def __init__(self, **kwargs):
        super().__init__(method="margin_sampling", **kwargs)


class EntropySampling(UncertaintySampling):
    """Entropy-based uncertainty sampling strategy."""

    def __init__(self, **kwargs):
        super().__init__(method="entropy", **kwargs)
