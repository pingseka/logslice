"""Tests for the logslice CLI module."""

import json
import os
import tempfile
import pytest

from logslice.cli import build_parser, parse_datetime_arg, parse_field_filter, run
from datetime import datetime
import argparse


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _write_log(lines):
    """Write JSON log lines to a temp file and return its path."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False)
    for line in lines:
        tmp.write(json.dumps(line) + "\n")
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# Unit tests for helper parsers
# ---------------------------------------------------------------------------

def test_parse_datetime_arg_iso():
    dt = parse_datetime_arg("2024-01-15T10:30:00")
    assert dt == datetime(2024, 1, 15, 10, 30, 0)


def test_parse_datetime_arg_space_sep():
    dt = parse_datetime_arg("2024-01-15 10:30:00")
    assert dt == datetime(2024, 1, 15, 10, 30, 0)


def test_parse_datetime_arg_date_only():
    dt = parse_datetime_arg("2024-01-15")
    assert dt == datetime(2024, 1, 15)


def test_parse_datetime_arg_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_datetime_arg("not-a-date")


def test_parse_field_filter_valid():
    field, pattern = parse_field_filter("level=ERROR")
    assert field == "level"
    assert pattern == "ERROR"


def test_parse_field_filter_no_equals():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_field_filter("levelERROR")


def test_parse_field_filter_value_with_equals():
    field, pattern = parse_field_filter("msg=a=b")
    assert field == "msg"
    assert pattern == "a=b"


# ---------------------------------------------------------------------------
# Integration tests using run()
# ---------------------------------------------------------------------------

@pytest.fixture()
def log_file():
    lines = [
        {"timestamp": "2024-03-01T08:00:00", "level": "INFO", "msg": "start"},
        {"timestamp": "2024-03-01T09:00:00", "level": "ERROR", "msg": "oops"},
        {"timestamp": "2024-03-01T10:00:00", "level": "INFO", "msg": "end"},
    ]
    path = _write_log(lines)
    yield path
    os.unlink(path)


def test_run_no_filters_returns_all(log_file, capsys):
    rc = run([log_file])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.count("\n") == 3


def test_run_start_filter(log_file, capsys):
    rc = run([log_file, "--start", "2024-03-01T09:00:00"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.count("\n") == 2


def test_run_field_filter(log_file, capsys):
    rc = run([log_file, "--field", "level=ERROR"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = [json.loads(l) for l in out.strip().splitlines()]
    assert len(parsed) == 1
    assert parsed[0]["level"] == "ERROR"


def test_run_count_flag(log_file, capsys):
    rc = run([log_file, "--count"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == "3"


def test_run_text_format(log_file, capsys):
    rc = run([log_file, "--format", "text"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "level=" in out or "msg=" in out


def test_run_missing_file(capsys):
    with pytest.raises(SystemExit):
        run(["nonexistent_file_xyz.log"])
