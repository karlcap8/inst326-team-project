# src/data_profiler.py

from __future__ import annotations
from typing import Optional
from copy import deepcopy
import os

# Reuse your Project 1 functions (keep their names the same in your library)
from src.research_data_lib import (
    remove_punctuation,     # (df) -> df
    handle_outliers,        # (df, threshold) -> df
    split_multi_response,   # (df, column_name, delimiter) -> df
    generate_data_profile,  # (df, report_file) -> str
)

class DataProfiler:
    """Encapsulates pandas-based data preparation and profiling steps.

    This class wraps Project 1 functions into an OOP interface:
      - remove punctuation from text columns
      - handle numeric outliers via IQR
      - split multi-response columns into binary indicators
      - generate a profiling report with charts

    Attributes are private and exposed via properties to satisfy encapsulation.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     "comment": ["Great!", "So-so...", "Bad :("],
        ...     "score": [10, 999, 5],
        ...     "hobbies": ["reading, music", "music, sports", None]
        ... })
        >>> profiler = DataProfiler(df, name="pilot", report_dir="reports")
        >>> profiler.clean_text()
        >>> profiler.fix_outliers(threshold=1.5)
        >>> profiler.split_multi("hobbies", delimiter=",")
        >>> path = profiler.profile()  # writes report + charts
        >>> str(profiler).startswith("DataProfiler 'pilot'")
        True
    """

    # ---------- Initialization & encapsulation ----------

    def __init__(self, df, name: str, *, report_dir: str = "reports") -> None:
        """Initialize a DataProfiler.

        Args:
            df (pd.DataFrame): Input dataset.
            name (str): Profile name for identification and output naming.
            report_dir (str): Directory to store profiling outputs (txt/pngs).

        Raises:
            ValueError: If df is empty or name is blank.
        """
        # Lazy import so this file can import without pandas at import time
        import pandas as pd  # type: ignore

        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if df.empty:
            raise ValueError("df cannot be empty.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string.")

        self._df = df.copy(deep=True)
        self._name = name.strip()
        self._report_dir = report_dir
        self._last_report_path: Optional[str] = None

    # ---------- Properties (controlled access) ----------

    @property
    def name(self) -> str:
        """Dataset/profile name (read-only)."""
        return self._name

    @property
    def df(self):
        """Return a defensive copy of the current working DataFrame."""
        return self._df.copy(deep=True)

    @property
    def shape(self) -> tuple[int, int]:
        """Current DataFrame shape (rows, cols)."""
        return self._df.shape

    @property
    def columns(self) -> list[str]:
        """Current column names."""
        return list(self._df.columns)

    @property
    def last_report_path(self) -> Optional[str]:
        """Path of the most recently generated report (if any)."""
        return self._last_report_path

    # ---------- Instance methods (integrate P1 functions) ----------

    def clean_text(self) -> None:
        """Remove punctuation from all string columns using remove_punctuation()."""
        self._df = remove_punctuation(self._df)

    def fix_outliers(self, *, threshold: float = 1.5) -> None:
        """Handle numeric outliers using IQR via handle_outliers()."""
        self._df = handle_outliers(self._df, threshold=threshold)

    def split_multi(self, column_name: str, *, delimiter: str = ",") -> None:
        """Split a multi-response column into binary indicator columns using split_multi_response()."""
        self._df = split_multi_response(self._df, column_name, delimiter=delimiter)

    def profile(self, *, filename: Optional[str] = None) -> str:
        """Generate a data profiling report with charts using generate_data_profile().

        Args:
            filename: Optional file name (e.g., 'profile.txt'). If None, uses '{name}_profile.txt'.

        Returns:
            str: Path to the written report file.
        """
        # Make sure the directory exists even if no subdir is given
        os.makedirs(self._report_dir, exist_ok=True)
        base = filename or f"{self._name}_profile.txt"
        path = os.path.join(self._report_dir, base)
        self._last_report_path = generate_data_profile(self._df, report_file=path)
        return self._last_report_path

    # ---------- Representations ----------

    def __str__(self) -> str:
        r, c = self.shape
        return f"DataProfiler '{self._name}' | {r} rows, {c} columns | report_dir='{self._report_dir}'"

    def __repr__(self) -> str:
        r, c = self.shape
        return f"DataProfiler(name={self._name!r}, shape=({r},{c}), report_dir={self._report_dir!r})"
