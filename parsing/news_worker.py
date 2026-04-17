from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from parsing.parser import parse_egs_file
from dictionaries.title_spellcheck import apply_title_spellcheck


class NewsLoadWorker(QObject):
    finished = Signal(list)
    progress = Signal(int, int)
    error = Signal(str)

    def __init__(self, files, channel_name, force_refresh=False):
        super().__init__()
        self.files = list(files)
        self.channel_name = channel_name
        self.force_refresh = force_refresh

    def process_file(self, file_path: Path):
        try:
            stat = os.stat(file_path)
            mtime = stat.st_mtime
            size = stat.st_size

            news = parse_egs_file(file_path, self.channel_name)
            corrected_title = apply_title_spellcheck(news.title, self.channel_name)

            final_text = news.final_text
            if corrected_title and corrected_title != news.title:
                lines = final_text.splitlines()
                if lines:
                    lines[0] = corrected_title
                    final_text = "\n".join(lines)

            return {
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
                "mtime": mtime,
                "size": size,
            }
        except Exception:
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
                futures = [executor.submit(self.process_file, f) for f in self.files]

                for i, future in enumerate(as_completed(futures), start=1):
                    result = future.result()
                    if result:
                        results.append(result)
                    self.progress.emit(i, total)

            results.sort(key=lambda x: (x.get("news_code", ""), x.get("title", "")))
            self.finished.emit(results)

        except Exception as exc:
            self.error.emit(str(exc))