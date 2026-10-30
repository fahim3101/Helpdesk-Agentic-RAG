import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from ragas.embeddings import BaseRagasEmbedding
from ragas.llms import InstructorBaseRagasLLM

from rag_evaluation.evaluation.ragas_evaluator import build_embeddings, build_llm, save_results


class ResultSavingTests(unittest.TestCase):
    def test_results_are_saved_in_json_and_csv(self):
        report = pd.DataFrame([
            {
                "user_input": "How do I reset my VPN?",
                "response": "Use the VPN portal and complete MFA.",
                "faithfulness": 0.9,
                "answer_relevancy": 0.8,
                "context_precision": 0.7,
                "context_recall": 0.8,
            }
        ])

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path, csv_path = save_results(report, Path(tmpdir))
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload), 1)
            self.assertIn("user_input", payload[0])

    def test_ragas_uses_native_wrappers_for_google_models(self):
        with unittest.mock.patch("rag_evaluation.evaluation.ragas_evaluator._resolve_google_key", return_value="fake-key"):
            llm = build_llm()
            embeddings = build_embeddings()

        self.assertIsInstance(llm, InstructorBaseRagasLLM)
        self.assertIsInstance(embeddings, BaseRagasEmbedding)


if __name__ == "__main__":
    unittest.main()
