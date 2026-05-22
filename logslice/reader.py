"""Read and iterate over log files, yielding parsed entries."""

from pathlib import Path
from typing import Generator, Dict, Any, Optional

from logslice.parser import parse_line, extract_timestamp


def iter_entries(
    path: str | Path,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Generator[Dict[str, Any], None, None]:
    """Yield parsed log entries from *path*, one per line.

    Lines that cannot be parsed are silently skipped.
    Each yielded dict is guaranteed to have a ``_raw`` key containing the
    original line and a ``_lineno`` key with the 1-based line number.
    If a timestamp was detected it is stored under ``timestamp``.
    """
    path = Path(path)
    with path.open(encoding=encoding, errors=errors) as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")
            entry = parse_line(line)
            if entry is None:
                continue
            entry["_raw"] = line
            entry["_lineno"] = lineno
            ts = extract_timestamp(entry)
            if ts is not None:
                entry["timestamp"] = ts
            yield entry


def count_entries(path: str | Path) -> int:
    """Return the total number of parseable entries in *path*."""
    return sum(1 for _ in iter_entries(path))
