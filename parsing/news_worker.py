from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import os
import sqlite3
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, Signal

from models.news_item import NewsItem
from parsing.news_service import NewsIngestService
from tools.error_reporter import record_parse_error


class NewsLoadWorker(QObject):
    finished = Signal(list)
    progress = Signal(int, int)
    error = Signal(str)

    def __init__(self, files, channel_name, force_refresh=False):
        super().__init__()
        self.files = list(files)
        self.channel_name = channel_name
        self.force_refresh = force_refresh
        self.ingest_service = NewsIngestService(channel_name)
        self._cancel_event = Event()

    def request_cancel(self):
        self._cancel_event.set()

    def process_file(self, file_path: Path) -> NewsItem | None:
        try:
            if self._cancel_event.is_set():
                return None
            return self.ingest_service.build_news_item(file_path)
        except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
            logging.getLogger("EGS.NewsWorker").exception(
                "Dosya islenemedi | kanal=%s | dosya=%s",
                self.channel_name,
                file_path,
            )
            try:
                record_parse_error(self.channel_name, str(file_path), exc, phase="worker")
            except (OSError, RuntimeError):
                logging.getLogger("EGS.NewsWorker").exception(
                    "Parse hata raporu yazilamadi | kanal=%s | dosya=%s",
                    self.channel_name,
                    file_path,
                )
            return None

    def run(self):
        try:
            results = []
            total = len(self.files)

            if total == 0:
                self.finished.emit([])
                return

            max_workers = min(4, max(1, os.cpu_count() or 2))

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for file_path in self.files:
                    if self._cancel_event.is_set():
                        break
                    futures.append(executor.submit(self.process_file, file_path))

                for i, future in enumerate(as_completed(futures), start=1):
                    if self._cancel_event.is_set():
                        break
                    result = future.result()
                    if result:
                        results.append(result)
                    self.progress.emit(i, total)

            if self._cancel_event.is_set():
                self.finished.emit(results)
                return

            results.sort(key=lambda item: (item.news_code, item.title))
            self.finished.emit(results)

        except (RuntimeError, OSError, ValueError, TypeError, sqlite3.Error) as exc:
            self.error.emit(str(exc))
