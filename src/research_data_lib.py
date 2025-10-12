import re

# Simple 1 - Karl
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



from datetime import datetime

# Medium 1 - Karl
def cast_row_types(row: dict, type_map: dict[str, str]) -> dict:
    """Cast a row's values to configured types (int, float, bool, str, datetime:<fmt>).

    Rules:
      - Only casts columns listed in type_map (others are unchanged).
      - Treats empty strings and common NA tokens ('na','n/a','null') as None.
      - For bool: true/yes/1 -> True, false/no/0 -> False (case-insensitive).
      - For datetime:<fmt>: uses strptime with the provided format.
      - On cast failure, leaves the original value unchanged.

    Args:
        row: A single record mapping column -> raw value.
        type_map: Mapping column -> type label, e.g., 'int', 'float', 'bool',
                  'str', or 'datetime:%Y-%m-%d'.

    Returns:
        A new dict with values cast where possible.

    Examples:
        >>> r = {'age':'19','score':'3.5','consent':'Yes','joined':'2024-10-01'}
        >>> tm = {'age':'int','score':'float','consent':'bool','joined':'datetime:%Y-%m-%d'}
        >>> out = cast_row_types(r, tm)
        >>> (out['age'], type(out['age'])) == (19, int)
        True
    """
    if not isinstance(row, dict) or not isinstance(type_map, dict):
        raise TypeError("cast_row_types: 'row' and 'type_map' must be dicts")

    def to_none_if_blank(x):
        if x is None:
            return None
        if isinstance(x, str):
            s = x.strip().lower()
            if s in ("", "na", "n/a", "null"):
                return None
        return x

    def to_bool(x):
        if isinstance(x, bool):
            return x
        if x is None:
            return None
        s = str(x).strip().lower()
        if s in ("true", "yes", "y", "1"):
            return True
        if s in ("false", "no", "n", "0"):
            return False
        raise ValueError("not a bool")

    out = dict(row)
    for col, tlabel in type_map.items():
        if col not in out:
            continue
        raw = to_none_if_blank(out[col])

        if tlabel == "str":
            out[col] = None if raw is None else str(raw)
            continue

        if raw is None:
            out[col] = None
            continue

        try:
            if tlabel == "int":
                out[col] = int(float(raw))  # handles "19.0"
            elif tlabel == "float":
                out[col] = float(raw)
            elif tlabel == "bool":
                out[col] = to_bool(raw)
            elif tlabel.startswith("datetime:"):
                fmt = tlabel.split(":", 1)[1]
                out[col] = datetime.strptime(str(raw), fmt)
            else:
                raise ValueError(f"Unsupported type label: {tlabel}")
        except Exception:
            # Leave value as-is on cast failure
            out[col] = raw
    return out


# Medium 2- Karl
def rename_columns(
    row: dict,
    rename_map: dict[str, str],
    *,
    drop_unmapped: bool = False,
    normalize_targets: bool = True,
) -> dict:
    """Rename columns in a single row using a mapping, with safe collision handling.

    Behavior:
      - If a source key exists in rename_map and maps to a non-empty string, rename it.
      - If a mapping value is an empty string (""), the column is dropped.
      - If a source key is not in rename_map:
          - keep it as-is by default; or
          - drop it if drop_unmapped=True.
      - If normalize_targets=True, target names are passed through normalize_header().
      - If the new name already exists, suffix with _2, _3, ... to avoid collision.

    Args:
        row: A single record (column -> value).
        rename_map: Mapping of old_name -> new_name (use "" to drop a column).
        drop_unmapped: If True, drop columns not present in rename_map.
        normalize_targets: If True, normalize target names via normalize_header().

    Returns:
        A new dict with renamed (and possibly dropped) keys.
    """
    if not isinstance(row, dict) or not isinstance(rename_map, dict):
        raise TypeError("rename_columns: 'row' and 'rename_map' must be dicts")

    out: dict = {}

    def put_safe(k: str, v):
        # Ensure unique keys by suffixing _2, _3, ...
        base = k
        idx = 2
        while k in out:
            k = f"{base}_{idx}"
            idx += 1
        out[k] = v

    for old_key, value in row.items():
        if old_key in rename_map:
            new_key = rename_map[old_key]
            # Empty string means drop this column
            if new_key == "":
                continue
            if normalize_targets:
                # Reuse our simple normalizer from above
                new_key = normalize_header(new_key)
            put_safe(new_key, value)
        else:
            # Not mapped
            if drop_unmapped:
                continue
            put_safe(old_key, value)

    return out

# Complex 1 - Karl
import re
from datetime import datetime

