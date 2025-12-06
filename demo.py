import pandas as pd
from research_data_lib.transformers import HeaderNormalizer, PIIRemover, TypeCaster
from research_data_lib.validators import RulesValidator
from research_data_lib.pipeline import Pipeline


def main():
    df = pd.DataFrame({
        "Q1 - Age": ["19", "21"],
        "Q2 - Consent": ["Yes", "no"],
        "Email Address": ["a@umd.edu", "b@umd.edu"]
    })

    steps = [
        HeaderNormalizer(),
        PIIRemover(["email_address"]),
        TypeCaster({"q1_age": "int", "q2_consent": "bool"})
    ]

    pipe = Pipeline(steps)
    cleaned = pipe.run(df)

    rules = {
        "q1_age": {"type": "int", "min": 0, "max": 120, "required": True},
        "q2_consent": {"type": "bool", "required": True}
    }

    report = RulesValidator().check(cleaned, rules)

    print("Cleaned Data:")
    print(cleaned)
    print(report.to_markdown())

if __name__ == "__main__":
    main()
