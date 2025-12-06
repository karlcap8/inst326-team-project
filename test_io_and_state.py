# test_io_and_state.py

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from research_data_lib.io_utils import (
    load_raw_csv,
    save_cleaned_csv,
    save_state,
    load_state,
    save_validation_report,
    StateFileError,
)
from research_data_lib.validators import ValidationReport


class TestIOUtils(unittest.TestCase):
    def test_load_raw_csv_success(self):
        """load_raw_csv reads a valid CSV into a non-empty DataFrame."""
        with TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "raw.csv"

            df = pd.DataFrame(
                {
                    "Name": ["Alice", "Bob"],
                    "Age": [21, 19],
                }
            )
            df.to_csv(tmp_path, index=False)

            loaded = load_raw_csv(tmp_path)
            self.assertEqual(len(loaded), 2)
            self.assertListEqual(list(loaded.columns), ["Name", "Age"])

    def test_load_raw_csv_missing_file(self):
        """load_raw_csv raises FileNotFoundError for a missing file."""
        with TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "does_not_exist.csv"
            with self.assertRaises(FileNotFoundError):
                load_raw_csv(missing_path)

    def test_save_cleaned_csv_writes_file(self):
        """save_cleaned_csv writes a CSV file to disk."""
        with TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "cleaned.csv"
            df = pd.DataFrame({"col": [1, 2, 3]})

            written_path = save_cleaned_csv(df, out_path)

            self.assertTrue(written_path.exists())
            reloaded = pd.read_csv(written_path)
            self.assertEqual(len(reloaded), 3)
            self.assertListEqual(list(reloaded["col"]), [1, 2, 3])

    def test_save_and_load_state_roundtrip(self):
        """save_state + load_state round-trips config and history."""
        with TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"

            config = {
                "input_csv": "data/sample_survey.csv",
                "output_dir": "outputs",
                "pii_columns": ["email"],
            }
            history = ["HeaderNormalizer()", "PIIRemover(columns=['email'])"]

            save_state(state_path, config=config, history=history)

            loaded = load_state(state_path)
            self.assertIn("config", loaded)
            self.assertIn("history", loaded)
            self.assertEqual(loaded["config"], config)
            self.assertEqual(loaded["history"], history)

    def test_load_state_invalid_json_raises(self):
        """load_state raises StateFileError when JSON is invalid."""
        with TemporaryDirectory() as tmpdir:
            state_path = Path(tmpdir) / "state.json"

            # Write invalid JSON
            state_path.write_text("{ this is not valid json }", encoding="utf-8")

            with self.assertRaises(StateFileError):
                load_state(state_path)

    def test_save_validation_report_writes_file(self):
        """save_validation_report writes the report markdown to disk."""
        with TemporaryDirectory() as tmpdir:
            report_path = Path(tmpdir) / "report.md"

            # A minimal ValidationReport: no issues
            report = ValidationReport(issues=[])

            written_path = save_validation_report(report, report_path)
            self.assertTrue(written_path.exists())

            content = written_path.read_text(encoding="utf-8")
            self.assertIsInstance(content, str)
            self.assertGreater(len(content), 0)
            # Optional extra check:
            self.assertIn("All checks passed", content)



if __name__ == "__main__":
    unittest.main()
