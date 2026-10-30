"""Evaluation logic for standalone RAG benchmarking."""

from .dataset_loader import load_dataset
from .ragas_evaluator import run_ragas_evaluation

__all__ = ["load_dataset", "run_ragas_evaluation"]
