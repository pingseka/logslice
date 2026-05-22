"""Tests for logslice.formatter."""

import json
import pytest

from logslice.formatter import (
    format_json,
    format_text,
    format_csv_header,
    format_csv,
    format_entry,
    FORMAT_JSON,
    FORMAT_TEXT,
    FORMAT_CSV,
)

SAMPLE = {"timestamp": "2024-01-15T10:00:00", "level": "INFO", "message": "started"}


# --- format_json ---

def test_format_json_roundtrip():
    result = format_json(SAMPLE)
    assert json.loads(result) == SAMPLE


def test_format_json_indent():
    result = format_json(SAMPLE, indent=2)
    assert "\n" in result


def test_format_json_non_serialisable_uses_str():
    from datetime import datetime
    entry = {"ts": datetime(2024, 1, 1)}
    result = format_json(entry)
    assert "2024-01-01" in result


# --- format_text ---

def test_format_text_all_fields():
    result = format_text(SAMPLE)
    assert "level=INFO" in result
    assert "message=started" in result


def test_format_text_selected_fields():
    result = format_text(SAMPLE, fields=["level", "message"])
    assert result == "level=INFO message=started"
    assert "timestamp" not in result


def test_format_text_missing_field_skipped():
    result = format_text(SAMPLE, fields=["level", "nonexistent"])
    assert result == "level=INFO"


# --- format_csv ---

def test_format_csv_header():
    header = format_csv_header(["timestamp", "level", "message"])
    assert header == "timestamp,level,message"


def test_format_csv_basic():
    result = format_csv(SAMPLE, ["timestamp", "level", "message"])
    assert result == "2024-01-15T10:00:00,INFO,started"


def test_format_csv_missing_field_empty():
    result = format_csv({"level": "WARN"}, ["timestamp", "level"])
    assert result == ",WARN"


def test_format_csv_quotes_value_with_comma():
    entry = {"msg": "hello, world"}
    result = format_csv(entry, ["msg"])
    assert result == '"hello, world"'


def test_format_csv_quotes_value_with_double_quote():
    entry = {"msg": 'say "hi"'}
    result = format_csv(entry, ["msg"])
    assert result == '"say ""hi"""'


# --- format_entry dispatch ---

def test_format_entry_json():
    result = format_entry(SAMPLE, fmt=FORMAT_JSON)
    assert json.loads(result) == SAMPLE


def test_format_entry_text():
    result = format_entry(SAMPLE, fmt=FORMAT_TEXT, fields=["level"])
    assert result == "level=INFO"


def test_format_entry_csv():
    result = format_entry(SAMPLE, fmt=FORMAT_CSV, fields=["level", "message"])
    assert result == "INFO,started"


def test_format_entry_csv_requires_fields():
    with pytest.raises(ValueError, match="fields"):
        format_entry(SAMPLE, fmt=FORMAT_CSV)


def test_format_entry_invalid_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        format_entry(SAMPLE, fmt="xml")
