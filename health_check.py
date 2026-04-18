from __future__ import annotations

import importlib
import traceback
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
REPORT_FILE = BASE_DIR / "health_check_report.txt"

REQUIRED_FILES = [
    "app.py",
    "main_window.py",
    "version_info.py",
    "health_check.py",
    "smoke_test.py",
    "help_content.md",
    "channel_rules.json",

    "core/__init__.py",
    "core/app_paths.py",
    "core/settings_manager.py",
    "core/settings_sync.py",
    "core/logger_setup.py",
    "core/rules_store.py",
    "core/text_utils.py",
    "core/window_state_manager.py",

    "data/__init__.py",
    "data/database.py",
    "data/cache_manager.py",
    "data/database_search.py",
    "data/database_merge.py",
    "data/news_repository.py",

    "dictionaries/__init__.py",
    "dictionaries/dictionary_store.py",
    "dictionaries/spell_backend.py",
    "dictionaries/title_transform.py",
    "dictionaries/title_spellcheck.py",

    "models/__init__.py",
    "models/archive_search_result.py",
    "models/news_item.py",
    "models/news_table_model.py",
    "models/news_list_model.py",

    "watchers/__init__.py",
    "watchers/live_reload.py",

    "parsing/__init__.py",
    "parsing/scanner.py",
    "parsing/parser.py",
    "parsing/news_service.py",
    "parsing/news_worker.py",
    "parsing/worker_manager.py",

    "dialogs/__init__.py",
    "dialogs/startup_dialog.py",
    "dialogs/help_dialog.py",
    "dialogs/info_dialog.py",
    "dialogs/log_viewer_dialog.py",
    "dialogs/code_filter_wizard.py",
    "dialogs/rules_manager_dialog.py",
    "dialogs/archive_search_dialog.py",
    "dialogs/find_replace_dialog.py",
    "dialogs/title_dictionary_manager.py",
    "dialogs/dictionary_bundle_dialog.py",
    "dialogs/external_db_manager.py",
    "dialogs/db_merge_dialog.py",

    "ui/__init__.py",
    "ui/main_window_topbar.py",
    "ui/main_window_filters.py",
    "ui/main_window_preview.py",
    "ui/main_window_context_menus.py",
    "ui/main_window_menu_builder.py",
    "ui/main_window_ui.py",

    "actions/__init__.py",
    "actions/main_window_actions.py",
    "actions/main_window_edit_actions.py",
    "actions/main_window_view_actions.py",
    "actions/main_window_data_actions.py",
    "actions/main_window_state_hooks.py",
]

MODULE_SYMBOLS = {
    "main_window": ["MainWindow"],
    "smoke_test": ["run_smoke_test"],
    "version_info": ["APP_NAME", "APP_VERSION", "APP_RELEASE_DATE"],

    "core.app_paths": ["BASE_DIR", "APP_DATA_DIR", "DATA_DIR", "DATABASES_DIR", "LOG_DIR", "RULES_FILE", "HELP_FILE"],
    "core.settings_manager": ["load_settings", "save_settings"],
    "core.settings_sync": ["SettingsSync"],
    "core.logger_setup": ["setup_logging", "install_exception_hook"],
    "core.rules_store": ["get_all_rules", "save_all_rules", "get_channel_rules"],
    "core.text_utils": ["normalize_search_text", "upper_tr"],
    "core.window_state_manager": ["save_window_state", "restore_window_state"],

    "data.database": [
        "init_db",
        "upsert_news",
        "delete_news_for_paths",
        "check_database_integrity",
        "vacuum_databases",
        "analyze_databases",
        "get_news_count_for_month",
        "get_all_codes_from_db",
        "search_archive",
        "merge_external_database_into_channel",
    ],
    "data.cache_manager": ["ensure_cache_table", "is_cached", "update_cache", "clear_cache"],
    "data.database_search": ["search_archive"],
    "data.database_merge": ["merge_external_database_into_channel"],
    "data.news_repository": ["NewsRepository"],

    "dictionaries.dictionary_store": [
        "load_common_dictionary",
        "save_common_dictionary",
        "load_channel_dictionary",
        "save_channel_dictionary",
        "add_title_dictionary_entry",
    ],
    "dictionaries.spell_backend": [
        "reload_spell_backend_status",
        "get_spell_backend_status_text",
        "has_spell_backend",
        "apply_spell_suggestions",
    ],
    "dictionaries.title_transform": [
        "apply_dictionary_pairs",
        "apply_title_spellcheck",
    ],
    "dictionaries.title_spellcheck": [
        "load_common_dictionary",
        "save_common_dictionary",
        "load_channel_dictionary",
        "save_channel_dictionary",
        "add_title_dictionary_entry",
        "reload_spell_backend_status",
        "get_spell_backend_status_text",
        "apply_dictionary_pairs",
        "apply_title_spellcheck",
    ],

    "models.archive_search_result": ["ArchiveSearchResult"],
    "models.news_item": ["NewsItem"],
    "models.news_table_model": ["NewsTableModel"],
    "models.news_list_model": ["NewsListModel"],

    "watchers.live_reload": ["LiveReloadWatcher"],

    "parsing.scanner": ["build_date_path", "scan_news_files"],
    "parsing.parser": ["ParsedNews", "parse_egs_file"],
    "parsing.news_service": ["NewsIngestService"],
    "parsing.news_worker": ["NewsLoadWorker"],
    "parsing.worker_manager": ["WorkerManager"],

    "dialogs.startup_dialog": ["StartupDialog"],
    "dialogs.help_dialog": ["HelpDialog"],
    "dialogs.info_dialog": ["InfoDialog"],
    "dialogs.log_viewer_dialog": ["LogViewerDialog"],
    "dialogs.code_filter_wizard": ["CodeFilterWizardDialog"],
    "dialogs.rules_manager_dialog": ["RulesManagerDialog"],
    "dialogs.archive_search_dialog": ["ArchiveSearchDialog"],
    "dialogs.find_replace_dialog": ["FindReplaceDialog"],
    "dialogs.title_dictionary_manager": ["TitleDictionaryManagerDialog"],
    "dialogs.dictionary_bundle_dialog": ["DictionaryBundleDialog"],
    "dialogs.external_db_manager": ["ExternalDbManagerDialog"],
    "dialogs.db_merge_dialog": ["DbMergeDialog"],

    "ui.main_window_topbar": ["build_topbar"],
    "ui.main_window_filters": ["build_filter_bar"],
    "ui.main_window_preview": ["build_news_list_panel", "build_preview_panel"],
    "ui.main_window_context_menus": ["show_header_context_menu", "show_news_context_menu", "open_source_file"],
    "ui.main_window_menu_builder": ["build_main_window_menu"],
    "ui.main_window_ui": ["build_main_window_ui", "attach_ui_helpers"],

    "actions.main_window_actions": ["MainWindowActions"],
    "actions.main_window_edit_actions": ["MainWindowEditActions"],
    "actions.main_window_view_actions": ["MainWindowViewActions"],
    "actions.main_window_data_actions": ["MainWindowDataActions"],
    "actions.main_window_state_hooks": ["MainWindowStateHooks"],
}


