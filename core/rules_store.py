from __future__ import annotations

import json

from core.app_paths import RULES_FILE


DEFAULT_RULES = {
    "A NEWS": {
        "news_codes": {
            "E": "EKONOMİ",
            "S": "SPOR",
            "T": "TÜRKİYE",
            "VO": "SES",
            "WAF": "AFRİKA KITASI",
            "WAM": "AMERİKA KITASI",
            "WAS": "ASYA KITASI",
            "WAU": "AVUSTRALYA KITASI",
            "WEU": "AVRUPA KITASI",
            "WME": "ORTA DOĞU",
            "WRU": "DOĞU AVRUPA",
            "WUK": "BRİTANYA ADASI",
            "WHZ": "SOFT HABERLER",
            "LIVE": "CANLI"
        }
    },
    "A HABER": {
        "news_codes": {
            "A": "ANKARA HABER",
            "AZ": "ANALİZ",
            "C": "CANLI",
            "D": "DIŞ HABER",
            "DA": "DIŞ HABER AKŞAM",
            "DG": "DIŞ HABER GECE",
            "DS": "DIŞ HABER SABAH",
            "I": "İSTANBUL HABER",
            "IA": "İSTANBUL HABER AKŞAM",
            "IG": "İSTANBUL HABER GECE",
            "IS": "İSTANBUL HABER SABAH",
            "MM": "MEMLEKET MESELESİ",
            "P": "PORTRE",
            "S": "SPOR",
            "YA": "YURT HABER AKŞAM",
            "YG": "YURT HABER GECE",
            "YS": "YURT HABER SABAH",
            "BTH": "BİR TÜRKÜNÜN HİKAYESİ",
            "E": "EKONOMİ",
            "PA": "PERDE ARKASI",
            "YY": "ÖZEL DOSYA",
            "YY-(OD)": "ÖZEL DOSYA",
            "YS-(OD)": "ÖZEL DOSYA",
            "ED": "EDİTÖR SES"
        }
    },
    "A SPOR": {
        "news_codes": {
            "B": "BARKO",
            "C": "CANLI",
            "Z": "BÜLTEN",
            "S": "SPOR",
            "KJ": "KJ",
            "G": "GRAFİK",
            "SA": "SPOR AJANSI",
            "SG": "SPOR GÜNDEMİ",
            "YHS": "YAŞASIN HAFTA SONU",
            "90+1": "90+1",
            "AH": "ANA HABER BÜLTENİ",
            "SS": "SON SAYFA",
            "TO": "TAKIM OYUNU"
        }
    },
    "A PARA": {
        "news_codes": {
            "AP": "HABER",
            "B": "BARKO",
            "C": "CANLI",
            "DS": "DIŞ HABER",
            "G": "GRAFİK",
            "K": "KONUK",
            "S": "SES",
            "E": "EKONOMİ",
            "K-STD": "KONUK STÜDYO"
        }
    }
}


def _extract_news_codes(channel_name: str, channel: dict) -> dict[str, str]:
    news_codes = {}

    existing = channel.get("news_codes")
    if isinstance(existing, dict):
        for code, label in existing.items():
            if isinstance(code, str) and isinstance(label, str) and code.strip():
                news_codes[code.strip()] = label.strip()

    codes = channel.get("codes")
    if isinstance(codes, dict):
        for code, config in codes.items():
            if not isinstance(code, str) or not code.strip():
                continue

            if isinstance(config, str):
                label = config.strip()
            elif isinstance(config, dict):
                label = str(config.get("label", "")).strip()
            else:
                label = ""

            if label:
                news_codes.setdefault(code.strip(), label)

    default_codes = DEFAULT_RULES.get(channel_name, {}).get("news_codes", {})
    if isinstance(default_codes, dict):
        for code, label in default_codes.items():
            if isinstance(code, str) and isinstance(label, str) and code.strip():
                news_codes.setdefault(code.strip(), label.strip())

    return news_codes


def _normalize_rules(data: dict) -> dict:
    normalized = {}

    for channel_name, channel in data.items():
        if not isinstance(channel_name, str):
            continue

        if not isinstance(channel, dict):
            normalized[channel_name] = channel
            continue

        current = dict(channel)
        current["news_codes"] = _extract_news_codes(channel_name, current)
        normalized[channel_name] = current

    for channel_name, channel in DEFAULT_RULES.items():
        if channel_name not in normalized:
            normalized[channel_name] = dict(channel)
            continue

        current = normalized[channel_name]
        if isinstance(current, dict):
            current.setdefault(
                "news_codes",
                dict(channel.get("news_codes", {})),
            )

    return normalized


def _load_rules() -> dict:
    if not RULES_FILE.exists():
        RULES_FILE.write_text(
            json.dumps(DEFAULT_RULES, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return _normalize_rules(dict(DEFAULT_RULES))

    try:
        data = json.loads(RULES_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return _normalize_rules(data)
    except Exception:
        pass

    return _normalize_rules(dict(DEFAULT_RULES))


def get_all_rules() -> dict:
    return _load_rules()


def save_all_rules(data: dict):
    RULES_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_channel_rules(channel_name: str) -> dict:
    rules = _load_rules()
    channel = rules.get(channel_name, {})
    if not isinstance(channel, dict):
        return {"news_codes": {}}

    if "news_codes" not in channel or not isinstance(channel["news_codes"], dict):
        channel = dict(channel)
        channel["news_codes"] = _extract_news_codes(channel_name, channel)

    return channel
