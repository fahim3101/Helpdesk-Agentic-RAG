import json
import tempfile
import unittest
from pathlib import Path

from rag_evaluation.evaluation.dataset_loader import load_dataset, validate_entry


class DatasetLoaderTests(unittest.TestCase):
    def test_valid_dataset_is_loaded(self):
        sample = [
            {"user_input": "How do I reset my password?", "reference": "Use the self-service portal."},
            {"user_input": "What is MFA?", "reference": "MFA is mandatory for protected systems."},
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "dataset.json"
            dataset_path.write_text(json.dumps(sample), encoding="utf-8")
            loaded = load_dataset(dataset_path)
            self.assertEqual(len(loaded), 2)
            self.assertIn("user_input", loaded[0])
            self.assertIn("reference", loaded[0])

    def test_missing_required_fields_are_rejected(self):
        bad_entry = {"user_input": "This question has no reference."}
        ok, msg = validate_entry(bad_entry)
        self.assertFalse(ok)
        self.assertIn("reference", msg.lower())

    def test_empty_dataset_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dataset_path = Path(tmpdir) / "dataset.json"
            dataset_path.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_dataset(dataset_path)


if __name__ == "__main__":
    unittest.main()
