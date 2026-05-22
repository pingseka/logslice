"""Tests for logslice.stats module."""

from datetime import datetime

import pytest

from logslice.stats import compute_stats, format_stats


def _make_entry(ts=None, level=None, **kwargs):
    entry = {}
    if ts is not None:
        entry["timestamp"] = ts
    if level is not None:
        entry["level"] = level
    entry.update(kwargs)
    return entry


DT1 = datetime(2024, 1, 1, 10, 0, 0)
DT2 = datetime(2024, 1, 1, 11, 0, 0)
DT3 = datetime(2024, 1, 1, 12, 0, 0)


def test_compute_stats_empty():
    result = compute_stats([])
    assert result["total"] == 0
    assert result["fields"] == []
    assert result["earliest"] is None
    assert result["latest"] is None
    assert result["level_counts"] == {}


def test_compute_stats_total():
    entries = [_make_entry(ts=DT1), _make_entry(ts=DT2)]
    result = compute_stats(entries)
    assert result["total"] == 2


def test_compute_stats_earliest_latest():
    entries = [_make_entry(ts=DT2), _make_entry(ts=DT1), _make_entry(ts=DT3)]
    result = compute_stats(entries)
    assert result["earliest"] == DT1
    assert result["latest"] == DT3


def test_compute_stats_no_timestamps():
    entries = [_make_entry(message="hello"), _make_entry(message="world")]
    result = compute_stats(entries)
    assert result["earliest"] is None
    assert result["latest"] is None


def test_compute_stats_fields_sorted():
    entries = [
        _make_entry(ts=DT1, message="a", host="h1"),
        _make_entry(ts=DT2, message="b"),
    ]
    result = compute_stats(entries)
    assert result["fields"] == sorted(result["fields"])
    assert "timestamp" in result["fields"]
    assert "message" in result["fields"]


def test_compute_stats_level_counts():
    entries = [
        _make_entry(level="info"),
        _make_entry(level="INFO"),
        _make_entry(level="error"),
        _make_entry(level="warn"),
    ]
    result = compute_stats(entries)
    assert result["level_counts"]["INFO"] == 2
    assert result["level_counts"]["ERROR"] == 1
    assert result["level_counts"]["WARN"] == 1


def test_compute_stats_severity_fallback():
    entries = [_make_entry(severity="DEBUG")]
    result = compute_stats(entries)
    assert result["level_counts"].get("DEBUG") == 1


def test_compute_stats_custom_timestamp_key():
    entries = [_make_entry(**{"time": DT1}), _make_entry(**{"time": DT2})]
    result = compute_stats(entries, timestamp_key="time")
    assert result["earliest"] == DT1
    assert result["latest"] == DT2


def test_format_stats_contains_total():
    entries = [_make_entry(ts=DT1, level="info", message="ok")]
    stats = compute_stats(entries)
    output = format_stats(stats)
    assert "Total entries" in output
    assert "1" in output


def test_format_stats_contains_levels():
    entries = [_make_entry(level="error"), _make_entry(level="info")]
    stats = compute_stats(entries)
    output = format_stats(stats)
    assert "ERROR" in output
    assert "INFO" in output


def test_format_stats_no_levels_omits_line():
    entries = [_make_entry(message="no level here")]
    stats = compute_stats(entries)
    output = format_stats(stats)
    assert "Levels" not in output
