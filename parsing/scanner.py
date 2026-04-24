from __future__ import annotations

import logging
import re
from pathlib import Path

from core.rules_store import get_channel_scan_options
from parsing.parser import _get_valid_news_codes, _match_exact_news_code, _match_numbered_news_code


_SUFFIX_RE = re.compile(r"_(?:[A-Z0-9]+)$", re.IGNORECASE)
_SEPARATOR_RE = re.compile(r"^[\+\-\=\_\.\sA-Z0-9ÇĞİÖŞÜ]+$")
_ROOT_ALIASES: dict[str, Path] = {}
_SUPPORTED_FILE_EXTENSIONS = {"", ".txt", ".text", ".egs", ".xml"}


def _date_parts(date_str: str) -> tuple[str, str, str, str]:
    day, month, year = date_str.split(".")
    folder_name = f"{month}{day}{year}.egs"
    return day, month, year, folder_name


def _iter_existing_search_bases(root: Path):
    seen = set()

    for base in [root, *root.parents]:
        base_key = str(base).casefold()
        if base_key in seen:
            continue
        seen.add(base_key)

        if base.exists() and base.is_dir():
            yield base


def _candidate_score(root: Path, candidate: Path) -> tuple[int, int]:
    root_parts = {part.casefold() for part in root.parts if part not in (root.drive, "\\", "/")}
    candidate_parts = {part.casefold() for part in candidate.parts}
    overlap = len(root_parts & candidate_parts)
    return overlap, -len(candidate.parts)


def _candidate_paths(root: Path, year: str, folder_name: str) -> list[Path]:
    candidates = []

    if root.name.casefold() == folder_name.casefold():
        candidates.append(root)

    containers = []
    root_name = root.name.casefold()
    for container in (
        root,
        *(()
          if root_name in {"haber"}
          else (
              root / "HABER",
              root / "Haber",
              root / "haber",
              root / "Haber" / "HABER",
              root / "haber" / "haber",
          )),
    ):
        key = str(container).casefold()
        if key in {str(item).casefold() for item in containers}:
            continue
        containers.append(container)

    for container in containers:
        candidates.append(container / year / folder_name)

    candidates.append(root / folder_name)
    return candidates


def _resolve_alias_root(root: Path) -> Path:
    alias = _ROOT_ALIASES.get(str(root).casefold())
    return alias if alias else root


def _remember_alias_root(root: Path, resolved_path: Path):
    key = str(root).casefold()
    _ROOT_ALIASES[key] = resolved_path.parent.parent


def _discover_root_alias(root: Path) -> Path | None:
    if root.exists():
        return root

    target_name = root.name.casefold()
    if not target_name:
        return None

    discovered: list[Path] = []
    for base in _iter_existing_search_bases(root):
        try:
            matches = [
                path
                for path in base.rglob(root.name)
                if path.is_dir()
            ]
        except OSError:
            continue

        if matches:
            matches.sort(key=lambda path: _candidate_score(root, path), reverse=True)
            discovered.extend(matches)
            break

    if not discovered:
        return None

    return discovered[0]


def build_date_path(root_folder: str, date_str: str) -> Path:
    logger = logging.getLogger("EGS.Scanner")
    _, _, year, folder_name = _date_parts(date_str)
    original_root = Path(root_folder)
    root = _resolve_alias_root(original_root)

    alias_root = _discover_root_alias(root)
    if alias_root is not None:
        root = alias_root
        _ROOT_ALIASES[str(original_root).casefold()] = alias_root

    candidates = _candidate_paths(root, year, folder_name)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    if root.exists():
        return candidates[0]

    discovered: list[Path] = []
    for base in _iter_existing_search_bases(root):
        try:
            matches = [
                path
                for path in base.rglob(folder_name)
                if path.is_dir() and path.parent.name == year
            ]
        except OSError:
            continue

        if matches:
            matches.sort(key=lambda path: _candidate_score(root, path), reverse=True)
            discovered.extend(matches)
            break

    if discovered:
        resolved = discovered[0]
        _remember_alias_root(original_root, resolved)
        logger.info(
            "Klasör otomatik eşlendi | kök=%s | hedef=%s",
            original_root,
            resolved,
        )
        return resolved

    return candidates[0]


def _matches_explicit_symbol_code(name: str, channel_name: str) -> bool:
    display_name = str(name or "").strip()
    if not display_name or display_name[0] not in "+!#*":
        return False

    for valid_code in _get_valid_news_codes(channel_name):
        if not valid_code or valid_code[0] not in "+!#*":
            continue
        if _match_exact_news_code(display_name, valid_code) is not None:
            return True
        if _match_numbered_news_code(display_name, valid_code) is not None:
            return True
    return False


