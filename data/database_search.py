import logging
import os
import re
import sqlite3
from pathlib import Path

from core.settings_manager import load_settings
from core.text_utils import normalize_search_text
from data.database import get_legacy_db_path, iter_internal_db_paths
from models.archive_search_result import ArchiveSearchResult


logger = logging.getLogger("EGS.ArchiveSearch")


def _normalize_db_file(path) -> str:
    text = str(path or "").strip()
    if not text:
        return ""
    return os.path.normpath(text)


def _normalize_code(code) -> str:
    return str(code or "").strip().upper()


def _normalize_editor_tokens(value) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    parts = re.split(r"[\n,;]+", text)
    return [normalize_search_text(part) for part in parts if part.strip()]


def _row_haystack(row, scope: str) -> str:
    if scope == "title":
        return row[2] or ""
    if scope == "body":
        return row[3] or ""
    if scope == "code":
        return row[1] or ""
    return f"{row[2] or ''}\n{row[3] or ''}"


def _row_matches_editor_filters(row, editor_filters) -> bool:
    filters = [_token for _token in (_normalize_editor_tokens(item) for item in (editor_filters or [])) if _token]
    filter_tokens = [token for group in filters for token in group]
    if not filter_tokens:
        return True

    row_editors = set(_normalize_editor_tokens(row[5] if len(row) > 5 else ""))
    if not row_editors:
        return False

    return any(token in row_editors for token in filter_tokens)


def _text_matches_query(haystack: str, query: str, use_regex: bool, exact_match: bool) -> bool:
    haystack = str(haystack or "")
    query = str(query or "")
    if not query:
        return False

    if use_regex:
        import re

        pattern = re.compile(query, re.IGNORECASE)
        found = pattern.search(haystack)
        if not found:
            return False
        if exact_match:
            return found.group(0) == haystack
        return True

    if exact_match:
        return normalize_search_text(haystack) == normalize_search_text(query)

    return normalize_search_text(query) in normalize_search_text(haystack)


def _row_matches_query_clauses(row, query_clauses, use_regex: bool, exact_match: bool) -> bool:
    clauses = [clause for clause in (query_clauses or []) if str(clause.get("text", "")).strip()]
    if not clauses:
        return True

    must_matches = []
    any_matches = []

    for clause in clauses:
        mode = str(clause.get("mode", "any") or "any").strip().lower()
        scope = str(clause.get("scope", "all") or "all").strip().lower()
        text = str(clause.get("text", "")).strip()
        matched = _text_matches_query(_row_haystack(row, scope), text, use_regex, exact_match)

        if mode == "exclude":
            if matched:
                return False
        elif mode == "must":
            must_matches.append(matched)
        else:
            any_matches.append(matched)

    if must_matches and not all(must_matches):
        return False

    if any_matches:
        return any(any_matches)

    return True


def _build_internal_label(channel_name: str, db_path: Path) -> str:
    legacy = get_legacy_db_path(channel_name)
    if db_path == legacy:
        return "Ana Veritabanı (Eski)"

    stem_parts = db_path.stem.split("_")
    if len(stem_parts) >= 3 and stem_parts[-1].isdigit() and stem_parts[-2].isdigit():
        return f"Ana Veritabanı ({stem_parts[-2]}.{stem_parts[-1]})"
    return "Ana Veritabanı"


def _iter_search_databases(channel_name: str, start_iso_date=None, end_iso_date=None) -> list[tuple[str, str]]:
    candidates = [
        (_build_internal_label(channel_name, path), str(path))
        for path in iter_internal_db_paths(
            channel_name,
            start_iso_date,
            end_iso_date,
            include_legacy=True,
            existing_only=True,
        )
    ]

    settings = load_settings()
    external_dbs = settings.get("external_databases", [])
    if isinstance(external_dbs, list):
        for raw_path in external_dbs:
            normalized = _normalize_db_file(raw_path)
            if normalized:
                label = Path(normalized).stem or normalized
                candidates.append((label, normalized))

    unique = []
    seen = set()
    for label, path in candidates:
        normalized = _normalize_db_file(path)
        if not normalized:
            continue

        key = normalized.casefold()
        if key in seen:
            continue
        seen.add(key)

        if Path(normalized).exists():
            unique.append((label, normalized))

    return unique


def _has_news_table(conn: sqlite3.Connection) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
    return cur.fetchone() is not None


