# Research Data Cleaning & Validation Pipeline  
### INST326 — Object-Oriented Programming for Information Science  
### Project 4

**Team:** Harrang Khalsa, Karl Capili, Sukhman Singh  
**Section:** 0301
**Date:** December 14, 2025
**Video Presentation Link:** https://drive.google.com/file/d/1CiS73ZGS9PSQ6WQos8D_KT_5sw6jBrWP/view?usp=sharing

---

# Overview

This project implements a survey data cleaning and validation pipeline using advanced object-oriented programming concepts:

- Inheritance via an abstract `Transformer` base class  
- Polymorphism through interchangeable data-cleaning steps  
- Composition in a `Pipeline` that executes multiple Transformers in sequence  
- Design patterns including the Template Method and Strategy patterns  

The system transforms raw survey exports (e.g., from Qualtrics or Google Forms) into clean, validated, analysis-ready datasets.

---
## 🧭 Domain: Survey Data Cleaning & Validation

Our project focuses on the **Survey Data Cleaning & Validation** domain, specializing in transforming raw survey exports (e.g., Qualtrics, Google Forms) into clean, standardized, and validated datasets suitable for research analysis.

Survey datasets often contain:
- Messy or inconsistent column names (e.g., “Q1 - Age”)
- Mixed data types (“19” as a string, “Yes/No” as text)
- Personally identifiable information (PII)
- Missing or invalid responses
- Columns with inconsistent formatting across survey waves

Our pipeline addresses these issues through:
This project implements a complete, modular Research Survey Data Pipeline that:

Cleans survey data through a configurable pipeline of transformers

Removes or anonymizes PII

Casts values into consistent data types

Validates cleaned data using rule-based checks

Saves the cleaned dataset, validation report, and a JSON state file

Provides a complete command-line interface for real end-to-end usage

Includes full unit, integration, and system test coverage

This domain mirrors real-world research workflows in academic labs, UX teams, and social science datasets.

This work extends Project 3 by adding a formal Python package (research_data_lib), a persistence layer, and the full CLI tool (app.py).
---

# System Architecture

## Inheritance Hierarchy

### Transformer Hierarchy
```

Transformer (ABC)
├── HeaderNormalizer
├── PIIRemover
└── TypeCaster

```

### Validator Hierarchy
```

RulesValidator
└── ValidationReport
└── ValidationIssue

```

## Composition Relationships

```

Pipeline
├── has-many Transformer objects
└── produces a cleaned DataFrame + step history log

RulesValidator
└── produces a ValidationReport
└── which contains multiple ValidationIssue objects

````

---

# Core Components

## 1. Transformer (Abstract Base Class)

Defines the shared interface and behavior for all cleaning steps.

**Abstract requirements:**
- `_apply(df)` – subclass-specific transformation logic  
- `required_columns` – columns required for the step to run  

**Concrete shared logic:**
- `apply()` – template method that:
  - Performs preflight validation  
  - Calls the subclass `_apply`  
  - Logs step history  

This ensures uniform behavior across all cleaning classes.

---

## 2. Concrete Transformers

### HeaderNormalizer
Normalizes messy column headers (e.g., `"Q1 - Age"` → `q1_age`).

### PIIRemover
Removes personally identifiable information (email, phone, names).

### TypeCaster
Converts survey values to the appropriate data types:
- `"19"` → `19`
- `"Yes"` → `True`

---

## 3. Pipeline (Composition)

The `Pipeline` composes multiple Transformers and executes them in sequence.

Example:
```python
steps = [
    HeaderNormalizer(),
    PIIRemover(["email_address"]),
    TypeCaster({"q1_age": "int"})
]
pipe = Pipeline(steps)
cleaned = pipe.run(df)
````

The Pipeline does not need to know the type of each step.
It simply calls `apply()` on all of them.
This is polymorphism.

---

## 4. Validators

### RulesValidator

Runs rule-based validation such as:

* Required fields
* Value ranges
* Data-type enforcement
* Allowed categories

### ValidationReport

Stores all issues and provides:

* `is_valid` boolean
* `to_markdown()` formatted output
* A list of `ValidationIssue` objects

---

# Class Diagram

```mermaid
classDiagram
    class Transformer{
      <<abstract>>
      +apply(df)
      +_apply(df)*
      +required_columns*
      +history()
    }

    Transformer <|-- HeaderNormalizer
    Transformer <|-- PIIRemover
    Transformer <|-- TypeCaster

    class Pipeline{
      -steps: List~Transformer~
      +run(df)
      +history
    }

    class ValidationIssue{
      column: str
      message: str
    }

    class ValidationReport{
      issues: List~ValidationIssue~
      +is_valid
      +to_markdown()
    }

    class RulesValidator{
      +check(df, rules) ValidationReport
    }

    Pipeline --> Transformer
    RulesValidator --> ValidationReport
    ValidationReport --> ValidationIssue
```

---

# Polymorphism Examples

### Example: Pipeline calling `apply()` without knowing the subclass type

```python
for step in steps:
    df = step.apply(df)
```

Behavior differs per subclass, but the interface stays the same.

Benefits:

* Steps are interchangeable
* New Transformers can be added freely
* No type-checking or conditional logic
* Pipeline stays simple

This follows the **Strategy Pattern**.

---

# Usage Example

```python
import pandas as pd
from transformers import HeaderNormalizer, PIIRemover, TypeCaster
from pipeline import Pipeline
from validators import RulesValidator

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

print(cleaned)
print(report.to_markdown())
```

**Expected Output:**

```
   q1_age  q2_consent
0      19        True
1      21       False
All checks passed 🎉
```

---

# Running the Demo

```
python demo.py
```

