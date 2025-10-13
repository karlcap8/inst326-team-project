## Research Data Pipeline Function Library - Reference Guide
# This document provides comprehensive reference information for all functions in the research data library.

## Function Reference

---

### normalize_header(name: str) -> str  
**Purpose:**  
Normalize a column header to safe `snake_case` format for CSV or SQL use.  

**Parameters:**  
- **name** (`str`): The raw column header text (e.g., `"Q3 - Overall Satisfaction (1-5)"`).  

**Returns:**  
- `str` — A cleaned and standardized header (e.g., `"q3_overall_satisfaction_1_5"`).  

**Raises:**  
- `TypeError` — If `name` is not a string.  

**Behavior:**  
- Converts all characters to lowercase.  
- Replaces non-alphanumeric symbols with underscores.  
- Collapses multiple underscores and trims leading/trailing ones.  
- Returns `"unnamed"` if the result is empty.  
- Prefixes `"col_"` if the cleaned name begins with a digit.  

**Example Usage:**  
```python
from src.research_data_lib import normalize_header

# Standard header
header = normalize_header("Q3 - Overall Satisfaction (1-5)")
# Returns: 'q3_overall_satisfaction_1_5'

# Removes spaces and symbols
header = normalize_header("   Email Address ")
# Returns: 'email_address'

# Handles numeric headers
header = normalize_header("123")
# Returns: 'col_123'

# Handles empty or symbol-only headers
header = normalize_header("!!!")
# Returns: 'unnamed'
````

---

### cast_row_types(row: dict, type_map: dict[str, str]) -> dict

**Purpose:**
Convert a row’s string-based values into the appropriate data types (e.g., `int`, `float`, `bool`, or `datetime`).
This ensures data consistency when cleaning survey or research datasets.

**Parameters:**

* **row** (`dict`): A single record mapping column names to raw string values.
* **type_map** (`dict[str, str]`): A mapping of column names to target type labels.

  * Supported types: `"int"`, `"float"`, `"bool"`, `"str"`, or `"datetime:<format>"`

    * Example: `"datetime:%Y-%m-%d"`

**Returns:**

* `dict` — A new dictionary where values are cast to their specified types.

**Raises:**

* `TypeError` — If `row` or `type_map` is not a dictionary.
* `ValueError` — If an unsupported type label is provided.

**Behavior:**

* Converts values using Python’s built-in type casting (with safe fallbacks).
* Handles blank or null-like entries (`"na"`, `"n/a"`, `"null"`) as `None`.
* Converts boolean-like strings (`"yes"`, `"true"`, `"1"`) to `True` and (`"no"`, `"false"`, `"0"`) to `False`.
* Parses dates according to the provided format in `datetime:<format>`.
* Leaves invalid or uncastable values unchanged.

**Example Usage:**

```python
from src.research_data_lib import cast_row_types

row = {
    'age': '19',
    'score': '3.5',
    'consent': 'Yes',
    'joined': '2024-10-01',
    'note': 'ok'
}

type_map = {
    'age': 'int',
    'score': 'float',
    'consent': 'bool',
    'joined': 'datetime:%Y-%m-%d'
}

result = cast_row_types(row, type_map)
print(result)
# Example output:
# {
#   'age': 19,
#   'score': 3.5,
#   'consent': True,
#   'joined': datetime.datetime(2024, 10, 1, 0, 0),
#   'note': 'ok'
# }
```

---

### rename_columns(row: dict, rename_map: dict[str, str], *, drop_unmapped: bool = False, normalize_targets: bool = True) -> dict

**Purpose:**
Rename or remove columns in a single dataset row based on a provided mapping, ensuring clean, standardized column names.
Useful for converting raw survey headers (e.g., “Q1”, “Email Address”) into meaningful, analysis-friendly names.

**Parameters:**

* **row** (`dict`): A single record mapping column names to their values.
* **rename_map** (`dict[str, str]`): Mapping of old column names to new names.

  * Use an empty string `""` to drop a column entirely.
* **drop_unmapped** (`bool`, optional): If `True`, columns not in `rename_map` are dropped. Defaults to `False`.
* **normalize_targets** (`bool`, optional): If `True`, cleans new column names using `normalize_header()` for safe formatting. Defaults to `True`.

**Returns:**

* `dict` — A new dictionary with renamed (and possibly dropped) keys.

**Raises:**

* `TypeError` — If either `row` or `rename_map` is not a dictionary.

**Behavior:**

* Renames columns according to the mapping provided.
* Drops columns with empty string mappings or unmapped columns (if `drop_unmapped=True`).
* Cleans target names to ensure they’re lowercase and underscore-separated.
* Prevents naming collisions by automatically suffixing duplicates (e.g., `_2`, `_3`).

**Example Usage:**

```python
from src.research_data_lib import rename_columns

