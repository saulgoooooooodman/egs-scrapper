import os
import sqlite3
from pathlib import Path
from datetime import date

from core.app_paths import DATABASES_DIR
from core.rules_store import get_channel_rules


_PATH_MIGRATIONS_DONE: set[str] = set()


def _safe_channel_name(channel_name: str) -> str:
    return (
        channel_name.lower()
        .replace(" ", "_")
        .replace("ç", "c")
        .replace("ğ", "g")
        .replace("ı", "i")
        .replace("İ", "i")
        .replace("ö", "o")
        .replace("ş", "s")
        .replace("ü", "u")
    )


def get_legacy_db_path(channel_name: str) -> Path:
    return DATABASES_DIR / f"{_safe_channel_name(channel_name)}.db"


def get_db_path(channel_name: str, iso_date: str | None = None) -> Path:
    safe_name = _safe_channel_name(channel_name)
    if iso_date:
        parts = str(iso_date).split("-")
        if len(parts) >= 2:
            year = parts[0]
            month = parts[1]
            if year.isdigit() and month.isdigit():
                return DATABASES_DIR / f"{safe_name}_{int(month):02d}_{year}.db"
    return get_legacy_db_path(channel_name)


def connect_db(channel_name: str, iso_date: str | None = None) -> sqlite3.Connection:
    return sqlite3.connect(get_db_path(channel_name, iso_date), timeout=30)


def normalize_db_path(path) -> str:
    text = str(path or "").strip()
    if not text:
        return ""
    return os.path.normpath(text)


def _path_key(path) -> str:
    normalized = normalize_db_path(path)
    return normalized.casefold()


def _ensure_column(cur, table, column, col_type):
    cur.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cur.fetchall()]
    if column not in columns:
        print(f"[DB MIGRATION] {column} ekleniyor")
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


def _dedupe_path_table(cur, table: str, id_expr: str):
    cur.execute(f"""
        SELECT {id_expr} AS row_id, path
        FROM {table}
        WHERE COALESCE(path, '') != ''
        ORDER BY row_id DESC
    """)
    rows = cur.fetchall()

    if not rows:
        return

    keepers = {}
    delete_ids = []
    updates = []

    for row_id, raw_path in rows:
        normalized_path = normalize_db_path(raw_path)
        if not normalized_path:
            continue

        key = _path_key(normalized_path)
        if key in keepers:
            delete_ids.append(row_id)
            continue

        keepers[key] = row_id
        if raw_path != normalized_path:
            updates.append((normalized_path, row_id))

    if delete_ids:
        placeholders = ",".join("?" for _ in delete_ids)
        cur.execute(f"DELETE FROM {table} WHERE {id_expr} IN ({placeholders})", delete_ids)

    for normalized_path, row_id in updates:
        cur.execute(
            f"UPDATE {table} SET path=? WHERE {id_expr}=?",
            (normalized_path, row_id),
        )


def _migrate_path_storage(conn: sqlite3.Connection, db_key: str):
    if db_key in _PATH_MIGRATIONS_DONE:
        return

    cur = conn.cursor()
    _dedupe_path_table(cur, "news", "id")
    _dedupe_path_table(cur, "cache", "rowid")

    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_news_path_nocase ON news(path COLLATE NOCASE)"
    )
    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_cache_path_nocase ON cache(path COLLATE NOCASE)"
    )

    conn.commit()
    _PATH_MIGRATIONS_DONE.add(db_key)


