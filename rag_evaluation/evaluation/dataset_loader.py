import json
from pathlib import Path
from typing import Any

DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[1] / "dataset" / "evaluation_dataset.json"


def validate_entry(entry: dict[str, Any]) -> tuple[bool, str | None]:
    if not isinstance(entry, dict):
        return False, "Each dataset row must be a JSON object."

    if "user_input" not in entry or not str(entry["user_input"]).strip():
        return False, "Each dataset row must contain a non-empty 'user_input'."

    if "reference" not in entry or not str(entry["reference"]).strip():
        return False, "Each dataset row must contain a non-empty 'reference'."

    return True, None


def load_dataset(dataset_path: str | Path | None = None) -> list[dict[str, str]]:
    """Load and validate the evaluation dataset from JSON."""
    path = Path(dataset_path) if dataset_path is not None else DEFAULT_DATASET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at: {path}")

    with path.open("r", encoding="utf-8") as handle:
        raw_data = json.load(handle)

    if isinstance(raw_data, dict):
        raw_data = raw_data.get("data", raw_data.get("items", []))

    if not isinstance(raw_data, list):
        raise ValueError("Evaluation dataset must be a list of objects or a dict containing a list.")

    validated: list[dict[str, str]] = []
    for index, entry in enumerate(raw_data, start=1):
        ok, message = validate_entry(entry)
        if not ok:
            raise ValueError(f"Dataset entry {index} is invalid: {message}")
        validated.append({
            "user_input": str(entry["user_input"]).strip(),
            "reference": str(entry["reference"]).strip(),
        })

    if not validated:
        raise ValueError("Evaluation dataset is empty.")

    return validated