def _fetch_from_database(
    db_path: str,
    query: str,
    start_iso_date=None,
    end_iso_date=None,
    selected_codes=None,
    hide_mode=False,
    use_regex=False,
    scope="all",
    exact_match=False,
    query_clauses=None,
    editor_filters=None,
    should_cancel=None,
):
    if callable(should_cancel) and should_cancel():
        return []

    conn = sqlite3.connect(db_path)
    try:
        if not _has_news_table(conn):
            return []

        cur = conn.cursor()
        sql = """
            SELECT path, news_code, title, final_text, iso_date, editors
            FROM news
            WHERE 1=1
        """
        params = []

        query_text = str(query or "")
        query_upper = query_text.upper()
        clauses = [clause for clause in (query_clauses or []) if str(clause.get("text", "")).strip()]

        if not use_regex and not clauses:
            if exact_match:
                if scope == "title":
                    sql += " AND title = ?"
                    params.append(query_text)
                elif scope == "body":
                    sql += " AND final_text = ?"
                    params.append(query_text)
                elif scope == "code":
                    sql += " AND UPPER(TRIM(COALESCE(news_code, ''))) = ?"
                    params.append(query_upper.strip())
                else:
                    sql += " AND (title = ? OR final_text = ?)"
                    params.extend([query_text, query_text])
            else:
                like = f"%{query_text}%"
                if scope == "title":
                    sql += " AND title LIKE ?"
                    params.append(like)
                elif scope == "body":
                    sql += " AND final_text LIKE ?"
                    params.append(like)
                elif scope == "code":
                    sql += " AND UPPER(TRIM(COALESCE(news_code, ''))) LIKE ?"
                    params.append(f"%{query_upper.strip()}%")
                else:
                    sql += " AND (title LIKE ? OR final_text LIKE ?)"
                    params.extend([like, like])

        if start_iso_date:
            sql += " AND iso_date >= ?"
            params.append(start_iso_date)

        if end_iso_date:
            sql += " AND iso_date <= ?"
            params.append(end_iso_date)

        codes = [_normalize_code(code) for code in (selected_codes or []) if _normalize_code(code)]
        if codes:
            placeholders = ",".join("?" for _ in codes)
            if hide_mode:
                sql += f" AND UPPER(TRIM(COALESCE(news_code, ''))) NOT IN ({placeholders})"
            else:
                sql += f" AND UPPER(TRIM(COALESCE(news_code, ''))) IN ({placeholders})"
            params.extend(codes)

        sql += """
            ORDER BY iso_date DESC, news_code COLLATE NOCASE, title COLLATE NOCASE
        """

        cur.execute(sql, params)
        rows = cur.fetchall()
        if clauses:
            matched_rows = []
            for row in rows:
                if callable(should_cancel) and should_cancel():
                    return matched_rows
                if (
                    _row_matches_query_clauses(row, clauses, use_regex, exact_match)
                    and _row_matches_editor_filters(row, editor_filters)
                ):
                    matched_rows.append(row)
            return matched_rows

        if not use_regex:
            return [row for row in rows if _row_matches_editor_filters(row, editor_filters)]
        matched = []
        for row in rows:
            if callable(should_cancel) and should_cancel():
                return matched
            haystack = _row_haystack(row, scope)
            if (
                _text_matches_query(haystack, query, use_regex, exact_match)
                and _row_matches_editor_filters(row, editor_filters)
            ):
                matched.append(row)
        return matched
    finally:
        conn.close()


def search_archive(
    channel_name,
    query,
    start_iso_date=None,
    end_iso_date=None,
    selected_codes=None,
    hide_mode=False,
    use_regex=False,
    scope="all",
    exact_match=False,
    query_clauses=None,
    editor_filters=None,
    should_cancel=None,
    error_sink=None,
):
    results: list[ArchiveSearchResult] = []
    seen = set()

    for source_name, db_path in _iter_search_databases(channel_name, start_iso_date, end_iso_date):
        if callable(should_cancel) and should_cancel():
            break
        try:
            rows = _fetch_from_database(
                db_path,
                query,
                start_iso_date,
                end_iso_date,
                selected_codes,
                hide_mode,
                use_regex,
                scope,
                exact_match,
                query_clauses,
                editor_filters,
                should_cancel,
            )
        except (sqlite3.Error, OSError, re.error, ValueError) as exc:
            error_info = {
                "channel_name": channel_name,
                "source_name": source_name,
                "db_path": db_path,
                "start_iso_date": start_iso_date or "",
                "end_iso_date": end_iso_date or "",
                "message": str(exc),
            }
            logger.exception(
                "Arşiv arama veritabanında hata | kanal=%s | kaynak=%s | db=%s | baslangic=%s | bitis=%s",
                channel_name,
                source_name,
                db_path,
                start_iso_date or "",
                end_iso_date or "",
            )
            if isinstance(error_sink, list):
                error_sink.append(error_info)
            elif callable(error_sink):
                try:
                    error_sink(error_info)
                except (TypeError, ValueError, RuntimeError):
                    logger.exception("Arşiv arama hata toplayıcısı başarısız | kanal=%s", channel_name)
            continue

        for raw_path, news_code, title, final_text, iso_date, editors in rows:
            if callable(should_cancel) and should_cancel():
                break
            normalized_path = _normalize_db_file(raw_path)
            dedupe_key = (
                normalized_path.casefold() if normalized_path else "",
                str(news_code or "").strip().casefold(),
                str(title or "").strip().casefold(),
                str(iso_date or "").strip(),
            )

            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)

            results.append(ArchiveSearchResult(
                news_code=news_code or "",
                title=title or "",
                final_text=final_text or "",
                iso_date=iso_date or "",
                source_name=source_name,
                source_path=db_path,
                path=normalized_path,
                editors=editors or "",
            ))

        if callable(should_cancel) and should_cancel():
            break

    results.sort(
        key=lambda item: (
            item.iso_date,
            item.news_code.lower(),
            item.title.lower(),
        ),
        reverse=True,
    )

    return results[:200]