def write_report(lines: list[str]) -> None:
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def check_required_files(report: list[str]) -> tuple[int, int]:
    report.append("=== DOSYA KONTROLÜ ===")
    ok = 0
    fail = 0

    for rel in REQUIRED_FILES:
        path = BASE_DIR / rel
        if path.exists():
            report.append(f"[OK] {rel}")
            ok += 1
        else:
            report.append(f"[EKSİK] {rel}")
            fail += 1

    report.append("")
    return ok, fail


def check_imports_and_symbols(report: list[str]) -> tuple[int, int]:
    report.append("=== MODÜL / SEMBOL KONTROLÜ ===")
    ok = 0
    fail = 0

    for module_name, symbols in MODULE_SYMBOLS.items():
        try:
            module = importlib.import_module(module_name)
            report.append(f"[OK] import {module_name}")
            ok += 1
        except Exception:
            report.append(f"[HATA] import {module_name}")
            report.append(traceback.format_exc().rstrip())
            fail += 1
            report.append("")
            continue

        for symbol in symbols:
            if hasattr(module, symbol):
                report.append(f"    [OK] {symbol}")
                ok += 1
            else:
                report.append(f"    [EKSİK] {symbol}")
                fail += 1

        report.append("")

    return ok, fail


def check_basic_runtime(report: list[str]) -> tuple[int, int]:
    report.append("=== TEMEL ÇALIŞMA ZAMANI KONTROLÜ ===")
    ok = 0
    fail = 0

    try:
        from core.settings_manager import load_settings
        data = load_settings()
        if isinstance(data, dict):
            report.append("[OK] settings_manager.load_settings dict döndürüyor")
            ok += 1
        else:
            report.append("[HATA] settings_manager.load_settings dict döndürmedi")
            fail += 1
    except Exception:
        report.append("[HATA] settings_manager.load_settings çağrısı başarısız")
        report.append(traceback.format_exc().rstrip())
        fail += 1

    try:
        from dictionaries.title_spellcheck import get_spell_backend_status_text
        status = get_spell_backend_status_text()
        report.append(f"[OK] Yazım denetimi durumu: {status}")
        ok += 1
    except Exception:
        report.append("[HATA] Yazım denetimi durumu okunamadı")
        report.append(traceback.format_exc().rstrip())
        fail += 1

    try:
        from core.app_paths import DATA_DIR, DATABASES_DIR, LOG_DIR
        for p in [DATA_DIR, DATABASES_DIR, LOG_DIR]:
            p.mkdir(parents=True, exist_ok=True)
        report.append("[OK] Veri klasörleri erişilebilir")
        ok += 1
    except Exception:
        report.append("[HATA] Veri klasörleri erişilemiyor")
        report.append(traceback.format_exc().rstrip())
        fail += 1

    try:
        from data.database import init_db
        init_db("A NEWS", "2026-04-16")
        report.append("[OK] init_db çalıştı")
        ok += 1
    except Exception:
        report.append("[HATA] init_db çalışmadı")
        report.append(traceback.format_exc().rstrip())
        fail += 1

    report.append("")
    return ok, fail


def main() -> int:
    report: list[str] = []
    report.append("EGS Scrapper Sağlık Kontrolü")
    report.append(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Klasör: {BASE_DIR}")
    report.append("")

    total_ok = 0
    total_fail = 0

    ok, fail = check_required_files(report)
    total_ok += ok
    total_fail += fail

    ok, fail = check_imports_and_symbols(report)
    total_ok += ok
    total_fail += fail

    ok, fail = check_basic_runtime(report)
    total_ok += ok
    total_fail += fail

    report.append("=== ÖZET ===")
    report.append(f"Başarılı kontrol: {total_ok}")
    report.append(f"Hatalı kontrol: {total_fail}")

    if total_fail == 0:
        report.append("SONUÇ: SAĞLIK KONTROLÜ BAŞARILI")
    else:
        report.append("SONUÇ: SAĞLIK KONTROLÜNDE HATALAR VAR")

    write_report(report)

    print("\n".join(report))
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
