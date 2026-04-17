from __future__ import annotations

import json

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
    "always_on_top": False,
    "live_watch_enabled": False,
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
        return merged
    except Exception:
        return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    merged = dict(DEFAULT_SETTINGS)
    merged.update(settings or {})
    SETTINGS_FILE.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
