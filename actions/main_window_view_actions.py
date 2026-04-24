import os
import subprocess
import sys
from copy import deepcopy

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication, QColorDialog, QMessageBox, QDialog

from dialogs.help_dialog import HelpDialog
from dialogs.info_dialog import InfoDialog
from dialogs.log_viewer_dialog import LogViewerDialog
from dialogs.external_db_manager import ExternalDbManagerDialog
from dialogs.archive_search_dialog import ArchiveSearchDialog
from dialogs.rules_manager_dialog import RulesManagerDialog
from dialogs.settings_dialog import SettingsDialog
from dialogs.statistics_dialog import StatisticsDialog
from dialogs.code_filter_wizard import CodeFilterWizardDialog
from core.app_paths import BASE_DIR, DATA_DIR, LOG_DIR, DATABASES_DIR
from core.rules_store import display_rule_code, get_all_rules, get_channel_rules, get_channel_scan_options, save_all_rules
from dictionaries.title_spellcheck import reload_spell_backend_status, get_spell_backend_status_text
from dialogs.dictionary_bundle_dialog import DictionaryBundleDialog
from dialogs.db_merge_dialog import DbMergeDialog
from data.database import analyze_databases, check_database_integrity, vacuum_databases


class MainWindowViewActions:
    def _capture_global_state(self) -> dict:
        return {
            "settings": deepcopy(dict(self.settings or {})),
            "rules": deepcopy(get_all_rules()),
        }

    def _push_global_undo_state(self):
        history = list(getattr(self, "_global_undo_history", []))
        history.append(self._capture_global_state())
        self._global_undo_history = history[-50:]
        self._global_redo_history = []

    def _restore_global_state(self, snapshot: dict):
        self.settings.clear()
        self.settings.update(deepcopy(snapshot.get("settings", {})))
        save_all_rules(deepcopy(snapshot.get("rules", {})))
        self.load_main_ui_settings()
        self.apply_news_table_styles(save=False)
        self.sync_symbol_prefixed_visibility_action()
        self.schedule_settings_save()
        self._apply_live_watch_setting()
        self.load_news(force_refresh=False)

    def undo_global_change(self) -> bool:
        history = list(getattr(self, "_global_undo_history", []))
        if not history:
            return False
        current = self._capture_global_state()
        snapshot = history.pop()
        redo_history = list(getattr(self, "_global_redo_history", []))
        redo_history.append(current)
        self._global_redo_history = redo_history[-50:]
        self._global_undo_history = history
        self._restore_global_state(snapshot)
        self.status_label.setText("Son ayar değişikliği geri alındı")
        return True

    def redo_global_change(self) -> bool:
        history = list(getattr(self, "_global_redo_history", []))
        if not history:
            return False
        current = self._capture_global_state()
        snapshot = history.pop()
        undo_history = list(getattr(self, "_global_undo_history", []))
        undo_history.append(current)
        self._global_undo_history = undo_history[-50:]
        self._global_redo_history = history
        self._restore_global_state(snapshot)
        self.status_label.setText("Son ayar değişikliği yeniden uygulandı")
        return True

    def _format_size_text(self, value: int) -> str:
        size = float(max(int(value or 0), 0))
        units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        return f"{size:.1f} {units[unit_index]}"

    def _show_database_maintenance_result(self, title: str, summary: str, details: list[str]):
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setIcon(QMessageBox.Information)
        dialog.setText(summary)
        if details:
            dialog.setDetailedText("\n".join(details))
        dialog.exec()

    def _run_database_maintenance(self, title: str, callback):
        result = None
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            result = callback()
        except (OSError, RuntimeError, ValueError) as exc:
            result = {
                "kind": "error",
                "title": title,
                "message": f"{title} sırasında hata oluştu:\n{exc}",
            }
        finally:
            QApplication.restoreOverrideCursor()
            QApplication.processEvents()
        return result

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

    def _current_spellcheck_mode(self) -> str:
        return str(
            self.settings.get(
                "title_spellcheck_mode",
                "auto" if bool(self.settings.get("auto_title_spellcheck", True)) else "manual",
            )
            or "manual"
        ).lower()

    def _sync_spellcheck_menu_checks(self):
        mode = self._current_spellcheck_mode()
        if hasattr(self, "action_spellcheck_off"):
            self.action_spellcheck_off.setChecked(mode == "off")
        if hasattr(self, "action_spellcheck_manual"):
            self.action_spellcheck_manual.setChecked(mode == "manual")
        if hasattr(self, "action_spellcheck_auto"):
            self.action_spellcheck_auto.setChecked(mode == "auto")

    def _normalized_row_style(self, value) -> dict:
        if not isinstance(value, dict):
            return {}
        result = {}
        for key in ("background", "foreground"):
            color = str(value.get(key, "") or "").strip()
            if color:
                result[key] = color
        return result

    def apply_news_table_styles(self, save: bool = False):
        code_styles = {}
        channel_rules = get_channel_rules(self.channel_name).get("codes", {})
        for raw_code, config in channel_rules.items():
            visible_code = display_rule_code(raw_code)
            if not visible_code:
                continue
            style = self._normalized_row_style({
                "background": str(config.get("row_background", "") or "").strip(),
                "foreground": str(config.get("row_foreground", "") or "").strip(),
            })
            if style:
                code_styles[visible_code] = style

        legacy_styles = self.settings.get("news_code_styles", {})
        if isinstance(legacy_styles, dict):
            for code, style in legacy_styles.items():
                normalized_code = str(code or "").strip().upper()
                if normalized_code and normalized_code not in code_styles:
                    normalized_style = self._normalized_row_style(style)
                    if normalized_style:
                        code_styles[normalized_code] = normalized_style

        old_news_style = self._normalized_row_style(self.settings.get("old_news_row_style", {}))
        self.news_model.set_styles(code_styles, old_news_style)
        if save:
            self.schedule_settings_save()

    def _pick_color(self, title: str, current_value: str = "") -> str:
        initial = QColor(current_value) if current_value else QColor()
        selected = QColorDialog.getColor(initial, self, title)
        if not selected.isValid():
            return ""
        return selected.name()

    def _update_code_style(self, code: str, field: str, title: str):
        visible_code = str(code or "").strip().upper()
        if not visible_code:
            self.status_label.setText("Renk atanacak haber kodu bulunamadı")
            return

        self._push_global_undo_state()
        rules = get_all_rules()
        channel_rules = dict(rules.get(self.channel_name, {}) or {})
        code_rules = dict(channel_rules.get("codes", {}) or {})

        raw_code = ""
        for candidate in code_rules.keys():
            if display_rule_code(candidate) == visible_code:
                raw_code = candidate
                break
        if not raw_code:
            raw_code = visible_code

        config = dict(code_rules.get(raw_code, {}) or {})
        rule_field = "row_background" if field == "background" else "row_foreground"
        selected = self._pick_color(title, str(config.get(rule_field, "") or ""))
        if not selected:
            return

        config[rule_field] = selected
        code_rules[raw_code] = config
        channel_rules["codes"] = code_rules
        rules[self.channel_name] = channel_rules
        save_all_rules(rules)
        self.apply_news_table_styles(save=True)
        self.status_label.setText(f"Haber kodu rengi güncellendi: {visible_code}")

    def clear_code_style(self, code: str):
        visible_code = str(code or "").strip().upper()
        self._push_global_undo_state()
        rules = get_all_rules()
        channel_rules = dict(rules.get(self.channel_name, {}) or {})
        code_rules = dict(channel_rules.get("codes", {}) or {})
        changed = False

        for raw_code, config in code_rules.items():
            if display_rule_code(raw_code) != visible_code:
                continue
            updated = dict(config or {})
            updated["row_background"] = ""
            updated["row_foreground"] = ""
            code_rules[raw_code] = updated
            changed = True
            break

        if changed:
            channel_rules["codes"] = code_rules
            rules[self.channel_name] = channel_rules
            save_all_rules(rules)
            self.apply_news_table_styles(save=True)
            self.status_label.setText(f"Haber kodu rengi temizlendi: {visible_code}")

    def set_code_background_color(self, code: str):
        self._update_code_style(code, "background", f"{code} kodu için satır rengi")

    def set_code_foreground_color(self, code: str):
        self._update_code_style(code, "foreground", f"{code} kodu için yazı rengi")

    def _update_old_news_style(self, field: str, title: str):
        self._push_global_undo_state()
        style = dict(self.settings.get("old_news_row_style", {}) or {})
        selected = self._pick_color(title, str(style.get(field, "") or ""))
        if not selected:
            return
        style[field] = selected
        self.settings["old_news_row_style"] = style
        self.apply_news_table_styles(save=True)
        self.status_label.setText("Eski haber satır rengi güncellendi")

    def set_old_news_background_color(self):
        self._update_old_news_style("background", "Eski haberler için satır rengi")

    def set_old_news_foreground_color(self):
        self._update_old_news_style("foreground", "Eski haberler için yazı rengi")

    def clear_old_news_style(self):
        self._push_global_undo_state()
        self.settings["old_news_row_style"] = {}
        self.apply_news_table_styles(save=True)
        self.status_label.setText("Eski haber rengi temizlendi")

    def load_main_ui_settings(self):
        scope = self.settings.get("main_search_scope", "Tümü")
        idx = self.search_scope_combo.findText(scope)
        if idx >= 0:
            self.search_scope_combo.setCurrentIndex(idx)
        self.search_regex_checkbox.setChecked(bool(self.settings.get("main_search_regex", False)))
        if hasattr(self, "action_search_regex"):
            self.action_search_regex.setChecked(self.search_regex_checkbox.isChecked())

        self.selected_codes = set(self.settings.get("main_selected_codes", []))
        self.code_filter_hide_mode = bool(self.settings.get("main_code_filter_hide_mode", False))

        hidden_columns = self.settings.get("main_hidden_columns", [])
        if not isinstance(hidden_columns, list):
            hidden_columns = []
        if bool(self.settings.get("main_hide_code_column", False)) and 0 not in hidden_columns:
            hidden_columns.append(0)
        for column in range(self.news_model.columnCount()):
            self.news_view.setColumnHidden(column, column in hidden_columns)

        if "main_duplicate_mode" not in self.settings:
            self.settings["main_duplicate_mode"] = "off"

        show_corrected_titles = bool(self.settings.get("show_corrected_titles_in_list", False))
        self.news_model.set_show_corrected_titles(show_corrected_titles)
        if hasattr(self, "action_show_corrected_titles"):
            self.action_show_corrected_titles.setChecked(show_corrected_titles)

        remember_geometry = bool(self.settings.get("remember_window_geometry", False))
        self.action_remember_window.setChecked(remember_geometry)

        remember_last_date = bool(self.settings.get("remember_last_date", False))
        if hasattr(self, "action_remember_last_date"):
            self.action_remember_last_date.setChecked(remember_last_date)

        always_on_top = bool(self.settings.get("always_on_top", False))
        self.action_always_on_top.setChecked(always_on_top)
        self._apply_always_on_top(always_on_top)

        self._sync_spellcheck_menu_checks()

        show_previous = bool(self.settings.get("show_previous_day_news", True))
        hide_previous = bool(self.settings.get("hide_previous_day_news", not show_previous))
        if hasattr(self, "action_show_previous_day_news"):
            self.action_show_previous_day_news.setChecked(hide_previous)

        self.apply_font_settings(save=False)
        self.apply_news_table_styles(save=False)
        self._sync_duplicate_menu_checks()
        self.sync_symbol_prefixed_visibility_action()

    def save_main_ui_settings(self, show_message: bool = False):
        self.settings["main_search_scope"] = self.search_scope_combo.currentText()
        self.settings["main_search_regex"] = bool(self.search_regex_checkbox.isChecked())
        self.settings["main_selected_codes"] = sorted(self.selected_codes)
        self.settings["main_code_filter_hide_mode"] = self.code_filter_hide_mode
        hidden_columns = [
            column
            for column in range(self.news_model.columnCount())
            if self.news_view.isColumnHidden(column)
        ]
        self.settings["main_hidden_columns"] = hidden_columns
        self.settings["main_hide_code_column"] = 0 in hidden_columns
        self.schedule_settings_save()
        if show_message:
            self.status_label.setText("Gorunum ayarlari kaydedildi")

    def on_main_splitter_moved(self, *_args):
        if not hasattr(self, "main_splitter"):
            return
        self.settings["main_splitter_sizes"] = [int(size) for size in self.main_splitter.sizes()]
        self.schedule_settings_save()

    def set_title_spellcheck_mode(self, mode: str):
        normalized_mode = str(mode or "manual").lower()
        if normalized_mode not in {"off", "manual", "auto"}:
            normalized_mode = "manual"

        self._push_global_undo_state()
        self.settings["title_spellcheck_mode"] = normalized_mode
        self.settings["auto_title_spellcheck"] = normalized_mode == "auto"
        self.schedule_settings_save()
        self._sync_spellcheck_menu_checks()

        if normalized_mode == "auto":
            self.status_label.setText("Başlık yazım denetimi otomatik moda alındı")
        elif normalized_mode == "manual":
            self.status_label.setText("Başlık yazım denetimi elle moda alındı")
        else:
            self.status_label.setText("Başlık yazım denetimi kapatıldı")

    def toggle_remember_last_date(self):
        self._push_global_undo_state()
        enabled = bool(self.action_remember_last_date.isChecked())
        self.settings["remember_last_date"] = enabled
        if enabled:
            self.settings["last_selected_date"] = self.date_edit.date().toString("yyyy-MM-dd")
            self.status_label.setText("Son açılan gün hatırlanacak")
        else:
            self.settings["last_selected_date"] = ""
            self.status_label.setText("Son açılan gün hatırlanmayacak")
        self.schedule_settings_save()

    def toggle_search_regex(self):
        self._push_global_undo_state()
        enabled = bool(self.action_search_regex.isChecked())
        self.search_regex_checkbox.setChecked(enabled)
        self.save_main_ui_settings()
        self.status_label.setText(
            "Düzenli ifadeler araması açıldı"
            if enabled
            else "Düzenli ifadeler araması kapatıldı"
        )

    def sync_symbol_prefixed_visibility_action(self):
        if not hasattr(self, "action_toggle_symbol_titles"):
            return
        options = get_channel_scan_options(self.channel_name)
        self.action_toggle_symbol_titles.blockSignals(True)
        self.action_toggle_symbol_titles.setChecked(bool(options.get("hide_symbol_prefixed_titles", True)))
        self.action_toggle_symbol_titles.blockSignals(False)

    def toggle_symbol_prefixed_titles(self):
        self._push_global_undo_state()
        hidden = bool(self.action_toggle_symbol_titles.isChecked())
        rules = get_all_rules()
        channel_rules = dict(rules.get(self.channel_name, {}) or {})
        scan_options = dict(channel_rules.get("scan_options", {}) or {})
        scan_options["hide_symbol_prefixed_titles"] = hidden
        channel_rules["scan_options"] = scan_options
        rules[self.channel_name] = channel_rules
        save_all_rules(rules)
        self.status_label.setText(
            "Sembol ile başlayan genel başlıklar gizlenecek"
            if hidden
            else "Sembol ile başlayan genel başlıklar gösterilecek"
        )
        self.load_news(force_refresh=True)

    def insert_search_pattern(self, pattern: str):
        self.search_input.insert(str(pattern or ""))
        self.search_input.setFocus()

    def set_column_visibility(self, column: int, visible: bool):
        if column < 0 or column >= self.news_model.columnCount():
            return
        self.news_view.setColumnHidden(column, not visible)
        self.save_main_ui_settings()

    def hide_code_column(self):
        self.set_column_visibility(0, False)

    def show_code_column(self):
        self.set_column_visibility(0, True)

    def toggle_code_column(self):
        self.set_column_visibility(0, self.news_view.isColumnHidden(0))

    def toggle_show_corrected_titles_in_list(self):
        enabled = bool(self.action_show_corrected_titles.isChecked())
        self.settings["show_corrected_titles_in_list"] = enabled
        self.news_model.set_show_corrected_titles(enabled)
        self.schedule_settings_save()
        self.status_label.setText(
            "Listede düzeltilmiş başlıklar gösteriliyor"
            if enabled
            else "Listede dosyadan gelen başlıklar gösteriliyor"
        )

    def _get_news_list_font_size(self) -> int:
        return max(9, min(22, int(self.settings.get("news_list_font_size", 11))))

    def _get_preview_text_font_size(self) -> int:
        return max(9, min(22, int(self.settings.get("preview_text_font_size", 11))))

    def apply_font_settings(self, save: bool = True):
        list_size = self._get_news_list_font_size()
        preview_size = self._get_preview_text_font_size()

        list_font = QFont(self.news_view.font())
        list_font.setPointSize(list_size)
        self.news_view.setFont(list_font)
        self.news_view.horizontalHeader().setFont(list_font)
        self.count_label.setFont(list_font)
        self.news_view.verticalHeader().setDefaultSectionSize(max(22, list_size + 12))

        preview_font = QFont(self.preview_text.font())
        preview_font.setPointSize(preview_size)
        self.preview_text.setFont(preview_font)

        title_font = QFont(preview_font)
        title_font.setPointSize(preview_size + 5)
        title_font.setBold(True)
        self.preview_title.setFont(title_font)

        corrected_font = QFont(preview_font)
        corrected_font.setPointSize(preview_size + 1)
        corrected_font.setBold(True)
        self.preview_corrected_title.setFont(corrected_font)

        info_font = QFont(preview_font)
        info_font.setPointSize(preview_size)
        self.preview_info.setFont(info_font)

        if save:
            self.schedule_settings_save()

    def _adjust_news_list_font_size(self, delta: int | None = None, reset: bool = False):
        size = 11 if reset else self._get_news_list_font_size() + int(delta or 0)
        self.settings["news_list_font_size"] = max(9, min(22, size))
        self.apply_font_settings()
        self.status_label.setText(f"Haber listesi yazı boyutu: {self._get_news_list_font_size()} pt")

    def _adjust_preview_text_font_size(self, delta: int | None = None, reset: bool = False):
        size = 11 if reset else self._get_preview_text_font_size() + int(delta or 0)
        self.settings["preview_text_font_size"] = max(9, min(22, size))
        self.apply_font_settings()
        self.status_label.setText(f"Haber metni yazı boyutu: {self._get_preview_text_font_size()} pt")

    def _resolve_font_target(self) -> str:
        if self.news_view.hasFocus():
            return "news_list"
        if self.preview_text.hasFocus():
            return "preview_text"
        return "preview_text"

    def increase_ui_font_size(self):
        target = self._resolve_font_target()
        if target == "news_list":
            self._adjust_news_list_font_size(1)
        else:
            self._adjust_preview_text_font_size(1)

    def decrease_ui_font_size(self):
        target = self._resolve_font_target()
        if target == "news_list":
            self._adjust_news_list_font_size(-1)
        else:
            self._adjust_preview_text_font_size(-1)

    def reset_ui_font_size(self):
        target = self._resolve_font_target()
        if target == "news_list":
            self._adjust_news_list_font_size(reset=True)
        else:
            self._adjust_preview_text_font_size(reset=True)

    def set_duplicate_mode_latest(self):
        self.settings["main_duplicate_mode"] = "latest"
        self._sync_duplicate_menu_checks()
        self.apply_filters()
        self.schedule_settings_save()

    def set_duplicate_mode_oldest(self):
        self.settings["main_duplicate_mode"] = "oldest"
        self._sync_duplicate_menu_checks()
        self.apply_filters()
        self.schedule_settings_save()

    def set_duplicate_mode_off(self):
        self.settings["main_duplicate_mode"] = "off"
        self._sync_duplicate_menu_checks()
        self.apply_filters()
        self.schedule_settings_save()

    def _apply_always_on_top(self, enabled: bool):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, enabled)
        self.show()

    def toggle_always_on_top(self):
        self._push_global_undo_state()
        enabled = self.action_always_on_top.isChecked()
        self.settings["always_on_top"] = enabled
        self.schedule_settings_save()
        self._apply_always_on_top(enabled)

    def toggle_remember_window_geometry(self):
        self._push_global_undo_state()
        enabled = self.action_remember_window.isChecked()
        self.settings["remember_window_geometry"] = enabled
        self.schedule_settings_save()
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
            except OSError:
                pass

        py_path = BASE_DIR / py_name
        if py_path.exists():
            try:
                subprocess.Popen([sys.executable, str(py_path)], cwd=str(BASE_DIR))
                return
            except OSError as exc:
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

    def run_database_integrity_check(self):
        def _task():
            results = check_database_integrity(self.channel_name)
            if not results:
                return {
                    "kind": "info",
                    "title": "Veritabanı Sağlığı",
                    "message": "Kontrol edilecek veritabanı bulunamadı.",
                }

            ok_count = sum(1 for item in results if item["ok"])
            details = []
            for item in results:
                status = "OK" if item["ok"] else "HATA"
                detail = ", ".join(item["messages"])
                details.append(f"[{status}] {item['path']} -> {detail}")

            summary = f"{ok_count}/{len(results)} veritabanı sağlıklı."
            return {
                "kind": "result",
                "title": "Veritabanı Sağlığı",
                "summary": summary,
                "details": details,
                "status": f"Veritabanı bütünlük kontrolü tamamlandı: {summary}",
            }

        result = self._run_database_maintenance("Veritabanı Sağlığı", _task)
        self._present_database_maintenance_feedback(result)

    def run_database_vacuum(self):
        def _task():
            results = vacuum_databases(self.channel_name)
            if not results:
                return {
                    "kind": "info",
                    "title": "Veritabanını Toparla",
                    "message": "Toparlanacak veritabanı bulunamadı.",
                }

            reclaimed_total = sum(item["reclaimed_bytes"] for item in results)
            details = []
            for item in results:
                details.append(
                    f"{item['path']} -> "
                    f"{self._format_size_text(item['before_size'])} -> "
                    f"{self._format_size_text(item['after_size'])} "
                    f"(kazanılan: {self._format_size_text(item['reclaimed_bytes'])})"
                )

            summary = (
                f"{len(results)} veritabanı toparlandı. "
                f"Toplam kazanılan alan: {self._format_size_text(reclaimed_total)}"
            )
            return {
                "kind": "result",
                "title": "Veritabanını Toparla",
                "summary": summary,
                "details": details,
                "status": summary,
            }

        result = self._run_database_maintenance("Veritabanını Toparla", _task)
        self._present_database_maintenance_feedback(result)

    def run_database_analyze(self):
        def _task():
            results = analyze_databases(self.channel_name)
            if not results:
                return {
                    "kind": "info",
                    "title": "Arama İstatistiklerini Yenile",
                    "message": "Güncellenecek veritabanı bulunamadı.",
                }

            details = [item["path"] for item in results]
            summary = f"{len(results)} veritabanı için arama istatistikleri yenilendi."
            return {
                "kind": "result",
                "title": "Arama İstatistiklerini Yenile",
                "summary": summary,
                "details": details,
                "status": summary,
            }

        result = self._run_database_maintenance("Arama İstatistiklerini Yenile", _task)
        self._present_database_maintenance_feedback(result)

    def _present_database_maintenance_feedback(self, result):
        if not result:
            return

        kind = result.get("kind")
        title = result.get("title", "Bilgi")
        if kind == "error":
            QMessageBox.critical(self, title, result.get("message", "İşlem sırasında hata oluştu."))
            return
        if kind == "info":
            QMessageBox.information(self, title, result.get("message", "Bilgi yok."))
            return
        if kind == "result":
            status = result.get("status", "")
            if status:
                self.status_label.setText(status)
            self._show_database_maintenance_result(
                title,
                result.get("summary", ""),
                result.get("details", []),
            )

    def open_external_db_manager(self):
        dialog = ExternalDbManagerDialog(self)
        dialog.exec()

    def open_dictionary_bundle_dialog(self):
        dialog = DictionaryBundleDialog(self.channel_name, self)
        dialog.exec()

    def open_db_merge_dialog(self):
        dialog = DbMergeDialog(self.channel_name, self)
        dialog.exec()

    def reload_spell_backend(self):
        reload_spell_backend_status()
        QMessageBox.information(
            self,
            "Yazım Denetimi",
            "Yazım denetimi yeniden algılandı.\n"
            "Program, gelişmiş yazım denetimi bileşenini yeniden kontrol etti.\n\n"
            f"{get_spell_backend_status_text()}"
        )
        self.load_news(force_refresh=True)

    def open_archive_search(self):
        dialog = ArchiveSearchDialog(self.channel_name, self)
        dialog.exec()

    def open_rules_manager(self):
        dialog = RulesManagerDialog(self.channel_name, self)
        dialog.exec()
        self.sync_symbol_prefixed_visibility_action()
        self.load_news(force_refresh=True)

    def open_settings_dialog(self):
        current_scan_options = get_channel_scan_options(self.channel_name)
        dialog = SettingsDialog(self.settings, self.channel_name, current_scan_options, self)
        if dialog.exec() != QDialog.Accepted:
            return

        self._push_global_undo_state()
        updated_settings, updated_scan_options = dialog.get_values()
        previous_hide_previous = bool(self.settings.get("hide_previous_day_news", False))
        previous_duplicate_mode = str(self.settings.get("main_duplicate_mode", "off"))
        previous_symbol_hide = bool(current_scan_options.get("hide_symbol_prefixed_titles", True))
        previous_live_watch = bool(self.settings.get("live_watch_enabled", False))
        previous_spell_mode = self._current_spellcheck_mode()

        self.settings.update(updated_settings)
        self.save_main_ui_settings()
        self.load_main_ui_settings()
        self._apply_live_watch_setting()

        if previous_live_watch and not bool(self.settings.get("live_watch_enabled", False)):
            self.live_reload_watcher.clear()

        if updated_scan_options != current_scan_options:
            rules = get_all_rules()
            channel_rules = dict(rules.get(self.channel_name, {}) or {})
            channel_rules["scan_options"] = dict(updated_scan_options)
            rules[self.channel_name] = channel_rules
            save_all_rules(rules)
            self.sync_symbol_prefixed_visibility_action()

        self.schedule_settings_save()

        if (
            previous_symbol_hide != bool(updated_scan_options.get("hide_symbol_prefixed_titles", True))
        ):
            self.load_news(force_refresh=True)
            return

        if (
            previous_hide_previous != bool(self.settings.get("hide_previous_day_news", False))
            or previous_duplicate_mode != str(self.settings.get("main_duplicate_mode", "off"))
        ):
            self.apply_filters()
        if previous_spell_mode != self._current_spellcheck_mode():
            self._sync_spellcheck_menu_checks()

        self.status_label.setText("Ayarlar güncellendi")

    def open_code_filter(self):
        rules = get_channel_rules(self.channel_name)
        raw_codes = rules.get("news_codes", {})
        all_codes = {}
        if isinstance(raw_codes, dict):
            for code, label in raw_codes.items():
                visible_code = display_rule_code(code)
                if visible_code and visible_code not in all_codes:
                    all_codes[visible_code] = label

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
        self._push_global_undo_state()
        hide_previous = self.action_show_previous_day_news.isChecked()
        self.settings["hide_previous_day_news"] = hide_previous
        self.settings["show_previous_day_news"] = not hide_previous
        self.schedule_settings_save()
        self.apply_filters()

    def open_statistics_dialog(self):
        dialog = StatisticsDialog(self.channel_name, self)
        dialog.exec()
