from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "EGS Scrapper"


def _get_base_data_dir() -> Path:
    local_appdata = os.getenv("LOCALAPPDATA")
    if local_appdata:
        return Path(local_appdata) / APP_NAME
    return Path.cwd() / "data_local"


BASE_DIR = Path(__file__).resolve().parent.parent
APP_DATA_DIR = _get_base_data_dir()

DATA_DIR = APP_DATA_DIR
DATABASES_DIR = BASE_DIR / "databases"
LOG_DIR = APP_DATA_DIR / "logs"
ERROR_REPORTS_DIR = BASE_DIR / "error_reports"

SETTINGS_FILE = BASE_DIR / "settings.json"
RULES_FILE = BASE_DIR / "channel_rules.json"
HELP_FILE = BASE_DIR / "help_content.md"

LOGO_FILE = BASE_DIR / "logo.svg"
LOGO_PNG_FILE = BASE_DIR / "logo.png"
LOGO_ICO_FILE = BASE_DIR / "logo.ico"
CHANNEL_LOGOS_DIR = BASE_DIR / "channel_logos"

COMMON_DICTIONARY_FILE = BASE_DIR / "common_dictionary.json"
CHANNEL_DICTIONARIES_DIR = BASE_DIR / "channel_dictionaries"

for path in [
    APP_DATA_DIR,
    DATABASES_DIR,
    LOG_DIR,
    ERROR_REPORTS_DIR,
    CHANNEL_DICTIONARIES_DIR,
    CHANNEL_LOGOS_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)


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
