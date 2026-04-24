from __future__ import annotations

import csv
import html
import os
import re
import subprocess
import sqlite3
from threading import Event

from PySide6.QtCore import QDate, Qt, QThread, Signal
from PySide6.QtGui import QAction, QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QMenu,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from data.database import search_archive
from core.settings_manager import load_settings, save_settings
from core.rules_store import get_channel_rules
from core.shell_utils import show_file_in_explorer
from dialogs.code_filter_wizard import CodeFilterWizardDialog
from ui.main_window_context_menus import show_readonly_text_context_menu


class ArchiveSearchWorker(QThread):
    results_ready = Signal(list, list)
    search_failed = Signal(str)
    search_cancelled = Signal()

    def __init__(
        self,
        channel_name: str,
        query: str,
        start_iso_date: str,
        end_iso_date: str,
        selected_codes: list[str],
        hide_mode: bool,
        use_regex: bool,
        scope: str,
        exact_match: bool,
        query_clauses: list[dict],
        editor_filters: list[str],
        parent=None,
    ):
        super().__init__(parent)
        self.channel_name = channel_name
        self.query = query
        self.start_iso_date = start_iso_date
        self.end_iso_date = end_iso_date
        self.selected_codes = selected_codes
        self.hide_mode = hide_mode
        self.use_regex = use_regex
        self.scope = scope
        self.exact_match = exact_match
        self.query_clauses = query_clauses
        self.editor_filters = editor_filters
        self._cancel_event = Event()

    def request_cancel(self):
        self._cancel_event.set()

    def run(self):
        try:
            search_errors = []
            results = search_archive(
                channel_name=self.channel_name,
                query=self.query,
                start_iso_date=self.start_iso_date,
                end_iso_date=self.end_iso_date,
                selected_codes=self.selected_codes,
                hide_mode=self.hide_mode,
                use_regex=self.use_regex,
                scope=self.scope,
                exact_match=self.exact_match,
                query_clauses=self.query_clauses,
                editor_filters=self.editor_filters,
                should_cancel=self._cancel_event.is_set,
                error_sink=search_errors,
            )
        except (sqlite3.Error, OSError, ValueError) as exc:
            self.search_failed.emit(str(exc))
            return

        if self._cancel_event.is_set():
            self.search_cancelled.emit()
            return

        self.results_ready.emit(results, search_errors)