def _is_hidden_by_prefix(name: str, channel_name: str) -> bool:
    stripped = name.strip()
    if not stripped.startswith(("+", "!", "#", "*")):
        return False

    if _matches_explicit_symbol_code(stripped, channel_name):
        return False

    options = get_channel_scan_options(channel_name)
    return bool(options.get("hide_symbol_prefixed_titles", True))


def _is_hidden_by_symbol(name: str) -> bool:
    stripped = name.strip()
    return stripped.startswith(("!", "#", "*"))


def _is_copluk_path(path: Path) -> bool:
    return any(part.upper() == "COPLUK" for part in path.parts)


def _is_separator_name(name: str) -> bool:
    upper = name.upper().strip()

    if "SEPARATOR" in upper:
        return True

    if re.fullmatch(r"[A-ZÇĞİÖŞÜ]\-+", upper):
        return True

    if re.fullmatch(r"[A-ZÇĞİÖŞÜ]{1,6}\-+", upper):
        return True

    if _SEPARATOR_RE.fullmatch(upper):
        hyphen_count = upper.count("-")
        if hyphen_count >= 8 and len(upper.replace("-", "").strip()) <= 6:
            return True

    return False


def _has_supported_extension(path: Path) -> bool:
    return path.suffix.lower() in _SUPPORTED_FILE_EXTENSIONS


def _is_hidden_by_keyword(name: str, channel_name: str) -> tuple[bool, str]:
    upper = name.upper()

    if "DSF" in upper:
        return True, "DSF"

    if channel_name == "A HABER" and upper.startswith("+++"):
        return True, "+++"

    return False, ""


def _strip_suffix(name: str) -> str:
    return _SUFFIX_RE.sub("", name).strip()


def scan_news_files(root_folder: str, date_str: str, channel_name: str) -> list[Path]:
    logger = logging.getLogger("EGS.Scanner")
    skipped_unsupported = 0
    skipped_symbol = 0
    skipped_prefix = 0
    skipped_separator = 0
    skipped_keyword = 0

    target_dir = build_date_path(root_folder, date_str)
    logger.info(
        "Tarama başladı | kanal=%s | tarih=%s | klasör=%s",
        channel_name,
        date_str,
        target_dir,
    )

    if not target_dir.exists():
        logger.info(
            "Tarama tamamlandı | kanal=%s | tarih=%s | bulunan=0",
            channel_name,
            date_str,
        )
        return []

    results: list[Path] = []

    for path in sorted(target_dir.rglob("*")):
        if path.is_dir():
            continue

        if _is_copluk_path(path):
            continue

        if not _has_supported_extension(path):
            skipped_unsupported += 1
            logger.debug(
                "Ayıklandı (desteklenmeyen uzantı) | kanal=%s | dosya=%s",
                channel_name,
                path.name,
            )
            continue

        raw_name = path.stem
        display_name = _strip_suffix(raw_name)

        if _is_hidden_by_symbol(display_name):
            skipped_symbol += 1
            logger.debug(
                "Gizlendi (sembol ile başlıyor) | kanal=%s | dosya=%s",
                channel_name,
                raw_name,
            )
            continue

        if _is_hidden_by_prefix(display_name, channel_name):
            skipped_prefix += 1
            logger.debug("Ayıklandı (+ ile başlıyor) | %s", raw_name)
            continue

        if _is_separator_name(display_name):
            skipped_separator += 1
            logger.debug("Ayıklandı (separator) | %s", raw_name)
            continue

        hidden_by_keyword, reason = _is_hidden_by_keyword(display_name, channel_name)
        if hidden_by_keyword:
            skipped_keyword += 1
            logger.debug(
                "Gizlendi (kelime eşleşmesi=%s) | kanal=%s | dosya=%s",
                reason,
                channel_name,
                raw_name,
            )
            continue

        results.append(path)

    logger.info(
        "Tarama tamamlandı | kanal=%s | tarih=%s | bulunan=%s | ayiklanan_uzanti=%s | gizlenen_sembol=%s | ayiklanan_on_ek=%s | ayiklanan_separator=%s | gizlenen_kelime=%s",
        channel_name,
        date_str,
        len(results),
        skipped_unsupported,
        skipped_symbol,
        skipped_prefix,
        skipped_separator,
        skipped_keyword,
    )
    return results
