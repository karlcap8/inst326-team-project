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