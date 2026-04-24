from __future__ import annotations

"""Eski veritabanı katmanı için uyumluluk sarmalı.

Bu modül artık kendi başına şema veya kayıt mantığı taşımaz.
Eski içe aktarımlar kırılsa bile veri işlemleri tek gerçek kaynak olan
`data.database` üzerinden yürüsün diye burada yalnızca yönlendirme yapılır.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from data.database import (
    connect_db,
    get_all_codes_from_db as _get_all_codes_from_db,
    get_db_path,
    get_news_count_for_month,
    init_db,
    iter_internal_db_paths,
    upsert_news,
)


def month_key_from_iso(iso_date: str) -> str:
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return dt.strftime("%Y_%m")


def db_path(channel_name: str, iso_date: str) -> Path:
    return get_db_path(channel_name, iso_date)


def connect(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(path))


def get_all_codes_from_db(channel_name: str, iso_date: str):
    return _get_all_codes_from_db(channel_name, iso_date)


def month_range(start_iso: str, end_iso: str):
    start = datetime.strptime(start_iso, "%Y-%m-%d")
    end = datetime.strptime(end_iso, "%Y-%m-%d")

    current = datetime(start.year, start.month, 1)
    last = datetime(end.year, end.month, 1)

    items = []
    while current <= last:
        items.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)

    return items


def db_paths_for_range(channel_name: str, start_iso: str, end_iso: str):
    return iter_internal_db_paths(
        channel_name,
        start_iso,
        end_iso,
        include_legacy=False,
        existing_only=True,
    )


def get_all_codes_for_range(channel_name: str, start_iso: str, end_iso: str):
    codes = set()
    for path in db_paths_for_range(channel_name, start_iso, end_iso):
        conn = connect(path)
        try:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT news_code FROM news WHERE news_code <> ''")
            for row in cur.fetchall():
                codes.add(row[0])
        finally:
            conn.close()
    return sorted(codes)
