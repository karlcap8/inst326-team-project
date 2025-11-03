import pandas as pd
import re

# Reuse your Project 1 functions (already in src/research_data_lib.py)
from src.research_data_lib import (
    validate_email,
    filter_rows_by_condition,
    count_unique_values,
    pivot_and_aggregate,
)

class DataAnalysis:
    """Encapsulates various data analysis operations such as email validation, filtering, counting unique values, and pivoting.

    This class provides utility functions for common data operations on pandas DataFrames and individual data validation.

    Attributes:
        df (pd.DataFrame): The DataFrame for analysis.
        history (list): A log of operations applied to the data.
        cleaned (bool): Whether the data has been cleaned or modified.
    
    Example:
        >>> df = pd.DataFrame({'age': [25, 30, 35], 'email': ['test@example.com', 'invalid-email', 'user@example.com']})
        >>> analysis = DataAnalysis(df)
        >>> analysis.filter_rows_by_condition(lambda row: row['age'] > 30)
        >>> analysis.count_unique_values()
        >>> analysis.pivot_and_aggregate('age', 'email', 'count')
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """Initialize the DataAnalysis object with a pandas DataFrame.

        Args:
            df (pd.DataFrame): The DataFrame to analyze.

        Raises:
            TypeError: If df is not a pandas DataFrame.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        
        self._df: pd.DataFrame = df.copy()
        self.history: list = []
        self.cleaned: bool = False

    # ---------- Instance Methods ----------

    def validate_email(self, email: str) -> bool:
        """Validate an email address using a regular expression.

        Args:
            email (str): The email address to validate.

        Returns:
            bool: True if the email is valid, False otherwise.

        Raises:
            TypeError: If email is not a string.
        """
        if not isinstance(email, str):
            raise TypeError("Input must be a string.")
        
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        return bool(re.match(email_regex, email))

    def filter_rows_by_condition(self, condition_func) -> pd.DataFrame:
        """Filter rows in the DataFrame based on a custom condition function.

        Args:
            condition_func (function): A function that takes a row (as a Series) and returns a boolean.

        Returns:
            pd.DataFrame: A DataFrame with rows that meet the condition.

        Raises:
            TypeError: If condition_func is not callable.
        """
        if not callable(condition_func):
            raise TypeError("condition_func must be a callable function.")
        
        filtered_df = self._df[self._df.apply(condition_func, axis=1)]
        self.history.append("filter_rows_by_condition")
        return filtered_df

    def count_unique_values(self) -> dict:
        """Count the number of unique values for each column in the DataFrame.

        Returns:
            dict: A dictionary where the keys are column names and values are the unique count.
        
        Raises:
            TypeError: If df is not a pandas DataFrame.
        """
        unique_counts = {col: self._df[col].nunique() for col in self._df.columns}
        self.history.append("count_unique_values")
        return unique_counts

    def pivot_and_aggregate(self, pivot_column: str, value_column: str, agg_func: str = 'sum') -> pd.DataFrame:
        """Pivot the DataFrame and aggregate values using the specified aggregation function.

        Args:
            pivot_column (str): The column to use for pivoting.
            value_column (str): The column whose values will be aggregated.
            agg_func (str): The aggregation function to use ('sum', 'mean', 'count', etc.).

        Returns:
            pd.DataFrame: A DataFrame with the pivoted and aggregated values.

        Raises:
            ValueError: If the pivot_column or value_column does not exist in the DataFrame.
        """
        if pivot_column not in self._df.columns or value_column not in self._df.columns:
            raise ValueError(f"Columns {pivot_column} or {value_column} not found in the DataFrame.")
        
        pivot_df = self._df.pivot_table(index=pivot_column, values=value_column, aggfunc=agg_func)
        self.history.append(f"pivot_and_aggregate({pivot_column}, {value_column}, {agg_func})")
        return pivot_df

    # ---------- String Representations ----------

    def __str__(self) -> str:
        rows, cols = self._df.shape
        return f"DataAnalysis | rows={rows}, cols={cols} | cleaned={self.cleaned} | steps={len(self.history)}"

    def __repr__(self) -> str:
        rows, cols = self._df.shape
        return f"DataAnalysis(df={self._df.shape}, cleaned={self.cleaned})"

    # ---------- Properties (controlled access) ----------

    @property
    def df(self) -> pd.DataFrame:
        """Return a deep copy of the internal DataFrame."""
        return self._df.copy()

    @property
    def is_cleaned(self) -> bool:
        """Whether cleaning operations have been applied."""
        return self.cleaned

    @property
    def history(self) -> list:
        """Return the history of operations performed on the DataFrame."""
        return self.history

