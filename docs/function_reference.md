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



