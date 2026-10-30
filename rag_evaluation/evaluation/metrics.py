from __future__ import annotations

from ragas.metrics import AnswerRelevancy, ContextPrecision, ContextRecall, Faithfulness


def build_evaluation_metrics(llm, embeddings=None):
    """Create the metric objects required by the installed Ragas version."""
    metrics = [
        Faithfulness(llm=llm),
        ContextPrecision(llm=llm),
        ContextRecall(llm=llm),
    ]
    metrics.insert(1, AnswerRelevancy(llm=llm, embeddings=embeddings))
    return metrics


METRIC_SUMMARY = {
    "faithfulness": {
        "name": "Faithfulness",
        "purpose": "Checks whether the generated answer is supported by the retrieved evidence.",
    },
    "answer_relevancy": {
        "name": "Answer Relevancy",
        "purpose": "Measures how well the answer addresses the original user question.",
    },
    "context_precision": {
        "name": "Context Precision",
        "purpose": "Measures whether the retrieved contexts are ranked and selected usefully.",
    },
    "context_recall": {
        "name": "Context Recall",
        "purpose": "Measures whether the retrieved contexts cover the information needed to answer the question.",
    },
}