row = {
    'Q1': '19',
    'Q2': 'Yes',
    'Email Address': 'a@b.com',
    'Note': 'ok'
}

rename_map = {
    'Q1': 'age',
    'Q2': 'consent',
    'Email Address': ''  # drop PII
}

result = rename_columns(row, rename_map)
print(result)
# Example output:
# {'age': '19', 'consent': 'Yes', 'Note': 'ok'}
```

---

### validate_dataset(rows: list[dict], rules: dict) -> list[dict]

**Purpose:**
Validate an entire dataset (a list of rows) against a set of defined rules for each column.
This ensures research data meets consistency, accuracy, and integrity standards before analysis.

**Parameters:**

* **rows** (`list[dict]`): A list of records (each row is a dictionary mapping column names to values).
* **rules** (`dict`): A mapping of column names to validation rule sets.
  Each rule set can include:

  * `required` (`bool`): Column must exist and be non-null.
  * `not_null` (`bool`): Value must not be null.
  * `type` (`str`): Expected data type (`'int'`, `'float'`, `'bool'`, `'str'`, `'datetime:<format>'`).
  * `min`, `max` (`number`): Allowed numeric range.
  * `len_min`, `len_max` (`int`): Allowed string length range.
  * `allowed` (`list`|`set`): Allowed categorical values.
  * `regex` (`str`): Pattern string for valid matches.
  * `unique` (`bool`): Values must be unique across all rows.

**Returns:**

* `list[dict]` — A list of issues found during validation.
  Each issue is represented as:

  ```python
  {
      "row_idx": int,
      "column": str,
      "rule": str,
      "value": any,
      "message": str
  }
  ```

**Raises:**

* `TypeError` — If `rows` is not a list or `rules` is not a dictionary.

**Behavior:**

* Automatically casts values using `cast_row_types()` before validation.
* Flags missing, null, or invalid data based on defined rules.
* Checks data types, numeric ranges, string lengths, allowed values, and regex patterns.
* Enforces uniqueness rules across rows.
* Treats `"na"`, `"n/a"`, `"null"`, and empty strings as null values.
* Returns all detected issues without halting execution.

**Example Usage:**

```python
from src.research_data_lib import validate_dataset

rows = [
    {"id": "A1", "age": "19", "consent": "Yes", "score": "3.5", "joined": "2024-10-01"},
    {"id": "A2", "age": "-5", "consent": "no",  "score": "x",   "joined": "2024-13-01"},
    {"id": "A1", "age": "200", "consent": "Y",  "score": "4.2", "joined": "2024-09-30"},
    {"id": "",   "age": "  ",  "consent": "",   "score": "",    "joined": ""}
]

rules = {
    "id": {"type": "str", "required": True, "len_min": 1, "unique": True},
    "age": {"type": "int", "min": 0, "max": 120, "required": True},
    "consent": {"type": "bool", "required": True},
    "score": {"type": "float", "min": 0.0, "max": 5.0},
    "joined": {"type": "datetime:%Y-%m-%d"}
}

issues = validate_dataset(rows, rules)
print(f"Issues found: {len(issues)}")
for issue in issues:
    print(issue)
