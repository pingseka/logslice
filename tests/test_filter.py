"""Tests for logslice.filter module."""

from datetime import datetime, timezone
import pytest

from logslice.filter import filter_by_time_range, filter_by_field, apply_filters

TS_EARLY = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
TS_MID = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
TS_LATE = datetime(2024, 1, 1, 14, 0, 0, tzinfo=timezone.utc)


# --- filter_by_time_range ---

def test_time_range_within_bounds():
    entry = {"timestamp": TS_MID}
    assert filter_by_time_range(entry, start=TS_EARLY, end=TS_LATE) is True


def test_time_range_before_start():
    entry = {"timestamp": TS_EARLY}
    assert filter_by_time_range(entry, start=TS_MID, end=TS_LATE) is False


def test_time_range_after_end():
    entry = {"timestamp": TS_LATE}
    assert filter_by_time_range(entry, start=TS_EARLY, end=TS_MID) is False


def test_time_range_no_timestamp_key():
    assert filter_by_time_range({}, start=TS_EARLY, end=TS_LATE) is False


def test_time_range_non_datetime_value():
    entry = {"timestamp": "not-a-datetime"}
    assert filter_by_time_range(entry, start=TS_EARLY, end=TS_LATE) is False


def test_time_range_on_boundary():
    entry = {"timestamp": TS_MID}
    assert filter_by_time_range(entry, start=TS_MID, end=TS_MID) is True


# --- filter_by_field ---

def test_field_filter_match():
    entry = {"level": "ERROR"}
    assert filter_by_field(entry, "level", "ERROR") is True


def test_field_filter_no_match():
    entry = {"level": "INFO"}
    assert filter_by_field(entry, "level", "ERROR") is False


def test_field_filter_missing_field():
    assert filter_by_field({}, "level", "ERROR") is False


def test_field_filter_case_insensitive():
    entry = {"level": "error"}
    assert filter_by_field(entry, "level", "ERROR", case_sensitive=False) is True


def test_field_filter_regex_partial():
    entry = {"message": "connection refused by server"}
    assert filter_by_field(entry, "message", r"refused") is True


# --- apply_filters ---

def test_apply_filters_all_pass():
    entry = {"timestamp": TS_MID, "level": "ERROR", "service": "api"}
    assert apply_filters(
        entry,
        start=TS_EARLY,
        end=TS_LATE,
        field_filters={"level": "ERROR", "service": "api"},
    ) is True


def test_apply_filters_time_fails():
    entry = {"timestamp": TS_EARLY, "level": "ERROR"}
    assert apply_filters(entry, start=TS_MID, end=TS_LATE) is False


def test_apply_filters_field_fails():
    entry = {"timestamp": TS_MID, "level": "INFO"}
    assert apply_filters(
        entry, start=TS_EARLY, end=TS_LATE, field_filters={"level": "ERROR"}
    ) is False


def test_apply_filters_no_constraints():
    entry = {"message": "hello"}
    assert apply_filters(entry) is True
