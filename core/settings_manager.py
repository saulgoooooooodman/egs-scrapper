from __future__ import annotations

import json

from core.atomic_io import atomic_write_json
from core.app_paths import SETTINGS_FILE


DEFAULT_SETTINGS = {
    "user_name": "",
    "channel_name": "A NEWS",
    "root_folder": r"C:\DeeR",
    "profile_avatar_path": "",
    "remember_me": False,
    "show_startup_wizard": True,
    "ui_font_size": 11,
    "main_search_scope": "Tümü",
    "main_search_regex": False,
    "main_selected_codes": [],
    "main_code_filter_hide_mode": False,
    "main_hide_code_column": False,
    "main_duplicate_mode": "off",
    "show_previous_day_news": True,
    "remember_window_geometry": False,
    "remember_last_date": False,
    "last_selected_date": "",
    "always_on_top": False,
    "live_watch_enabled": False,
    "title_spellcheck_mode": "auto",
    "auto_title_spellcheck": True,
    "suppress_empty_folder_warning": False,
    "main_splitter_sizes": [450, 980],
    "news_code_styles": {},
    "old_news_row_style": {},
    "window_geometry": None,
    "external_databases": [],
}


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return dict(DEFAULT_SETTINGS)

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return dict(DEFAULT_SETTINGS)

        merged = dict(DEFAULT_SETTINGS)
        merged.update(data)
        if "title_spellcheck_mode" not in merged:
            merged["title_spellcheck_mode"] = "auto" if bool(merged.get("auto_title_spellcheck", True)) else "manual"
        merged["auto_title_spellcheck"] = merged.get("title_spellcheck_mode") == "auto"
        return merged
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    merged = dict(DEFAULT_SETTINGS)
    merged.update(settings or {})
    atomic_write_json(SETTINGS_FILE, merged, ensure_ascii=False, indent=2)
