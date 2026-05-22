"""Command-line interface for logslice."""

import argparse
import sys
from datetime import datetime
from typing import Optional

from logslice.slicer import slice_log
from logslice.formatter import format_entry


DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
]


def parse_datetime_arg(value: str) -> datetime:
    """Parse a datetime string from CLI argument."""
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(
        f"Cannot parse datetime '{value}'. "
        "Expected formats: YYYY-MM-DDTHH:MM:SS, YYYY-MM-DD HH:MM:SS, YYYY-MM-DD"
    )


def parse_field_filter(value: str) -> tuple:
    """Parse a field=pattern filter argument."""
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            f"Invalid field filter '{value}'. Expected format: field=pattern"
        )
    field, _, pattern = value.partition("=")
    return field.strip(), pattern.strip()


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="Extract and filter structured log entries from large files.",
    )
    parser.add_argument("file", help="Path to the log file to process")
    parser.add_argument(
        "--start", type=parse_datetime_arg, default=None,
        metavar="DATETIME", help="Start of time range (inclusive)"
    )
    parser.add_argument(
        "--end", type=parse_datetime_arg, default=None,
        metavar="DATETIME", help="End of time range (inclusive)"
    )
    parser.add_argument(
        "--field", action="append", type=parse_field_filter,
        metavar="FIELD=PATTERN", dest="fields",
        help="Filter by field value pattern (repeatable)"
    )
    parser.add_argument(
        "--format", choices=["json", "text", "csv"], default="json",
        dest="output_format", help="Output format (default: json)"
    )
    parser.add_argument(
        "--fields", nargs="+", metavar="FIELD", dest="output_fields",
        help="Limit output to specified fields"
    )
    parser.add_argument(
        "--count", action="store_true",
        help="Print only the count of matching entries"
    )
    return parser


def run(argv=None) -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    field_filters = dict(args.fields) if args.fields else {}

    entries = slice_log(
        path=args.file,
        start=args.start,
        end=args.end,
        field_filters=field_filters,
    )

    if args.count:
        total = sum(1 for _ in entries)
        print(total)
        return 0

    first = True
    for entry in entries:
        if args.output_format == "csv" and first:
            from logslice.formatter import format_csv_header
            print(format_csv_header(entry, args.output_fields))
            first = False
        line = format_entry(entry, fmt=args.output_format, fields=args.output_fields)
        print(line)

    return 0


if __name__ == "__main__":
    sys.exit(run())
