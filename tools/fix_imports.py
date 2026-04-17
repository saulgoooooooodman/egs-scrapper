from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

REPLACEMENTS = {
    "from main_window_ui": "from ui.main_window_ui",
    "from main_window_topbar": "from ui.main_window_topbar",
    "from main_window_filters": "from ui.main_window_filters",
    "from main_window_preview": "from ui.main_window_preview",
    "from main_window_menu_builder": "from ui.main_window_menu_builder",
    "from main_window_context_menus": "from ui.main_window_context_menus",

    "from main_window_actions": "from actions.main_window_actions",
    "from main_window_edit_actions": "from actions.main_window_edit_actions",
    "from main_window_view_actions": "from actions.main_window_view_actions",
    "from main_window_data_actions": "from actions.main_window_data_actions",
    "from main_window_state_hooks": "from actions.main_window_state_hooks",

    "from database": "from data.database",
    "from database_core": "from data.database_core",
    "from database_search": "from data.database_search",
    "from database_merge": "from data.database_merge",
    "from cache_manager": "from data.cache_manager",

    "from parser": "from parsing.parser",
    "from scanner": "from parsing.scanner",
    "from news_worker": "from parsing.news_worker",
    "from worker_manager": "from parsing.worker_manager",

    "from title_spellcheck": "from dictionaries.title_spellcheck",
    "from dictionary_store": "from dictionaries.dictionary_store",
    "from spell_backend": "from dictionaries.spell_backend",
    "from title_transform": "from dictionaries.title_transform",

    "from archive_search_dialog": "from dialogs.archive_search_dialog",
    "from startup_dialog": "from dialogs.startup_dialog",
    "from find_replace_dialog": "from dialogs.find_replace_dialog",
    "from code_filter_wizard": "from dialogs.code_filter_wizard",
    "from help_dialog": "from dialogs.help_dialog",
    "from info_dialog": "from dialogs.info_dialog",
    "from log_viewer_dialog": "from dialogs.log_viewer_dialog",
    "from rules_manager_dialog": "from dialogs.rules_manager_dialog",
    "from title_dictionary_manager": "from dialogs.title_dictionary_manager",
    "from dictionary_bundle_dialog": "from dialogs.dictionary_bundle_dialog",
    "from external_db_manager": "from dialogs.external_db_manager",
    "from db_merge_dialog": "from dialogs.db_merge_dialog",

    "from app_paths": "from core.app_paths",
    "from settings_manager": "from core.settings_manager",
    "from logger_setup": "from core.logger_setup",
    "from rules_store": "from core.rules_store",
    "from text_utils": "from core.text_utils",
    "from window_state_manager": "from core.window_state_manager",

    "from live_reload": "from watchers.live_reload",

    "from news_table_model": "from models.news_table_model",
    "from news_list_model": "from models.news_list_model",
}


def process_file(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    original = text

    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)

    if text != original:
        backup_path = file_path.with_suffix(".bak")
        backup_path.write_text(original, encoding="utf-8")
        file_path.write_text(text, encoding="utf-8")
        return True

    return False


def main():
    print("=== IMPORT DUZELTME BASLIYOR ===\n")

    changed = 0

    for py_file in BASE_DIR.rglob("*.py"):
        if "fix_imports.py" in str(py_file):
            continue

        try:
            if process_file(py_file):
                print(f"[DUZELTILDI] {py_file}")
                changed += 1
        except Exception as e:
            print(f"[HATA] {py_file} -> {e}")

    print("\n=== TAMAMLANDI ===")
    print(f"Degistirilen dosya sayisi: {changed}")


if __name__ == "__main__":
    main()