def validate_dataset(rows: list[dict], rules: dict) -> list[dict]:
    """Validate a dataset (list of rows) against column rules.

    Supported rule keys per column:
      - required: bool                # column must exist and be non-null
      - not_null: bool                # if present, value cannot be null
      - type: 'int'|'float'|'bool'|'str'|'datetime:%Y-%m-%d'
      - min: number                   # numeric lower bound (inclusive)
      - max: number                   # numeric upper bound (inclusive)
      - len_min: int                  # string length lower bound
      - len_max: int                  # string length upper bound
      - allowed: list|set             # allowed categorical values (after casting)
      - regex: str                    # pattern the (string) value must match
      - unique: bool                  # values must be unique across rows (non-null)

    Returns:
        List of issues: 
        [{ 'row_idx': int, 'column': str, 'rule': str, 'value': any, 'message': str }, ...]

    Notes:
        - Uses cast_row_types() when a 'type' rule is provided to interpret values.
        - Treats "", "na", "n/a", "null" (case-insensitive) as null.
        - For uniqueness, nulls are ignored.
    """
    if not isinstance(rows, list) or not isinstance(rules, dict):
        raise TypeError("validate_dataset: 'rows' must be list and 'rules' must be dict")

    def is_null(x):
        if x is None:
            return True
        if isinstance(x, str) and x.strip().lower() in ("", "na", "n/a", "null"):
            return True
        return False

    # Prepare type map from rules for casting
    type_map: dict[str, str] = {}
    for col, spec in rules.items():
        tlabel = spec.get("type")
        if isinstance(tlabel, str):
            type_map[col] = tlabel

    issues: list[dict] = []

    # First pass: optionally cast by type for validation (non-destructive)
    casted_rows: list[dict] = []
    if type_map:
        try:
            casted_rows = [cast_row_types(r, type_map) for r in rows]  # uses our medium func
        except NameError:
            # Fallback if cast_row_types isn't available yet
            casted_rows = [dict(r) for r in rows]
    else:
        casted_rows = [dict(r) for r in rows]

    # Track values for uniqueness checks
    unique_track: dict[str, dict] = {}
    for col, spec in rules.items():
        if spec.get("unique"):
            unique_track[col] = {"seen": {}, "dups": set()}  # value -> first_idx, plus dup idxs

    # Row-wise validation
    for idx, (raw_row, row) in enumerate(zip(rows, casted_rows)):
        for col, spec in rules.items():
            val_present = col in row
            raw_present = col in raw_row
            required = bool(spec.get("required", False))
            not_null = bool(spec.get("not_null", False))
            tlabel = spec.get("type")
            v = row.get(col, None)

            # required: must exist AND be non-null
            if required and (not raw_present or is_null(raw_row.get(col))):
                issues.append({
                    "row_idx": idx,
                    "column": col,
                    "rule": "required",
                    "value": raw_row.get(col) if raw_present else None,
                    "message": "Required column missing or null."
                })
                # continue to next rule; still check others to surface more issues
            # not_null: if provided, cannot be null
            if raw_present and not_null and is_null(raw_row.get(col)):
                issues.append({
                    "row_idx": idx,
                    "column": col,
                    "rule": "not_null",
                    "value": raw_row.get(col),
                    "message": "Value cannot be null."
                })

            if not val_present:
                continue  # nothing else to validate

            # type check (post-cast)
            if isinstance(tlabel, str):
                ok = True
                if tlabel == "int":
                    ok = isinstance(v, int)
                elif tlabel == "float":
                    ok = isinstance(v, float) or isinstance(v, int)
                elif tlabel == "bool":
                    ok = isinstance(v, bool)
                elif tlabel == "str":
                    ok = (v is None) or isinstance(v, str)
                elif tlabel.startswith("datetime:"):
                    ok = isinstance(v, datetime)
                else:
                    ok = True  # unknown type label already flagged in cast_row_types
                if not ok:
                    issues.append({
                        "row_idx": idx,
                        "column": col,
                        "rule": "type",
                        "value": raw_row.get(col),
                        "message": f"Expected {tlabel}."
                    })

            # numeric range checks
            if isinstance(v, (int, float)):
                if "min" in spec and v < spec["min"]:
                    issues.append({
                        "row_idx": idx, "column": col, "rule": "min", "value": v,
                        "message": f"Value {v} < min {spec['min']}."
                    })
                if "max" in spec and v > spec["max"]:
                    issues.append({
                        "row_idx": idx, "column": col, "rule": "max", "value": v,
                        "message": f"Value {v} > max {spec['max']}."
                    })

            # string length checks
            if isinstance(v, str):
                if "len_min" in spec and len(v) < spec["len_min"]:
                    issues.append({
                        "row_idx": idx, "column": col, "rule": "len_min", "value": v,
                        "message": f"Length {len(v)} < len_min {spec['len_min']}."
                    })
                if "len_max" in spec and len(v) > spec["len_max"]:
                    issues.append({
                        "row_idx": idx, "column": col, "rule": "len_max", "value": v,
                        "message": f"Length {len(v)} > len_max {spec['len_max']}."
                    })

            # allowed set
            if "allowed" in spec and not is_null(v):
                allowed = set(spec["allowed"])
                if v not in allowed:
                    issues.append({
                        "row_idx": idx, "column": col, "rule": "allowed", "value": v,
                        "message": f"Value {v!r} not in allowed set ({len(allowed)} items)."
                    })

            # regex check
            if "regex" in spec and isinstance(v, str) and not is_null(v):
                pattern = spec["regex"]
                if re.fullmatch(pattern, v) is None:
                    issues.append({
                        "row_idx": idx, "column": col, "rule": "regex", "value": v,
                        "message": "String does not match required pattern."
                    })

            # collect for uniqueness
            if spec.get("unique") and not is_null(v):
                track = unique_track[col]
                if v in track["seen"]:
                    track["dups"].add(idx)
                else:
                    track["seen"][v] = idx

    # After scanning rows, emit uniqueness issues
    for col, track in unique_track.items():
        if not track["dups"]:
            continue
        # Mark first occurrences of dup values and all subsequent dups
        first_idxs = set(track["seen"].values())
        dup_firsts = {track["seen"][val] for val in track["seen"] if any(
            rows[j].get(col) == val for j in track["dups"]
        )}
        for i in sorted(dup_firsts.union(track["dups"])):
            issues.append({
                "row_idx": i,
                "column": col,
                "rule": "unique",
                "value": rows[i].get(col),
                "message": "Duplicate value violates uniqueness."
            })

    return issues



