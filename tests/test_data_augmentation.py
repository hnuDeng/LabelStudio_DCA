import unittest
from backend.data_augmentation.augmenters import TextAugmenter, NumericAugmenter, CategoricalAugmenter

class TestDataAugmentation(unittest.TestCase):
    def test_text_augmenter(self):
        augmenter = TextAugmenter(random_swap=True, random_deletion=True)
        data = {"text": "hello world from active learning", "other": 123}

        # Test basic output
        res = augmenter.augment(data, num_samples=3)
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0]["other"], 123)

        # Original text has 5 words. random_swap or random_deletion might change it.
        # Let's just verify it returns a valid string.
        self.assertIsInstance(res[0]["text"], str)

    def test_numeric_augmenter(self):
        augmenter = NumericAugmenter(noise_std=0.1, scale_range=(0.9, 1.1))
        data = {"val1": 10.0, "val2": 5, "text": "hello"}

        res = augmenter.augment(data, num_samples=2)
        self.assertEqual(len(res), 2)

        # Type checks
        self.assertIsInstance(res[0]["val1"], float)
        self.assertIsInstance(res[0]["val2"], float)
        self.assertEqual(res[0]["text"], "hello") # text should be untouched

    def test_categorical_augmenter(self):
        categories = {"label": ["positive", "negative", "neutral"]}
        # High probability to guarantee a flip
        augmenter = CategoricalAugmenter(flip_probability=1.0, categories=categories)
        data = {"label": "positive", "score": 10}

        res = augmenter.augment(data, num_samples=1)
        self.assertEqual(len(res), 1)
        self.assertIn(res[0]["label"], ["negative", "neutral"])
        self.assertEqual(res[0]["score"], 10) # unaffected
