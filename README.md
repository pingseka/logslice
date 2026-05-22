# logslice

> Command-line utility for extracting and filtering structured log entries from large files by time range or field patterns.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

```bash
# Extract log entries between two timestamps
logslice --file app.log --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00"

# Filter by a specific field pattern
logslice --file app.log --field level=ERROR

# Combine time range and field filter
logslice --file app.log --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00" --field service=auth

# Output results to a file
logslice --file app.log --field level=WARN --output filtered.log
```

### Options

| Flag | Description |
|------|-------------|
| `--file` | Path to the log file |
| `--start` | Start of the time range (ISO 8601) |
| `--end` | End of the time range (ISO 8601) |
| `--field` | Filter by field in `key=value` format |
| `--output` | Write results to a file instead of stdout |
| `--format` | Log format hint: `json`, `logfmt` (default: auto-detect) |

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).