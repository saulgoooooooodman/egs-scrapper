from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NewsItem:
    path: str = ""
    file_name: str = ""
    title: str = ""
    corrected_title: str = ""
    news_code: str = ""
    news_category: str = ""
    format_code: str = ""
    format_name: str = ""
    summary: str = ""
    body: str = ""
    kj_lines: list[str] = field(default_factory=list)
    final_text: str = ""
    editors: list[str] = field(default_factory=list)
    iso_date: str = ""
    date_str: str = ""
    mtime: float | None = None
    size: int | None = None

    FIELD_NAMES = (
        "path",
        "file_name",
        "title",
        "corrected_title",
        "news_code",
        "news_category",
        "format_code",
        "format_name",
        "summary",
        "body",
        "kj_lines",
        "final_text",
        "editors",
        "iso_date",
        "date_str",
        "mtime",
        "size",
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "NewsItem") -> "NewsItem":
        if isinstance(data, cls):
            return data.copy()

        payload = {field_name: data.get(field_name) for field_name in cls.FIELD_NAMES}
        payload["kj_lines"] = list(payload.get("kj_lines") or [])
        payload["editors"] = list(payload.get("editors") or [])
        return cls(**payload)

    @classmethod
    def from_parsed(cls, parsed_news, **extra: Any) -> "NewsItem":
        payload = {
            "path": getattr(parsed_news, "path", ""),
            "file_name": getattr(parsed_news, "file_name", ""),
            "title": getattr(parsed_news, "title", ""),
            "corrected_title": getattr(parsed_news, "corrected_title", ""),
            "news_code": getattr(parsed_news, "news_code", ""),
            "news_category": getattr(parsed_news, "news_category", ""),
            "format_code": getattr(parsed_news, "format_code", ""),
            "format_name": getattr(parsed_news, "format_name", ""),
            "summary": getattr(parsed_news, "summary", ""),
            "body": getattr(parsed_news, "body", ""),
            "kj_lines": list(getattr(parsed_news, "kj_lines", []) or []),
            "final_text": getattr(parsed_news, "final_text", ""),
            "editors": list(getattr(parsed_news, "editors", []) or []),
        }
        payload.update(extra)
        return cls(**payload)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "file_name": self.file_name,
            "title": self.title,
            "corrected_title": self.corrected_title,
            "news_code": self.news_code,
            "news_category": self.news_category,
            "format_code": self.format_code,
            "format_name": self.format_name,
            "summary": self.summary,
            "body": self.body,
            "kj_lines": list(self.kj_lines),
            "final_text": self.final_text,
            "editors": list(self.editors),
            "iso_date": self.iso_date,
            "date_str": self.date_str,
            "mtime": self.mtime,
            "size": self.size,
        }

    def copy(self) -> "NewsItem":
        return self.from_dict(self.to_dict())

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def keys(self):
        return self.to_dict().keys()

    def items(self):
        return self.to_dict().items()

    def values(self):
        return self.to_dict().values()
