"""Statistics and summary utilities for log entries."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional


def compute_stats(entries: List[Dict[str, Any]], timestamp_key: str = "timestamp") -> Dict[str, Any]:
    """Return summary statistics for a list of parsed log entries.

    Parameters
    ----------
    entries:
        Iterable of parsed log entry dicts.
    timestamp_key:
        The field name used for timestamps.

    Returns
    -------
    dict with keys: total, fields, earliest, latest, level_counts
    """
    if not entries:
        return {
            "total": 0,
            "fields": [],
            "earliest": None,
            "latest": None,
            "level_counts": {},
        }

    field_counter: Counter = Counter()
    level_counter: Counter = Counter()
    timestamps: List[datetime] = []

    for entry in entries:
        for key in entry:
            field_counter[key] += 1

        ts = entry.get(timestamp_key)
        if isinstance(ts, datetime):
            timestamps.append(ts)

        level = entry.get("level") or entry.get("severity") or entry.get("log_level")
        if level is not None:
            level_counter[str(level).upper()] += 1

    return {
        "total": len(entries),
        "fields": sorted(field_counter.keys()),
        "earliest": min(timestamps) if timestamps else None,
        "latest": max(timestamps) if timestamps else None,
        "level_counts": dict(level_counter),
    }


def format_stats(stats: Dict[str, Any]) -> str:
    """Render a stats dict as a human-readable string."""
    lines = [
        f"Total entries : {stats['total']}",
        f"Fields present: {', '.join(stats['fields']) if stats['fields'] else '(none)'}",
        f"Earliest      : {stats['earliest'] or 'N/A'}",
        f"Latest        : {stats['latest'] or 'N/A'}",
    ]
    if stats.get("level_counts"):
        level_str = ", ".join(
            f"{lvl}={cnt}" for lvl, cnt in sorted(stats["level_counts"].items())
        )
        lines.append(f"Levels        : {level_str}")
    return "\n".join(lines)
