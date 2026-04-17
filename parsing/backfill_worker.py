from __future__ import annotations

import time
from datetime import datetime, timedelta

from PySide6.QtCore import QDate, QThread, Signal

from data.cache_manager import ensure_cache_table, update_cache
from data.database import connect_db, init_db, upsert_news
from dictionaries.title_spellcheck import apply_title_spellcheck
from parsing.parser import parse_egs_file
from parsing.scanner import scan_news_files


class BackfillWorker(QThread):
    progress = Signal(int, str)
    finished_report = Signal(dict)

    def __init__(self, root_folder: str, channel_name: str, start_date: QDate, end_date: QDate):
        super().__init__()
        self.root_folder = root_folder
        self.channel_name = channel_name
        self.start_date = start_date
        self.end_date = end_date

    def run(self):
        start_py = datetime(self.start_date.year(), self.start_date.month(), self.start_date.day())
        end_py = datetime(self.end_date.year(), self.end_date.month(), self.end_date.day())

        total_days = (end_py - start_py).days + 1
        if total_days <= 0:
            self.finished_report.emit({
                "days": 0,
                "files_found": 0,
                "indexed": 0,
                "errors": 0,
                "seconds": 0.0,
            })
            return

        started = time.time()
        files_found = 0
        indexed = 0
        errors = 0
        current = start_py
        day_index = 0

        while current <= end_py:
            if self.isInterruptionRequested():
                break

            day_index += 1
            date_str = current.strftime("%d.%m.%Y")
            iso_date = current.strftime("%Y-%m-%d")

            init_db(self.channel_name, iso_date)

            self.progress.emit(
                int((day_index / total_days) * 100),
                f"Taranıyor: {date_str} ({day_index}/{total_days})",
            )

            try:
                files = scan_news_files(self.root_folder, date_str, self.channel_name)
            except Exception:
                files = []

            files_found += len(files)

            conn = connect_db(self.channel_name, iso_date)
            ensure_cache_table(conn)

            try:
                for file_path in files:
                    try:
                        news = parse_egs_file(file_path, self.channel_name)
                        corrected_title = apply_title_spellcheck(news.title, self.channel_name)

                        final_text = news.final_text
                        if corrected_title and corrected_title != news.title:
                            lines = final_text.splitlines()
                            if lines:
                                lines[0] = corrected_title
                                final_text = "\n".join(lines)

                        stat = file_path.stat()
                        item_data = {
                            "path": str(file_path),
                            "file_name": file_path.name,
                            "title": news.title,
                            "corrected_title": corrected_title,
                            "news_code": news.news_code,
                            "news_category": news.news_category,
                            "format_code": news.format_code,
                            "format_name": news.format_name,
                            "summary": news.summary,
                            "body": news.body,
                            "kj_lines": news.kj_lines,
                            "final_text": final_text,
                            "editors": news.editors,
                            "date_str": date_str,
                            "iso_date": iso_date,
                            "mtime": stat.st_mtime,
                            "size": stat.st_size,
                        }
                        upsert_news(self.channel_name, item_data, conn=conn)
                        update_cache(conn, item_data["path"], item_data["mtime"], item_data["size"])
                        indexed += 1
                    except Exception:
                        errors += 1

                conn.commit()
            finally:
                conn.close()

            current += timedelta(days=1)

        seconds = time.time() - started
        self.finished_report.emit({
            "days": day_index,
            "files_found": files_found,
            "indexed": indexed,
            "errors": errors,
            "seconds": seconds,
        })
