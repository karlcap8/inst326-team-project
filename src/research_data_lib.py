import re

def normalize_header(name: str) -> str:
    """Normalize a column header to snake_case (safe for CSV/SQL).

    Rules:
      - Lowercase everything
      - Replace non-alphanumeric characters with underscores
      - Collapse repeated underscores; trim leading/trailing underscores
      - If the result is empty, return "unnamed"
      - If the name starts with a digit, prefix "col_"

    Args:
        name: Raw header text (e.g., "Q3 - Overall Satisfaction (1-5)")

    Returns:
        A normalized header string (e.g., "q3_overall_satisfaction_1_5").

    Raises:
        TypeError: If `name` is not a string.

    Examples:
        >>> normalize_header("Q3 - Overall Satisfaction (1-5)")
        'q3_overall_satisfaction_1_5'
        >>> normalize_header("   Email Address ")
        'email_address'
        >>> normalize_header("123")
        'col_123'
        >>> normalize_header("!!!")
        'unnamed'
    """
    if not isinstance(name, str):
        raise TypeError("normalize_header: 'name' must be a str")
    s = name.strip().lower()
    s = re.sub(r"[^0-9a-z]+", "_", s)         # non-alnum → _
    s = re.sub(r"_+", "_", s).strip("_")      # collapse/truncate _
    if not s:
        return "unnamed"
    if s[0].isdigit():
        s = f"col_{s}"
    return s

