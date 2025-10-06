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


