from __future__ import annotations

import re


TR_MAP = str.maketrans({
    "I": "ı",
    "İ": "i",
})


def normalize_search_text(text: str) -> str:
    if not text:
        return ""
    text = text.translate(TR_MAP).lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def upper_tr(text: str) -> str:
    mapping = str.maketrans({
        "i": "İ",
        "ı": "I",
    })
    return text.translate(mapping).upper()


def lower_tr(text: str) -> str:
    mapping = str.maketrans({
        "I": "ı",
        "İ": "i",
    })
    return text.translate(mapping).lower()


def title_tr(text: str) -> str:
    words = []
    for word in str(text or "").split(" "):
        if not word:
            words.append("")
            continue
        first = upper_tr(word[:1])
        rest = lower_tr(word[1:])
        words.append(f"{first}{rest}")
    return " ".join(words)


def upper_en(text: str) -> str:
    return str(text or "").upper()


def lower_en(text: str) -> str:
    return str(text or "").lower()


def title_en(text: str) -> str:
    words = []
    for word in str(text or "").split(" "):
        if not word:
            words.append("")
            continue
        words.append(f"{upper_en(word[:1])}{lower_en(word[1:])}")
    return " ".join(words)


def transform_case_for_channel(text: str, mode: str, channel_name: str | None = None) -> str:
    normalized_channel = str(channel_name or "").strip().upper()

    if normalized_channel == "A NEWS":
        if mode == "upper":
            return upper_en(text)
        if mode == "lower":
            return lower_en(text)
        return title_en(text)

    if mode == "upper":
        return upper_tr(text)
    if mode == "lower":
        return lower_tr(text)
    return title_tr(text)
