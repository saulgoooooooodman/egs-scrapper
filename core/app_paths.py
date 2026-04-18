from __future__ import annotations

import os
import shutil
from pathlib import Path


APP_NAME = "EGS Scrapper"


def _get_env_path(name: str) -> Path | None:
    value = str(os.getenv(name, "") or "").strip()
    if not value:
        return None
    return Path(value).expanduser()


def _get_base_data_dir() -> Path:
    override = _get_env_path("EGS_SCRAPPER_APP_DATA_DIR")
    if override:
        return override

    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / APP_NAME
    return Path.cwd() / "data_local"


BASE_DIR = Path(__file__).resolve().parent.parent
APP_DATA_DIR = _get_base_data_dir()

DATA_DIR = APP_DATA_DIR
DATABASES_DIR = APP_DATA_DIR / "databases"
LOG_DIR = APP_DATA_DIR / "logs"
ERROR_REPORTS_DIR = APP_DATA_DIR / "error_reports"

SETTINGS_FILE = APP_DATA_DIR / "settings.json"
RULES_FILE = BASE_DIR / "channel_rules.json"
HELP_FILE = BASE_DIR / "help_content.md"

LOGO_FILE = BASE_DIR / "logo.svg"
LOGO_PNG_FILE = BASE_DIR / "logo.png"
LOGO_ICO_FILE = BASE_DIR / "logo.ico"
CHANNEL_LOGOS_DIR = BASE_DIR / "channel_logos"

COMMON_DICTIONARY_FILE = APP_DATA_DIR / "common_dictionary.json"
CHANNEL_DICTIONARIES_DIR = APP_DATA_DIR / "channel_dictionaries"

LEGACY_DATABASES_DIR = BASE_DIR / "databases"
LEGACY_ERROR_REPORTS_DIR = BASE_DIR / "error_reports"
LEGACY_SETTINGS_FILE = BASE_DIR / "settings.json"
LEGACY_COMMON_DICTIONARY_FILE = BASE_DIR / "common_dictionary.json"
LEGACY_CHANNEL_DICTIONARIES_DIR = BASE_DIR / "channel_dictionaries"


def _is_migration_enabled() -> bool:
    value = str(os.getenv("EGS_SCRAPPER_DISABLE_MIGRATION", "") or "").strip().lower()
    return value not in {"1", "true", "yes", "on"}


def _copy_legacy_file(source: Path, target: Path) -> None:
    if target.exists() or not source.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _copy_legacy_tree(source: Path, target: Path) -> None:
    if not source.exists():
        return

    target.mkdir(parents=True, exist_ok=True)
    if any(target.iterdir()):
        return

    shutil.copytree(source, target, dirs_exist_ok=True)


def _migrate_legacy_writable_data() -> None:
    if not _is_migration_enabled():
        return

    _copy_legacy_file(LEGACY_SETTINGS_FILE, SETTINGS_FILE)
    _copy_legacy_file(LEGACY_COMMON_DICTIONARY_FILE, COMMON_DICTIONARY_FILE)
    _copy_legacy_tree(LEGACY_DATABASES_DIR, DATABASES_DIR)
    _copy_legacy_tree(LEGACY_ERROR_REPORTS_DIR, ERROR_REPORTS_DIR)
    _copy_legacy_tree(LEGACY_CHANNEL_DICTIONARIES_DIR, CHANNEL_DICTIONARIES_DIR)

for path in [
    APP_DATA_DIR,
    DATABASES_DIR,
    LOG_DIR,
    ERROR_REPORTS_DIR,
    CHANNEL_DICTIONARIES_DIR,
    CHANNEL_LOGOS_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)

_migrate_legacy_writable_data()


def channel_dictionary_file(channel_name: str) -> Path:
    safe_name = (
        channel_name.lower()
        .replace(" ", "_")
        .replace("ç", "c")
        .replace("ğ", "g")
        .replace("ı", "i")
        .replace("İ", "i")
        .replace("ö", "o")
        .replace("ş", "s")
        .replace("ü", "u")
    )
    return CHANNEL_DICTIONARIES_DIR / f"{safe_name}_dictionary.json"


def channel_logo_file(channel_name: str) -> Path:
    safe_name = (
        channel_name.lower()
        .replace(" ", "_")
        .replace("ç", "c")
        .replace("ğ", "g")
        .replace("ı", "i")
        .replace("İ", "i")
        .replace("ö", "o")
        .replace("ş", "s")
        .replace("ü", "u")
    )
    return CHANNEL_LOGOS_DIR / f"{safe_name}.png"