```

**Example Output:**

```python
Issues found: 6
{'row_idx': 1, 'column': 'age', 'rule': 'min', 'value': -5, 'message': 'Value -5 < min 0.'}
{'row_idx': 1, 'column': 'score', 'rule': 'type', 'value': 'x', 'message': 'Expected float.'}
{'row_idx': 1, 'column': 'joined', 'rule': 'type', 'value': '2024-13-01', 'message': 'Expected datetime:%Y-%m-%d.'}
{'row_idx': 2, 'column': 'age', 'rule': 'max', 'value': 200, 'message': 'Value 200 > max 120.'}
{'row_idx': 3, 'column': 'id', 'rule': 'required', 'value': '', 'message': 'Required column missing or null.'}
{'row_idx': 2, 'column': 'id', 'rule': 'unique', 'value': 'A1', 'message': 'Duplicate value violates uniqueness.'}
```

---
### strip_whitespace(df: pd.DataFrame) -> pd.DataFrame

**Purpose:** 
Remove leading and trailing whitespace from all string-type columns in a pandas DataFrame.

**Parameters:** 

* df (pd.DataFrame): Input dataset containing string and/or numeric columns.

**Returns:** 

* pd.DataFrame - A new DataFrame with all string columns cleaned of extra spaces.

**Raises:** 

* TypeError - If the input is not a pandas DataFrame.

**Behavior:** 

* Operates only on columns with dtype object or string.

* Creates and returns a copy, leaving the original DataFrame unmodified.

* Uses pandas .str.strip() to clean whitespace from text fields

**Example Usage**

```python
from src.research_data_lib import strip_whitespace
import pandas as pd

raw_df = pd.DataFrame({"Name": ["  Jimmy  ", " Bob", "Tim "]})
clean_df = strip_whitespace(raw_df)
```
**Example Output:**

```python
# Returns a new DataFrame:
#   Name
# 0  Jimmy
# 1  Bob
# 2  Tim
```

---
### merge_datasets(df_list: list[pd.DataFrame], how: str = "outer") -> pd.DataFrame

**Purpose:**
Merge multiple pandas DataFrames on their shared columns into a single combined dataset.

**Parameters:**

* df_list (list[pd.DataFrame]): List of DataFrames to merge.

* how (str, optional): Merge strategy — one of "inner", "outer", "left", or "right". Defaults to "outer".

**Returns:**

* pd.DataFrame - The merged DataFrame containing data from all sources.

**Raises:**

* ValueError - If the list is empty or the DataFrames have no shared columns.

* TypeError - If any element in the list is not a DataFrame.

**Behavior:**

* Finds shared columns dynamically and merges iteratively across all DataFrames.

* Removes duplicated columns after each merge.

* Resets the index after completion.

**Example Usage:**

```python
from src.research_data_lib import merge_datasets
import pandas as pd

df1 = pd.DataFrame({"ID": [1, 2], "Score": [85, 90]})
df2 = pd.DataFrame({"ID": [2, 3], "City": ["NYC", "LA"]})

merged = merge_datasets([df1, df2], how="outer")
```
**Example Output:**

```python
# Returns DataFrame:
#    ID  Score   City
# 0   1   85.0    NaN
# 1   2   90.0    NYC
# 2   3    NaN     LA
```

---
### fill_missing_values(df: pd.DataFrame, strategy: str = "median") -> pd.DataFrame

**Purpose:**
Fill missing numeric values in a DataFrame using a specified imputation strategy.

**Parameters:**

* df (pd.DataFrame): Input dataset containing missing values.

* strategy (str, optional): Method for imputation - "mean", "median", "mode", or "zero". Defaults to "median".

**Returns:**

* pd.DataFrame - A new DataFrame with numeric NaNs replaced using the chosen method.

**Raises:**

* TypeError - If input is not a DataFrame.

* ValueError - If an unsupported strategy is provided.

**Behavior:**

* Operates only on numeric columns (int, float).

* Automatically calculates replacement values based on the strategy.

* Does not modify the original DataFrame.

**Example Usage:**

```python
from src.research_data_lib import fill_missing_values
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "Math": [90, np.nan, 80],
    "Science": [np.nan, 85, np.nan]
})

