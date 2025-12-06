# app.py
"""
Project 4 main entrypoint for the Research Survey Data Pipeline.

Usage (from repo root):
    py -3 app.py path/to/raw_survey.csv --output-dir outputs --state-file state/state.json
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from research_data_lib.pipeline import Pipeline
from research_data_lib.transformers import HeaderNormalizer, PIIRemover, TypeCaster
from research_data_lib.validators import RulesValidator
from research_data_lib.io_utils import (
    load_raw_csv,
    save_cleaned_csv,
    save_validation_report,
    save_state,
)


# ---------------------------------------------------------------------
# Default configuration (you can tweak for your actual survey schema)
# ---------------------------------------------------------------------

# Columns that are considered PII in your survey export.
# Update this list to match your real column names.
DEFAULT_PII_COLUMNS = [
    "email",
    "name",
    "phone",
]

# Type labels must match what cast_row_types in research_data_lib.py understands.
# Replace keys with your actual question/column names.
DEFAULT_TYPE_MAP = {
    # "age": "int",
    # "consent": "bool",
}

# Simple example validation rules; customize for your dataset.
DEFAULT_VALIDATION_RULES: Dict[str, Dict[str, Any]] = {
    # "age": {"type": "int", "min": 0, "max": 120, "required": True},
    # "consent": {"type": "bool", "required": True},
}


def build_pipeline() -> Pipeline:
    """
    Construct the standard cleaning pipeline:

    1. Normalize headers to snake_case.
    2. Remove PII columns.
    3. Cast selected columns to appropriate types.
    """
    steps = [
        HeaderNormalizer(),
        PIIRemover(columns=DEFAULT_PII_COLUMNS),
        TypeCaster(type_map=DEFAULT_TYPE_MAP),
    ]
    return Pipeline(steps)


def run_workflow(
    input_csv: Path,
    output_dir: Path,
    state_path: Path | None = None,
) -> int:
    """
    Run the full survey cleaning + validation workflow.

    Steps:
      1. Load raw CSV.
      2. Run cleaning pipeline.
      3. Validate cleaned data.
      4. Save cleaned CSV and validation report.
      5. Optionally save JSON state (config + history).

    Returns:
        Exit code (0 = success, non-zero = error).
    """
    try:
        raw_df = load_raw_csv(input_csv)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERROR] {e}")
        return 1

    print(f"[INFO] Loaded raw CSV with shape: {raw_df.shape}")

    # Build and run pipeline
    pipe = build_pipeline()
    cleaned_df = pipe.run(raw_df)

    print(f"[INFO] Pipeline finished. Cleaned shape: {cleaned_df.shape}")

    # Run rules-based validation (if any rules are defined)
    validator = RulesValidator()
    if DEFAULT_VALIDATION_RULES:
        report = validator.check(cleaned_df, DEFAULT_VALIDATION_RULES)
    else:
        # If no rules are configured yet, create a dummy "all good" report.
        # This keeps the flow working until you define real rules.
        report = validator.check(cleaned_df, {})

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save artifacts
    cleaned_path = save_cleaned_csv(cleaned_df, output_dir / "cleaned_survey.csv")
    report_path = save_validation_report(report, output_dir / "validation_report.md")

    print(f"[INFO] Cleaned dataset saved to: {cleaned_path}")
    print(f"[INFO] Validation report saved to: {report_path}")
    print()
    print("Validation summary:")
    print(report.to_markdown())

    # Save state (optional but recommended for Project 4)
    if state_path is not None:
        config = {
            "input_csv": str(input_csv),
            "output_dir": str(output_dir),
            "pii_columns": DEFAULT_PII_COLUMNS,
            "type_map": DEFAULT_TYPE_MAP,
            "rules": DEFAULT_VALIDATION_RULES,
        }
        save_state(state_path, config=config, history=pipe.history)
        print(f"\n[INFO] State saved to: {state_path}")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Research Survey Data Cleaning & Validation Pipeline"
    )
    parser.add_argument(
        "input_csv",
        type=str,
        help="Path to the raw survey CSV export (e.g., from Qualtrics).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Directory where cleaned data and reports will be written.",
    )
    parser.add_argument(
        "--state-file",
        type=str,
        default="state/state.json",
        help="Path to JSON file where pipeline state will be stored.",
    )
    parser.add_argument(
        "--no-state",
        action="store_true",
        help="If set, do not write a JSON state file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_csv = Path(args.input_csv)
    output_dir = Path(args.output_dir)
    state_path = None if args.no_state else Path(args.state_file)

    exit_code = run_workflow(input_csv, output_dir, state_path)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
