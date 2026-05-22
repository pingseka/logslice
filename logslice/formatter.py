"""Output formatters for log entries."""

import json
from typing import Any, Dict, List, Optional


FORMAT_JSON = "json"
FORMAT_TEXT = "text"
FORMAT_CSV = "csv"

SUPPORTED_FORMATS = (FORMAT_JSON, FORMAT_TEXT, FORMAT_CSV)


def format_json(entry: Dict[str, Any], indent: Optional[int] = None) -> str:
    """Serialize a log entry as a JSON string."""
    return json.dumps(entry, default=str, indent=indent)


def format_text(entry: Dict[str, Any], fields: Optional[List[str]] = None) -> str:
    """Format a log entry as a human-readable key=value string.

    If *fields* is provided only those keys are included, in order.
    """
    if fields:
        pairs = [(k, entry[k]) for k in fields if k in entry]
    else:
        pairs = list(entry.items())
    return " ".join(f"{k}={v}" for k, v in pairs)


def format_csv_header(fields: List[str]) -> str:
    """Return a CSV header row for the given field names."""
    return ",".join(fields)


def format_csv(entry: Dict[str, Any], fields: List[str]) -> str:
    """Format a log entry as a CSV row.

    Missing fields are rendered as empty strings.
    Values containing commas or quotes are quoted per RFC 4180.
    """
    parts = []
    for field in fields:
        value = str(entry.get(field, ""))
        if "," in value or '"' in value or "\n" in value:
            value = '"' + value.replace('"', '""') + '"'
        parts.append(value)
    return ",".join(parts)


def format_entry(
    entry: Dict[str, Any],
    fmt: str = FORMAT_JSON,
    fields: Optional[List[str]] = None,
    indent: Optional[int] = None,
) -> str:
    """Dispatch to the appropriate formatter.

    Args:
        entry: Parsed log entry dictionary.
        fmt: One of 'json', 'text', or 'csv'.
        fields: Optional list of field names (used by 'text' and 'csv').
        indent: JSON indentation level (only used when fmt='json').

    Returns:
        Formatted string representation of the entry.

    Raises:
        ValueError: If *fmt* is not a supported format.
    """
    if fmt == FORMAT_JSON:
        return format_json(entry, indent=indent)
    if fmt == FORMAT_TEXT:
        return format_text(entry, fields=fields)
    if fmt == FORMAT_CSV:
        if not fields:
            raise ValueError("'fields' must be provided for CSV format")
        return format_csv(entry, fields)
    raise ValueError(f"Unsupported format {fmt!r}. Choose from {SUPPORTED_FORMATS}")
