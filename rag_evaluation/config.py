from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class EvaluationSettings(BaseSettings):
    """Configuration used only by the evaluation package."""

    google_api_keys: str = ""
    google_api_key: str = ""
    # Models are tried in this order. Keep only models that the Google API
    # still serves: retired IDs return 404 and overloaded ones return 503.
    gemini_model: str = "gemini-3.6-flash"
    gemini_fallback_models: list[str] = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
    ]
    embedding_model: str = "models/gemini-embedding-001"
    app_env: str = "development"
    evaluation_dataset_path: str = str(BASE_DIR / "rag_evaluation" / "dataset" / "evaluation_dataset.json")
    evaluation_results_dir: str = str(BASE_DIR / "rag_evaluation" / "results")
    evaluation_batch_size: int = 2

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


@lru_cache
def get_settings() -> EvaluationSettings:
    return EvaluationSettings()