def _resolve_news_category(channel_name: str, news_code: str) -> str:
    rules = get_channel_rules(channel_name)
    codes = rules.get("news_codes", {})
    return codes.get(news_code, codes.get((news_code or "").upper(), ""))


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _parse_iso_date(iso_date: str | None) -> date | None:
    if not iso_date:
        return None
    parts = str(iso_date).split("-")
    if len(parts) != 3:
        return None
    try:
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def iter_internal_db_paths(
    channel_name: str,
    start_iso_date: str | None = None,
    end_iso_date: str | None = None,
    include_legacy: bool = True,
    existing_only: bool = False,
) -> list[Path]:
    safe_name = _safe_channel_name(channel_name)
    paths: list[Path] = []

    start_value = _parse_iso_date(start_iso_date)
    end_value = _parse_iso_date(end_iso_date)

    if start_value and not end_value:
        end_value = start_value
    if end_value and not start_value:
        start_value = end_value
    if start_value and end_value and start_value > end_value:
        start_value, end_value = end_value, start_value

    if start_value and end_value:
        current = _month_start(start_value)
        finish = _month_start(end_value)
        while current <= finish:
            path = get_db_path(channel_name, current.isoformat())
            if not existing_only or path.exists():
                paths.append(path)

            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
    else:
        monthly = sorted(DATABASES_DIR.glob(f"{safe_name}_??_????.db"))
        paths.extend(path for path in monthly if not existing_only or path.exists())

    if include_legacy:
        legacy = get_legacy_db_path(channel_name)
        if not existing_only or legacy.exists():
            paths.append(legacy)

    unique: list[Path] = []
    seen = set()
    for path in paths:
        key = str(path.resolve() if path.exists() else path).casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _iter_news_connections(channel_name: str, start_iso_date: str | None = None, end_iso_date: str | None = None):
    for db_path in iter_internal_db_paths(
        channel_name,
        start_iso_date,
        end_iso_date,
        include_legacy=True,
        existing_only=True,
    ):
        conn = sqlite3.connect(db_path, timeout=30)
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
            if cur.fetchone():
                yield db_path, conn
        finally:
            conn.close()


