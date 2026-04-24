from __future__ import annotations

import re

from core.settings_manager import load_settings
from dictionaries.dictionary_store import load_channel_dictionary
from dictionaries.spell_backend import apply_spell_suggestions, has_spell_backend


def apply_dictionary_pairs(text: str, replacements: dict[str, str]) -> str:
    result = text
    for wrong, correct in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = re.compile(rf"\b{re.escape(wrong)}\b", re.IGNORECASE)
        result = pattern.sub(correct, result)

    result = re.sub(r"\s{2,}", " ", result).strip()
    return result


def _cleanup_title_artifacts(title: str) -> str:
    result = title or ""

    result = re.sub(r"\bAPS\b", "", result, flags=re.IGNORECASE)
    result = re.sub(r"\bANALİZ--+\b", "ANALİZ-", result, flags=re.IGNORECASE)
    result = re.sub(r"\bANALIZ--+\b", "ANALİZ-", result, flags=re.IGNORECASE)
    result = re.sub(r"\s*-\s*-\s*", "-", result)
    result = result.replace("(OD)", "").replace(" (OD)", "").strip()
    result = re.sub(r"([A-ZÇĞİÖŞÜ0-9])\((PKG|VTR|SOT|VO|LIVE)\)", r"\1 (\2)", result)
    result = re.sub(r"(\((?:PKG|VTR|SOT|VO|LIVE)\))(\d+)", r"\1 \2", result)
    return re.sub(r"\s{2,}", " ", result).strip()


def _should_apply_spell_backend(channel_name: str, respect_auto_setting: bool) -> bool:
    if not has_spell_backend():
        return False

    normalized_channel = str(channel_name or "").strip().upper()
    if normalized_channel == "A NEWS":
        return False

    settings = load_settings()
    mode = str(
        settings.get(
            "title_spellcheck_mode",
            "auto" if bool(settings.get("auto_title_spellcheck", True)) else "manual",
        )
        or "manual"
    ).lower()

    if not respect_auto_setting:
        return mode in {"auto", "manual"}

    return mode == "auto"


def apply_title_spellcheck(
    title: str,
    channel_name: str,
    news_code: str = "",
    *,
    respect_auto_setting: bool = True,
) -> str:
    if not title.strip():
        return title

    result = apply_dictionary_pairs(title, load_channel_dictionary(channel_name))

    if _should_apply_spell_backend(channel_name, respect_auto_setting):
        result = apply_spell_suggestions(result)

    result = _cleanup_title_artifacts(result)
    result = re.sub(r"\s{2,}", " ", result).strip()
    return result
