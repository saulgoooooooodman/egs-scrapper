from __future__ import annotations

import sqlite3

from data.database import (
    clear_cache_for_channel,
    connect_db,
    get_db_path,
    get_news_count_for_month,
    get_news_for_date,
    init_db,
    search_archive,
    upsert_news,
)
from models.archive_search_result import ArchiveSearchResult
from models.news_item import NewsItem


class NewsRepository:
    def __init__(self, channel_name: str):
        self.channel_name = channel_name

    def ensure_storage(self, iso_date: str | None = None) -> None:
        init_db(self.channel_name, iso_date)

    def get_db_path(self, iso_date: str | None = None):
        return get_db_path(self.channel_name, iso_date)

    def connect(self, iso_date: str | None = None) -> sqlite3.Connection:
        self.ensure_storage(iso_date)
        return connect_db(self.channel_name, iso_date)

    def save_item(self, item: NewsItem | dict, conn: sqlite3.Connection | None = None) -> None:
        news_item = NewsItem.from_dict(item)
        upsert_news(self.channel_name, news_item.to_dict(), conn=conn)

    def save_items(self, items: list[NewsItem | dict], conn: sqlite3.Connection | None = None) -> None:
        for item in items:
            self.save_item(item, conn=conn)

    def fetch_by_date(self, iso_date: str) -> list[NewsItem]:
        return [NewsItem.from_dict(item) for item in get_news_for_date(self.channel_name, iso_date)]

    def count_for_month(self, iso_date: str | None = None) -> int:
        return get_news_count_for_month(self.channel_name, iso_date)

    def search_archive(
        self,
        query_text: str,
        start_date: str,
        end_date: str,
        *,
        selected_codes: list[str] | None = None,
        hide_mode: bool = False,
        use_regex: bool = False,
        scope: str = "all",
        exact_match: bool = False,
        query_clauses: list[dict] | None = None,
        editor_filters: list[str] | None = None,
        error_sink=None,
    ) -> list[ArchiveSearchResult]:
        return search_archive(
            self.channel_name,
            query_text,
            start_date,
            end_date,
            selected_codes=selected_codes,
            hide_mode=hide_mode,
            use_regex=use_regex,
            scope=scope,
            exact_match=exact_match,
            query_clauses=query_clauses,
            editor_filters=editor_filters,
            error_sink=error_sink,
        )

    def clear_cache(self) -> None:
        clear_cache_for_channel(self.channel_name)
