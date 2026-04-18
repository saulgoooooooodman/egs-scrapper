from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ArchiveSearchResult:
    news_code: str = ""
    title: str = ""
    final_text: str = ""
    iso_date: str = ""
    source_name: str = ""
    source_path: str = ""
    path: str = ""
    editors: str = ""
