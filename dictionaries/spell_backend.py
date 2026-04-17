from __future__ import annotations

import re


_spell_backend = {
    "available": False,
    "name": "Yalnızca sözlük",
    "checker": None,
}


def upper_tr(text: str) -> str:
    mapping = str.maketrans({
        "i": "İ",
        "ı": "I",
    })
    return text.translate(mapping).upper()


def tokenize(text: str):
    return re.findall(r"[A-ZÇĞİÖŞÜa-zçğıöşü]+|[^A-ZÇĞİÖŞÜa-zçğıöşü]+", text, flags=re.UNICODE)


def try_init_enchant():
    global _spell_backend

    try:
        import enchant  # type: ignore
    except Exception:
        _spell_backend = {
            "available": False,
            "name": "Yalnızca sözlük",
            "checker": None,
        }
        return

    for lang in ("tr_TR", "tr"):
        try:
            checker = enchant.Dict(lang)
            _spell_backend = {
                "available": True,
                "name": f"Enchant ({lang})",
                "checker": checker,
            }
            return
        except Exception:
            continue

    _spell_backend = {
        "available": False,
        "name": "Yalnızca sözlük",
        "checker": None,
    }


def reload_spell_backend_status():
    try_init_enchant()


def get_spell_backend_status_text() -> str:
    return f"Başlık düzeltme: {_spell_backend['name']}"


def has_spell_backend() -> bool:
    return _spell_backend["checker"] is not None


def apply_spell_suggestions(title: str) -> str:
    checker = _spell_backend.get("checker")
    if not checker:
        return title

    tokens = tokenize(title)
    corrected = []

    for token in tokens:
        if re.fullmatch(r"[A-ZÇĞİÖŞÜa-zçğıöşü]+", token, flags=re.UNICODE):
            if len(token) <= 2:
                corrected.append(token)
                continue

            try:
                lower_variant = token.lower()
                if checker.check(lower_variant):
                    corrected.append(upper_tr(lower_variant) if token.isupper() else lower_variant)
                else:
                    suggestions = checker.suggest(lower_variant)
                    if suggestions:
                        suggestion = suggestions[0]
                        corrected.append(upper_tr(suggestion) if token.isupper() else suggestion)
                    else:
                        corrected.append(token)
            except Exception:
                corrected.append(token)
        else:
            corrected.append(token)

    return "".join(corrected)


try_init_enchant()