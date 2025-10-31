# src/dataset.py

from __future__ import annotations
from typing import List, Dict, Optional, Set
from copy import deepcopy

# Reuse your Project 1 functions (already in src/research_data_lib.py)
from src.research_data_lib import (
    normalize_header,
    rename_columns,
    cast_row_types,
    validate_dataset,
)


class Dataset:
    """Represents a research dataset with utilities for cleaning and validation.

    This class encapsulates tabular data (list of row dicts) and exposes
    methods that integrate Project 1 functions to:
      - normalize headers
      - rename columns
      - cast column types
      - validate against rules

    Attributes are encapsulated (private) with read-only properties where appropriate.

    Example:
        >>> rows = [
        ...     {"Q1": "19", "Q2": "Yes", "Email Address": "a@b.com", "joined": "2024-10-01"},
        ...     {"Q1": "21", "Q2": "No",  "Email Address": "c@d.com", "joined": "2024-10-03"},
        ... ]
        >>> ds = Dataset(rows, name="pilot_survey",
        ...              rename_map={"Q1": "age", "Q2": "consent", "Email Address": ""},  # drop PII
        ...              type_map={"age": "int", "consent": "bool", "joined": "datetime:%Y-%m-%d"})
        >>> ds.clean_headers()           # normalize source keys (optional but recommended)
        >>> ds.apply_rename_map()        # rename + drop columns based on mapping
        >>> ds.cast_types()              # cast columns using type_map
        >>> issues = ds.validate({
        ...     "age": {"type": "int", "min": 0, "max": 120, "required": True},
        ...     "consent": {"type": "bool", "required": True},
        ...     "joined": {"type": "datetime:%Y-%m-%d", "required": True}
        ... })
        >>> len(issues) == 0
        True
        >>> str(ds)
        "Dataset 'pilot_survey' | 2 rows, 3 columns (cleaned=True)"
    """

    # ---------- Initialization & encapsulation ----------

    def __init__(
        self,
        rows: List[Dict],
        name: str,
        *,
        rename_map: Optional[Dict[str, str]] = None,
        type_map: Optional[Dict[str, str]] = None,
        pii_columns: Optional[Set[str]] = None,
    ) -> None:
        """Initialize a Dataset with basic validation and optional config.

        Args:
            rows: List of row dictionaries (each row: column -> value).
            name: A human-friendly dataset name.
            rename_map: Optional mapping of old -> new column names ('' means drop).
            type_map: Optional mapping of column -> type label (e.g., 'int', 'datetime:%Y-%m-%d').
            pii_columns: Optional set of column names to drop when calling drop_pii().

        Raises:
            ValueError: If rows is empty or not a list of dicts; if name is blank.
        """
        if not isinstance(rows, list) or not rows or not all(isinstance(r, dict) for r in rows):
            raise ValueError("rows must be a non-empty list of dictionaries")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")

        self._name: str = name.strip()
        # Store a deep copy to protect internal state
        self._rows: List[Dict] = deepcopy(rows)

        # Optional configuration for convenience
        self._rename_map: Dict[str, str] = dict(rename_map or {})
        self._type_map: Dict[str, str] = dict(type_map or {})
        self._pii_columns: Set[str] = set(pii_columns or set())

        # Derived / status flags
        self._cleaned: bool = False
        self._last_validation_issues: List[Dict] = []

    # ---------- Properties (controlled access) ----------

    @property
    def name(self) -> str:
        """Dataset name (read-only)."""
        return self._name

    @property
    def is_cleaned(self) -> bool:
        """Whether cleaning methods have been applied."""
        return self._cleaned

    @property
    def n_rows(self) -> int:
        """Number of rows."""
        return len(self._rows)

    @property
    def n_cols(self) -> int:
        """Number of columns (based on union of keys across rows)."""
        return len(self.columns)

    @property
    def columns(self) -> List[str]:
        """Current column names (union across all rows), sorted."""
        cols = set()
        for r in self._rows:
            cols.update(r.keys())
        return sorted(cols)

    @property
    def last_validation_issues(self) -> List[Dict]:
        """The most recent validation issues (list of dicts)."""
        return deepcopy(self._last_validation_issues)

    def snapshot(self) -> List[Dict]:
        """Return a deep copy of the current rows (read-only snapshot)."""
        return deepcopy(self._rows)

    # ---------- Methods integrating Project 1 functions ----------

    def clean_headers(self) -> None:
        """Normalize header keys for all rows using normalize_header()."""
        cleaned: List[Dict] = []
        for row in self._rows:
            new_row = {normalize_header(k): v for k, v in row.items()}
            cleaned.append(new_row)
        self._rows = cleaned
        self._cleaned = True

    def apply_rename_map(self, *, drop_unmapped: bool = False, normalize_targets: bool = True) -> None:
        """Rename/drop columns across rows using rename_columns() and this dataset's rename_map.

        Args:
            drop_unmapped: If True, discard columns not present in the rename_map.
            normalize_targets: If True, normalize target names via normalize_header().
        """
        if not self._rename_map:
            # Nothing to do
            return
        renamed: List[Dict] = []
        for row in self._rows:
            renamed.append(
                rename_columns(
                    row,
                    self._rename_map,
                    drop_unmapped=drop_unmapped,
                    normalize_targets=normalize_targets,
                )
            )
        self._rows = renamed
        self._cleaned = True

    def cast_types(self) -> None:
        """Cast columns to configured types across all rows using cast_row_types()."""
        if not self._type_map:
            return
        casted: List[Dict] = []
        for row in self._rows:
            casted.append(cast_row_types(row, self._type_map))
        self._rows = casted
        self._cleaned = True

    def drop_pii(self) -> None:
        """Drop configured PII columns (if any) from all rows.

        Note:
            This method performs a simple key-removal pass. If you later add a
            dedicated `drop_pii()` function to your P1 library, you can replace
            this logic with a call to that function.
        """
        if not self._pii_columns:
            return
        filtered: List[Dict] = []
        for row in self._rows:
            filtered.append({k: v for k, v in row.items() if k not in self._pii_columns})
        self._rows = filtered
        self._cleaned = True

    def validate(self, rules: Dict) -> List[Dict]:
        """Validate current rows against rules using validate_dataset().

        Args:
            rules: Mapping of column -> rule dicts, compatible with validate_dataset().

        Returns:
            List of issue dicts (also stored in `last_validation_issues`).
        """
        issues = validate_dataset(self._rows, rules)
        self._last_validation_issues = issues
        return deepcopy(issues)

    # ---------- Representations ----------

    def __str__(self) -> str:
        return f"Dataset '{self._name}' | {self.n_rows} rows, {self.n_cols} columns (cleaned={self._cleaned})"

    def __repr__(self) -> str:
        return f"Dataset(name={self._name!r}, rows={self.n_rows}, cols={self.n_cols}, cleaned={self._cleaned})"