filled = fill_missing_values(df, strategy="mean")
# Missing values replaced with column means.
```

---
### generate_data_report(df: pd.DataFrame, filename: str = "data_report.txt") -> str

**Purpose:**
Generate a structured text report summarizing column-level statistics for a DataFrame.

**Parameters:**

* df (pd.DataFrame): Dataset to analyze.

* filename (str, optional): Path and name for the output .txt report file. Defaults to "data_report.txt".

**Returns:**

* str - The path of the generated report file.

**Raises:**

* TypeError - If input is not a DataFrame.

* ValueError - If the DataFrame is empty.

**Behavior:**

* Calculates missing value counts and percentages per column.

* Records unique counts and sample values (up to 5 examples).

* Automatically includes timestamp and file metadata.

* Creates output directories if needed.

**Example Usage:**

```python
from src.research_data_lib import generate_data_report
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alex", "Aidan", "Jake"],
    "Score": [85, None, 92]
})

path = generate_data_report(df, "outputs/report.txt")
```

**Example Output:**

```python
# Creates a detailed text file like:
# DATA REPORT - 2025-10-12 14:35:22
# Rows: 3, Columns: 2
# Name (object)
#   Missing: 0 (0.0%)
#   Unique: 3
#   Sample: Alex, Aidan, Jake
```


## `validate_email(email: str) -> bool`

**Purpose:**  
Validate an email address using a regular expression to ensure the format is correct.

**Parameters:**

- `email` (str): The email address to validate (e.g., "test@example.com").

**Returns:**

- `bool`: `True` if the email is valid, `False` otherwise.

**Raises:**

- `TypeError`: If `email` is not a string.

**Behavior:**

- Uses a regular expression to check if the email address follows a standard email pattern (e.g., "example@domain.com").
- Returns `True` for valid emails and `False` for invalid ones.
- If the input is not a string, a `TypeError` is raised.

**Example Usage:**

```python
from src.research_data_lib import validate_email

# Valid email
email = "test@example.com"
print(validate_email(email))  # Returns: True

# Invalid email
email = "invalid-email"
print(validate_email(email))  # Returns: False
```



## `filter_rows_by_condition(df, condition_func)`

**Purpose:**  
Filter rows in a DataFrame based on a custom condition function.

### Parameters:
- `df` (pd.DataFrame): The DataFrame to filter.
- `condition_func` (function): A function that takes a row (as a Series) and returns a boolean. This function is applied to each row, and only rows where the function evaluates to `True` will be included in the result.

### Returns:
- `pd.DataFrame`: A DataFrame containing the rows that meet the condition specified by `condition_func`.

### Raises:
- `TypeError`: If `df` is not a pandas DataFrame or `condition_func` is not callable.

### Behavior:
- Filters the rows of the DataFrame where the `condition_func` evaluates to `True` for each row.
- The filtering happens by applying `condition_func` to each row, and the resulting rows are returned in a new DataFrame.

### Example Usage:

```python
import pandas as pd
from your_module import filter_rows_by_condition

# Sample DataFrame
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "David"],
    "age": [25, 35, 30, 40],
    "city": ["New York", "Los Angeles", "Chicago", "Miami"]
})

# Custom filter condition: filter by age greater than 30
filtered_df = filter_rows_by_condition(df, lambda row: row['age'] > 30)

print(filtered_df)
```


## `count_unique_values(df)`

**Purpose:**  
Count the number of unique values for each column in a DataFrame.

### Parameters:
- `df` (pd.DataFrame): The DataFrame to analyze.

### Returns:
- `dict`: A dictionary where the keys are column names and the values are the count of unique values for each respective column.

### Raises:
- `TypeError`: If `df` is not a pandas DataFrame.

### Behavior:
- The function iterates through each column in the DataFrame and counts how many unique values exist in that column.
- The result is returned as a dictionary where the column names are the keys, and the number of unique values for each column is the value.

### Example Usage:

```python
import pandas as pd
from your_module import count_unique_values

