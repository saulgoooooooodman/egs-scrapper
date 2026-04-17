from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QLineEdit,
    QCheckBox,
)

from core.rules_store import get_all_rules, save_all_rules


DEFAULT_CHANNELS = [
    "A NEWS",
    "A HABER",
    "ATV",
    "A SPOR",
    "A PARA",
]


class RulesManagerDialog(QDialog):
    def __init__(self, current_channel: str = "A NEWS", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kanal Kuralları")
        self.resize(860, 600)

        self.current_channel = current_channel
        self.rules_data = get_all_rules()

        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Kanal:"))

        self.channel_combo = QComboBox()
        self.channel_combo.addItems(self._available_channels())
        idx = self.channel_combo.findText(current_channel)
        if idx >= 0:
            self.channel_combo.setCurrentIndex(idx)
        self.channel_combo.currentTextChanged.connect(self.reload_channel)
        top_row.addWidget(self.channel_combo, 1)

        layout.addLayout(top_row)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Filtre:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Kod veya açıklama ara...")
        self.search_input.textChanged.connect(self.apply_filter)
        search_row.addWidget(self.search_input, 1)

        self.show_empty_checkbox = QCheckBox("Boş satırları göster")
        self.show_empty_checkbox.stateChanged.connect(self.apply_filter)
        search_row.addWidget(self.show_empty_checkbox)

        layout.addLayout(search_row)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Kod", "Açıklama"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()

        self.add_btn = QPushButton("Satır Ekle")
        self.add_btn.clicked.connect(self.add_row)
        btn_row.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Seçili Satırı Sil")
        self.delete_btn.clicked.connect(self.delete_selected_row)
        btn_row.addWidget(self.delete_btn)

        self.sort_btn = QPushButton("Koda Göre Sırala")
        self.sort_btn.clicked.connect(self.sort_rows)
        btn_row.addWidget(self.sort_btn)

        btn_row.addStretch(1)

        self.save_btn = QPushButton("Kaydet")
        self.save_btn.clicked.connect(self.save_rules)
        btn_row.addWidget(self.save_btn)

        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.close_btn)

        layout.addLayout(btn_row)
        self.reload_channel()

    def _available_channels(self):
        channels = set(DEFAULT_CHANNELS)
        channels.update(self.rules_data.keys())
        return sorted(channels)

    def _ensure_channel_container(self, channel: str):
        if channel not in self.rules_data or not isinstance(self.rules_data[channel], dict):
            self.rules_data[channel] = {"news_codes": {}}
            return

        current = self.rules_data[channel]
        if "news_codes" in current and isinstance(current["news_codes"], dict):
            return

        pairs = {}
        codes = current.get("codes")
        if isinstance(codes, dict):
            for code, config in codes.items():
                if not isinstance(code, str) or not code.strip():
                    continue

                if isinstance(config, dict):
                    label = str(config.get("label", "")).strip()
                elif isinstance(config, str):
                    label = config.strip()
                else:
                    label = ""

                if label:
                    pairs[code.strip()] = label

        if not pairs:
            pairs = {
                k: v for k, v in current.items()
                if isinstance(k, str) and isinstance(v, str)
            }

        current["news_codes"] = pairs

    def _get_channel_pairs(self, channel: str):
        self._ensure_channel_container(channel)
        return self.rules_data[channel].get("news_codes", {})

    def reload_channel(self):
        channel = self.channel_combo.currentText()
        pairs = self._get_channel_pairs(channel)

        self.table.setRowCount(0)
        for code, desc in sorted(pairs.items(), key=lambda x: x[0].lower()):
            self._append_table_row(code, desc)

        if self.table.rowCount() == 0:
            for _ in range(6):
                self._append_table_row("", "")

        self.apply_filter()

    def _append_table_row(self, code: str, desc: str):
        row = self.table.rowCount()
        self.table.insertRow(row)

        code_item = QTableWidgetItem(code)
        desc_item = QTableWidgetItem(desc)

        code_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        desc_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.table.setItem(row, 0, code_item)
        self.table.setItem(row, 1, desc_item)

    def add_row(self):
        self._append_table_row("", "")
        self.apply_filter()

    def delete_selected_row(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Bilgi", "Önce bir satır seç.")
            return
        self.table.removeRow(row)

    def sort_rows(self):
        rows = []
        for r in range(self.table.rowCount()):
            code = self.table.item(r, 0).text().strip() if self.table.item(r, 0) else ""
            desc = self.table.item(r, 1).text().strip() if self.table.item(r, 1) else ""
            rows.append((code, desc))

        rows.sort(key=lambda x: x[0].lower())

        self.table.setRowCount(0)
        for code, desc in rows:
            self._append_table_row(code, desc)

        self.apply_filter()

    def apply_filter(self):
        needle = self.search_input.text().strip().lower()
        show_empty = self.show_empty_checkbox.isChecked()

        for r in range(self.table.rowCount()):
            code = self.table.item(r, 0).text().strip() if self.table.item(r, 0) else ""
            desc = self.table.item(r, 1).text().strip() if self.table.item(r, 1) else ""

            empty = (not code and not desc)
            if empty and not show_empty:
                self.table.setRowHidden(r, True)
                continue

            if not needle:
                self.table.setRowHidden(r, False)
                continue

            matched = needle in code.lower() or needle in desc.lower()
            self.table.setRowHidden(r, not matched)

    def _collect_pairs_from_table(self):
        pairs = {}
        for r in range(self.table.rowCount()):
            code = self.table.item(r, 0).text().strip() if self.table.item(r, 0) else ""
            desc = self.table.item(r, 1).text().strip() if self.table.item(r, 1) else ""
            if code:
                pairs[code] = desc
        return pairs

    def save_rules(self):
        channel = self.channel_combo.currentText()
        self._ensure_channel_container(channel)
        pairs = self._collect_pairs_from_table()
        self.rules_data[channel]["news_codes"] = pairs

        existing_codes = self.rules_data[channel].get("codes")
        if isinstance(existing_codes, dict):
            rebuilt_codes = {}
            for code, label in pairs.items():
                existing = existing_codes.get(code, {})
                if not isinstance(existing, dict):
                    existing = {}

                updated = dict(existing)
                updated["label"] = label
                updated.setdefault("prepend_to_title", False)
                updated.setdefault("dedupe_prefix_words", [])
                rebuilt_codes[code] = updated

            self.rules_data[channel]["codes"] = rebuilt_codes

        try:
            save_all_rules(self.rules_data)
            QMessageBox.information(self, "Tamam", "Kanal kuralları kaydedildi.")
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Kayıt başarısız:\n{exc}")
