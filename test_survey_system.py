import unittest
import pandas as pd

from research_data_lib.transformers import HeaderNormalizer, PIIRemover, TypeCaster
from research_data_lib.pipeline import Pipeline
from research_data_lib.validators import RulesValidator, ValidationReport



class TestHeaderNormalizer(unittest.TestCase):
    def test_header_normalizer_changes_headers(self):
        """HeaderNormalizer should normalize raw column names to snake_case."""
        df = pd.DataFrame({
            "Q1 - Age": [19, 21],
            "Email Address": ["a@umd.edu", "b@umd.edu"]
        })

        step = HeaderNormalizer()
        out = step.apply(df)

        # Columns should be snake_case versions of the originals
        self.assertIn("q1_age", out.columns)
        self.assertIn("email_address", out.columns)

        # Data should be unchanged except for header names
        self.assertListEqual(out["q1_age"].tolist(), [19, 21])
        self.assertListEqual(out["email_address"].tolist(), ["a@umd.edu", "b@umd.edu"])


class TestPIIRemover(unittest.TestCase):
    def test_pii_remover_drops_columns(self):
        """PIIRemover should drop configured PII columns and keep non-PII."""
        df = pd.DataFrame({
            "email_address": ["a@umd.edu", "b@umd.edu"],
            "age": [20, 21],
            "phone_number": ["123", "456"]
        })

        step = PIIRemover(columns=["email_address", "phone_number"])
        out = step.apply(df)

        # PII columns should be removed
        self.assertNotIn("email_address", out.columns)
        self.assertNotIn("phone_number", out.columns)

        # Non-PII column should remain
        self.assertIn("age", out.columns)
        self.assertListEqual(out["age"].tolist(), [20, 21])


class TestTypeCaster(unittest.TestCase):
    def test_type_caster_casts_types(self):
        """TypeCaster should cast configured columns to requested types."""
        df = pd.DataFrame({
            "age": ["19", "21"],
            "consent": ["Yes", "no"]
        })

        step = TypeCaster(type_map={"age": "int", "consent": "bool"})
        out = step.apply(df)

        # age should be integer-typed
        self.assertIn(out["age"].dtype.kind, ("i", "u"))
        self.assertListEqual(out["age"].tolist(), [19, 21])

        # consent should be boolean and all values True/False
        self.assertTrue(out["consent"].isin([True, False]).all())
        # And the logical casting should match the inputs
        self.assertListEqual(out["consent"].tolist(), [True, False])


class TestValidation(unittest.TestCase):
    def test_validation_report_passes_when_no_issues(self):
        """RulesValidator should produce a valid report when all rules pass."""
        df = pd.DataFrame({
            "age": [25, 30],
            "consent": [True, False]
        })

        rules = {
            "age": {
                "type": "int",
                "min": 0,
                "max": 120,
                "required": True,
            },
            "consent": {
                "type": "bool",
                "required": True,
            }
        }

        validator = RulesValidator()
        report: ValidationReport = validator.check(df, rules)

        # No issues should be reported
        self.assertTrue(report.is_valid)
        self.assertEqual(len(report.issues), 0)
        # Optional: markdown output should indicate success
        md = report.to_markdown()
        self.assertIn("All checks passed", md)


class TestPipeline(unittest.TestCase):
    def test_pipeline_runs_all_steps_in_order(self):
        """
        Pipeline should run each Transformer in sequence and reflect combined effects:
        - HeaderNormalizer normalizes headers.
        - PIIRemover removes PII columns.
        """
        df = pd.DataFrame({
            "Q1 - Age": [19],
            "Email Address": ["a@umd.edu"]
        })

        steps = [
            HeaderNormalizer(),
            PIIRemover(columns=["email_address"]),
        ]
        pipe = Pipeline(steps)
        out = pipe.run(df)

        # HeaderNormalizer: header normalized
        self.assertIn("q1_age", out.columns)

        # PIIRemover: email_address removed
        self.assertNotIn("email_address", out.columns)

        # Data still intact in remaining column
        self.assertListEqual(out["q1_age"].tolist(), [19])


if __name__ == "__main__":
    unittest.main()
