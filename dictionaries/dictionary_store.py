from __future__ import annotations

import json

from core.app_paths import channel_dictionary_file, COMMON_DICTIONARY_FILE


DEFAULT_COMMON_DICTIONARY = {
    "ERDOGAN": "ERDOĞAN",
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
    "SAVAS": "SAVAŞ",
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
    "A NEWS": {
        "ERDOGAN": "ERDOĞAN",
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
        "SAVAS": "SAVAŞ",
        "OZEL": "ÖZEL",
        "YORESEL": "YÖRESEL",
        "KOMBESI": "KÖMBESİ",
        "AKCADAG": "AKÇADAĞ",
        "BELEDIYESI": "BELEDİYESİ",
        "BAKANLIGI": "BAKANLIĞI",
        "BUYUKSEHIR": "BÜYÜKŞEHİR",
        "ILCE": "İLÇE",
    },
    "A HABER": {
        "ERDOGAN": "ERDOĞAN",
        "HAKAN FIDAN": "HAKAN FİDAN",
        "DOGALGAZ": "DOĞALGAZ",
        "DISISLERI": "DIŞİŞLERİ",
    },
    "ATV": {
        "ERDOGAN": "ERDOĞAN",
        "HAKAN FIDAN": "HAKAN FİDAN",
    },
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


def _normalize_dict(data: dict) -> dict[str, str]:
    return {
        str(k).upper().strip(): str(v).strip()
        for k, v in data.items()
        if str(k).strip()
    }


def _load_json(path, fallback):
    if not path.exists():
        path.write_text(
            json.dumps(fallback, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return _normalize_dict(fallback)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return _normalize_dict(data)
    except Exception:
        pass

    return _normalize_dict(fallback)


def load_common_dictionary() -> dict[str, str]:
    return _load_json(COMMON_DICTIONARY_FILE, DEFAULT_COMMON_DICTIONARY)


def save_common_dictionary(data: dict[str, str]):
    COMMON_DICTIONARY_FILE.write_text(
        json.dumps(_normalize_dict(data), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def load_channel_dictionary(channel_name: str) -> dict[str, str]:
    fallback = DEFAULT_CHANNEL_DICTIONARY.get(channel_name, {})
    path = channel_dictionary_file(channel_name)
    data = _load_json(path, fallback)

    if channel_name == "A NEWS":
        merged = dict(_normalize_dict(fallback))
        merged.update(data)
        if merged != data:
            save_channel_dictionary(channel_name, merged)
        return merged

    return data


def save_channel_dictionary(channel_name: str, data: dict[str, str]):
    channel_dictionary_file(channel_name).write_text(
        json.dumps(_normalize_dict(data), ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_title_dictionary_entry(channel_name: str, wrong: str, correct: str, use_common: bool = False):
    wrong = (wrong or "").upper().strip()
    correct = (correct or "").strip()

    if not wrong or not correct:
        return

    if use_common and channel_name != "A NEWS":
        data = load_common_dictionary()
        data[wrong] = correct
        save_common_dictionary(data)
    else:
        data = load_channel_dictionary(channel_name)
        data[wrong] = correct
        save_channel_dictionary(channel_name, data)
