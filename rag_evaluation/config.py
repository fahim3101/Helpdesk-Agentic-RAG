from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class EvaluationSettings(BaseSettings):
    """Configuration used only by the evaluation package."""

    google_api_keys: str = ""
    google_api_key: str = ""
    gemini_model: str = "gemini-flash-lite-latest"
    embedding_model: str = "models/gemini-embedding-001"
    app_env: str = "development"
    evaluation_dataset_path: str = str(BASE_DIR / "rag_evaluation" / "dataset" / "evaluation_dataset.json")
    evaluation_results_dir: str = str(BASE_DIR / "rag_evaluation" / "results")
    evaluation_batch_size: int = 5

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")


@lru_cache
def get_settings() -> EvaluationSettings:
    return EvaluationSettings()