# Sample DataFrame
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie", "Alice", "Bob"],
    "age": [25, 35, 30, 25, 35],
    "city": ["New York", "Los Angeles", "Chicago", "New York", "Los Angeles"]
})

# Count unique values for each column
unique_counts = count_unique_values(df)

print(unique_counts)
```


## `pivot_and_aggregate(df, pivot_column, value_column, agg_func='sum')`

**Purpose:**  
Pivot a DataFrame and aggregate values using the specified aggregation function.

### Parameters:
- `df` (pd.DataFrame): The DataFrame to pivot.
- `pivot_column` (str): The column to use for pivoting.
- `value_column` (str): The column whose values will be aggregated.
- `agg_func` (str, optional): The aggregation function to use. Default is `'sum'`. Supported values are:
  - `'sum'`: Sum of values.
  - `'mean'`: Mean (average) of values.
  - `'count'`: Count of non-NA values.
  - `'min'`: Minimum value.
  - `'max'`: Maximum value.
  - `'std'`: Standard deviation.
  - Others: Any other pandas-supported aggregation function.

### Returns:
- `pd.DataFrame`: A DataFrame with the pivoted and aggregated values.

### Raises:
- `ValueError`: If the `pivot_column` or `value_column` does not exist in the DataFrame.
- `TypeError`: If `df` is not a pandas DataFrame.

### Behavior:
- The function pivots the DataFrame using the specified `pivot_column` and aggregates the values in the `value_column` based on the chosen `agg_func`.
- It returns a new DataFrame that contains the pivoted structure, with the aggregation performed as specified.

### Example Usage:

```python
import pandas as pd
from your_module import pivot_and_aggregate

# Sample DataFrame
df = pd.DataFrame({
    "category": ["A", "B", "A", "B", "A"],
    "sales": [100, 200, 150, 250, 300],
    "region": ["East", "West", "East", "West", "East"]
})

# Pivot and aggregate using sum as the aggregation function
pivot_df = pivot_and_aggregate(df, pivot_column="category", value_column="sales", agg_func="sum")

print(pivot_df)
```


### `remove_punctuation(df: pd.DataFrame) -> pd.DataFrame`
**Purpose:**  
Remove punctuation from all string-type columns in a pandas DataFrame.

**Parameters:**
- `df (pd.DataFrame)`: Input DataFrame containing string or numeric columns.

**Returns:**
- `pd.DataFrame`: A new DataFrame with punctuation removed from string-type columns.

**Raises:**
- `TypeError`: If the input is not a pandas DataFrame.

**Behavior:**
- Operates only on columns with dtype `object` or `string`.
- Removes all non-alphanumeric characters (punctuation marks) from string columns.
- Leaves other columns (e.g., numeric, datetime) unchanged.
- Creates and returns a copy, leaving the original DataFrame unmodified.

**Example Usage:**

```python
from src.research_data_lib import remove_punctuation
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice!", "Bob?", "Charlie."],
    "Email": ["alice@email.com", "bob@email.com", "charlie@email.com"],
    "Score": [90, 85, 88]
})

# Clean the DataFrame by removing punctuation
clean_df = remove_punctuation(df)

print(clean_df)
# Example output:
#    Name              Email  Score
# 0  Alice     alice@email.com     90
# 1    Bob      bob@email.com     85
# 2 Charlie  charlie@email.com     88


### `handle_outliers(df: pd.DataFrame, threshold: float = 1.5) -> pd.DataFrame`
**Purpose:**  
Identify and replace outliers in numeric columns using the Interquartile Range (IQR) method.

**Parameters:**
- `df (pd.DataFrame)`: Input DataFrame containing numeric columns.
- `threshold (float, optional)`: The IQR threshold for identifying outliers. Default is `1.5`.

