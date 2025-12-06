# dataset.py

from __future__ import annotations
from typing import List, Dict, Optional, Set
from copy import deepcopy

# Reuse Project 1 functions 
from .research_data_lib import (
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

# Reuse Project 1 functions
from research_data_lib import (
    strip_whitespace,
    merge_datasets,
    fill_missing_values,
    generate_data_report,
)
