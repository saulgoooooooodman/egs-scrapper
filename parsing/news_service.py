from __future__ import annotations

import os
from pathlib import Path

from dictionaries.title_spellcheck import apply_title_spellcheck
from models.news_item import NewsItem
from parsing.parser import parse_egs_file


class NewsIngestService:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name

    def build_news_item(
        self,
        file_path: str | Path,
        *,
        iso_date: str = "",
        date_str: str = "",
    ) -> NewsItem:
        source_path = Path(file_path)
        stat = os.stat(source_path)

        news = parse_egs_file(source_path, self.channel_name)
        corrected_title = apply_title_spellcheck(news.title, self.channel_name)

        final_text = news.final_text
        if corrected_title and corrected_title != news.title:
            lines = final_text.splitlines()
            if lines:
                lines[0] = corrected_title
                final_text = "\n".join(lines)

        return NewsItem.from_parsed(
            news,
            path=str(source_path),
            file_name=source_path.name,
            corrected_title=corrected_title,
            final_text=final_text,
            iso_date=iso_date,
            date_str=date_str,
            mtime=stat.st_mtime,
            size=stat.st_size,
        )
