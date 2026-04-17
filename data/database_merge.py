import sqlite3

from data.database import init_db, get_db_path


def merge_external_database_into_channel(channel_name, external_db_path):
    source = sqlite3.connect(external_db_path)
    scur = source.cursor()

    scur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
    if not scur.fetchone():
        source.close()
        target.close()
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
    targets = {}

    for row in rows:
        try:
            iso_date = row[13] or ""
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
        except Exception:
            pass

    source.close()
    for target in targets.values():
        target.commit()
        target.close()
