from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.settings_manager import load_settings
from data.database import get_news_for_date
from parsing.scanner import _candidate_paths, build_date_path, scan_news_files


def run_debug(root_folder: str, channel_name: str, date_str: str) -> int:
    day, month, year = date_str.split(".")
    folder_name = f"{month}{day}{year}.egs"
    root = Path(root_folder)

    print("=== EGS Day Scan Debugger ===")
    print(f"Channel   : {channel_name}")
    print(f"Date      : {date_str}")
    print(f"Root      : {root}")
    print()

    print("Candidate paths:")
    for candidate in _candidate_paths(root, year, folder_name):
        print(f" - {candidate} | exists={candidate.exists()}")
    print()

    target_dir = build_date_path(root_folder, date_str)
    print(f"Resolved path : {target_dir}")
    print(f"Exists        : {target_dir.exists()}")
    print()

    files = scan_news_files(root_folder, date_str, channel_name)
    db_items = get_news_for_date(channel_name, f"{year}-{month}-{day}")

    file_names = {path.name.casefold() for path in files}
    db_names = {str(item.get('file_name', '')).strip().casefold() for item in db_items}

    missing_in_db = sorted(file_names - db_names)
    extra_in_db = sorted(db_names - file_names)

    print(f"Scanned files  : {len(files)}")
    print(f"DB records     : {len(db_items)}")
    print(f"Missing in DB  : {len(missing_in_db)}")
    print(f"Extra in DB    : {len(extra_in_db)}")
    print()

    if missing_in_db:
        print("Sample missing in DB:")
        for name in missing_in_db[:20]:
            print(f" - {name}")
        print()

    if extra_in_db:
        print("Sample extra in DB:")
        for name in extra_in_db[:20]:
            print(f" - {name}")
        print()

    print("Done.")
    return 0


def main() -> int:
    settings = load_settings()

    parser = argparse.ArgumentParser(description="Diagnose day scan / DB mismatches.")
    parser.add_argument("--root", default=str(settings.get("root_folder", "") or ""))
    parser.add_argument("--channel", default=str(settings.get("channel_name", "") or "A HABER"))
    parser.add_argument("--date", default="16.04.2026")
    args = parser.parse_args()

    return run_debug(args.root, args.channel, args.date)


if __name__ == "__main__":
    raise SystemExit(main())
