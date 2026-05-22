"""Tests for logslice.parser module."""

import pytest
from datetime import datetime
from logslice.parser import (
    parse_timestamp,
    parse_json_line,
    parse_kv_line,
    parse_line,
    extract_timestamp,
)


def test_parse_timestamp_iso_with_microseconds():
    result = parse_timestamp("2024-03-15T12:30:45.123456Z")
    assert result == datetime(2024, 3, 15, 12, 30, 45, 123456)


def test_parse_timestamp_iso_basic():
    result = parse_timestamp("2024-03-15T12:30:45")
    assert result == datetime(2024, 3, 15, 12, 30, 45)


def test_parse_timestamp_invalid():
    assert parse_timestamp("not-a-date") is None


def test_parse_json_line_valid():
    line = '{"level": "info", "msg": "started", "timestamp": "2024-01-01T00:00:00Z"}'
    result = parse_json_line(line)
    assert result == {"level": "info", "msg": "started", "timestamp": "2024-01-01T00:00:00Z"}


def test_parse_json_line_invalid():
    assert parse_json_line("not json") is None


def test_parse_json_line_array():
    assert parse_json_line("[1, 2, 3]") is None


def test_parse_kv_line_basic():
    line = 'level=info msg="service started" host=web-01'
    result = parse_kv_line(line)
    assert result["level"] == "info"
    assert result["msg"] == "service started"
    assert result["host"] == "web-01"


def test_parse_kv_line_empty():
    assert parse_kv_line("") is None


def test_parse_line_detects_json():
    line = '{"event": "login", "user": "alice"}'
    result = parse_line(line)
    assert result == {"event": "login", "user": "alice"}


def test_parse_line_detects_kv():
    line = "event=login user=alice"
    result = parse_line(line)
    assert result["event"] == "login"
    assert result["user"] == "alice"


def test_parse_line_blank():
    assert parse_line("") is None
    assert parse_line("   ") is None


def test_extract_timestamp_standard_field():
    entry = {"timestamp": "2024-06-01T10:00:00Z", "msg": "ok"}
    result = extract_timestamp(entry)
    assert result == datetime(2024, 6, 1, 10, 0, 0)


def test_extract_timestamp_fallback_field():
    entry = {"ts": "2024-06-01T10:00:00", "msg": "ok"}
    result = extract_timestamp(entry)
    assert result == datetime(2024, 6, 1, 10, 0, 0)


def test_extract_timestamp_missing():
    entry = {"msg": "no time here"}
    assert extract_timestamp(entry) is None
