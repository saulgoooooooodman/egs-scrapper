from __future__ import annotations

import re

from core.text_utils import lower_tr, title_tr, upper_tr


_spell_backend = {
    "available": False,
    "name": "Yalnızca sözlük",
    "checker": None,
    "zipf_frequency": None,
    "lexicon_by_key": {},
    "lexicon_keys": [],
    "process_extract_one": None,
    "fuzzy_ratio": None,
}


_SPELL_KEY_MAP = str.maketrans({
    "ç": "c",
    "ğ": "g",
    "ı": "i",
    "i": "i",
    "ö": "o",
    "ş": "s",
    "ü": "u",
    "â": "a",
    "î": "i",
    "û": "u",
})


_PRESERVE_TOKENS = {
    "APR",
    "PKG",
    "SOT",
    "VTR",
    "VO",
    "LIVE",
    "KJ",
}


def tokenize(text: str):
    return re.findall(r"[A-ZÇĞİÖŞÜa-zçğıöşü]+|[^A-ZÇĞİÖŞÜa-zçğıöşü]+", text, flags=re.UNICODE)


def _spell_key(text: str) -> str:
    return lower_tr(str(text or "")).translate(_SPELL_KEY_MAP)


def _try_init_enchant():
    try:
        import enchant  # type: ignore
    except Exception:
        return None, ""

    for lang in ("tr_TR", "tr"):
        try:
            return enchant.Dict(lang), f"Enchant ({lang})"
        except Exception:
            continue

    return None, ""


def _try_init_frequency_backend():
    try:
        from rapidfuzz import fuzz, process
        from wordfreq import top_n_list, zipf_frequency
    except Exception:
        return {}

    words = top_n_list("tr", 50000)
    lexicon_by_key = {}
    word_scores = {}

    for word in words:
        clean_word = str(word or "").strip()
        if not clean_word:
            continue

        key = _spell_key(clean_word)
        if not key:
            continue

        score = float(zipf_frequency(clean_word, "tr"))
        if key not in word_scores or score >= word_scores[key]:
            lexicon_by_key[key] = clean_word
            word_scores[key] = score

    return {
        "zipf_frequency": zipf_frequency,
        "lexicon_by_key": lexicon_by_key,
        "lexicon_keys": list(lexicon_by_key.keys()),
        "process_extract_one": process.extractOne,
        "fuzzy_ratio": fuzz.ratio,
    }


def try_init_enchant():
    checker, enchant_name = _try_init_enchant()
    frequency_backend = _try_init_frequency_backend()

    available = bool(checker or frequency_backend)
    name_parts = []
    if frequency_backend:
        name_parts.append("Wordfreq + RapidFuzz (tr)")
    if enchant_name:
        name_parts.append(enchant_name)

    _spell_backend.update({
        "available": available,
        "name": " + ".join(name_parts) if name_parts else "Yalnızca sözlük",
        "checker": checker,
        "zipf_frequency": frequency_backend.get("zipf_frequency"),
        "lexicon_by_key": frequency_backend.get("lexicon_by_key", {}),
        "lexicon_keys": frequency_backend.get("lexicon_keys", []),
        "process_extract_one": None,
        "fuzzy_ratio": None,
    })


def reload_spell_backend_status():
    try_init_enchant()


def get_spell_backend_status_text() -> str:
    return f"Başlık düzeltme: {_spell_backend['name']}"


def has_spell_backend() -> bool:
    return bool(_spell_backend["available"])


def _preserve_case(original: str, suggestion: str) -> str:
    if not suggestion:
        return original
    if original.isupper():
        return upper_tr(suggestion)
    if original[:1].isupper() and original[1:].islower():
        return title_tr(suggestion)
    return lower_tr(suggestion)


def _is_valid_dictionary_word(token: str) -> bool:
    checker = _spell_backend.get("checker")
    if checker is None:
        return False

    try:
        return bool(checker.check(lower_tr(token)))
    except Exception:
        return False


def _lookup_exact_candidate(token: str):
    lexicon_by_key = _spell_backend.get("lexicon_by_key", {})
    zipf_frequency = _spell_backend.get("zipf_frequency")
    if not lexicon_by_key or zipf_frequency is None:
        return ""

    token_lower = lower_tr(token)
    token_key = _spell_key(token_lower)
    candidate = str(lexicon_by_key.get(token_key, "") or "").strip()
    if not candidate:
        return ""

    if lower_tr(candidate) == token_lower:
        return ""

    base_score = float(zipf_frequency(token_lower, "tr"))
    candidate_score = float(zipf_frequency(candidate, "tr"))
    if candidate_score >= max(base_score + 0.2, 3.0):
        return candidate
    return ""


def _correct_word_token(token: str) -> str:
    clean_token = str(token or "")
    if len(clean_token) <= 3:
        return clean_token

    if clean_token.upper() in _PRESERVE_TOKENS:
        return clean_token

    if clean_token.isupper() and len(clean_token) <= 4:
        return clean_token

    if _is_valid_dictionary_word(clean_token):
        return clean_token

    candidate = _lookup_exact_candidate(clean_token)
    if not candidate:
        return clean_token

    return _preserve_case(clean_token, candidate)


def apply_spell_suggestions(title: str) -> str:
    if not has_spell_backend():
        return title

    corrected = []

    for token in tokenize(title):
        if re.fullmatch(r"[A-ZÇĞİÖŞÜa-zçğıöşü]+", token, flags=re.UNICODE):
            corrected.append(_correct_word_token(token))
        else:
            corrected.append(token)

    return "".join(corrected)


try_init_enchant()
