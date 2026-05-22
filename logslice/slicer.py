"""High-level API: slice a log file by time range and/or field filters."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, Any, Optional

from logslice.reader import iter_entries
from logslice.filter import apply_filters


def slice_log(
    path: str | Path,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    field_filters: Optional[Dict[str, str]] = None,
    case_sensitive: bool = True,
    encoding: str = "utf-8",
) -> Generator[Dict[str, Any], None, None]:
    """Yield log entries from *path* that satisfy all provided filters.

    Parameters
    ----------
    path:           Path to the log file.
    start:          Inclusive lower bound on entry timestamps.
    end:            Inclusive upper bound on entry timestamps.
    field_filters:  Mapping of field name → regex pattern.
    case_sensitive: Whether field regex matching is case-sensitive.
    encoding:       File encoding (default: utf-8).
    """
    for entry in iter_entries(path, encoding=encoding):
        if apply_filters(
            entry,
            start=start,
            end=end,
            field_filters=field_filters,
            case_sensitive=case_sensitive,
        ):
            yield entry


def slice_to_list(
    path: str | Path,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    field_filters: Optional[Dict[str, str]] = None,
    case_sensitive: bool = True,
    encoding: str = "utf-8",
) -> list[Dict[str, Any]]:
    """Convenience wrapper around :func:`slice_log` that returns a list."""
    return list(
        slice_log(
            path,
            start=start,
            end=end,
            field_filters=field_filters,
            case_sensitive=case_sensitive,
            encoding=encoding,
        )
    )
