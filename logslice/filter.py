"""Filter log entries by time range and field patterns."""

from datetime import datetime
from typing import Any, Dict, Optional, Pattern
import re


def filter_by_time_range(
    entry: Dict[str, Any],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> bool:
    """Return True if the entry's timestamp falls within [start, end]."""
    ts = entry.get("timestamp")
    if ts is None:
        return False
    if not isinstance(ts, datetime):
        return False
    if start is not None and ts < start:
        return False
    if end is not None and ts > end:
        return False
    return True


def filter_by_field(
    entry: Dict[str, Any],
    field: str,
    pattern: str,
    case_sensitive: bool = True,
) -> bool:
    """Return True if entry[field] matches the given regex pattern."""
    value = entry.get(field)
    if value is None:
        return False
    flags = 0 if case_sensitive else re.IGNORECASE
    return bool(re.search(pattern, str(value), flags))


def apply_filters(
    entry: Dict[str, Any],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    field_filters: Optional[Dict[str, str]] = None,
    case_sensitive: bool = True,
) -> bool:
    """Apply all active filters to an entry; return True if it passes all."""
    if (start is not None or end is not None) and not filter_by_time_range(
        entry, start, end
    ):
        return False
    if field_filters:
        for field, pattern in field_filters.items():
            if not filter_by_field(entry, field, pattern, case_sensitive):
                return False
    return True
