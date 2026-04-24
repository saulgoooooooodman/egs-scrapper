from __future__ import annotations

import json
from pathlib import Path

from core.atomic_io import atomic_write_json
from core.app_paths import (
    APP_DATA_DIR,
    COMMON_DICTIONARY_FILE,
    LEGACY_COMMON_DICTIONARY_FILE,
    channel_dictionary_file,
)


_SHARED_DEFAULTS = {
    "ERDOGAN": "ERDOĞAN",
    "MILLI": "MİLLİ",
    "HAKAN FIDAN": "HAKAN FİDAN",
    "ISTANBUL": "İSTANBUL",
    "VALILIGI": "VALİLİĞİ",
    "TURKIYE": "TÜRKİYE",
    "CUMHURIYETI": "CUMHURİYETİ",
    "BASKANI": "BAŞKANI",
    "DIS": "DIŞ",
    "EKONOMI": "EKONOMİ",
    "GUNDEMI": "GÜNDEMİ",
    "ATESKES": "ATEŞKES",
    "OZET": "ÖZET",
    "DIN": "DİN",
    "SAVAS": "SAVAŞ",
    "SAVASI": "SAVAŞI",
    "COKUSU": "ÇÖKÜŞÜ",
    "OZEL": "ÖZEL",
    "YORESEL": "YÖRESEL",
    "KOMBESI": "KÖMBESİ",
    "AKCADAG": "AKÇADAĞ",
    "BELEDIYESI": "BELEDİYESİ",
    "BAKANLIGI": "BAKANLIĞI",
    "BUYUKSEHIR": "BÜYÜKŞEHİR",
    "ILCE": "İLÇE",
}

DEFAULT_CHANNEL_DICTIONARY = {
    "A NEWS": dict(_SHARED_DEFAULTS),
    "A HABER": {
        **_SHARED_DEFAULTS,
        "DOGALGAZ": "DOĞALGAZ",
        "DISISLERI": "DIŞİŞLERİ",
    },
    "ATV": dict(_SHARED_DEFAULTS),
    "A SPOR": {
        "FENERBAHCE": "FENERBAHÇE",
        "BESIKTAS": "BEŞİKTAŞ",
        "ERDOGAN": "ERDOĞAN",
    },
    "A PARA": {
        "EKONOMI": "EKONOMİ",
        "MERKEZ BANKASI": "MERKEZ BANKASI",
        "ERDOGAN": "ERDOĞAN",
    },
}

LEGACY_COMMON_MIGRATION_MARKER = APP_DATA_DIR / ".common_dictionary_migrated_v1"


def _normalize_dict(data: dict) -> dict[str, str]:
    return {
        str(k).upper().strip(): str(v).strip()
        for k, v in data.items()
        if str(k).strip()
    }


def _load_json(path: Path, fallback: dict[str, str]) -> dict[str, str]:
    if not path.exists():
        atomic_write_json(path, fallback, ensure_ascii=False, indent=2)
        return _normalize_dict(fallback)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return _normalize_dict(data)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        pass

    return _normalize_dict(fallback)


def _load_legacy_common_dictionary() -> dict[str, str]:
    merged: dict[str, str] = {}
    for path in (COMMON_DICTIONARY_FILE, LEGACY_COMMON_DICTIONARY_FILE):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
        if isinstance(data, dict):
            merged.update(_normalize_dict(data))
    return merged


def _channel_fallback(channel_name: str) -> dict[str, str]:
    return _normalize_dict(DEFAULT_CHANNEL_DICTIONARY.get(channel_name, {}))


def _load_channel_dictionary_raw(channel_name: str) -> dict[str, str]:
    return _load_json(channel_dictionary_file(channel_name), _channel_fallback(channel_name))


def _save_migration_marker() -> None:
    LEGACY_COMMON_MIGRATION_MARKER.write_text("migrated", encoding="utf-8")


def _migrate_legacy_common_dictionary() -> None:
    if LEGACY_COMMON_MIGRATION_MARKER.exists():
        return

    legacy_common = _load_legacy_common_dictionary()
    if not legacy_common:
        _save_migration_marker()
        return

    for channel_name in DEFAULT_CHANNEL_DICTIONARY:
        channel_data = _load_channel_dictionary_raw(channel_name)
        merged = dict(legacy_common)
        merged.update(channel_data)
        save_channel_dictionary(channel_name, merged)

    _save_migration_marker()


def load_channel_dictionary(channel_name: str) -> dict[str, str]:
    _migrate_legacy_common_dictionary()
    fallback = _channel_fallback(channel_name)
    current = _load_channel_dictionary_raw(channel_name)
    merged = dict(fallback)
    merged.update(current)
    return merged


def save_channel_dictionary(channel_name: str, data: dict[str, str]):
    atomic_write_json(
        channel_dictionary_file(channel_name),
        _normalize_dict(data),
        ensure_ascii=False,
        indent=2,
    )


def add_title_dictionary_entry(channel_name: str, wrong: str, correct: str, use_common: bool = False):
    del use_common

    wrong = (wrong or "").upper().strip()
    correct = (correct or "").strip()

    if not wrong or not correct:
        return

    data = load_channel_dictionary(channel_name)
    data[wrong] = correct
    save_channel_dictionary(channel_name, data)
