from __future__ import annotations

import os
from pathlib import Path

from core.title_rules import apply_title_rules, get_body_prefix_text, is_special_od_code
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
        base_title = str(news.title or "").strip()
        list_title = apply_title_spellcheck(
            base_title,
            self.channel_name,
            news.news_code,
            respect_auto_setting=True,
        )
        corrected_title = apply_title_rules(list_title or base_title, self.channel_name, news.news_code)

        body_prefix = get_body_prefix_text(self.channel_name, news.news_code, corrected_title)
        final_text = build_story_text(
            original_title=base_title,
            corrected_title=corrected_title,
            summary=news.summary,
            body=news.body,
            kj_lines=news.kj_lines,
            body_prefix=body_prefix,
            news_code=news.news_code,
        )

        return NewsItem.from_parsed(
            news,
            path=str(source_path),
            file_name=source_path.name,
            list_title=list_title or base_title,
            corrected_title=corrected_title,
            final_text=final_text,
            iso_date=iso_date,
            date_str=date_str,
            mtime=stat.st_mtime,
            size=stat.st_size,
        )


def build_story_headline(title: str, body_prefix: str = "", news_code: str = "") -> str:
    clean_title = str(title or "").strip()
    clean_prefix = str(body_prefix or "").strip()
    if not clean_title:
        return clean_prefix
    if clean_prefix and is_special_od_code(news_code):
        return f"{clean_prefix}-{clean_title}".strip("- ")
    if clean_prefix:
        return f"{clean_prefix}\n\n{clean_title}".strip()
    return clean_title


def build_story_text(
    *,
    original_title: str,
    corrected_title: str,
    summary: str,
    body: str,
    kj_lines: list[str],
    body_prefix: str = "",
    news_code: str = "",
) -> str:
    parts = []
    clean_original = str(original_title or "").strip()
    clean_corrected = str(corrected_title or "").strip()
    lead_title = clean_corrected if clean_corrected and clean_corrected != clean_original else clean_original
    lead_block = build_story_headline(lead_title, body_prefix=body_prefix, news_code=news_code)

    if lead_block.strip():
        parts.append(lead_block.strip())

    if clean_corrected and clean_corrected != clean_original and clean_original:
        parts.append(clean_original)

    if summary.strip():
        parts.append(summary.strip())
    if body.strip():
        parts.append(body.strip())

    kj_clean = [
        line.strip()
        for line in kj_lines
        if line.strip()
        and line.strip() != clean_original
        and line.strip() != clean_corrected
        and line.strip() != str(body_prefix or "").strip()
        and line.strip() != lead_block.strip()
    ]
    if kj_clean:
        parts.append("\n".join(kj_clean))

    return "\n\n".join(part for part in parts if part).strip()
