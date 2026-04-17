from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from core.app_paths import DATABASES_DIR


def _safe_channel_name(channel_name: str) -> str:
    value = channel_name.lower().strip()
    value = value.replace(" ", "_")
    value = value.replace("ç", "c").replace("ğ", "g").replace("ı", "i").replace("ö", "o").replace("ş", "s").replace("ü", "u")
    value = re.sub(r"[^a-z0-9_]+", "", value)
    return value or "default"


def month_key_from_iso(iso_date: str) -> str:
    dt = datetime.strptime(iso_date, "%Y-%m-%d")
    return dt.strftime("%Y_%m")


def db_path(channel_name: str, iso_date: str) -> Path:
    channel_key = _safe_channel_name(channel_name)
    month_key = month_key_from_iso(iso_date)
    return DATABASES_DIR / f"{channel_key}_{month_key}.db"


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(channel_name: str, iso_date: str):
    path = db_path(channel_name, iso_date)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = connect(path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            file_name TEXT UNIQUE,
            title TEXT,
            corrected_title TEXT,
            news_code TEXT,
            news_category TEXT,
            format_code TEXT,
            format_name TEXT,
            summary TEXT,
            body TEXT,
            kj_lines TEXT,
            final_text TEXT,
            editors TEXT,
            date_str TEXT,
            iso_date TEXT
        )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_news_iso_date ON news(iso_date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_news_title ON news(title)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_news_code ON news(news_code)")

    conn.commit()
    conn.close()


def upsert_news(channel_name: str, data: dict):
    iso_date = data["iso_date"]
    init_db(channel_name, iso_date)
    path = db_path(channel_name, iso_date)

    conn = connect(path)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO news (
            path, file_name, title, corrected_title, news_code, news_category,
            format_code, format_name, summary, body, kj_lines, final_text,
            editors, date_str, iso_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(file_name) DO UPDATE SET
            path=excluded.path,
            title=excluded.title,
            corrected_title=excluded.corrected_title,
            news_code=excluded.news_code,
            news_category=excluded.news_category,
            format_code=excluded.format_code,
            format_name=excluded.format_name,
            summary=excluded.summary,
            body=excluded.body,
            kj_lines=excluded.kj_lines,
            final_text=excluded.final_text,
            editors=excluded.editors,
            date_str=excluded.date_str,
            iso_date=excluded.iso_date
    """, (
        data.get("path", ""),
        data.get("file_name", ""),
        data.get("title", ""),
        data.get("corrected_title", ""),
        data.get("news_code", ""),
        data.get("news_category", ""),
        data.get("format_code", ""),
        data.get("format_name", ""),
        data.get("summary", ""),
        data.get("body", ""),
        json.dumps(data.get("kj_lines", []), ensure_ascii=False),
        data.get("final_text", ""),
        json.dumps(data.get("editors", []), ensure_ascii=False),
        data.get("date_str", ""),
        data.get("iso_date", ""),
    ))

    conn.commit()
    conn.close()


def get_news_count_for_month(channel_name: str, iso_date: str) -> int:
    path = db_path(channel_name, iso_date)
    if not path.exists():
        return 0

    conn = connect(path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM news")
    row = cur.fetchone()
    conn.close()
    return int(row["cnt"]) if row else 0


def get_all_codes_from_db(channel_name: str, iso_date: str):
    path = db_path(channel_name, iso_date)
    if not path.exists():
        return []

    conn = connect(path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT news_code FROM news WHERE news_code <> '' ORDER BY news_code")
    rows = [r["news_code"] for r in cur.fetchall()]
    conn.close()
    return rows


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
    channel_key = _safe_channel_name(channel_name)
    months = month_range(start_iso, end_iso)
    paths = []

    for ym in months:
        year, month = ym.split("-")
        path = DATABASES_DIR / f"{channel_key}_{year}_{month}.db"
        if path.exists():
            paths.append(path)

    return paths


def get_all_codes_for_range(channel_name: str, start_iso: str, end_iso: str):
    codes = set()
    for path in db_paths_for_range(channel_name, start_iso, end_iso):
        conn = connect(path)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT news_code FROM news WHERE news_code <> ''")
        for row in cur.fetchall():
            codes.add(row["news_code"])
        conn.close()
    return sorted(codes)