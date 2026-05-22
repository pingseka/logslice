"""Integration tests for logslice.slicer using temporary log files."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from logslice.slicer import slice_to_list


def _write_json_log(path: Path, entries: list[dict]) -> None:
    with path.open("w") as fh:
        for entry in entries:
            fh.write(json.dumps(entry) + "\n")


@pytest.fixture()
def sample_log(tmp_path):
    log_file = tmp_path / "app.log"
    _write_json_log(
        log_file,
        [
            {"timestamp": "2024-06-01T10:00:00Z", "level": "INFO", "msg": "started"},
            {"timestamp": "2024-06-01T11:00:00Z", "level": "ERROR", "msg": "boom"},
            {"timestamp": "2024-06-01T12:00:00Z", "level": "INFO", "msg": "recovered"},
            {"timestamp": "2024-06-01T13:00:00Z", "level": "WARN", "msg": "slow query"},
        ],
    )
    return log_file


def test_slice_no_filters_returns_all(sample_log):
    results = slice_to_list(sample_log)
    assert len(results) == 4


def test_slice_by_start_time(sample_log):
    start = datetime(2024, 6, 1, 11, 0, 0, tzinfo=timezone.utc)
    results = slice_to_list(sample_log, start=start)
    assert len(results) == 3
    assert all(e["timestamp"] >= start for e in results)


def test_slice_by_end_time(sample_log):
    end = datetime(2024, 6, 1, 11, 0, 0, tzinfo=timezone.utc)
    results = slice_to_list(sample_log, end=end)
    assert len(results) == 2


def test_slice_by_time_range(sample_log):
    start = datetime(2024, 6, 1, 11, 0, 0, tzinfo=timezone.utc)
    end = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    results = slice_to_list(sample_log, start=start, end=end)
    assert len(results) == 2


def test_slice_by_field_filter(sample_log):
    results = slice_to_list(sample_log, field_filters={"level": "ERROR"})
    assert len(results) == 1
    assert results[0]["level"] == "ERROR"


def test_slice_combined_filters(sample_log):
    start = datetime(2024, 6, 1, 10, 30, 0, tzinfo=timezone.utc)
    results = slice_to_list(
        sample_log, start=start, field_filters={"level": "INFO"}
    )
    assert len(results) == 1
    assert results[0]["msg"] == "recovered"


def test_slice_empty_result(sample_log):
    results = slice_to_list(sample_log, field_filters={"level": "CRITICAL"})
    assert results == []
