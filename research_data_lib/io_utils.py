from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import json

import pandas as pd

from .validators import ValidationReport


class StateFileError(Exception):
    """Raised when a state file is present but invalid."""


def _ensure_parent_dir(path: Path) -> None:
    """
    Ensure the parent directory for `path` exists.
    Does nothing if it already exists.
    """
    path.parent.mkdir(parents=True, exist_ok=True)


def load_raw_csv(path: str | Path) -> pd.DataFrame:
    """
    Load a raw survey CSV into a DataFrame with basic error handling.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file cannot be parsed as CSV or is empty.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input CSV not found: {p}")

    try:
        df = pd.read_csv(p)
    except Exception as e:
        raise ValueError(f"Failed to read CSV at {p}: {e}") from e

    if df.empty:
        raise ValueError(f"CSV at {p} is empty or has no data rows")

    return df


def save_cleaned_csv(df: pd.DataFrame, path: str | Path) -> Path:
    """
    Save the cleaned survey data to CSV (no index).
    Returns the Path to the written file.
    """
    p = Path(path)
    _ensure_parent_dir(p)
    df.to_csv(p, index=False)
    return p


def save_validation_report(report: ValidationReport, path: str | Path) -> Path:
    """
    Save a ValidationReport as a Markdown/text file.
    Returns the Path to the written file.
    """
    p = Path(path)
    _ensure_parent_dir(p)
    text = report.to_markdown()
    p.write_text(text, encoding="utf-8")
    return p


def save_state(
    path: str | Path,
    *,
    config: Dict[str, Any],
    history: List[str],
) -> Path:
    """
    Save a simple JSON state file containing configuration + pipeline history.

    The JSON structure is:
    {
        "config": {...},
        "history": [...]
    }
    """
    p = Path(path)
    _ensure_parent_dir(p)

    state = {
        "config": config,
        "history": history,
    }
    p.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return p


def load_state(path: str | Path) -> Dict[str, Any]:
    """
    Load a JSON state file created by save_state.

    Returns:
        Parsed state dict with 'config' and 'history' keys.

    Raises:
        FileNotFoundError: if the file does not exist.
        StateFileError: if JSON is invalid or missing required keys.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"State file not found: {p}")

    try:
        raw = p.read_text(encoding="utf-8")
        state = json.loads(raw)
    except json.JSONDecodeError as e:
        raise StateFileError(f"State file {p} contains invalid JSON: {e}") from e

    if not isinstance(state, dict) or "config" not in state or "history" not in state:
        raise StateFileError(
            f"State file {p} must contain a JSON object with 'config' and 'history' keys"
        )

    return state