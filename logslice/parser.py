"""Log entry parser for structured log formats (JSON and key=value)."""

import json
import re
from datetime import datetime
from typing import Optional


LOG_TIMESTAMP_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
]

KV_PATTERN = re.compile(r'(\w+)=("[^"]*"|\S+)')


def parse_timestamp(value: str) -> Optional[datetime]:
    """Attempt to parse a timestamp string using known formats."""
    for fmt in LOG_TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def parse_json_line(line: str) -> Optional[dict]:
    """Parse a JSON log line into a dictionary."""
    try:
        entry = json.loads(line.strip())
        if isinstance(entry, dict):
            return entry
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def parse_kv_line(line: str) -> Optional[dict]:
    """Parse a key=value log line into a dictionary."""
    matches = KV_PATTERN.findall(line.strip())
    if not matches:
        return None
    return {k: v.strip('"') for k, v in matches}


def parse_line(line: str) -> Optional[dict]:
    """Auto-detect and parse a structured log line."""
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("{"):
        return parse_json_line(stripped)
    return parse_kv_line(stripped)


def extract_timestamp(entry: dict, ts_field: str = "timestamp") -> Optional[datetime]:
    """Extract and parse the timestamp from a log entry dict."""
    for key in (ts_field, "time", "ts", "@timestamp"):
        if key in entry:
            result = parse_timestamp(str(entry[key]))
            if result:
                return result
    return None
