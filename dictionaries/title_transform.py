from __future__ import annotations

import re

from dictionaries.dictionary_store import (
    load_common_dictionary,
    load_channel_dictionary,
)
from dictionaries.spell_backend import (
    has_spell_backend,
    apply_spell_suggestions,
)


def apply_dictionary_pairs(text: str, replacements: dict[str, str]) -> str:
    result = text
    for wrong, correct in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = re.compile(rf"\b{re.escape(wrong)}\b", re.IGNORECASE)
        result = pattern.sub(correct, result)

    result = re.sub(r"\s{2,}", " ", result).strip()
    return result


def _cleanup_title_artifacts(title: str, channel_name: str) -> str:
    result = title or ""

    # APS ifadesi başlıktan atılsın
    result = re.sub(r"\bAPS\b", "", result, flags=re.IGNORECASE)

    # ANALİZ-- gibi çift tireleri tekilleştir
    result = re.sub(r"\bANALİZ--+\b", "ANALİZ-", result, flags=re.IGNORECASE)
    result = re.sub(r"\bANALIZ--+\b", "ANALİZ-", result, flags=re.IGNORECASE)

    # Fazla tire/boşluk temizliği
    result = re.sub(r"\s*-\s*-\s*", "-", result)
    result = re.sub(r"\s{2,}", " ", result).strip()

    # Özel dosya kalıntısı
    result = result.replace("(OD)", "").replace(" (OD)", "").strip()

    # Format parantezi öncesi boşluk
    result = re.sub(r"([A-ZÇĞİÖŞÜ0-9])\((PKG|VTR|SOT|VO|LIVE)\)", r"\1 (\2)", result)

    # Format sonrası sayı ayrımı: (PKG)31 -> (PKG) 31
    result = re.sub(r"(\((?:PKG|VTR|SOT|VO|LIVE)\))(\d+)", r"\1 \2", result)

    # A PARA için -APR ekle
    if channel_name == "A PARA":
        if result and not result.endswith("-APR"):
            result = f"{result} -APR"

    return re.sub(r"\s{2,}", " ", result).strip()


def apply_title_spellcheck(title: str, channel_name: str) -> str:
    if not title.strip():
        return title

    result = title

    if channel_name != "A NEWS":
        # A NEWS ortak sözlükten ayrıldı; yalnızca kendi kanal sözlüğünü kullanır.
        result = apply_dictionary_pairs(result, load_common_dictionary())

    # Sonra kanala özel sözlük
    result = apply_dictionary_pairs(result, load_channel_dictionary(channel_name))

    # Sonra backend önerisi
    if has_spell_backend():
        result = apply_spell_suggestions(result)

    result = _cleanup_title_artifacts(result, channel_name)
    result = re.sub(r"\s{2,}", " ", result).strip()
    return result
