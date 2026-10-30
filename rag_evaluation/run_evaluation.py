from __future__ import annotations

import argparse
from pathlib import Path

from rag_evaluation.config import get_settings
from rag_evaluation.evaluation.dataset_loader import load_dataset
from rag_evaluation.evaluation.metrics import METRIC_SUMMARY
from rag_evaluation.evaluation.ragas_evaluator import run_ragas_evaluation, save_results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a standalone RAG evaluation using Ragas.")
    parser.add_argument("--dataset", type=str, default=None, help="Path to the evaluation dataset JSON file.")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on how many evaluation rows to process.")
    parser.add_argument("--results-dir", type=str, default=None, help="Directory where JSON and CSV reports will be written.")
    return parser.parse_args()


def print_metric_overview() -> None:
    print("\nRAGAS metrics used:")
    for key, details in METRIC_SUMMARY.items():
        print(f"- {details['name']}: {details['purpose']}")


def main() -> int:
    args = parse_args()
    settings = get_settings()

    dataset_path = args.dataset or settings.evaluation_dataset_path
    results_dir = args.results_dir or settings.evaluation_results_dir

    dataset = load_dataset(dataset_path)
    selected_rows = dataset[: args.limit] if args.limit is not None else dataset

    print(f"Loaded {len(dataset)} evaluation rows.")
    print(f"Evaluating {len(selected_rows)} rows.")
    print_metric_overview()

    report, _ = run_ragas_evaluation(selected_rows)
    json_path, csv_path = save_results(report, results_dir)

    print("\nEvaluation results saved to:")
    print(f"- JSON: {json_path}")
    print(f"- CSV:  {csv_path}")
    print("\nReport preview:")
    print(report.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