---

# Running Tests

```
python -m unittest test_survey_system -v
```

Tests verify:

* Inheritance
* Abstract method enforcement
* Polymorphism in Pipeline
* Behavior of each Transformer
* Validation logic and reporting

---
## 🧩 Design Decisions

Our design is centered around clear separation of concerns, extensibility, and the use of object-oriented design principles.

### 1. Use of an Abstract Base Class (ABC)
We created a `Transformer` abstract class to define the required interface for all cleaning steps:
- Every transformer must implement `_apply(self, df)`
- Every transformer declares `required_columns`
- Shared behavior (`apply`, `_preflight`, `_log`, `history`) lives in the ABC

**Why?**  
This enforces consistency and allows the Pipeline to treat all cleaning steps uniformly, enabling polymorphism.

---

### 2. Polymorphism via the Pipeline
The `Pipeline` executes a list of Transformers without caring about their concrete types.  
This is classic **Strategy pattern** behavior.

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/karlcap8/inst326-team-project
cd inst326-team-project
```
### 2. Install dependencies
Dependencies are listed in requirements.txt.

Install them with:

```bash
pip install -r requirements.txt
```
### 3. Verify installation
Run the unit tests:

```bash
python -m unittest test_survey_system -v
```
Run the demo script:

```bash
python demo.py
```
If both commands run without errors, the project is correctly installed.

### Requirements
- Python 3.10+
- pandas
- numpy

All dependencies are included in the repository’s requirements.txt.

---

```markdown
## ▶️ Basic Usage Guide With Examples

### 1. Prepare a CSV file
Place your raw survey CSV in a directory such as:

```

data/sample_survey.csv

````

### 2. Run the app on a dataset

```bash
py -3 app.py data/sample_survey.csv --output-dir outputs --state-file state/state.json
````

This will generate:

* `outputs/cleaned_survey.csv`
* `outputs/validation_report.md`
* `state/state.json`

### 3. Run the app without saving state

```bash
py -3 app.py data/sample_survey.csv --no-state
```

### 4. Output example (terminal)

```
[INFO] Loaded raw CSV with shape: (3, 6)
[INFO] Pipeline finished. Cleaned shape: (3, 4)
[INFO] Cleaned dataset saved to: outputs/cleaned_survey.csv
[INFO] Validation report saved to: outputs/validation_report.md
[INFO] State saved to: state/state.json
```

---

## 🧪 Running Tests

### Run all tests (Project 3 + Project 4)

```bash
py -3 -m unittest
```

### Run a specific test file

```bash
py -3 -m unittest test_io_and_state.py
```

### Included test suites

| Test File                 | Description                                     |
| ------------------------- | ----------------------------------------------- |
| `test_survey_system.py`   | Baseline tests from Project 3                   |
| `test_io_and_state.py`    | Unit tests for I/O + state saving               |
| `test_integration.py`     | Tests pipeline + validator + I/O together       |
| `test_system_workflow.py` | System tests using full `run_workflow` function |

All tests currently pass.

# 🔧 Configuration

DEFAULT_PII_COLUMNS, DEFAULT_TYPE_MAP, and DEFAULT_VALIDATION_RULES appear in app.py.

These should be customized based on your survey schema.

Example:
```
DEFAULT_PII_COLUMNS = ["name", "email", "phone"]

DEFAULT_TYPE_MAP = {
    "age": "int",
    "consent": "bool",
}

DEFAULT_VALIDATION_RULES = {
    "age": {"type": "int", "min": 0, "max": 120, "required": True},
    "consent": {"type": "bool", "required": True},
}
```

# File Structure

```
inst326-team-project/
│
├── app.py                           # Main CLI application (Project 4)
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
│
├── research_data_lib/               # Project 4 Python package
│   ├── __init__.py
│   ├── base_classes.py              # Abstract base classes for pipeline steps
│   ├── dataset.py                   # Dataset helpers (legacy from Project 3)
│   ├── pipeline.py                  # Pipeline class (step composition)
│   ├── research_data_lib.py         # Core functions from Project 1 (normalize, cast, etc.)
│   ├── transformers.py              # HeaderNormalizer, PIIRemover, TypeCaster
│   ├── validators.py                # RulesValidator + ValidationReport
│   └── io_utils.py                  # CSV loading, saving, and JSON state persistence
│
├── test_survey_system.py            # Original Project 3 tests
├── test_io_and_state.py             # Unit tests for I/O + state (Project 4)
├── test_integration.py              # Integration tests (pipeline + validator + I/O)
├── test_system_workflow.py          # System tests (full workflow via run_workflow)
│
├── outputs/                         # Example output directory (auto-created)
├── state/                           # Example state directory (auto-created)
└── data/                            # Sample datasets (optional)

```

---

# Requirement Checklist

### Inheritance

* Abstract base class
* Concrete subclasses
* Proper `super()` usage

### Polymorphism

* Pipeline executes all Transformers via shared interface

### Composition

* Pipeline has multiple Transformer objects
* RulesValidator produces a ValidationReport

### Design Patterns

* Template Method
* Strategy Pattern

### Testing

* All tests included in `test_survey_system.py`

### Documentation

* Updated README
* Architecture document in `/docs/Architecture.md`

---

# Team Information

| Team Member     | Contributions                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| **Karl Capili** | Pipeline development, I/O utilities, app CLI implementation, architecture documentation, system tests |
| **Harrang**     | Transformer implementations, rule validation logic, integration tests, test design, debugging         |
| **Sukhman**     | Dataset helpers, unit testing, documentation, code review, presentation                               |
| **ALL**         | Had an even distribution of technical and documentation work contributions throughout this project    |

