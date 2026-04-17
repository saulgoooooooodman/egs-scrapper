import os
import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox

from core.settings_manager import save_settings
from dialogs.help_dialog import HelpDialog
from dialogs.info_dialog import InfoDialog
from dialogs.log_viewer_dialog import LogViewerDialog
from dialogs.external_db_manager import ExternalDbManagerDialog
from dialogs.archive_search_dialog import ArchiveSearchDialog
from dialogs.rules_manager_dialog import RulesManagerDialog
from dialogs.code_filter_wizard import CodeFilterWizardDialog
from core.app_paths import BASE_DIR, DATA_DIR, LOG_DIR, DATABASES_DIR
from core.rules_store import get_channel_rules
from dictionaries.title_spellcheck import reload_spell_backend_status, get_spell_backend_status_text
from dialogs.dictionary_bundle_dialog import DictionaryBundleDialog
from dialogs.db_merge_dialog import DbMergeDialog


class MainWindowViewActions:
    def _apply_styles(self):
        self.setStyleSheet("""
            QTableView::item {
                padding: 0px 3px;
            }
            QPushButton {
                padding: 4px 8px;
            }
            QMenu::separator {
                height: 1px;
                background: #6b7280;
                margin: 4px 8px;
            }
        """)

    def _sync_duplicate_menu_checks(self):
        mode = self.settings.get("main_duplicate_mode", "off")
        self.action_show_all_titles.setChecked(mode == "off")
        self.action_hide_old.setChecked(mode == "latest")
        self.action_hide_new.setChecked(mode == "oldest")

    def load_main_ui_settings(self):
        scope = self.settings.get("main_search_scope", "Tümü")
        idx = self.search_scope_combo.findText(scope)
        if idx >= 0:
            self.search_scope_combo.setCurrentIndex(idx)
        self.search_regex_checkbox.setChecked(bool(self.settings.get("main_search_regex", False)))

        self.selected_codes = set(self.settings.get("main_selected_codes", []))
        self.code_filter_hide_mode = bool(self.settings.get("main_code_filter_hide_mode", False))

        hide_code = bool(self.settings.get("main_hide_code_column", False))
        self.news_view.setColumnHidden(0, hide_code)

        if "main_duplicate_mode" not in self.settings:
            self.settings["main_duplicate_mode"] = "off"

        remember_geometry = bool(self.settings.get("remember_window_geometry", False))
        self.action_remember_window.setChecked(remember_geometry)

        always_on_top = bool(self.settings.get("always_on_top", False))
        self.action_always_on_top.setChecked(always_on_top)
        self._apply_always_on_top(always_on_top)

        show_previous = bool(self.settings.get("show_previous_day_news", True))
        if hasattr(self, "action_show_previous_day_news"):
            self.action_show_previous_day_news.setChecked(show_previous)

        self.apply_ui_font_size(int(self.settings.get("ui_font_size", 11)), save=False)
        self._sync_duplicate_menu_checks()

    def save_main_ui_settings(self):
        self.settings["main_search_scope"] = self.search_scope_combo.currentText()
        self.settings["main_search_regex"] = bool(self.search_regex_checkbox.isChecked())
        self.settings["main_selected_codes"] = sorted(self.selected_codes)
        self.settings["main_code_filter_hide_mode"] = self.code_filter_hide_mode
        self.settings["main_hide_code_column"] = self.news_view.isColumnHidden(0)
        save_settings(self.settings)
        self.status_label.setText("Profil ayarları kaydedildi")

    def hide_code_column(self):
        self.news_view.setColumnHidden(0, True)
        self.save_main_ui_settings()

    def show_code_column(self):
        self.news_view.setColumnHidden(0, False)
        self.save_main_ui_settings()

    def toggle_code_column(self):
        hidden = self.news_view.isColumnHidden(0)
        self.news_view.setColumnHidden(0, not hidden)
        self.save_main_ui_settings()

    def apply_ui_font_size(self, size: int, save: bool = True):
        size = max(9, min(22, int(size)))
        self.settings["ui_font_size"] = size

        base_font = QFont(self.font())
        base_font.setPointSize(size)
        self.setFont(base_font)
        if self.menuBar():
            self.menuBar().setFont(base_font)
        if self.centralWidget():
            self.centralWidget().setFont(base_font)

        self.news_view.verticalHeader().setDefaultSectionSize(max(22, size + 12))

        title_font = QFont(base_font)
        title_font.setPointSize(size + 5)
        title_font.setBold(True)
        self.preview_title.setFont(title_font)

        corrected_font = QFont(base_font)
        corrected_font.setPointSize(size + 1)
        corrected_font.setBold(True)
        self.preview_corrected_title.setFont(corrected_font)

        info_font = QFont(base_font)
        info_font.setPointSize(size)
        self.preview_info.setFont(info_font)

        if save:
            save_settings(self.settings)
            self.status_label.setText(f"Yazı boyutu: {size} pt")

    def increase_ui_font_size(self):
        self.apply_ui_font_size(int(self.settings.get("ui_font_size", 11)) + 1)

    def decrease_ui_font_size(self):
        self.apply_ui_font_size(int(self.settings.get("ui_font_size", 11)) - 1)

    def reset_ui_font_size(self):
        self.apply_ui_font_size(11)

    def set_duplicate_mode_latest(self):
        self.settings["main_duplicate_mode"] = "latest"
        self._sync_duplicate_menu_checks()
        self.apply_filters()
        save_settings(self.settings)

    def set_duplicate_mode_oldest(self):
        self.settings["main_duplicate_mode"] = "oldest"
        self._sync_duplicate_menu_checks()
        self.apply_filters()
        save_settings(self.settings)

    def set_duplicate_mode_off(self):
        self.settings["main_duplicate_mode"] = "off"
        self._sync_duplicate_menu_checks()
        self.apply_filters()
        save_settings(self.settings)

    def _apply_always_on_top(self, enabled: bool):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, enabled)
        self.show()

    def toggle_always_on_top(self):
        enabled = self.action_always_on_top.isChecked()
        self.settings["always_on_top"] = enabled
        save_settings(self.settings)
        self._apply_always_on_top(enabled)

    def toggle_remember_window_geometry(self):
        enabled = self.action_remember_window.isChecked()
        self.settings["remember_window_geometry"] = enabled
        save_settings(self.settings)
        self.status_label.setText("Pencere konumu ayarı güncellendi")

    def focus_search(self):
        self.search_input.setFocus()

    def open_help_dialog(self):
        dialog = HelpDialog(self)
        dialog.exec()

    def open_log_viewer(self):
        dialog = LogViewerDialog(self)
        dialog.exec()

    def _run_support_tool(self, bat_name: str, py_name: str, title: str):
        bat_path = BASE_DIR / bat_name
        if bat_path.exists():
            try:
                os.startfile(str(bat_path))
                return
            except Exception:
                pass

        py_path = BASE_DIR / py_name
        if py_path.exists():
            try:
                subprocess.Popen([sys.executable, str(py_path)], cwd=str(BASE_DIR))
                return
            except Exception as exc:
                QMessageBox.critical(self, title, f"{title} başlatılamadı:\n{exc}")
                return

        QMessageBox.warning(self, title, f"{bat_name} veya {py_name} bulunamadı.")

    def run_health_check_tool(self):
        self._run_support_tool("saglik_kontrolu.bat", "health_check.py", "Sağlık Kontrolü")

    def run_smoke_test_tool(self):
        self._run_support_tool("smoke_test.bat", "smoke_test.py", "Smoke Test")

    def show_info_dialog(self):
        dialog = InfoDialog(self)
        dialog.exec()

    def open_data_folder(self):
        os.startfile(str(DATA_DIR))

    def open_logs_folder(self):
        os.startfile(str(LOG_DIR))

    def open_databases_folder(self):
        os.startfile(str(DATABASES_DIR))

    def open_external_db_manager(self):
        dialog = ExternalDbManagerDialog(self)
        dialog.exec()

    def open_dictionary_bundle_dialog(self):
        dialog = DictionaryBundleDialog(self)
        dialog.exec()

    def open_db_merge_dialog(self):
        dialog = DbMergeDialog(self.channel_name, self)
        dialog.exec()

    def reload_spell_backend(self):
        reload_spell_backend_status()
        QMessageBox.information(
            self,
            "Yazım Denetimi",
            get_spell_backend_status_text()
        )
        self.load_news(force_refresh=True)

    def open_archive_search(self):
        dialog = ArchiveSearchDialog(self.channel_name, self)
        dialog.exec()

    def open_rules_manager(self):
        dialog = RulesManagerDialog(self.channel_name, self)
        dialog.exec()
        self.load_news(force_refresh=True)

    def open_code_filter(self):
        rules = get_channel_rules(self.channel_name)
        all_codes = rules.get("news_codes", {})

        if not all_codes:
            QMessageBox.information(
                self,
                "Kod Filtreleri",
                "Bu kanal için kod tanımı yok. Gerekirse önce Kanal Kuralları ekranından ekle."
            )
            return

        dialog = CodeFilterWizardDialog(
            all_codes,
            self.selected_codes,
            hide_mode=self.code_filter_hide_mode,
            parent=self
        )

        if dialog.exec():
            self.selected_codes = set(dialog.get_selected_codes())
            self.code_filter_hide_mode = dialog.is_hide_mode()
            self.apply_filters()
            self.save_main_ui_settings()

    def toggle_previous_day_news(self):
        enabled = self.action_show_previous_day_news.isChecked()
        self.settings["show_previous_day_news"] = enabled
        save_settings(self.settings)
        self.apply_filters()