class ArchiveSearchDialog(QDialog):
    def __init__(self, channel_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Arşiv Arama")
        self.resize(1040, 700)

        self.channel_name = channel_name
        self.results = []
        self.selected_codes = set()
        self.code_filter_hide_mode = False
        self.query_rows = []
        self.search_worker = None
        self._last_query_clauses = []
        self._settings = self._load_dialog_settings()

        layout = QVBoxLayout(self)
        parent_date = None
        if parent is not None and hasattr(parent, "date_edit"):
            try:
                parent_date = parent.date_edit.date()
            except RuntimeError:
                parent_date = None
        selected_date = parent_date if parent_date and parent_date.isValid() else QDate.currentDate()

        query_top = QHBoxLayout()
        query_top.addWidget(QLabel("Arama Satırları:"))

        self.scope_combo = QComboBox()
        self.scope_combo.addItem("Tümü", "all")
        self.scope_combo.addItem("Başlık", "title")
        self.scope_combo.addItem("Haber Metni", "body")
        self.scope_combo.addItem("Haber Kodu", "code")
        self.scope_combo.setToolTip("Arama satırlarındaki ifadenin hangi alanda aranacağını seç.")
        query_top.addWidget(self.scope_combo)

        self.regex_checkbox = QCheckBox("Regex")
        self.regex_checkbox.setToolTip("İşaretlersen arama satırları normal kelime yerine regex olarak yorumlanır.")
        query_top.addWidget(self.regex_checkbox)

        self.exact_checkbox = QCheckBox("Tam Eşleşme")
        self.exact_checkbox.setToolTip("İşaretlersen aranan ifade alanla birebir aynı olmalıdır.")
        query_top.addWidget(self.exact_checkbox)

        query_top.addStretch(1)

        self.search_btn = QPushButton("Ara")
        self.search_btn.setAutoDefault(False)
        self.search_btn.setDefault(False)
        self.search_btn.setToolTip("Seçilen tarih aralığında arşiv veritabanlarını tarar.")
        self.search_btn.clicked.connect(self.run_search)
        query_top.addWidget(self.search_btn)

        self.export_btn = QPushButton("Dışa Aktar")
        self.export_btn.setAutoDefault(False)
        self.export_btn.setDefault(False)
        self.export_btn.setEnabled(False)
        self.export_btn.setToolTip("Arşiv sonuçlarını CSV veya XLS olarak kaydeder.")
        self.export_btn.clicked.connect(self.export_results)
        query_top.addWidget(self.export_btn)

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setToolTip("Süren arşiv aramasını durdurur.")
        self.cancel_btn.clicked.connect(self.cancel_search)
        query_top.addWidget(self.cancel_btn)

        layout.addLayout(query_top)

        self.query_mode_helper = QLabel("Ayrı: en az biri bulunsun | Birlikte: mutlaka bulunsun | Hariç: bulunanları dışla")
        self.query_mode_helper.setWordWrap(True)
        self.query_mode_helper.setToolTip("Birden fazla arama satırını birlikte kullanırken her satırın davranışını açıklar.")
        layout.addWidget(self.query_mode_helper)

        self.query_rows_container = QWidget()
        self.query_rows_layout = QVBoxLayout(self.query_rows_container)
        self.query_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.query_rows_layout.setSpacing(4)
        layout.addWidget(self.query_rows_container)

        self.add_query_row(mode="any")

        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Başlangıç:"))

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.start_date.setDate(selected_date)
        self.start_date.setToolTip("Arşiv aramanın başlangıç tarihini seç.")
        date_row.addWidget(self.start_date)

        date_row.addWidget(QLabel("Bitiş:"))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.setDate(selected_date)
        self.end_date.setToolTip("Arşiv aramanın bitiş tarihini seç.")
        date_row.addWidget(self.end_date)

        self.code_filter_btn = QPushButton("Kod Filtreleri...")
        self.code_filter_btn.setAutoDefault(False)
        self.code_filter_btn.setDefault(False)
        self.code_filter_btn.setToolTip("Belirli haber kodlarını göster veya gizle.")
        self.code_filter_btn.clicked.connect(self.open_code_filter)
        date_row.addWidget(self.code_filter_btn)

        self.code_filter_label = QLabel("Kod filtresi: Yok")
        self.code_filter_label.setWordWrap(True)
        self.code_filter_label.setToolTip("Seçili haber kodu filtresinin özetini gösterir.")
        date_row.addWidget(self.code_filter_label, 1)

        layout.addLayout(date_row)

        editor_row = QHBoxLayout()
        editor_row.addWidget(QLabel("Editör Filtresi:"))

        self.editor_filter_input = QLineEdit()
        self.editor_filter_input.setPlaceholderText("Virgülle editör yaz... örn: BURHAN AYTEKIN, METIN ALGUL")
        self.editor_filter_input.setToolTip(
            "Arşiv sonuçlarını editör adına göre süzer. "
            "Birden fazla editörü virgülle ayırabilirsin; herhangi biri eşleşirse kayıt gösterilir."
        )
        self.editor_filter_input.returnPressed.connect(self.run_search)
        editor_row.addWidget(self.editor_filter_input, 1)

        layout.addLayout(editor_row)

        self.result_info_label = QLabel("Hazır")
        self.result_info_label.setToolTip("Arşiv aramasının mevcut durumunu ve sonuç bilgisini gösterir.")
        layout.addWidget(self.result_info_label)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Tarih", "Kod", "Başlık", "Editör", "Kaynak", "Önizleme"])
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionsMovable(True)
        for column in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(column, QHeaderView.Interactive)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_results_context_menu)
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self.show_header_context_menu)
        self.table.horizontalHeader().sectionResized.connect(lambda *_: self._save_table_preferences())
        self.table.horizontalHeader().sectionMoved.connect(lambda *_: self._save_table_preferences())
        self.table.setToolTip("Arşiv arama sonuçları. Bir satır seçtiğinde alt bölümde tam önizleme açılır.")
        layout.addWidget(self.table, 1)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setToolTip("Seçili arşiv kaydının tam metin önizlemesi.")
        self.preview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.preview.customContextMenuRequested.connect(
            lambda pos: show_readonly_text_context_menu(self.preview, pos, self)
        )
        layout.addWidget(self.preview, 1)

        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet("padding:4px 6px; border-top:1px solid #cbd5e1; color:#334155;")
        layout.addWidget(self.status_label)

        self._update_code_filter_label()
        self._refresh_query_row_buttons()
        self._apply_table_preferences()

    def _set_search_state(self, is_running: bool, message: str):
        self.search_btn.setEnabled(not is_running)
        self.search_btn.setText("Aranıyor..." if is_running else "Ara")
        self.cancel_btn.setEnabled(is_running)
        self.result_info_label.setText(message)
        self.status_label.setText(message)

    def _load_dialog_settings(self) -> dict:
        parent = self.parent()
        if parent is not None and hasattr(parent, "settings"):
            return parent.settings
        return load_settings()

    def _persist_dialog_settings(self):
        parent = self.parent()
        if parent is not None and hasattr(parent, "schedule_settings_save"):
            parent.schedule_settings_save()
        else:
            save_settings(self._settings)

    def _save_table_preferences(self):
        self._settings["archive_table_widths"] = [
            int(self.table.columnWidth(column))
            for column in range(self.table.columnCount())
        ]
        self._settings["archive_table_hidden_columns"] = [
            column
            for column in range(self.table.columnCount())
            if self.table.isColumnHidden(column)
        ]
        self._persist_dialog_settings()

    def _apply_table_preferences(self):
        default_widths = [110, 90, 320, 180, 150, 260]
        widths = self._settings.get("archive_table_widths", default_widths)
        if not isinstance(widths, list):
            widths = default_widths
        for column in range(self.table.columnCount()):
            width = widths[column] if column < len(widths) else default_widths[min(column, len(default_widths) - 1)]
            self.table.setColumnWidth(column, int(width))

        hidden = self._settings.get("archive_table_hidden_columns", [])
        if not isinstance(hidden, list):
            hidden = []
        for column in range(self.table.columnCount()):
            self.table.setColumnHidden(column, column in hidden)

    def show_header_context_menu(self, pos):
        menu = QMenu(self)
        for column, label in enumerate(["Tarih", "Kod", "Başlık", "Editör", "Kaynak", "Önizleme"]):
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(not self.table.isColumnHidden(column))
            action.toggled.connect(lambda checked, col=column: self._set_column_visible(col, checked))
            menu.addAction(action)
        menu.exec(self.table.horizontalHeader().viewport().mapToGlobal(pos))

    def _set_column_visible(self, column: int, visible: bool):
        self.table.setColumnHidden(column, not visible)
        self._save_table_preferences()

    def _cleanup_search_worker(self):
        worker = self.search_worker
        self.search_worker = None
        if worker is None:
            return
        worker.deleteLater()

    def cancel_search(self):
        if self.search_worker is None:
            return
        self.search_worker.request_cancel()
        self._set_search_state(True, "İptal isteği gönderildi...")

    def add_query_row(self, mode="any", text=""):
        row_widget = QWidget(self)
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(6)

        mode_combo = QComboBox()
        mode_combo.addItem("Ayrı", "any")
        mode_combo.addItem("Birlikte", "must")
        mode_combo.addItem("Hariç", "exclude")
        mode_index = max(0, mode_combo.findData(mode))
        mode_combo.setCurrentIndex(mode_index)
        row_layout.addWidget(mode_combo)

        input_box = QLineEdit()
        input_box.setPlaceholderText("Aranacak kelime ya da ifade...")
        input_box.setText(text)
        input_box.returnPressed.connect(lambda box=input_box: self._run_search_from_query_input(box))
        input_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row_layout.addWidget(input_box, 1)

        add_btn = QPushButton("+")
        add_btn.setFixedWidth(32)
        add_btn.setAutoDefault(False)
        add_btn.setDefault(False)
        add_btn.clicked.connect(lambda: self.add_query_row())
        row_layout.addWidget(add_btn)

        remove_btn = QPushButton("-")
        remove_btn.setFixedWidth(32)
        remove_btn.setAutoDefault(False)
        remove_btn.setDefault(False)
        remove_btn.clicked.connect(lambda: self.remove_query_row(row_widget))
        row_layout.addWidget(remove_btn)

        row_data = {
            "widget": row_widget,
            "mode_combo": mode_combo,
            "input": input_box,
            "add_btn": add_btn,
            "remove_btn": remove_btn,
        }
        self.query_rows.append(row_data)
        self.query_rows_layout.addWidget(row_widget)
        self._refresh_query_row_buttons()
        input_box.setFocus()

    def _run_search_from_query_input(self, input_box: QLineEdit):
        if not input_box.text().strip():
            return
        self.run_search()

    def _format_display_date(self, iso_date: str) -> str:
        parsed = QDate.fromString(str(iso_date or "").strip(), "yyyy-MM-dd")
        if parsed.isValid():
            return parsed.toString("dd.MM.yyyy")
        return str(iso_date or "")

    def _format_editors(self, editors: str) -> str:
        cleaned = [part.strip() for part in re.split(r"[\n,;]+", str(editors or "")) if part.strip()]
        return ", ".join(cleaned)

    def _selected_result(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.results):
            return None
        return self.results[row]

    def _build_result_copy_text(self, result) -> str:
        header_parts = [
            self._format_display_date(result.iso_date),
            result.news_code or "",
            result.title or "",
        ]
        editors = self._format_editors(result.editors)
        if editors:
            header_parts.append(f"Editör: {editors}")
        if result.source_name:
            header_parts.append(result.source_name)
        header = " | ".join(part for part in header_parts if part)
        return f"{header}\n\n{result.final_text or ''}".strip()

    def copy_selected_result(self):
        result = self._selected_result()
        if result is None:
            return
        text = self._build_result_copy_text(result)
        if not text:
            return
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def go_to_selected_date(self):
        result = self._selected_result()
        if result is None:
            return
        host = self.parent()
        if host is None or not hasattr(host, "date_edit"):
            QMessageBox.information(self, "Bilgi", "Ana pencereye tarih aktarilamadi.")
            return
        target_date = QDate.fromString(str(result.iso_date or "").strip(), "yyyy-MM-dd")
        if not target_date.isValid():
            QMessageBox.information(self, "Bilgi", "Kaydin tarihi okunamadi.")
            return
        host.date_edit.setDate(target_date)
        if hasattr(host, "raise_"):
            host.raise_()
        if hasattr(host, "activateWindow"):
            host.activateWindow()

    def show_selected_source_in_folder(self):
        result = self._selected_result()
        if result is None:
            return
        source_path = os.path.normpath(str(result.path or "").strip())
        if not source_path:
            QMessageBox.information(self, "Bilgi", "Kaynak dosya yolu bulunamadi.")
            return
        if not os.path.exists(source_path):
            QMessageBox.warning(self, "Uyarı", f"Dosya bulunamadi:\n{source_path}")
            return
        try:
            show_file_in_explorer(source_path)
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            QMessageBox.critical(self, "Hata", f"Kaynak klasör açılamadi:\n{exc}")

    def show_results_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if index.isValid():
            self.table.selectRow(index.row())
        result = self._selected_result()
        if result is None:
            return

        menu = QMenu(self)

        copy_action = QAction("Kopyala", self)
        copy_action.triggered.connect(self.copy_selected_result)
        menu.addAction(copy_action)

        goto_action = QAction("Tarihe Git", self)
        goto_action.triggered.connect(self.go_to_selected_date)
        menu.addAction(goto_action)

        open_source_action = QAction("Kaynağı Klasörde Göster", self)
        open_source_action.triggered.connect(self.show_selected_source_in_folder)
        menu.addAction(open_source_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def remove_query_row(self, widget):
        if len(self.query_rows) <= 1:
            return

        for index, row_data in enumerate(list(self.query_rows)):
            if row_data["widget"] is widget:
                self.query_rows.pop(index)
                row_data["widget"].deleteLater()
                break

        self._refresh_query_row_buttons()

    def _refresh_query_row_buttons(self):
        total = len(self.query_rows)
        show_modes = total > 1
        self.query_mode_helper.setVisible(show_modes)
        for index, row_data in enumerate(self.query_rows):
            row_data["remove_btn"].setEnabled(total > 1)
            row_data["add_btn"].setVisible(index == total - 1)
            row_data["mode_combo"].setVisible(show_modes and index > 0)

    def _collect_query_clauses(self):
        clauses = []
        single_row = len(self.query_rows) <= 1
        for row_data in self.query_rows:
            text = row_data["input"].text().strip()
            if not text:
                continue
            clauses.append({
                "mode": "any" if single_row else (row_data["mode_combo"].currentData() or "any"),
                "scope": self.scope_combo.currentData() or "all",
                "text": text,
            })
        return clauses

    def _update_code_filter_label(self):
        if not self.selected_codes:
            self.code_filter_label.setText("Kod filtresi: Yok")
            return

        mode = "Gizle" if self.code_filter_hide_mode else "Göster"
        codes = ", ".join(sorted(self.selected_codes))
        self.code_filter_label.setText(f"Kod filtresi: {mode} ({codes})")

    def open_code_filter(self):
        start_date = self.start_date.date()
        end_date = self.end_date.date()
        if start_date > end_date:
            QMessageBox.warning(self, "Uyarı", "Başlangıç tarihi bitiş tarihinden büyük olamaz.")
            return

        rules = get_channel_rules(self.channel_name)
        codes = rules.get("news_codes", {})
        if not codes:
            QMessageBox.information(
                self,
                "Bilgi",
                "Bu kanal için tanımlı haber kodu yok. Gerekirse önce Kanal Kuralları ekranından ekle."
            )
            return

        dialog = CodeFilterWizardDialog(
            codes,
            self.selected_codes,
            hide_mode=self.code_filter_hide_mode,
            parent=self,
        )
        if dialog.exec():
            self.selected_codes = set(dialog.get_selected_codes())
            self.code_filter_hide_mode = dialog.is_hide_mode()
            self._update_code_filter_label()
            if self._collect_query_clauses():
                self.run_search()

    def run_search(self):
        if self.search_worker is not None:
            return

        clauses = self._collect_query_clauses()
        if not clauses:
            QMessageBox.information(self, "Bilgi", "En az bir arama satırı doldur.")
            return

        start_date = self.start_date.date()
        end_date = self.end_date.date()
        if start_date > end_date:
            QMessageBox.warning(self, "Uyarı", "Başlangıç tarihi bitiş tarihinden büyük olamaz.")
            return

        if self.regex_checkbox.isChecked():
            for clause in clauses:
                try:
                    re.compile(clause["text"], re.IGNORECASE)
                except re.error as exc:
                    QMessageBox.warning(self, "Regex", f"Geçersiz regex:\n{exc}")
                    return

        self.table.setRowCount(0)
        self.preview.clear()
        self._last_query_clauses = list(clauses)
        self.export_btn.setEnabled(False)
        self._set_search_state(True, "Arşiv aranıyor...")

        self.search_worker = ArchiveSearchWorker(
            self.channel_name,
            clauses[0]["text"],
            start_date.toString("yyyy-MM-dd"),
            end_date.toString("yyyy-MM-dd"),
            sorted(self.selected_codes),
            self.code_filter_hide_mode,
            self.regex_checkbox.isChecked(),
            self.scope_combo.currentData() or "all",
            self.exact_checkbox.isChecked(),
            clauses,
            [part.strip() for part in self.editor_filter_input.text().split(",") if part.strip()],
            self,
        )
        self.search_worker.results_ready.connect(self._on_search_results_ready)
        self.search_worker.search_failed.connect(self._on_search_failed)
        self.search_worker.search_cancelled.connect(self._on_search_cancelled)
        self.search_worker.finished.connect(self._cleanup_search_worker)
        self.search_worker.start()

    def _show_search_warnings(self, errors):
        if not errors:
            return

        summary = f"{len(errors)} veritabani aramada hata verdi."
        details = []
        for item in errors:
            details.append(
                f"[{item.get('source_name', 'Bilinmeyen kaynak')}] "
                f"{item.get('db_path', '')}\n{item.get('message', '')}"
            )

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Arşiv Arama Uyarisi")
        dialog.setIcon(QMessageBox.Warning)
        dialog.setText(
            summary + "\n\nArama diger veritabanlarinda devam etti. Ayrinti icin loglara da bakabilirsin."
        )
        dialog.setDetailedText("\n\n".join(details[:20]))
        dialog.exec()

    def _on_search_results_ready(self, results, errors):
        self.results = list(results or [])
        self.table.setRowCount(0)

        for row_index, row_data in enumerate(self.results):
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QTableWidgetItem(self._format_display_date(row_data.iso_date)))
            self.table.setItem(row_index, 1, QTableWidgetItem(row_data.news_code or ""))
            self.table.setItem(row_index, 2, QTableWidgetItem(row_data.title or ""))
            self.table.setItem(row_index, 3, QTableWidgetItem(self._format_editors(row_data.editors)))
            self.table.setItem(row_index, 4, QTableWidgetItem(row_data.source_name or ""))
            self.table.setItem(row_index, 5, QTableWidgetItem((row_data.final_text or "")[:140]))
            self._apply_result_row_highlights(row_index, row_data)

        if self.results:
            self.table.selectRow(0)
            status = f"{len(self.results)} sonuç bulundu."
        else:
            self.preview.clear()
            status = "Sonuç bulunamadı."

        if errors:
            status += f" {len(errors)} veritabani hata verdi."

        self._set_search_state(False, status)
        self.export_btn.setEnabled(bool(self.results))
        self._show_search_warnings(errors)
        self._save_table_preferences()

    def _on_search_failed(self, message: str):
        self.results = []
        self.table.setRowCount(0)
        self.preview.clear()
        self.export_btn.setEnabled(False)
        self._set_search_state(False, "Arama başarısız.")
        QMessageBox.critical(self, "Hata", f"Arama başarısız:\n{message}")

    def _on_search_cancelled(self):
        self.results = []
        self.table.setRowCount(0)
        self.preview.clear()
        self.export_btn.setEnabled(False)
        self._set_search_state(False, "Arama iptal edildi.")

    def on_selection_changed(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.results):
            self.preview.clear()
            self.preview.setExtraSelections([])
            return

        header = " | ".join(
            part for part in [
                self._format_display_date(self.results[row].iso_date),
                self.results[row].news_code or "",
                self.results[row].title or "",
                f"Editör: {self._format_editors(self.results[row].editors)}" if self._format_editors(self.results[row].editors) else "",
                self.results[row].source_name or "",
            ] if part
        )
        text = f"{header}\n\n{self.results[row].final_text or ''}"
        self.preview.setPlainText(text)
        self._apply_preview_highlights()

    def _plain_highlight_clauses(self) -> list[dict]:
        return [
            clause
            for clause in (self._last_query_clauses or [])
            if str(clause.get("text", "") or "").strip()
        ]

    def _text_matches_clause(self, text: str, clause: dict) -> bool:
        value = str(text or "")
        pattern = str(clause.get("text", "") or "").strip()
        if not value or not pattern:
            return False

        if self.regex_checkbox.isChecked():
            try:
                return bool(re.search(pattern, value, re.IGNORECASE))
            except re.error:
                return False

        from core.text_utils import normalize_search_text

        haystack = normalize_search_text(value)
        needle = normalize_search_text(pattern)
        if not haystack or not needle:
            return False
        if self.exact_checkbox.isChecked():
            return haystack == needle
        return needle in haystack

    def _apply_result_row_highlights(self, row_index: int, row_data):
        values = {
            0: self._format_display_date(row_data.iso_date),
            1: row_data.news_code or "",
            2: row_data.title or "",
            3: self._format_editors(row_data.editors),
            4: row_data.source_name or "",
            5: (row_data.final_text or "")[:140],
        }
        highlight_color = QColor("#FFF3A3")
        for clause in self._plain_highlight_clauses():
            for column, value in values.items():
                if not self._text_matches_clause(value, clause):
                    continue
                item = self.table.item(row_index, column)
                if item is not None:
                    item.setBackground(highlight_color)

    def _apply_preview_highlights(self):
        selections = []
        text = self.preview.toPlainText()
        if not text:
            self.preview.setExtraSelections(selections)
            return

        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#FFF3A3"))

        for clause in self._plain_highlight_clauses():
            pattern = str(clause.get("text", "") or "").strip()
            if not pattern:
                continue
            if self.regex_checkbox.isChecked():
                try:
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                except re.error:
                    matches = []
            else:
                matches = list(re.finditer(re.escape(pattern), text, re.IGNORECASE))

            for match in matches:
                cursor = self.preview.textCursor()
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.KeepAnchor)
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.format = highlight_format
                selections.append(selection)

        self.preview.setExtraSelections(selections)

    def export_results(self):
        if not self.results:
            QMessageBox.information(self, "Dışa Aktar", "Önce arama sonucu oluştur.")
            return

        default_name = f"arsiv_arama_{QDate.currentDate().toString('yyyyMMdd')}"
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Arşiv Sonuçlarını Dışa Aktar",
            default_name,
            "CSV Dosyası (*.csv);;Excel Dosyası (*.xls)",
        )
        if not file_path:
            return

        headers = ["Tarih", "Kod", "Başlık", "Editör", "Kaynak", "Önizleme"]
        rows = [
            [
                self._format_display_date(result.iso_date),
                result.news_code or "",
                result.title or "",
                self._format_editors(result.editors),
                result.source_name or "",
                result.final_text or "",
            ]
            for result in self.results
        ]

        try:
            if file_path.lower().endswith(".xls") or "xls" in selected_filter.lower():
                self._export_results_xls(file_path, headers, rows)
            else:
                self._export_results_csv(file_path, headers, rows)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, "Dışa Aktar", f"Dışa aktarma başarısız:\n{exc}")
            return

        self.status_label.setText(f"Sonuçlar dışa aktarıldı: {file_path}")

    def _export_results_csv(self, file_path: str, headers: list[str], rows: list[list[str]]):
        export_path = file_path if file_path.lower().endswith(".csv") else f"{file_path}.csv"
        with open(export_path, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)

    def _export_results_xls(self, file_path: str, headers: list[str], rows: list[list[str]]):
        export_path = file_path if file_path.lower().endswith(".xls") else f"{file_path}.xls"
        table_headers = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
        table_rows = []
        for row in rows:
            cells = "".join(f"<td>{html.escape(str(value or ''))}</td>" for value in row)
            table_rows.append(f"<tr>{cells}</tr>")

        content = (
            "<html><head><meta charset='utf-8'></head><body>"
            "<table border='1'>"
            f"<thead><tr>{table_headers}</tr></thead>"
            f"<tbody>{''.join(table_rows)}</tbody>"
            "</table></body></html>"
        )
        with open(export_path, "w", encoding="utf-8") as handle:
            handle.write(content)

    def accept(self):
        self._save_table_preferences()
        super().accept()

    def reject(self):
        self._save_table_preferences()
        super().reject()
