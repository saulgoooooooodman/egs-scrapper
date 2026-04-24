from __future__ import annotations

import re

from core.rules_store import get_channel_title_cleanup, resolve_code_config
from core.text_utils import normalize_search_text


def _strip_phrases(text: str, phrases: list[str]) -> str:
    result = str(text or "")
    for phrase in phrases:
        clean_phrase = str(phrase or "").strip()
        if not clean_phrase:
            continue
        pattern = re.compile(re.escape(clean_phrase), re.IGNORECASE)
        result = pattern.sub("", result)
    return re.sub(r"\s{2,}", " ", result).strip()


def _strip_trailing_numbers(text: str) -> str:
    result = str(text or "").strip()
    while True:
        updated = re.sub(r"(?:\s*-\s*|\s+)(\d{1,4}(?::\d{2})?)$", "", result).strip()
        if updated == result:
            return result
        result = updated


def _starts_with_any_prefix(title: str, prefixes: list[str]) -> bool:
    title_key = normalize_search_text(title)
    for prefix in prefixes:
        prefix_key = normalize_search_text(prefix)
        if prefix_key and title_key.startswith(prefix_key):
            return True
    return False


def _apply_title_affixes(title: str, prefix: str, suffix: str) -> str:
    result = str(title or "").strip()
    raw_prefix = str(prefix or "")
    raw_suffix = str(suffix or "")
    clean_prefix = raw_prefix.strip()
    clean_suffix = raw_suffix.strip()

    if clean_prefix and not _starts_with_any_prefix(result, [clean_prefix]):
        if clean_prefix.endswith("-"):
            result = f"{clean_prefix} {result}".strip()
        else:
            result = f"{clean_prefix} {result}".strip()

    if clean_suffix and not result.endswith(clean_suffix):
        if clean_suffix[:1] in "-/),.;:!?":
            result = f"{result}{clean_suffix}".strip()
        else:
            result = f"{result} {clean_suffix}".strip()

    return re.sub(r"\s{2,}", " ", result).strip()


def _strip_title_prefix(title: str, prefix: str) -> str:
    result = str(title or "").strip()
    clean_prefix = str(prefix or "").strip()
    if not result or not clean_prefix:
        return result

    normalized_result = normalize_search_text(result)
    normalized_prefix = normalize_search_text(clean_prefix)
    if normalized_prefix and normalized_result.startswith(normalized_prefix):
        updated = result[len(clean_prefix):].strip()
        return re.sub(r"^\s*-\s*", "", updated).strip()

    pattern = re.compile(
        rf"^\s*{re.escape(clean_prefix)}(?:\s*-\s*|\s+)?",
        re.IGNORECASE,
    )
    updated = pattern.sub("", result, count=1).strip()
    if updated != result:
        return re.sub(r"^\s*-\s*", "", updated).strip()
    return result


def _ends_with_any_suffix(title: str, suffixes: list[str]) -> bool:
    title_key = normalize_search_text(title)
    for suffix in suffixes:
        suffix_key = normalize_search_text(suffix)
        if suffix_key and title_key.endswith(suffix_key):
            return True
    return False


def is_special_od_code(news_code: str) -> bool:
    normalized_code = str(news_code or "").strip().upper()
    return normalized_code.endswith("-OD") or normalized_code.endswith("-(OD)")


def apply_title_rules(title: str, channel_name: str, news_code: str) -> str:
    result = str(title or "").strip()

    channel_cleanup = get_channel_title_cleanup(channel_name)
    code_config = resolve_code_config(channel_name, news_code, result)

    result = _strip_phrases(result, channel_cleanup.get("remove_phrases", []))
    result = _strip_phrases(result, code_config.get("title_remove_phrases", []))

    if channel_cleanup.get("remove_trailing_numbers"):
        result = _strip_trailing_numbers(result)
    if code_config.get("remove_trailing_numbers"):
        result = _strip_trailing_numbers(result)

    if code_config.get("prepend_to_title"):
        label = str(code_config.get("label", "") or "").strip()
        dedupe_words = code_config.get("dedupe_prefix_words", []) or [label]
        if label and not _starts_with_any_prefix(result, dedupe_words):
            result = f"{label}- {result}".strip()

    if code_config.get("append_to_title"):
        label = str(code_config.get("label", "") or "").strip()
        dedupe_words = code_config.get("dedupe_prefix_words", []) or [label]
        if label and not _ends_with_any_suffix(result, dedupe_words):
            result = f"{result}-{label}".strip("- ")

    result = _apply_title_affixes(
        result,
        channel_cleanup.get("prefix", ""),
        channel_cleanup.get("suffix", ""),
    )
    result = _apply_title_affixes(
        result,
        code_config.get("title_prefix", ""),
        code_config.get("title_suffix", ""),
    )

    result = re.sub(r"\s*-\s*-\s*", "-", result)
    result = re.sub(r"-\s{2,}", "- ", result)
    result = re.sub(r"\s{2,}", " ", result).strip()
    return result


def get_body_prefix_text(channel_name: str, news_code: str, title: str = "") -> str:
    if is_special_od_code(news_code):
        return "ÖZEL DOSYA"
    return ""


def build_list_corrected_title(title: str, channel_name: str, news_code: str) -> str:
    result = str(title or "").strip()
    if not result:
        return ""

    channel_cleanup = get_channel_title_cleanup(channel_name)
    code_config = resolve_code_config(channel_name, news_code, result)

    prefixes = []
    if code_config.get("prepend_to_title"):
        label = str(code_config.get("label", "") or "").strip()
        if label:
            prefixes.append(label)
    prefixes.extend(
        prefix
        for prefix in [
            channel_cleanup.get("prefix", ""),
            code_config.get("title_prefix", ""),
        ]
        if str(prefix or "").strip()
    )

    original_result = result
    for prefix in prefixes:
        result = _strip_title_prefix(result, str(prefix or ""))

    if result == original_result and code_config.get("prepend_to_title") and "-" in result:
        result = result.split("-", 1)[1].strip()

    return re.sub(r"\s{2,}", " ", result).strip(" -")
