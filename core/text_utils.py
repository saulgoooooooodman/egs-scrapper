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