#Sukhman - Simple Function
def strip_whitespace(df):
    """
    Short Description:
        Removes leading and trailing whitespace from all string columns in a DataFrame.

    Rules:
        - Operates only on columns with dtype 'object' or 'string'.
        - Returns a cleaned copy of the DataFrame.
        - Does not modify the original DataFrame.

    Args:
        df (pd.DataFrame): Input DataFrame to clean.

    Returns:
        pd.DataFrame: A new DataFrame with stripped string values.

    Raises:
        TypeError: If df is not a pandas DataFrame.

    Example:
        >>> clean_df = strip_whitespace(raw_df)
    """
    import pandas as pd
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
    return df

#Sukhman - Medium Function 1
def merge_datasets(df_list, how="outer"):
    """
    Short Description:
        Merges multiple pandas DataFrames on their shared columns.

    Rules:
        - Requires at least one common column to merge on.
        - All inputs must be DataFrames.
        - Returns a merged DataFrame with duplicate columns removed.

    Args:
        df_list (list[pd.DataFrame]): List of DataFrames to merge.
        how (str): Type of merge to perform ("inner", "outer", "left", "right").

    Returns:
        pd.DataFrame: A merged DataFrame.

    Raises:
        ValueError: If list is empty or has no common columns.
        TypeError: If any list element is not a DataFrame.

    Example:
        >>> combined = merge_datasets([survey1, survey2, survey3], how="outer")
    """
    import pandas as pd
    if not df_list:
        raise ValueError("merge_datasets: empty list provided.")
    if not all(isinstance(df, pd.DataFrame) for df in df_list):
        raise TypeError("merge_datasets: all items must be DataFrames.")

    merged = df_list[0].copy()
    for df in df_list[1:]:
        common_cols = list(set(merged.columns) & set(df.columns))
        if not common_cols:
            raise ValueError("merge_datasets: no common columns to merge on.")
        merged = pd.merge(merged, df, on=common_cols, how=how)
        merged = merged.loc[:, ~merged.columns.duplicated()]

    merged.reset_index(drop=True, inplace=True)
    return merged

#Sukhman - Medium Function 2
def fill_missing_values(df, strategy="median"):
    """
    Short Description:
        Fills missing numeric values in a DataFrame using a specified strategy.

    Rules:
        - Works only on numeric columns.
        - Strategy options: "mean", "median", "mode", or "zero".
        - Returns a new DataFrame; original is not modified.

    Args:
        df (pd.DataFrame): Input DataFrame.
        strategy (str): Method to fill missing values.

    Returns:
        pd.DataFrame: DataFrame with filled numeric values.

    Raises:
        TypeError: If input is not a DataFrame.
        ValueError: If strategy is unsupported.

    Example:
        >>> clean_df = fill_missing_values(df, strategy="mean")
    """
    import pandas as pd
    import numpy as np
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a DataFrame.")
    if strategy not in ("mean", "median", "mode", "zero"):
        raise ValueError("Unsupported strategy.")

    df = df.copy()
    for col in df.select_dtypes(include=[np.number]).columns:
        if strategy == "mean":
            val = df[col].mean()
        elif strategy == "median":
            val = df[col].median()
        elif strategy == "mode":
            mode_vals = df[col].mode()
            val = mode_vals[0] if not mode_vals.empty else 0
        else:
            val = 0
        df[col].fillna(val, inplace=True)
    return df

