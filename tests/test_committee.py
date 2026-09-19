import unittest
from backend.active_learning.strategies.committee import QueryByCommittee
import numpy as np

class TestQueryByCommittee(unittest.TestCase):
    def setUp(self):
        self.strategy = QueryByCommittee(committee_size=3, disagreement_method='vote_entropy')

    def test_compute_vote_entropy_empty(self):
        self.assertEqual(self.strategy.compute_vote_entropy([]), 0.0)

    def test_compute_vote_entropy_single(self):
        # Only one prediction -> 0 entropy
        preds = [{'result': [{'value': {'choices': ['A']}}]}]
        self.assertEqual(self.strategy.compute_vote_entropy(preds), 0.0)

    def test_compute_vote_entropy_disagreement(self):
        preds = [
            {'result': [{'value': {'choices': ['A']}}]},
            {'result': [{'value': {'choices': ['B']}}]},
            {'result': [{'value': {'choices': ['A']}}]}
        ]
        entropy = self.strategy.compute_vote_entropy(preds)
        self.assertTrue(0 < entropy <= 1.0)

    def test_select_tasks(self):
        tasks = [
            {'id': 1},
            {'id': 2},
            {'id': 3}
        ]
        predictions = {
            1: [
                {'result': [{'value': {'choices': ['A']}}]},
                {'result': [{'value': {'choices': ['B']}}]},
                {'result': [{'value': {'choices': ['A']}}]}
            ],
            2: [
                {'result': [{'value': {'choices': ['A']}}]},
                {'result': [{'value': {'choices': ['A']}}]},
                {'result': [{'value': {'choices': ['A']}}]}
            ],
            3: [
                {'result': [{'value': {'choices': ['A']}}]},
                {'result': [{'value': {'choices': ['B']}}]},
                {'result': [{'value': {'choices': ['C']}}]}
            ]
        }

        selected, scores = self.strategy.select(tasks, predictions, batch_size=2)
        self.assertEqual(len(selected), 2)

        # Task 3 has max disagreement (A, B, C)
        # Task 1 has some disagreement (A, B, A)
        # Task 2 has no disagreement (A, A, A)
        self.assertEqual(selected[0], 3)
        self.assertEqual(selected[1], 1)
        self.assertGreater(scores[3], scores[1])
        self.assertGreater(scores[1], scores[2])
