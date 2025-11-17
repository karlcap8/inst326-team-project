from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class Transformer(ABC):
    """Abstract base class for one survey-data cleaning step.

    Team Members: Harrang Khalsa, Karl Capili, Sukhman Singh, Aaron Coogan
    Domain: Research Data Pipeline (Survey Data Cleaning & Validation)

    This ABC defines the contract for a *single* transformation in the pipeline
    (e.g., header normalization, PII removal, type casting, imputation).
    All subclasses must implement the abstract methods and properties so that
    a Pipeline can invoke them polymorphically in a fixed order.
    """

    def __init__(self, name: str, notes: str = "") -> None:
        """Initialize shared attributes for all transformers.

        Args:
            name: Short name of the step (e.g., 'HeaderNormalizer').
            notes: Optional description or version info.
        """
        self.name = name
        self.notes = notes
        self.created_at = datetime.now()
        self._history: list[str] = []

    # === ABSTRACT INTERFACE (must be implemented by subclasses) ===

    @abstractmethod
    def _apply(self, df) -> Any:
        """Subclass-specific transformation logic.

        Each concrete transformer must implement this method.
        It should accept a pandas DataFrame (or DataFrame-like) and
        return a transformed DataFrame.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def required_columns(self) -> list[str]:
        """Columns that must exist before this step can run.

        Subclasses return a list of column names they depend on.
        Return an empty list if the step can run on any schema.
        """
        raise NotImplementedError

    # === CONCRETE TEMPLATE METHOD (shared across all subclasses) ===

    def apply(self, df):
        """Run this step: preflight checks, transform, and log.

        This is the method that Pipeline calls. It is the same for
        all subclasses and delegates the actual work to `_apply`.
        """
        self._preflight(df)
        out = self._apply(df)
        self._log(f"{self.name} finished")
        return out

    # === SHARED HELPERS (concrete) ===

    def _preflight(self, df) -> None:
        """Check that required columns exist in the incoming DataFrame."""
        # Make sure df has a .columns attribute
        if not hasattr(df, "columns"):
            raise TypeError(
                f"{self.name}: expected a DataFrame-like object with `.columns`"
            )

        if self.required_columns:
            missing = [c for c in self.required_columns if c not in df.columns]
            if missing:
                raise KeyError(f"{self.name}: missing required columns: {missing}")

    def _log(self, message: str) -> None:
        """Record a log message for this step."""
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {self.name}: {message}"
        self._history.append(line)

    def history(self) -> list[str]:
        """Return a copy of the internal history log."""
        return list(self._history)