**Returns:**
- `pd.DataFrame`: A DataFrame where outliers are replaced by `NaN` (or removed based on the handling strategy).

**Raises:**
- `TypeError`: If the input is not a pandas DataFrame.
- `ValueError`: If there are no numeric columns in the DataFrame.

**Behavior:**
- Computes the IQR for each numeric column.
- Flags rows that fall outside the acceptable range (`Q1 - threshold * IQR` to `Q3 + threshold * IQR`).
- Replaces the outlier values with `NaN`.
- Returns a new DataFrame with outliers handled.

**Example Usage:**

```python
from src.research_data_lib import handle_outliers
import pandas as pd

df = pd.DataFrame({
    "Age": [25, 30, 35, 40, 500],
    "Score": [88, 92, 95, 78, 1000]
})

# Handle outliers by replacing them with NaN
clean_df = handle_outliers(df, threshold=1.5)

print(clean_df)
# Example output:
#    Age  Score
# 0  25   88.0
# 1  30   92.0
# 2  35   95.0
# 3  40   78.0
# 4 NaN   NaN


### `split_multi_response(df: pd.DataFrame, column_name: str, delimiter: str = ",") -> pd.DataFrame`
**Purpose:**  
Split a column with multiple responses into separate binary columns based on the delimiter.

**Parameters:**
- `df (pd.DataFrame)`: Input DataFrame with a column containing multi-response values.
- `column_name (str)`: The name of the column to split.
- `delimiter (str, optional)`: The character used to separate multi-response values. Default is `","`.

**Returns:**
- `pd.DataFrame`: A DataFrame where the original multi-response column is split into separate binary columns (1 for presence, 0 for absence).

**Raises:**
- `TypeError`: If the input is not a pandas DataFrame or the column name is not a string.
- `ValueError`: If the specified column doesn't exist in the DataFrame.

**Behavior:**
- Splits the values in the `column_name` based on the specified delimiter.
- Creates new binary columns for each possible response, using the column name with a suffix like `_response_1`, `_response_2`, etc.
- Fills the new columns with 1 for presence and 0 for absence of each response.

**Example Usage:**

```python
from src.research_data_lib import split_multi_response
import pandas as pd

df = pd.DataFrame({
    "Responses": ["Yes, No", "Yes, Maybe", "No, Maybe"]
})

# Split the multi-response column into separate binary columns
split_df = split_multi_response(df, column_name="Responses", delimiter=", ")

print(split_df)
# Example output:
#    Responses  Responses_response_1  Responses_response_2  Responses_response_3
# 0  Yes, No                   1                   1                    0
# 1  Yes, Maybe                1                   0                    1
# 2  No, Maybe                 0                   1                    1


### `generate_data_profile(df: pd.DataFrame, report_file: str = "data_profile_report.txt") -> str`

**Purpose:**  
Generate a structured text report summarizing column-level statistics, including missing values, unique counts, and sample values.

**Parameters:**
- `df (pd.DataFrame)`: The dataset to analyze.
- `report_file (str, optional)`: Path and name for the output text report file. Default is `"data_profile_report.txt"`.

**Returns:**
- `str`: The path to the generated report file.

**Raises:**
- `TypeError`: If the input is not a pandas DataFrame.
- `ValueError`: If the DataFrame is empty.

**Behavior:**
- Analyzes the DataFrame to compute the following for each column:
  - Missing value percentage.
  - Unique value count.
  - Sample values (up to 5 examples).
- Generates a timestamped report that includes these statistics.
- Saves the report to the specified `report_file` and returns its path.

**Example Usage:**

```python
from src.research_data_lib import generate_data_profile
import pandas as pd

df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "David"],
    "Age": [25, 30, 35, None],
    "Score": [90, None, 88, 92]
})

# Generate the data profiling report
report_path = generate_data_profile(df, report_file="outputs/data_profile_report.txt")

print(f"Report generated at: {report_path}")
# Example output:
# Report generated at: outputs/data_profile_report.txt