#Sukhman Class

from __future__ import annotations
from typing import List, Optional
from copy import deepcopy
import pandas as pd

# Reuse your Project 1 functions
from src.research_data_lib import (
    strip_whitespace,
    merge_datasets,
    fill_missing_values,
    generate_data_report,
)


class DataPipeline:
    """Encapsulates a research data pipeline for cleaning, merging, and reporting.

    This class manages a pandas DataFrame and provides methods that integrate
    the Project 1 function library. It supports step-by-step cleaning, merging,
    imputation, and report generation while maintaining encapsulation and
    validation of internal state.

    Attributes:
        _df (pd.DataFrame): Private DataFrame holding the current dataset.
        _name (str): Human-readable name for this dataset.
        _history (List[str]): Log of operations applied in sequence.

    Example:
        >>> import pandas as pd
        >>> df1 = pd.DataFrame({"Name": [" Alice ", "Bob"], "Age": [23, None]})
        >>> df2 = pd.DataFrame({"Name": ["Charlie"], "Age": [30]})
        >>> dp = DataPipeline(df1, name="survey_batch1")
        >>> dp.strip_text()                  # Clean whitespace
        >>> dp.fill_missing(strategy="mean") # Fill missing age
        >>> dp.merge([df2])                  # Merge another dataset
        >>> dp.generate_report("output/report.txt")
        >>> print(dp)
        DataPipeline 'survey_batch1' | rows=3, cols=2 | steps=3
    """

    # ---------- Initialization & Encapsulation ----------

    def __init__(self, df: pd.DataFrame, name: str) -> None:
        """Initialize the DataPipeline with validation and setup.

        Args:
            df (pd.DataFrame): The initial dataset.
            name (str): The name of the dataset/pipeline instance.

        Raises:
            TypeError: If df is not a DataFrame.
            ValueError: If name is blank.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("DataPipeline requires a pandas DataFrame.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string.")

        self._df: pd.DataFrame = df.copy()
        self._name: str = name.strip()
        self._history: List[str] = []
        self._cleaned: bool = False

    # ---------- Properties ----------

    @property
    def name(self) -> str:
        """Return the dataset name (read-only)."""
        return self._name

    @property
    def df(self) -> pd.DataFrame:
        """Return a deep copy of the internal DataFrame."""
        return deepcopy(self._df)

    @property
    def history(self) -> List[str]:
        """Return a copy of the operation history."""
        return deepcopy(self._history)

    @property
    def is_cleaned(self) -> bool:
        """Return True if cleaning operations have been applied."""
        return self._cleaned

    @property
    def shape(self) -> tuple:
        """Return the shape (rows, cols) of the dataset."""
        return self._df.shape

    # ---------- Instance Methods integrating Project 1 functions ----------

    def strip_text(self) -> None:
        """Remove leading/trailing whitespace from all string columns."""
        self._df = strip_whitespace(self._df)
        self._history.append("strip_whitespace")
        self._cleaned = True

    def fill_missing(self, strategy: str = "median") -> None:
        """Fill missing numeric values using the specified strategy.

        Args:
            strategy (str): One of 'mean', 'median', 'mode', or 'zero'.
        """
        self._df = fill_missing_values(self._df, strategy=strategy)
        self._history.append(f"fill_missing_values({strategy})")
        self._cleaned = True

    def merge(self, others: List[pd.DataFrame], how: str = "outer") -> None:
        """Merge current dataset with one or more others using merge_datasets().

        Args:
            others (list[pd.DataFrame]): List of DataFrames to merge.
            how (str): Merge type ('inner', 'outer', 'left', 'right').
        """
        all_dfs = [self._df] + others
        self._df = merge_datasets(all_dfs, how=how)
        self._history.append(f"merge_datasets({len(others)} datasets, how={how})")

    def generate_report(self, filename: str = "data_report.txt") -> str:
        """Generate a structured report summarizing dataset stats."""
        path = generate_data_report(self._df, filename)
        self._history.append(f"generate_data_report('{filename}')")
        return path

    def snapshot(self) -> pd.DataFrame:
        """Return a deep copy of the dataset (safe read-only view)."""
        return deepcopy(self._df)

    # ---------- Representations ----------

    def __str__(self) -> str:
        rows, cols = self._df.shape
        return f"DataPipeline '{self._name}' | rows={rows}, cols={cols} | steps={len(self._history)}"

    def __repr__(self) -> str:
        return f"DataPipeline(name={self._name!r}, rows={self._df.shape[0]}, cols={self._df.shape[1]}, cleaned={self._cleaned})"

