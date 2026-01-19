#!/usr/bin/env python3
"""
sync_copy_with_report.py

Usage:
    python sync_copy_with_report.py /path/to/source /path/to/destination [--report-dir /path/to/reportdir]

Behavior:
- Recursively copies files from source to destination.
- If destination file does not exist -> copy (new).
- If destination file exists and sizes differ -> overwrite (overwritten).
- If destination file exists and sizes are identical -> skip (skipped).
- Produces a report file named YYYY-MM-DD_Report.txt (America/Chicago date).
"""

import argparse
import os
import shutil
from datetime import datetime
try:
    # Python 3.9+
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

def chicago_today_str():
    """Return today's date string YYYY-MM-DD using America/Chicago where possible."""
    try:
        if ZoneInfo is not None:
            tz = ZoneInfo("America/Chicago")
            now = datetime.now(tz)
        else:
            # Fallback to system local time if zoneinfo not available
            now = datetime.now()
    except Exception:
        now = datetime.now()
    return now.strftime("%Y-%m-%d")

def ensure_parent_dir(path):
    parent = os.path.dirname(path)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

def sync_copy(src, dst):
    """
    Copy files from src -> dst with logic:
      - new files: file doesn't exist in dst -> copy
      - overwritten: file exists in dst but size differs -> copy (overwrite)
      - skipped: file exists in dst and size equal -> skip
    Returns dict with lists: new, overwritten, skipped, errors
    """
    results = {
        "new": [],
        "overwritten": [],
        "skipped": [],
        "errors": []
    }

    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    if not os.path.exists(src):
        raise FileNotFoundError(f"Source not found: {src}")
    if not os.path.isdir(src):
        raise NotADirectoryError(f"Source is not a directory: {src}")

    # Walk through source directory
    for root, dirs, files in os.walk(src, followlinks=False):
        # Compute corresponding destination directory
        rel_dir = os.path.relpath(root, src)
        if rel_dir == ".":
            rel_dir = ""
        dst_dir = os.path.join(dst, rel_dir)
        # ensure destination directory exists
        os.makedirs(dst_dir, exist_ok=True)

        for fname in files:
            src_path = os.path.join(root, fname)
            dst_path = os.path.join(dst_dir, fname)

            try:
                # If dst file doesn't exist -> new copy
                if not os.path.exists(dst_path):
                    # ensure parent exists (already created per dir loop)
                    shutil.copy2(src_path, dst_path, follow_symlinks=False)
                    results["new"].append(os.path.relpath(dst_path, dst))
                    continue

                # both files exist -> compare sizes
                try:
                    src_size = os.path.getsize(src_path)
                except OSError:
                    src_size = None
                try:
                    dst_size = os.path.getsize(dst_path)
                except OSError:
                    dst_size = None

                if src_size is None or dst_size is None:
                    # fallback: use byte-by-byte check if sizes unavailable (rare)
                    # but for safety, treat as different and overwrite
                    shutil.copy2(src_path, dst_path, follow_symlinks=false)
                    results["overwritten"].append(os.path.relpath(dst_path, dst))
                elif src_size != dst_size:
                    shutil.copy2(src_path, dst_path, follow_symlinks=false)
                    results["overwritten"].append(os.path.relpath(dst_path, dst))
                else:
                    # same size -> skip
                    results["skipped"].append(os.path.relpath(dst_path, dst))
            except Exception as e:
                results["errors"].append(f"{os.path.relpath(src_path, src)} -> {e}")

    return results


def write_error_report(error_message, report_directory, file_name):
    date_str = chicago_today_str()
    report_name = f"{date_str}_{file_name}.txt"
    os.makedirs(report_directory, exist_ok=True)
    report_path = os.path.join(report_directory, report_name)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Report date (America/Chicago): {date_str}\n")
        f.write("Summary:\n")
        f.write("  New files:         0\n")
        f.write("  Overwritten files: 0\n")
        f.write("  Skipped files:     0\n")
        f.write("  Errors:            1\n\n")
        f.write("Errors:\n")
        f.write(f"  {error_message}\n\n")
        f.write("End of report\n")

    return report_path

def write_report(results, report_directory, file_name):
    date_str = chicago_today_str()
    report_name = f"{date_str}_{file_name}.txt"
    os.makedirs(report_directory, exist_ok=True)
    report_path = os.path.join(report_directory, report_name)

    new_count = len(results.get("new", []))
    overwritten_count = len(results.get("overwritten", []))
    skipped_count = len(results.get("skipped", []))
    errors = results.get("errors", [])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Report date (America/Chicago): {date_str}\n")
        f.write("Summary:\n")
        f.write(f"  New files:         {new_count}\n")
        f.write(f"  Overwritten files: {overwritten_count}\n")
        f.write(f"  Skipped files:     {skipped_count}\n")
        f.write(f"  Errors:            {len(errors)}\n")
        f.write("\n")

        # Optionally include lists (first 200 entries each to avoid massive files)
        max_list_items = 200

        if errors:
            f.write("Errors:\n")
            for e in errors:
                f.write(f"  {e}\n")
            f.write("\n")

        f.write("End of report\n")

    return report_path

def parse_args():
    p = argparse.ArgumentParser(description="Sync copy with size-based overwrite and report")
    p.add_argument("src", help="Source directory to copy from")
    p.add_argument("dst", help="Destination directory to copy to")
    p.add_argument("--report-dir", "-r", default=None,
                   help="Directory where report file will be written. Defaults to destination directory.")
    p.add_argument("--file_name", "-f", default="example", help="file name for the report file.  Defaults to example")
    return p.parse_args()

def main():
    args = parse_args()
    src = args.src
    dst = args.dst
    report_dir = args.report_dir or dst
    file_name = args.file_name

    try:
        # Validate source first
        if not os.path.exists(src):
            raise FileNotFoundError(f"Source directory does not exist: {os.path.abspath(src)}")
        if not os.path.isdir(src):
            raise NotADirectoryError(f"Source is not a directory: {os.path.abspath(src)}")

        # Ensure destination exists or can be created
        try:
            os.makedirs(dst, exist_ok=True)
        except Exception as e:
            raise PermissionError(f"Cannot create destination directory: {os.path.abspath(dst)} ({e})")

        print(f"Copying from: {src}")
        print(f"Copying to:   {dst}")

        results = sync_copy(src, dst)
        report_path = write_report(results, report_dir, file_name)

        print("\nDone.")
        print(f"Report written to: {report_path}")
        print(
            f"New: {len(results['new'])}, "
            f"Overwritten: {len(results['overwritten'])}, "
            f"Skipped: {len(results['skipped'])}, "
            f"Errors: {len(results['errors'])}"
        )

    except Exception as exc:
        # ALWAYS write a report even on failure
        error_message = str(exc)
        report_path = write_error_report(error_message, report_dir, file_name)
        print(f"Fatal error: {error_message}")
        print(f"Error report written to: {report_path}")

if __name__ == "__main__":
    main()
