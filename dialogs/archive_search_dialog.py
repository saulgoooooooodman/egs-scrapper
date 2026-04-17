from __future__ import annotations

import re

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from data.database import search_archive
from core.rules_store import get_channel_rules
from dialogs.code_filter_wizard import CodeFilterWizardDialog
from ui.main_window_context_menus import show_readonly_text_context_menu


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

        layout = QVBoxLayout(self)

        query_top = QHBoxLayout()
        query_top.addWidget(QLabel("Arama Satırları:"))

        self.scope_combo = QComboBox()
        self.scope_combo.addItem("Tümü", "all")
        self.scope_combo.addItem("Başlık", "title")
        self.scope_combo.addItem("Haber Metni", "body")
        self.scope_combo.addItem("Haber Kodu", "code")
        query_top.addWidget(self.scope_combo)

        self.regex_checkbox = QCheckBox("Regex")
        query_top.addWidget(self.regex_checkbox)

        self.exact_checkbox = QCheckBox("Tam Eşleşme")
        query_top.addWidget(self.exact_checkbox)

        query_top.addStretch(1)

        self.search_btn = QPushButton("Ara")
        self.search_btn.clicked.connect(self.run_search)
        query_top.addWidget(self.search_btn)

        layout.addLayout(query_top)

        helper = QLabel("Ayrı: en az biri bulunsun | Birlikte: mutlaka bulunsun | Hariç: bulunanları dışla")
        helper.setWordWrap(True)
        layout.addWidget(helper)

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
        self.start_date.setDate(QDate(2000, 1, 1))
        date_row.addWidget(self.start_date)

        date_row.addWidget(QLabel("Bitiş:"))

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.setDate(QDate.currentDate())
        date_row.addWidget(self.end_date)

        self.code_filter_btn = QPushButton("Kod Filtreleri...")
        self.code_filter_btn.clicked.connect(self.open_code_filter)
        date_row.addWidget(self.code_filter_btn)

        self.code_filter_label = QLabel("Kod filtresi: Yok")
        self.code_filter_label.setWordWrap(True)
        date_row.addWidget(self.code_filter_label, 1)

        layout.addLayout(date_row)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Tarih", "Kod", "Başlık", "Kaynak", "Önizleme"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table, 1)

        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setContextMenuPolicy(Qt.CustomContextMenu)
        self.preview.customContextMenuRequested.connect(
            lambda pos: show_readonly_text_context_menu(self.preview, pos, self)
        )
        layout.addWidget(self.preview, 1)

        self._update_code_filter_label()

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
        input_box.returnPressed.connect(self.run_search)
        input_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row_layout.addWidget(input_box, 1)

        add_btn = QPushButton("+")
        add_btn.setFixedWidth(32)
        add_btn.clicked.connect(lambda: self.add_query_row())
        row_layout.addWidget(add_btn)

        remove_btn = QPushButton("-")
        remove_btn.setFixedWidth(32)
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
        for index, row_data in enumerate(self.query_rows):
            row_data["remove_btn"].setEnabled(total > 1)
            row_data["add_btn"].setVisible(index == total - 1)

    def _collect_query_clauses(self):
        clauses = []
        for row_data in self.query_rows:
            text = row_data["input"].text().strip()
            if not text:
                continue
            clauses.append({
                "mode": row_data["mode_combo"].currentData() or "any",
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

        try:
            self.results = search_archive(
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
            )
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Arama başarısız:\n{exc}")
            return

        self.table.setRowCount(0)

        for row_index, row_data in enumerate(self.results):
            news_code, title, final_text, iso_date, source_name = row_data
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QTableWidgetItem(iso_date or ""))
            self.table.setItem(row_index, 1, QTableWidgetItem(news_code or ""))
            self.table.setItem(row_index, 2, QTableWidgetItem(title or ""))
            self.table.setItem(row_index, 3, QTableWidgetItem(source_name or ""))
            self.table.setItem(row_index, 4, QTableWidgetItem((final_text or "")[:140]))

        if self.results:
            self.table.selectRow(0)
        else:
            self.preview.clear()

    def on_selection_changed(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.results):
            self.preview.clear()
            return

        news_code, title, final_text, iso_date, source_name = self.results[row]
        header = " | ".join(
            part for part in [iso_date or "", news_code or "", title or "", source_name or ""] if part
        )
        text = f"{header}\n\n{final_text or ''}"
        self.preview.setPlainText(text)
