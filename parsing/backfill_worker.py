from __future__ import annotations

import logging
import sqlite3
import time
from datetime import datetime, timedelta

from PySide6.QtCore import QDate, QThread, Signal

from data.cache_manager import ensure_cache_table, update_cache
from data.news_repository import NewsRepository
from parsing.news_service import NewsIngestService
from parsing.scanner import scan_news_files
from tools.error_reporter import record_parse_error


class BackfillWorker(QThread):
    progress = Signal(int, str)
    finished_report = Signal(dict)

    def __init__(self, root_folder: str, channel_name: str, start_date: QDate, end_date: QDate):
        super().__init__()
        self.root_folder = root_folder
        self.channel_name = channel_name
        self.start_date = start_date
        self.end_date = end_date
        self.repository = NewsRepository(channel_name)
        self.ingest_service = NewsIngestService(channel_name)

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

            self.repository.ensure_storage(iso_date)

            self.progress.emit(
                int((day_index / total_days) * 100),
                f"Taraniyor: {date_str} ({day_index}/{total_days})",
            )

            try:
                files = scan_news_files(self.root_folder, date_str, self.channel_name)
            except (OSError, ValueError, RuntimeError):
                logging.getLogger("EGS.Backfill").exception(
                    "Arsiv gunu taranamadi | kanal=%s | tarih=%s",
                    self.channel_name,
                    iso_date,
                )
                errors += 1
                files = []

            files_found += len(files)

            conn = self.repository.connect(iso_date)
            ensure_cache_table(conn)

            try:
                for file_path in files:
                    if self.isInterruptionRequested():
                        break
                    try:
                        item = self.ingest_service.build_news_item(
                            file_path,
                            iso_date=iso_date,
                            date_str=date_str,
                        )
                        self.repository.save_item(item, conn=conn)
                        update_cache(conn, item.path, item.mtime, item.size)
                        indexed += 1
                    except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
                        logging.getLogger("EGS.Backfill").exception(
                            "Arsiv dosyasi islenemedi | kanal=%s | tarih=%s | dosya=%s",
                            self.channel_name,
                            iso_date,
                            file_path,
                        )
                        try:
                            record_parse_error(
                                self.channel_name,
                                str(file_path),
                                exc,
                                phase="backfill",
                            )
                        except (OSError, RuntimeError):
                            logging.getLogger("EGS.Backfill").exception(
                                "Parse hata raporu yazilamadi | kanal=%s | tarih=%s | dosya=%s",
                                self.channel_name,
                                iso_date,
                                file_path,
                            )
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
