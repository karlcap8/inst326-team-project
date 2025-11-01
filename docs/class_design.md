### Dataset Class

**Purpose:**  
The `Dataset` class represents a collection of research data records (rows) and provides tools for cleaning, transforming, and validating them. It serves as the foundation of the Research Data Pipeline by encapsulating data and connecting multiple functions from Project 1 within an object-oriented design. This allows users to manage datasets more intuitively, ensuring data integrity and reproducibility.

**Key Attributes:**
- `_name` (`str`): Dataset name, used for identification.  
- `_rows` (`list[dict]`): Stores the dataset as a list of dictionaries.  
- `_rename_map` (`dict[str, str]`): Defines how to rename or drop columns.  
- `_type_map` (`dict[str, str]`): Defines how to cast column types (e.g., `int`, `float`, `datetime`).  
- `_pii_columns` (`set[str]`): Contains columns to drop for privacy.  
- `_cleaned` (`bool`): Indicates whether the dataset has been cleaned.  
- `_last_validation_issues` (`list[dict]`): Stores the most recent validation results.  

**Key Methods:**
- `clean_headers()` – Normalizes column names using `normalize_header()` from Project 1.  
- `apply_rename_map()` – Renames or drops columns using `rename_columns()`.  
- `cast_types()` – Converts column data types using `cast_row_types()`.  
- `drop_pii()` – Removes sensitive (PII) fields from the dataset.  
- `validate()` – Checks data quality and consistency using `validate_dataset()`.  

**Encapsulation & Access Control:**  
All attributes are private (prefixed with `_`) to prevent external modification.  
Properties such as `name`, `columns`, `n_rows`, and `is_cleaned` provide controlled, read-only access.  
This enforces proper encapsulation and prevents data corruption.

**Integration with Project 1:**  
This class directly integrates four core functions from Project 1:  
`normalize_header`, `rename_columns`, `cast_row_types`, and `validate_dataset`.  
By encapsulating them inside methods, the Dataset class transitions from a procedural to an object-oriented design while maintaining code reusability.

**Example Usage:**
```python
from src.dataset import Dataset

rows = [
    {"Q1": "19", "Q2": "Yes", "Email Address": "a@b.com", "joined": "2024-10-01"},
    {"Q1": "21", "Q2": "No",  "Email Address": "c@d.com", "joined": "2024-10-03"},
]

ds = Dataset(
    rows,
    name="pilot_survey",
    rename_map={"Q1": "age", "Q2": "consent", "Email Address": ""},
    type_map={"age": "int", "consent": "bool", "joined": "datetime:%Y-%m-%d"},
)

ds.clean_headers()
ds.apply_rename_map()
ds.cast_types()
issues = ds.validate({
    "age": {"type": "int", "min": 0, "max": 120, "required": True},
    "consent": {"type": "bool", "required": True},
    "joined": {"type": "datetime:%Y-%m-%d", "required": True},
})

print(ds)
```


### DataPipeline Class

**Purpose:**
The `DataPipeline` class provides a modular framework for managing and transforming research datasets throughout the cleaning and preparation stages. It encapsulates common preprocessing tasks—such as whitespace removal, missing value imputation, dataset merging, and data reporting—into an object-oriented structure. This design enables researchers to run sequential data operations while maintaining a clear record of each transformation step, ensuring reproducibility and consistency across datasets.

**Key Attributes:**
- `_df (pd.DataFrame)`: Stores the working dataset.
- `_name (str)`: Name or identifier for the pipeline instance.
- `_history (list[str])`: Keeps a log of all operations performed on the dataset.
- `_is_cleaned (bool)`: Tracks whether cleaning steps have been applied.
- `_last_report_path (str)`: Stores the most recent generated report’s file path.

**Key Methods:**
- `strip_text()` – Removes extra whitespace from all string columns using `strip_whitespace()`.
- `fill_missing(strategy="median")` – Fills missing numeric values based on a defined strategy using `fill_missing_values()`.
- `merge(datasets, how="outer")` – Combines multiple DataFrames into one unified dataset with `merge_datasets()`.
- `generate_report(filename)` – Creates a detailed text-based report summarizing dataset statistics via `generate_data_report()`.
- `snapshot()` – Returns a short preview of the cleaned dataset for quick inspection.

**Encapsulation & Access Control:**
Core attributes are private (prefixed with `_`) to prevent accidental modification and ensure data integrity. Read-only access is provided through properties such as `name`, `shape`, `history`, and `is_cleaned`. This design enforces encapsulation while maintaining transparency in data transformations.

**Integration with Project 1:**
The `DataPipeline` class integrates four key functions from Project 1:
- `strip_whitespace()`
- `fill_missing_values()`
- `merge_datasets()`
- `generate_data_report()`
By embedding these functions as methods, the class demonstrates the transition from procedural programming to object-oriented design, promoting modularity, reusability, and cleaner code organization.

**Example Usage:**
```python
import pandas as pd
from src.data_pipeline import DataPipeline

df1 = pd.DataFrame({
    "Name": [" Alice ", "Bob ", "  Carol"],
    "Age": [25, None, 29],
    "Department": ["Research ", " Dev", " Research"]
})

df2 = pd.DataFrame({
    "Name": ["Dave", "Eve"],
    "Age": [31, 27],
    "Department": ["Dev", "Research"]
})

pipeline = DataPipeline(df1, name="employee_batch_1")

pipeline.strip_text()
pipeline.fill_missing(strategy="mean")
pipeline.merge([df2], how="outer")
report_path = pipeline.generate_report("output/employee_report.txt")

print(pipeline)
print("Shape:", pipeline.shape)
print("History:", pipeline.history)
print("Snapshot:\n", pipeline.snapshot().head())
```
