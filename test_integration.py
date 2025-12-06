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
            "Age": ["21", "19"],        # stored as strings → TypeCaster should convert
            "Consent": ["Yes", "No"]
        })

        # Step 2: Build pipeline
        pipeline = Pipeline([
            HeaderNormalizer(),             # converts headers → snake_case
            PIIRemover(columns=["email"]),  # drops PII column
            TypeCaster(type_map={"age": "int"})  # cast age → int
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


if __name__ == "__main__":
    unittest.main()