#Sukhman - Complex Function
def generate_data_report(df, filename="data_report.txt"):
    """
    Short Description:
        Generates a structured text report summarizing key statistics of a DataFrame.

    Rules:
        - Calculates missing percentages, unique counts, and sample values per column.
        - Writes results to a .txt file with timestamp.
        - Creates the output directory if it doesn't exist.

    Args:
        df (pd.DataFrame): Input dataset to analyze.
        filename (str): Output file path for the report.

    Returns:
        str: Path to the generated report.

    Raises:
        TypeError: If input is not a DataFrame.
        ValueError: If the DataFrame is empty.

    Example:
        >>> report_path = generate_data_report(clean_df, "outputs/report.txt")
    """
    import pandas as pd
    import numpy as np
    import datetime, os

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a DataFrame.")
    if df.empty:
        raise ValueError("Cannot generate report on empty DataFrame.")

    lines = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"DATA REPORT - {now}\n" + "=" * 80 + "\n")
    lines.append(f"Rows: {len(df)}, Columns: {len(df.columns)}\n\n")

    for col in df.columns:
        series = df[col]
        dtype = str(series.dtype)
        missing = series.isna().sum()
        missing_pct = round((missing / len(df)) * 100, 2)
        unique_vals = series.nunique(dropna=True)
        sample_vals = series.dropna().unique()[:5]
        lines.append(f"{col} ({dtype})\n")
        lines.append(f"  Missing: {missing} ({missing_pct}%)\n")
        lines.append(f"  Unique: {unique_vals}\n")
        lines.append("  Sample: " + ", ".join(map(str, sample_vals)) + "\n")
        lines.append("-" * 80 + "\n")

    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return filename



#Simple 1 - Harrang
import re

def validate_email(email: str) -> bool:
    """Validate an email address using a regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.

    Raises:
        TypeError: If email is not a string.

    Examples:
        >>> validate_email("test@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not isinstance(email, str):
        raise TypeError("Input must be a string.")
    
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    return bool(re.match(email_regex, email))

#Medium 1 - Harrang
def filter_rows_by_condition(df, condition_func):
    """Filter rows in a DataFrame based on a custom condition function.

    Args:
        df (pd.DataFrame): The DataFrame to filter.
        condition_func (function): A function that takes a row (as a Series) and returns a boolean.

    Returns:
        pd.DataFrame: A DataFrame with rows that meet the condition.

    Raises:
        TypeError: If df is not a pandas DataFrame or condition_func is not callable.

    Example:
        >>> filtered_df = filter_rows_by_condition(df, lambda row: row['age'] > 30)
    """
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if not callable(condition_func):
        raise TypeError("condition_func must be a callable function.")
    
    return df[df.apply(condition_func, axis=1)]


#Medium 2 - Harrang
def count_unique_values(df) -> dict:
    """Count the number of unique values for each column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to analyze.

    Returns:
        dict: A dictionary where the keys are column names and values are the unique count.

    Raises:
        TypeError: If df is not a pandas DataFrame.

    Example:
        >>> unique_counts = count_unique_values(df)
    """
    import pandas as pd
    
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    
    return {col: df[col].nunique() for col in df.columns}

#Complex 1 - Harrang
def pivot_and_aggregate(df, pivot_column: str, value_column: str, agg_func: str = 'sum') -> pd.DataFrame:
    """Pivot a DataFrame and aggregate values using the specified aggregation function.

    Args:
        df (pd.DataFrame): The DataFrame to pivot.
        pivot_column (str): The column to use for pivoting.
        value_column (str): The column whose values will be aggregated.
        agg_func (str): The aggregation function to use ('sum', 'mean', 'count', etc.).

    Returns:
        pd.DataFrame: A DataFrame with the pivoted and aggregated values.

    Raises:
        ValueError: If the pivot_column or value_column does not exist in the DataFrame.
        TypeError: If df is not a pandas DataFrame.

    Example:
        >>> pivot_df = pivot_and_aggregate(df, 'category', 'sales', 'mean')
    """
    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if pivot_column not in df.columns or value_column not in df.columns:
        raise ValueError(f"Columns {pivot_column} or {value_column} not found in the DataFrame.")

    return df.pivot_table(index=pivot_column, values=value_column, aggfunc=agg_func)
