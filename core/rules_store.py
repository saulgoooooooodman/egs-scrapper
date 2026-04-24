from __future__ import annotations

import json
import re
from copy import deepcopy

from core.app_paths import LEGACY_RULES_FILE, RULES_FILE


FALLBACK_DEFAULT_RULES = {
    "A NEWS": {
        "news_codes": {
            "E": "EKONOMI",
            "S": "SPOR",
            "T": "TURKIYE",
            "VO": "SES",
            "WAF": "AFRIKA KITASI",
            "WAM": "AMERIKA KITASI",
            "WAS": "ASYA KITASI",
            "WAU": "AVUSTRALYA KITASI",
            "WEU": "AVRUPA KITASI",
            "WME": "ORTA DOGU",
            "WRU": "DOGU AVRUPA",
            "WUK": "BRITANYA ADASI",
            "WHZ": "SOFT HABERLER",
            "LIVE": "CANLI",
        }
    },
    "A HABER": {
        "codes": {
            "AZ": {
                "label": "ANALIZ",
                "prepend_to_title": True,
                "dedupe_prefix_words": ["ANALIZ", "ANALİZ"],
                "title_suffix": "VTR",
            },
        },
        "news_codes": {
            "A": "ANKARA HABER",
            "AZ": "ANALIZ",
            "C": "CANLI",
            "D": "DIS HABER",
            "DA": "DIS HABER AKSAM",
            "DG": "DIS HABER GECE",
            "DS": "DIS HABER SABAH",
            "I": "ISTANBUL HABER",
            "IA": "ISTANBUL HABER AKSAM",
            "IG": "ISTANBUL HABER GECE",
            "IS": "ISTANBUL HABER SABAH",
            "MM": "MEMLEKET MESELESI",
            "P": "PORTRE",
            "S": "SPOR",
            "YA": "YURT HABER AKSAM",
            "YG": "YURT HABER GECE",
            "YS": "YURT HABER SABAH",
            "BTH": "BIR TURKUNUN HIKAYESI",
            "E": "EKONOMI",
            "PA": "PERDE ARKASI",
            "YY": "OZEL DOSYA",
            "YY-OD": "OZEL DOSYA",
            "YS-OD": "OZEL DOSYA",
            "ED": "EDITOR SES",
        }
    },
    "A SPOR": {
        "news_codes": {
            "B": "BARKO",
            "C": "CANLI",
            "Z": "BULTEN",
            "S": "SPOR",
            "SP": "SPOR BULTENI",
            "KJ": "KJ",
            "G": "GRAFIK",
            "SA": "SPOR AJANSI",
            "SG": "SPOR GUNDEMI",
            "YHS": "YASASIN HAFTA SONU",
            "90+1": "90+1",
            "AH": "ANA HABER BULTENI",
            "SS": "SON SAYFA",
            "TO": "TAKIM OYUNU",
        }
    },
    "A PARA": {
        "news_codes": {
            "AP": "HABER",
            "B": "BARKO",
            "C": "CANLI",
            "DS": "DIS HABER",
            "G": "GRAFIK",
            "K": "KONUK",
            "S": "SES",
            "E": "EKONOMI",
            "K-STD": "KONUK STUDYO",
        },
        "title_cleanup": {
            "prefix": "",
            "suffix": "-APR",
            "remove_phrases": [],
            "remove_trailing_numbers": False,
        },
    },
}


DEFAULT_TITLE_CLEANUP = {
    "prefix": "",
    "suffix": "",
    "remove_phrases": [],
    "remove_trailing_numbers": False,
}

DEFAULT_SCAN_OPTIONS = {
    "hide_symbol_prefixed_titles": True,
}


DEFAULT_CODE_RULE = {
    "label": "",
    "prepend_to_title": False,
    "append_to_title": False,
    "dedupe_prefix_words": [],
    "title_prefix": "",
    "title_suffix": "",
    "title_remove_phrases": [],
    "remove_trailing_numbers": False,
    "dynamic_title_rules": [],
    "row_background": "",
    "row_foreground": "",
}


