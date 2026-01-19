# file_sync_py

A small CLI utility to recursively copy files from a source directory to a destination directory with size-based overwrite logic and a generated report.

```
python test_copy.py exports exports_new --report-dir ~/Desktop --file_name www
```

- New files are copied when they don't exist in the destination.
- If a destination file exists and the sizes differ, the source file overwrites the destination.
- If a destination file exists and sizes are identical, the file is skipped.
- A report is written after the run (or on fatal error) summarizing the operation.

Written in Python; intended to be run as a script (e.g., `python file_sync.py ...`).

## Features

- Recursively copies files from source to destination.
- Overwrites destination files only when file sizes differ (to avoid unnecessary writes).
- Produces a human-readable report named `{YYYY-MM-DD}_{file_name}.txt` (date in America/Chicago where possible).
- Writes an error report if a fatal exception occurs.
- Handles creation of destination and report directories automatically.

## Requirements

- Python 3.x (Python 3.9+ recommended so the script can use the standard library `zoneinfo` for America/Chicago timestamps; script will fall back to system local time if zoneinfo is unavailable).
- No external dependencies.

## Installation

Clone the repository or copy `file_sync.py` to a machine with Python installed.

Optionally make the script executable:
```
chmod +x file_sync.py
```

Then run with Python:
```
python file_sync.py <src> <dst> [--report-dir REPORT_DIR] [--file_name FILE_NAME]
```

Or, if executable:
```
./file_sync.py <src> <dst> ...
```

## How to use

Basic usage:
```
python file_sync.py /path/to/source /path/to/destination
```

With optional report directory and custom report filename:
```
python file_sync.py /path/to/source /path/to/destination --report-dir /path/to/reports --file_name my_report
```

Short forms:
- `-r` or `--report-dir` — Directory where the report file will be written. If not provided, the destination directory is used.
- `-f` or `--file_name` — Base name used for the report file (default: `example`).

Report filename:
- The generated report will be named `{YYYY-MM-DD}_{file_name}.txt`.
- The date uses the America/Chicago timezone when available (via `zoneinfo`), otherwise it uses system local time.

Example:
```
python file_sync.py ~/Documents/source ~/backup/destination -r ~/backup/reports -f daily_backup
```

After the run you will see output like:
- "Copying from: /home/user/Documents/source"
- "Copying to:   /home/user/backup/destination"
- "Done."
- "Report written to: /home/user/backup/reports/2026-01-19_daily_backup.txt"
- And counts for New, Overwritten, Skipped, Errors

If a fatal error occurs (for example, source missing or permissions issue), the script will still write a report describing the error to the chosen report directory.

## Report format

The report includes:
- Report date (America/Chicago where possible)
- Summary counts:
  - New files
  - Overwritten files
  - Skipped files
  - Errors
- Optionally includes lists of file paths for new/overwritten/skipped (the script limits lists to avoid extremely large reports)
- Errors section with messages for failed file operations

There is also a specific `write_error_report` helper used to always produce a single-file report with an error message if the script crashes early.

## Behavior details & notes

- Directory creation: destination and report directories are created automatically if they don't exist (using `os.makedirs(..., exist_ok=True)`).
- Symlinks: the script uses copy semantics with `follow_symlinks=False` for `shutil.copy2`. Behavior for symlinks will therefore depend on the platform and `shutil.copy2` behavior with `follow_symlinks=False`.
- Size-based comparison: the script primarily compares file sizes. If sizes are not retrievable (rare), it falls back to treating the files as different and will overwrite.
- Errors for individual files are collected and written to the report; the script attempts to continue where possible.
- Permissions: if the destination directory cannot be created due to permissions, the script will raise and write an error report.

## Example report snippet

Report start:
```
Report date (America/Chicago): 2026-01-19
Summary:
  New files:         3
  Overwritten files: 2
  Skipped files:     11
  Errors:            0

New:
  path/to/newfile1.txt
  path/to/newfile2.txt

Overwritten:
  path/to/changedfile.txt

End of report
```

## Troubleshooting

- "Source directory does not exist": verify the `src` path and that it is a directory.
- Permission errors when creating `dst` or `report-dir`: run with sufficient privileges or choose a writable directory.
- If timezone isn't America/Chicago in the report date, ensure you're running on Python 3.9+ or install and configure a proper tzdata provider for your environment.

## Contributing

If you want to add features (dry-run, preserve timestamps/ownership more explicitly, parallel copy, exclusions, logging levels), open an issue or make a pull request with tests and usage examples.

---

If you'd like, I can:
- Commit this README.md to the repository for you, or
- Add usage examples in a separate examples/ directory, or
- Add a small automated test for sync behavior.

Tell me which of those you'd like me to do next.
