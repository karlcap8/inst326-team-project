# test_integration.py

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import pandas as pd

from research_data_lib.pipeline import Pipeline
from research_data_lib.transformers import HeaderNormalizer, PIIRemover, TypeCaster
from research_data_lib.validators import RulesValidator
from research_data_lib.io_utils import (
    save_cleaned_csv,
    save_validation_report,
)


class TestPipelineIntegration(unittest.TestCase):
    def test_pipeline_and_validation_integration(self):
        """
        Integration test:
        - raw DataFrame
        - run pipeline (header normalize, PII removal, type casting)
        - run validation with simple rules
        - save outputs using I/O functions
        """
        # Step 1: Make a fake "raw CSV" DataFrame
        raw = pd.DataFrame({
            "Full Name": ["Alice", "Bob"],
            "Email": ["alice@example.com", "bob@example.com"],
            "Age": ["21", "19"],  # stored as strings → TypeCaster should convert
            "Consent": ["Yes", "No"],
        })

        # Step 2: Build pipeline
        pipeline = Pipeline([
            HeaderNormalizer(),              # converts headers → snake_case
            PIIRemover(columns=["email"]),   # drops PII column
            TypeCaster(type_map={"age": "int"}),  # cast age → int
        ])

        cleaned = pipeline.run(raw)

        # Assert pipeline steps worked
        self.assertIn("age", cleaned.columns)
        self.assertNotIn("email", cleaned.columns)
        self.assertEqual(cleaned["age"].dtype, "int64")
        self.assertListEqual(list(cleaned["age"]), [21, 19])

        # Step 3: Add validation rules
        rules = {
            "age": {"type": "int", "min": 0, "max": 120},
            "consent": {"type": "str"},
        }

        validator = RulesValidator()
        report = validator.check(cleaned, rules)

        # Assert validation report is valid
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.issues), 0)

        # Step 4: Save artifacts using I/O utilities
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            cleaned_path = save_cleaned_csv(cleaned, tmpdir / "clean.csv")
            report_path = save_validation_report(report, tmpdir / "report.md")

            self.assertTrue(cleaned_path.exists())
            self.assertTrue(report_path.exists())

            # Re-load cleaned file to confirm it was written correctly
            reloaded = pd.read_csv(cleaned_path)
            self.assertEqual(len(reloaded), 2)
            self.assertIn("age", reloaded.columns)

    def test_integration_invalid_data_detected_by_validator(self):
        """
        Integration test:
        - pipeline tries to cast bad data
        - validator should report issues
        """
        # Create data that will break validation rules
        df = pd.DataFrame({
            "email": ["a@a.com", "b@b.com"],
            "age": ["not_an_int", "still_not_int"],  # invalid type
        })

        pipeline = Pipeline([
            HeaderNormalizer(),
            PIIRemover(columns=["email"]),
            TypeCaster(type_map={"age": "int"}),
        ])

        cleaned_df = pipeline.run(df)

        rules = {
            "age": {"type": "int", "min": 0, "max": 120, "required": True},
        }

        validator = RulesValidator()
        report = validator.check(cleaned_df, rules)

        # Should detect issues
        self.assertFalse(report.is_valid)
        self.assertGreater(len(report.issues), 0)

    def test_integration_pipeline_without_pii_removal(self):
        """
        Integration test:
        - pipeline without PIIRemover
        - ensures flexibility of pipeline configuration
        """
        df = pd.DataFrame({
            "Name ": ["Alice"],
            "Age ": ["30"],
        })

        pipeline = Pipeline([
            HeaderNormalizer(),              # should normalize to "name" and "age"
            TypeCaster(type_map={"age": "int"}),
        ])

        cleaned_df = pipeline.run(df)

        # Columns should remain (no PII removal)
        self.assertIn("name", cleaned_df.columns)
        self.assertIn("age", cleaned_df.columns)

        # Types should be converted
        self.assertEqual(cleaned_df.loc[0, "age"], 30)

    def test_integration_validation_report_export(self):
        """
        Integration test:
        - run pipeline + validation
        - export validation report via I/O layer
        """
        df = pd.DataFrame({
            "email": ["x@y.com"],
            "age": ["25"],
        })

        pipeline = Pipeline([
            HeaderNormalizer(),
            PIIRemover(columns=["email"]),
            TypeCaster(type_map={"age": "int"}),
        ])

        cleaned_df = pipeline.run(df)

        rules = {
            "age": {"type": "int", "min": 0, "max": 120, "required": True},
        }

        validator = RulesValidator()
        report = validator.check(cleaned_df, rules)

        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            report_path = tmpdir / "report.md"
            save_validation_report(report, report_path)

            # File exists & contents look correct
            self.assertTrue(report_path.exists())
            text = report_path.read_text(encoding="utf-8")
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 0)

    def test_integration_pipeline_history_records_steps(self):
        """
        Integration test:
        - ensure pipeline.history records the steps that ran
        """
        df = pd.DataFrame({
            "Full Name": ["Alice"],
            "Email": ["alice@example.com"],
            "Age": ["21"],
        })

        pipeline = Pipeline([
            HeaderNormalizer(),
            PIIRemover(columns=["email"]),
            TypeCaster(type_map={"age": "int"}),
        ])

        _ = pipeline.run(df)

        # history should be a non-empty list of strings
        self.assertIsInstance(pipeline.history, list)
        self.assertGreater(len(pipeline.history), 0)
        # At least one entry should mention HeaderNormalizer (or similar)
        self.assertTrue(
            any("HeaderNormalizer" in entry for entry in pipeline.history)
        )


if __name__ == "__main__":
    unittest.main()
