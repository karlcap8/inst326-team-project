
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Iterable

class Transformer(ABC):
    """Abstract base class for one survey-data cleaning step.

    Team Members: Harrang Khalsa, Karl Capili, Sukhman Singh, Aaron Coogan
    Domain: Research Data Pipeline (Survey Data Cleaning & Validation)

    This ABC defines the contract for a *single* transformation in the pipeline
    (e.g., header normalization, PII removal, type casting, imputation).
    All subclasses must implement the abstract methods and properties so that
    a Pipeline can invoke them polymorphically in a fixed order.
    """

    def __init__(self, param1: str, param2: str):
        """Initialize shared attributes.

        Args:
            param1: Step name (e.g., 'HeaderNormalizer', 'PIIRemover').
            param2: Step notes/version (e.g., 'v1.0' or a short description).
        """
        self.param1 = param1              # step name
        self.param2 = param2              # notes/version
        self.created_at = datetime.now()  # common metadata for logging
        self._history: list[str] = []     # shared history/log messages

    # === ABSTRACT METHODS (must be implemented) ===

    @abstractmethod
    def required_behavior1(self, dataset: Any) -> Any:
        """Apply this transformation to the dataset and return the result.

        WHY ABSTRACT: Each cleaning step uses a different algorithm
        (normalize headers vs. drop PII vs. cast types vs. impute missing),
        so behavior varies by subclass.

        TEAM CONTRACT: The Pipeline will call `required_behavior1(dataset)`
        on every Transformer in order, without caring about the concrete type.

        Returns:
            The transformed dataset (same type as input).
        """
        pass

    @abstractmethod
    def required_behavior2(self) -> str:
        """Human-readable description of what this step does.

        WHY ABSTRACT: Each subclass should describe its own action and parameters
        (e.g., which columns it touches, strategy used) for audit/reporting.

        Returns:
            A concise, single-line description of the step.
        """
        pass

    # === ABSTRACT PROPERTIES (required data) ===

    @property
    @abstractmethod
    def required_data(self) -> Iterable[str]:
        """Columns this step *requires* to exist before running.

        WHY PROPERTY: The pipeline can preflight-check the dataset schema before
        executing steps and provide helpful errors if inputs are missing.

        Can be implemented as:
        - Stored attribute (e.g., a set of column names)
        - Computed value (depends on constructor args)
        - Fixed constant (for universal requirements)

        Returns:
            Iterable[str]: Column names required by this step.
        """
        pass

    # === CONCRETE METHODS (shared functionality) ===

    def shared_calculation(self) -> str:
        """Build a standardized log line for this step.

        WHY CONCRETE: All subclasses benefit from consistent logging/reporting.

        Uses abstract methods/properties: required_behavior2(), required_data

        Returns:
            A string like: "[12:03:11] HeaderNormalizer (needs: id,email)"
        """
        stamp = datetime.now().strftime("%H:%M:%S")
        desc = self.required_behavior2()
        needs = ", ".join(self.required_data) if self.required_data else "none"
        line = f"[{stamp}] {self.param1} — {desc} (needs: {needs})"
        self._history.append(line)
        return line

    def another_shared_method(self, param: Any) -> Any:
        """Attach an audit note to this step and return it (passthrough).

        Args:
            param: Any note/metadata (e.g., {'affected_rows': 42})

        Returns:
            The same param, after recording it in the history for traceability.
        """
        stamp = datetime.now().isoformat(timespec="seconds")
        self._history.append(f"{stamp} | note={param!r}")
        return param

