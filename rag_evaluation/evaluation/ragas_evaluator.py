from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd
from google import genai
from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset
from ragas.embeddings import GoogleEmbeddings
from ragas.embeddings.base import BaseRagasEmbedding
from ragas.llms import llm_factory


class GoogleEmbeddingCompat(BaseRagasEmbedding):
    """Compatibility adapter for Ragas metrics that still call embed_query()."""

    def __init__(self, inner: GoogleEmbeddings):
        super().__init__()
        self.inner = inner

    def embed_text(self, text: str, **kwargs):
        return self.inner.embed_text(text, **kwargs)

    async def aembed_text(self, text: str, **kwargs):
        return await self.inner.aembed_text(text, **kwargs)

    def embed_query(self, text: str):
        return self.inner.embed_text(text)

    def embed_documents(self, texts: list[str]):
        return [self.inner.embed_text(text) for text in texts]

    async def aembed_query(self, text: str):
        return await self.inner.aembed_text(text)

    async def aembed_documents(self, texts: list[str]):
        return await self.inner.aembed_texts(texts)

from app.core.keypool import google_keys
from app.rag.vectorstore import get_retriever
from app.rag.workflow import ask
from rag_evaluation.config import get_settings
from rag_evaluation.evaluation.metrics import build_evaluation_metrics


def _resolve_google_key() -> str:
    settings = get_settings()
    keys = google_keys() or [settings.google_api_key or settings.google_api_keys]
    selected = next((k for k in keys if k and str(k).strip()), None)
    if not selected:
        raise ValueError(
            "No Google API key is configured. Set GOOGLE_API_KEYS or GOOGLE_API_KEY in the project .env file."
        )
    return selected


def build_llm():
    """Create a Ragas-compatible Gemini LLM using the modern Google GenAI client."""
    settings = get_settings()
    key = _resolve_google_key()
    client = genai.Client(api_key=key)
    return llm_factory(
        model=settings.gemini_model,
        provider="google",
        client=client,
        adapter="instructor",
        temperature=0,
    )


def build_embeddings():
    """Create a Ragas-compatible Gemini embedding model using the modern Google client."""
    settings = get_settings()
    key = _resolve_google_key()
    client = genai.Client(api_key=key)
    inner = GoogleEmbeddings(
        client=client,
        model=settings.embedding_model,
    )
    return GoogleEmbeddingCompat(inner)


def collect_rag_record(question: str, reference: str) -> dict[str, Any]:
    """Invoke the real existing RAG pipeline and retrieve the actual contexts."""
    try:
        answer_result = ask(question)
    except Exception as exc:  # pragma: no cover - depends on live LLM state
        raise RuntimeError(f"Existing RAG pipeline failed for question: {question!r}") from exc

    answer = str(answer_result.get("answer", "")).strip()
    if not answer:
        raise ValueError(f"Generated answer is empty for question: {question!r}")

    try:
        docs = get_retriever().invoke(question)
    except Exception as exc:  # pragma: no cover - depends on vector store state
        raise RuntimeError(f"Retriever failed for question: {question!r}") from exc

    contexts = [
        str(doc.page_content).strip()
        for doc in docs
        if getattr(doc, "page_content", "").strip()
    ]
    if not contexts:
        raise ValueError(f"No retrieved contexts were returned for question: {question!r}")

    return {
        "user_input": question,
        "response": answer,
        "retrieved_contexts": contexts,
        "reference": reference,
    }


def prepare_dataframe(dataset_rows: list[dict[str, str]]) -> pd.DataFrame:
    """Prepare the exact DataFrame shape required by the installed Ragas version."""
    records = [collect_rag_record(row["user_input"], row["reference"]) for row in dataset_rows]
    return pd.DataFrame(
        records,
        columns=["user_input", "response", "retrieved_contexts", "reference"],
    )


def run_ragas_evaluation(dataset_rows: list[dict[str, str]], *, limit: int | None = None) -> tuple[pd.DataFrame, Any]:
    """Execute the evaluation pipeline using the actual app workflow and retrieval layer."""
    selected = dataset_rows[:limit] if limit is not None else dataset_rows
    if not selected:
        raise ValueError("No dataset rows were provided for evaluation.")

    data_frame = prepare_dataframe(selected)
    llm = build_llm()
    embeddings = build_embeddings()
    metrics = build_evaluation_metrics(llm=llm, embeddings=embeddings)
    dataset = EvaluationDataset.from_pandas(data_frame)
    result = evaluate(
        dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        show_progress=False,
        raise_exceptions=True,
    )
    report = result.to_pandas()
    return report, result


def save_results(report: pd.DataFrame, output_dir: str | Path) -> tuple[Path, Path]:
    """Persist evaluation results to JSON and CSV for reporting."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = output_path / "ragas_evaluation_results.json"
    csv_path = output_path / "ragas_evaluation_results.csv"

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(report.to_dict(orient="records"), handle, ensure_ascii=False, indent=2)

    report.to_csv(csv_path, index=False)
    return json_path, csv_path