def init_db(channel_name: str, iso_date: str | None = None):
    db_path = get_db_path(channel_name, iso_date)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path, timeout=30)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE,
            file_name TEXT,
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
            iso_date TEXT,
            date_str TEXT,
            mtime REAL,
            size INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            path TEXT PRIMARY KEY,
            mtime REAL,
            size INTEGER
        )
    """)

    _ensure_column(cur, "news", "corrected_title", "TEXT")
    _ensure_column(cur, "news", "format_code", "TEXT")
    _ensure_column(cur, "news", "format_name", "TEXT")
    _ensure_column(cur, "news", "kj_lines", "TEXT")
    _ensure_column(cur, "news", "mtime", "REAL")
    _ensure_column(cur, "news", "size", "INTEGER")

    conn.commit()
    _migrate_path_storage(conn, str(db_path).casefold())
    conn.close()


def upsert_news(channel_name: str, item: dict, conn: sqlite3.Connection | None = None):
    own_connection = conn is None
    if own_connection:
        conn = connect_db(channel_name, item.get("iso_date"))

    cur = conn.cursor()
    path = normalize_db_path(item.get("path", ""))
    news_code = str(item.get("news_code", "") or "").strip()
    news_category = str(item.get("news_category", "") or "").strip()
    if news_code and not news_category:
        news_category = _resolve_news_category(channel_name, news_code)

    editors = item.get("editors", [])
    if isinstance(editors, list):
        editors_text = "\n".join(editors)
    else:
        editors_text = str(editors or "")

    kj_lines = item.get("kj_lines", [])
    if isinstance(kj_lines, list):
        kj_lines_text = "\n".join(kj_lines)
    else:
        kj_lines_text = str(kj_lines or "")

    cur.execute("""
        INSERT INTO news (
            path, file_name, title, corrected_title,
            news_code, news_category,
            format_code, format_name,
            summary, body, kj_lines, final_text,
            editors, iso_date, date_str,
            mtime, size
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT DO UPDATE SET
            file_name=excluded.file_name,
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
            iso_date=excluded.iso_date,
            date_str=excluded.date_str,
            mtime=excluded.mtime,
            size=excluded.size
    """, (
        path,
        item.get("file_name", ""),
        item.get("title", ""),
        item.get("corrected_title", ""),
        news_code,
        news_category,
        item.get("format_code", ""),
        item.get("format_name", ""),
        item.get("summary", ""),
        item.get("body", ""),
        kj_lines_text,
        item.get("final_text", ""),
        editors_text,
        item.get("iso_date", ""),
        item.get("date_str", ""),
        item.get("mtime", None),
        item.get("size", None),
    ))

    if own_connection:
        conn.commit()
        conn.close()


def delete_news_for_paths(
    channel_name: str,
    paths: list[str],
    iso_date: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> int:
    own_connection = conn is None
    if own_connection:
        conn = connect_db(channel_name, iso_date)

    normalized_paths = []
    for raw_path in paths:
        normalized = normalize_db_path(raw_path)
        if normalized:
            normalized_paths.append(normalized)

    if not normalized_paths:
        if own_connection:
            conn.close()
        return 0

    cur = conn.cursor()
    placeholders = ",".join("?" for _ in normalized_paths)
    params = list(normalized_paths)
    sql = f"DELETE FROM news WHERE path COLLATE NOCASE IN ({placeholders})"

    if iso_date:
        sql += " AND iso_date = ?"
        params.append(iso_date)

    cur.execute(sql, params)
    deleted = max(cur.rowcount, 0)

    if own_connection:
        conn.commit()
        conn.close()

    return deleted


def _text_to_lines(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [line.strip() for line in str(value).splitlines() if line.strip()]


def get_news_for_date(channel_name: str, iso_date: str) -> list[dict]:
    items = []
    seen_paths = set()
    for _, conn in _iter_news_connections(channel_name, iso_date, iso_date):
        cur = conn.cursor()
        cur.execute("""
            SELECT
                path,
                file_name,
                title,
                corrected_title,
                news_code,
                news_category,
                format_code,
                format_name,
                summary,
                body,
                kj_lines,
                final_text,
                editors,
                iso_date,
                date_str,
                mtime,
                size
            FROM news
            WHERE iso_date = ?
            ORDER BY news_code COLLATE NOCASE, title COLLATE NOCASE, file_name COLLATE NOCASE
        """, (iso_date,))

        for row in cur.fetchall():
            path = normalize_db_path(row[0] or "")
            if path:
                path_key = _path_key(path)
                if path_key in seen_paths:
                    continue
                seen_paths.add(path_key)

            news_code = row[4] or ""
            news_category = row[5] or _resolve_news_category(channel_name, news_code)
            items.append({
                "path": path,
                "file_name": row[1] or "",
                "title": row[2] or "",
                "corrected_title": row[3] or "",
                "news_code": news_code,
                "news_category": news_category,
                "format_code": row[6] or "",
                "format_name": row[7] or "",
                "summary": row[8] or "",
                "body": row[9] or "",
                "kj_lines": _text_to_lines(row[10]),
                "final_text": row[11] or "",
                "editors": _text_to_lines(row[12]),
                "iso_date": row[13] or "",
                "date_str": row[14] or "",
                "mtime": row[15],
                "size": row[16],
            })

    items.sort(key=lambda item: (
        str(item.get("news_code", "")).lower(),
        str(item.get("title", "")).lower(),
        str(item.get("file_name", "")).lower(),
    ))

    return items


def get_news_count_for_month(channel_name: str, iso_date: str):
    month = (iso_date or "")[:7]
    seen = set()

    for _, conn in _iter_news_connections(channel_name, iso_date, iso_date):
        cur = conn.cursor()
        cur.execute("""
            SELECT path, file_name, iso_date
            FROM news
            WHERE substr(COALESCE(iso_date,''),1,7)=?
        """, (month,))
        for path, file_name, row_iso_date in cur.fetchall():
            normalized = normalize_db_path(path or "")
            key = (
                _path_key(normalized) if normalized else "",
                str(file_name or "").strip().casefold(),
                str(row_iso_date or "").strip(),
            )
            seen.add(key)

    return len(seen)


def get_all_codes_from_db(channel_name: str, iso_date: str | None = None):
    codes = set()

    for _, conn in _iter_news_connections(channel_name, iso_date, iso_date):
        cur = conn.cursor()
        if iso_date:
            month = iso_date[:7]
            cur.execute("""
                SELECT DISTINCT news_code FROM news
                WHERE news_code IS NOT NULL
                  AND news_code != ''
                  AND substr(COALESCE(iso_date,''),1,7)=?
            """, (month,))
        else:
            cur.execute("""
                SELECT DISTINCT news_code FROM news
                WHERE news_code IS NOT NULL
                  AND news_code != ''
            """)

        for row in cur.fetchall():
            code = row[0]
            if code:
                codes.add(code)

    return sorted(codes, key=str.lower)


def get_all_codes_for_range(channel_name: str, start_date: str | None = None, end_date: str | None = None):
    codes = set()

    for _, conn in _iter_news_connections(channel_name, start_date, end_date):
        cur = conn.cursor()

        sql = """
            SELECT DISTINCT news_code
            FROM news
            WHERE news_code IS NOT NULL
              AND news_code != ''
        """
        params = []

        if start_date:
            sql += " AND iso_date >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND iso_date <= ?"
            params.append(end_date)

        cur.execute(sql, params)
        for row in cur.fetchall():
            code = row[0]
            if code:
                codes.add(code)

    return sorted(codes, key=str.lower)


def clear_cache_for_channel(channel_name: str):
    for db_path in iter_internal_db_paths(channel_name, include_legacy=True, existing_only=True):
        conn = sqlite3.connect(db_path, timeout=30)
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cache'")
            if cur.fetchone():
                cur.execute("DELETE FROM cache")
                conn.commit()
        finally:
            conn.close()


def check_database_integrity(
    channel_name: str,
    start_iso_date: str | None = None,
    end_iso_date: str | None = None,
) -> list[dict]:
    results: list[dict] = []

    for db_path in iter_internal_db_paths(
        channel_name,
        start_iso_date,
        end_iso_date,
        include_legacy=True,
        existing_only=True,
    ):
        conn = sqlite3.connect(db_path, timeout=30)
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check")
            rows = [str(row[0] or "").strip() for row in cur.fetchall()]
            messages = [row for row in rows if row]
            ok = len(messages) == 1 and messages[0].lower() == "ok"
            results.append({
                "path": str(db_path),
                "ok": ok,
                "messages": messages or ["ok"],
            })
        finally:
            conn.close()

    return results


def vacuum_databases(
    channel_name: str,
    start_iso_date: str | None = None,
    end_iso_date: str | None = None,
) -> list[dict]:
    results: list[dict] = []

    for db_path in iter_internal_db_paths(
        channel_name,
        start_iso_date,
        end_iso_date,
        include_legacy=True,
        existing_only=True,
    ):
        before_size = db_path.stat().st_size if db_path.exists() else 0
        conn = sqlite3.connect(db_path, timeout=30)
        try:
            conn.execute("VACUUM")
        finally:
            conn.close()

        after_size = db_path.stat().st_size if db_path.exists() else 0
        results.append({
            "path": str(db_path),
            "before_size": before_size,
            "after_size": after_size,
            "reclaimed_bytes": max(before_size - after_size, 0),
        })

    return results


def analyze_databases(
    channel_name: str,
    start_iso_date: str | None = None,
    end_iso_date: str | None = None,
) -> list[dict]:
    results: list[dict] = []

    for db_path in iter_internal_db_paths(
        channel_name,
        start_iso_date,
        end_iso_date,
        include_legacy=True,
        existing_only=True,
    ):
        conn = sqlite3.connect(db_path, timeout=30)
        try:
            conn.execute("ANALYZE")
            conn.commit()
        finally:
            conn.close()

        results.append({
            "path": str(db_path),
        })

    return results


def search_archive(
    channel_name: str,
    query: str,
    start_iso_date: str | None = None,
    end_iso_date: str | None = None,
    selected_codes: list[str] | None = None,
    hide_mode: bool = False,
    use_regex: bool = False,
    scope: str = "all",
    exact_match: bool = False,
    editor_filters: list[str] | None = None,
    query_clauses: list[dict] | None = None,
    should_cancel=None,
    error_sink=None,
):
    from data.database_search import search_archive as _search_archive
    return _search_archive(
        channel_name=channel_name,
        query=query,
        start_iso_date=start_iso_date,
        end_iso_date=end_iso_date,
        selected_codes=selected_codes,
        hide_mode=hide_mode,
        use_regex=use_regex,
        scope=scope,
        exact_match=exact_match,
        query_clauses=query_clauses,
        editor_filters=editor_filters,
        should_cancel=should_cancel,
        error_sink=error_sink,
    )


def merge_external_database_into_channel(channel_name: str, external_db_path: str):
    from data.database_merge import merge_external_database_into_channel as _merge
    return _merge(channel_name, external_db_path)