def display_rule_code(code: str) -> str:
    text = normalize_rule_code(code)
    if text[:1] in "+!#*":
        return text[1:].strip()
    return text


def _load_template_rules() -> dict:
    loaded = {}
    if LEGACY_RULES_FILE.exists():
        try:
            data = json.loads(LEGACY_RULES_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                loaded = data
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            loaded = {}

    if not loaded:
        loaded = deepcopy(FALLBACK_DEFAULT_RULES)

    for channel_name, fallback_channel in FALLBACK_DEFAULT_RULES.items():
        loaded.setdefault(channel_name, {})
        current_channel = loaded.get(channel_name)
        if not isinstance(current_channel, dict):
            loaded[channel_name] = deepcopy(fallback_channel)
            continue

        if "title_cleanup" not in current_channel and "title_cleanup" in fallback_channel:
            current_channel["title_cleanup"] = deepcopy(fallback_channel["title_cleanup"])
        if "scan_options" not in current_channel:
            current_channel["scan_options"] = dict(DEFAULT_SCAN_OPTIONS)

    return loaded


DEFAULT_RULES = _load_template_rules()


def normalize_rule_code(code: str) -> str:
    text = str(code or "").strip().upper()
    if not text:
        return ""

    if "-" not in text and " " not in text:
        return text.strip("()")

    parts = [part.strip() for part in re.split(r"\s*-\s*|\s+", text) if part.strip()]
    if not parts:
        return ""
    parts = [part.strip("()") for part in parts if part.strip("()")]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return "-".join(parts)


def _normalize_string_list(values) -> list[str]:
    if not isinstance(values, list):
        return []
    result = []
    seen = set()
    for value in values:
        text = str(value or "").strip()
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result


def _normalize_title_cleanup(value) -> dict:
    current = dict(DEFAULT_TITLE_CLEANUP)
    if isinstance(value, dict):
        current["prefix"] = str(value.get("prefix", "") or "").strip()
        current["suffix"] = str(value.get("suffix", "") or "").strip()
        current["remove_phrases"] = _normalize_string_list(value.get("remove_phrases", []))
        current["remove_trailing_numbers"] = bool(value.get("remove_trailing_numbers", False))
    return current


def _normalize_scan_options(value) -> dict:
    current = dict(DEFAULT_SCAN_OPTIONS)
    if isinstance(value, dict):
        current["hide_symbol_prefixed_titles"] = bool(
            value.get(
                "hide_symbol_prefixed_titles",
                value.get("hide_plus_prefixed_files", True),
            )
        )
    return current


def _normalize_dynamic_rule(value) -> dict:
    if not isinstance(value, dict):
        return {}
    return {
        "if_title_contains_any": _normalize_string_list(value.get("if_title_contains_any", [])),
        "override_label": str(value.get("override_label", "") or "").strip(),
        "override_dedupe_prefix_words": _normalize_string_list(value.get("override_dedupe_prefix_words", [])),
    }


def _normalize_code_rule(code: str, config) -> tuple[str, dict]:
    normalized_code = normalize_rule_code(code)
    if not normalized_code:
        return "", {}

    current = dict(DEFAULT_CODE_RULE)

    if isinstance(config, str):
        current["label"] = config.strip()
    elif isinstance(config, dict):
        current["label"] = str(config.get("label", "") or "").strip()
        current["prepend_to_title"] = bool(config.get("prepend_to_title", False))
        current["append_to_title"] = bool(config.get("append_to_title", False))
        current["dedupe_prefix_words"] = _normalize_string_list(config.get("dedupe_prefix_words", []))
        current["title_prefix"] = str(config.get("title_prefix", "") or "").strip()
        current["title_suffix"] = str(config.get("title_suffix", "") or "").strip()
        current["title_remove_phrases"] = _normalize_string_list(config.get("title_remove_phrases", []))
        current["remove_trailing_numbers"] = bool(config.get("remove_trailing_numbers", False))
        current["row_background"] = str(config.get("row_background", "") or "").strip()
        current["row_foreground"] = str(config.get("row_foreground", "") or "").strip()
        current["dynamic_title_rules"] = [
            dynamic_rule
            for dynamic_rule in (
                _normalize_dynamic_rule(item)
                for item in config.get("dynamic_title_rules", [])
            )
            if dynamic_rule
        ]

    if not current["dedupe_prefix_words"] and current["label"]:
        current["dedupe_prefix_words"] = [current["label"]]

    return normalized_code, current


def _extract_codes(channel_name: str, channel: dict) -> dict[str, dict]:
    extracted: dict[str, dict] = {}

    codes = channel.get("codes")
    if isinstance(codes, dict):
        for code, config in codes.items():
            normalized_code, normalized_config = _normalize_code_rule(code, config)
            if normalized_code:
                extracted[normalized_code] = normalized_config

    existing_news_codes = channel.get("news_codes")
    if isinstance(existing_news_codes, dict):
        for code, label in existing_news_codes.items():
            normalized_code, normalized_config = _normalize_code_rule(code, {"label": label})
            if not normalized_code:
                continue
            if normalized_code in extracted:
                extracted[normalized_code]["label"] = extracted[normalized_code]["label"] or normalized_config["label"]
            else:
                extracted[normalized_code] = normalized_config

    default_channel = DEFAULT_RULES.get(channel_name, {})
    default_codes = default_channel.get("codes")
    if isinstance(default_codes, dict):
        for code, config in default_codes.items():
            normalized_code, normalized_config = _normalize_code_rule(code, config)
            if not normalized_code:
                continue
            if normalized_code not in extracted:
                extracted[normalized_code] = normalized_config
                continue

            merged = dict(normalized_config)
            merged.update(extracted[normalized_code])
            if not merged.get("dedupe_prefix_words"):
                merged["dedupe_prefix_words"] = normalized_config.get("dedupe_prefix_words", [])
            if not merged.get("dynamic_title_rules"):
                merged["dynamic_title_rules"] = normalized_config.get("dynamic_title_rules", [])
            if not merged.get("title_prefix"):
                merged["title_prefix"] = normalized_config.get("title_prefix", "")
            if not merged.get("title_suffix"):
                merged["title_suffix"] = normalized_config.get("title_suffix", "")
            if not merged.get("title_remove_phrases"):
                merged["title_remove_phrases"] = normalized_config.get("title_remove_phrases", [])
            extracted[normalized_code] = merged

    default_news_codes = default_channel.get("news_codes")
    if isinstance(default_news_codes, dict):
        for code, label in default_news_codes.items():
            normalized_code, normalized_config = _normalize_code_rule(code, {"label": label})
            if not normalized_code:
                continue
            if normalized_code in extracted:
                extracted[normalized_code]["label"] = extracted[normalized_code]["label"] or normalized_config["label"]
            else:
                extracted[normalized_code] = normalized_config

    return extracted


def _build_news_codes(codes: dict[str, dict]) -> dict[str, str]:
    result = {}
    for code, config in codes.items():
        label = str(config.get("label", "") or "").strip()
        if label:
            result[code] = label
    return result


def _normalize_channel_rules(channel_name: str, channel) -> dict:
    if not isinstance(channel, dict):
        return {
            "codes": {},
            "news_codes": {},
            "title_cleanup": dict(DEFAULT_TITLE_CLEANUP),
            "scan_options": dict(DEFAULT_SCAN_OPTIONS),
        }

    current = dict(channel)
    current["codes"] = _extract_codes(channel_name, current)
    current["news_codes"] = _build_news_codes(current["codes"])

    default_cleanup = _normalize_title_cleanup(DEFAULT_RULES.get(channel_name, {}).get("title_cleanup", {}))
    merged_cleanup = dict(default_cleanup)
    raw_cleanup = current.get("title_cleanup", {})
    if isinstance(raw_cleanup, dict):
        if "prefix" in raw_cleanup:
            merged_cleanup["prefix"] = str(raw_cleanup.get("prefix", "") or "").strip()
        if "suffix" in raw_cleanup:
            merged_cleanup["suffix"] = str(raw_cleanup.get("suffix", "") or "").strip()
        if "remove_phrases" in raw_cleanup:
            merged_cleanup["remove_phrases"] = _normalize_string_list(raw_cleanup.get("remove_phrases", []))
        if "remove_trailing_numbers" in raw_cleanup:
            merged_cleanup["remove_trailing_numbers"] = bool(raw_cleanup.get("remove_trailing_numbers", False))
    current["title_cleanup"] = merged_cleanup
    current["scan_options"] = _normalize_scan_options(current.get("scan_options", {}))

    return current


def _normalize_rules(data: dict) -> dict:
    normalized = {}

    for channel_name, channel in data.items():
        if not isinstance(channel_name, str):
            continue
        normalized[channel_name] = _normalize_channel_rules(channel_name, channel)

    for channel_name, channel in DEFAULT_RULES.items():
        if channel_name not in normalized:
            normalized[channel_name] = _normalize_channel_rules(channel_name, channel)

    return normalized


def _load_rules() -> dict:
    if not RULES_FILE.exists():
        normalized_defaults = _normalize_rules(deepcopy(DEFAULT_RULES))
        RULES_FILE.write_text(
            json.dumps(normalized_defaults, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return normalized_defaults

    try:
        data = json.loads(RULES_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return _normalize_rules(data)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        pass

    return _normalize_rules(deepcopy(DEFAULT_RULES))


def get_all_rules() -> dict:
    return _load_rules()


def save_all_rules(data: dict):
    normalized = _normalize_rules(data if isinstance(data, dict) else {})
    RULES_FILE.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_channel_rules(channel_name: str) -> dict:
    rules = _load_rules()
    return _normalize_channel_rules(channel_name, rules.get(channel_name, {}))


def get_channel_code_rules(channel_name: str) -> dict[str, dict]:
    return get_channel_rules(channel_name).get("codes", {})


def get_channel_title_cleanup(channel_name: str) -> dict:
    return get_channel_rules(channel_name).get("title_cleanup", dict(DEFAULT_TITLE_CLEANUP))


def get_channel_scan_options(channel_name: str) -> dict:
    return get_channel_rules(channel_name).get("scan_options", dict(DEFAULT_SCAN_OPTIONS))


def resolve_code_config(channel_name: str, news_code: str, title: str = "") -> dict:
    rules = get_channel_rules(channel_name)
    code_key = normalize_rule_code(news_code)
    config = dict(DEFAULT_CODE_RULE)
    code_rules = rules.get("codes", {})
    config.update(code_rules.get(code_key, {}))

    if config == dict(DEFAULT_CODE_RULE):
        display_key = display_rule_code(code_key)
        for raw_code, raw_config in code_rules.items():
            if display_rule_code(raw_code) == display_key:
                config.update(raw_config)
                break

    title_upper = str(title or "").upper()
    for dynamic_rule in config.get("dynamic_title_rules", []):
        checks = dynamic_rule.get("if_title_contains_any", [])
        if not checks:
            continue
        if any(str(check or "").upper() in title_upper for check in checks):
            override_label = str(dynamic_rule.get("override_label", "") or "").strip()
            if override_label:
                config["label"] = override_label
            override_dedupe = _normalize_string_list(dynamic_rule.get("override_dedupe_prefix_words", []))
            if override_dedupe:
                config["dedupe_prefix_words"] = override_dedupe
            break

    return config
