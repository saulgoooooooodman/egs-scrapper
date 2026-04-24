import logging
import sqlite3

from data.database import get_db_path, init_db


def merge_external_database_into_channel(channel_name, external_db_path):
    logger = logging.getLogger("EGS.DatabaseMerge")
    targets = {}
    merged_count = 0
    skipped_count = 0
    failed_count = 0

    try:
        source = sqlite3.connect(external_db_path)
        try:
            scur = source.cursor()

            scur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
            if not scur.fetchone():
                raise RuntimeError("Harici veritabanında 'news' tablosu bulunamadı.")

            scur.execute("""
                SELECT path, file_name, title, corrected_title,
                       news_code, news_category,
                       format_code, format_name,
                       summary, body, kj_lines, final_text,
                       editors, iso_date, date_str,
                       mtime, size
                FROM news
            """)

            rows = scur.fetchall()

            for row in rows:
                iso_date = str(row[13] or "").strip()
                if not iso_date:
                    skipped_count += 1
                    logger.warning(
                        "Harici DB satırı atlandı | kanal=%s | sebep=iso_date eksik | dosya=%s",
                        channel_name,
                        row[1] or row[0] or "",
                    )
                    continue

                try:
                    init_db(channel_name, iso_date)
                    target = targets.get(iso_date)
                    if target is None:
                        target = sqlite3.connect(get_db_path(channel_name, iso_date))
                        targets[iso_date] = target

                    tcur = target.cursor()
                    tcur.execute("""
                        INSERT INTO news (
                            path, file_name, title, corrected_title,
                            news_code, news_category,
                            format_code, format_name,
                            summary, body, kj_lines, final_text,
                            editors, iso_date, date_str,
                            mtime, size
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(path) DO UPDATE SET
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
                    """, row)
                    merged_count += 1
                except sqlite3.Error:
                    failed_count += 1
                    logger.exception(
                        "Harici DB satırı birleştirilemedi | kanal=%s | tarih=%s | dosya=%s",
                        channel_name,
                        iso_date,
                        row[1] or row[0] or "",
                    )
        finally:
            source.close()

        for target in targets.values():
            target.commit()
    finally:
        for target in targets.values():
            try:
                target.close()
            except sqlite3.Error:
                pass

    return {
        "merged": merged_count,
        "skipped": skipped_count,
        "failed": failed_count,
    }
