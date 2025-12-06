# test_system_workflow.py

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import json

import pandas as pd

from app import run_workflow


class TestSystemWorkflow(unittest.TestCase):
    def _make_sample_csv(self, path: Path) -> None:
        """Helper to write a small sample survey CSV to `path`."""
        df = pd.DataFrame(
            {
                "Name": ["Alice", "Bob"],
                "Email": ["alice@example.com", "bob@example.com"],
                "Phone": ["555-1111", "555-2222"],
                "Age": [21, 19],
                "Consent": ["Yes", "No"],
            }
        )
        df.to_csv(path, index=False)

    def test_run_workflow_happy_path_with_state(self):
        """
        System test:

        - Create a real CSV file
        - Call run_workflow with output + state paths
        - Assert cleaned CSV, validation report, and state file exist
        - Assert state has expected keys
        """
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            input_csv = tmpdir / "raw.csv"
            output_dir = tmpdir / "outputs"
            state_file = tmpdir / "state.json"

            # Create sample CSV
            self._make_sample_csv(input_csv)

            # Run the full workflow
            exit_code = run_workflow(input_csv, output_dir, state_file)

            self.assertEqual(exit_code, 0)
            cleaned_path = output_dir / "cleaned_survey.csv"
            report_path = output_dir / "validation_report.md"

            self.assertTrue(cleaned_path.exists(), "cleaned_survey.csv was not created")
            self.assertTrue(report_path.exists(), "validation_report.md was not created")
            self.assertTrue(state_file.exists(), "state.json was not created")

            # Check that state file has config + history
            state = json.loads(state_file.read_text(encoding="utf-8"))
            self.assertIn("config", state)
            self.assertIn("history", state)
            self.assertIsInstance(state["history"], list)

    def test_run_workflow_happy_path_without_state(self):
        """
        System test:

        - Same as above, but do not provide a state path
        - Ensure workflow still succeeds and outputs are created
        """
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            input_csv = tmpdir / "raw.csv"
            output_dir = tmpdir / "outputs"

            self._make_sample_csv(input_csv)

            exit_code = run_workflow(input_csv, output_dir, state_path=None)

            self.assertEqual(exit_code, 0)
            cleaned_path = output_dir / "cleaned_survey.csv"
            report_path = output_dir / "validation_report.md"

            self.assertTrue(cleaned_path.exists())
            self.assertTrue(report_path.exists())

    def test_run_workflow_missing_input_file(self):
        """
        System test:

        - Give run_workflow a non-existent CSV path
        - Expect a non-zero exit code and no outputs/state
        """
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            input_csv = tmpdir / "missing.csv"  # we do NOT create this file
            output_dir = tmpdir / "outputs"
            state_file = tmpdir / "state.json"

            exit_code = run_workflow(input_csv, output_dir, state_file)

            self.assertNotEqual(exit_code, 0)
            self.assertFalse(output_dir.exists(), "Output dir should not exist on failure")
            self.assertFalse(state_file.exists(), "State file should not exist on failure")


if __name__ == "__main__":
    unittest.main()
