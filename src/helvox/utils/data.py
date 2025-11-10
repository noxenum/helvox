import json
from pathlib import Path


def read_dataset(path: Path) -> list[dict]:
    """
    Reads a JSON dataset from the given path and validates its structure.
    Expected format:
        [
            {"id": "string", "de": "string"},
            ...
        ]
    """
    with open(path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    # Check that the top-level element is a list
    if not isinstance(data, list):
        raise ValueError(f"Invalid format: expected a list, got {type(data).__name__}")

    # Validate each item in the list
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(
                f"Invalid item at index {i}: expected dict, got {type(item).__name__}"
            )
        if "id" not in item or "de" not in item:
            raise ValueError(
                f"Missing required keys in item at index {i}: found {list(item.keys())}"
            )

    return data
