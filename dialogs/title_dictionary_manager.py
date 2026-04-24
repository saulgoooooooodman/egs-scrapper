from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from dictionaries.dictionary_store import load_channel_dictionary, save_channel_dictionary


class TitleDictionaryManagerDialog(QDialog):
    def __init__(self, channel_name: str, parent=None):
        super().__init__(parent)
        self.resize(820, 620)

        self.channel_name = channel_name
        self._dirty = False
        self._loading_table = False

        layout = QVBoxLayout(self)

        info_label = QLabel(f"Bu pencere yalnızca `{channel_name}` kanalının başlık sözlüğünü düzenler.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        form = QHBoxLayout()
        wrong_label = QLabel("Yanlış:")
        form.addWidget(wrong_label)
        self.wrong_input = QLineEdit()
        form.addWidget(self.wrong_input, 1)

        correct_label = QLabel("Doğru:")
        form.addWidget(correct_label)
        self.correct_input = QLineEdit()
        form.addWidget(self.correct_input, 1)

        self.add_btn = QPushButton("Ekle")
        self.add_btn.clicked.connect(self.add_entry)
        form.addWidget(self.add_btn)
        layout.addLayout(form)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Yanlış", "Doğru"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        self.delete_btn = QPushButton("Seçileni Sil")
        self.delete_btn.clicked.connect(self.delete_selected)
        actions.addWidget(self.delete_btn)

        self.save_btn = QPushButton("Kaydet")
        self.save_btn.clicked.connect(self.save_data)
        actions.addWidget(self.save_btn)

        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.accept)
        actions.addWidget(self.close_btn)

        actions.addStretch(1)
        layout.addLayout(actions)

        self.reload_data()

    def _update_window_title(self):
        title = f"Başlık Sözlüğü - {self.channel_name}"
        if self._dirty:
            title += " *"
        self.setWindowTitle(title)

    def _set_dirty(self, value: bool):
        self._dirty = bool(value)
        self._update_window_title()

    def _on_item_changed(self, item):
        if self._loading_table:
            return
        self._set_dirty(True)

    def _collect_table_data(self) -> dict[str, str]:
        data = {}
        for row in range(self.table.rowCount()):
            wrong = self.table.item(row, 0).text().strip() if self.table.item(row, 0) else ""
            correct = self.table.item(row, 1).text().strip() if self.table.item(row, 1) else ""
            if wrong:
                data[wrong] = correct
        return data

    def _save_scope(self, *, show_message: bool) -> bool:
        try:
            save_channel_dictionary(self.channel_name, self._collect_table_data())
        except (OSError, TypeError, ValueError) as exc:
            QMessageBox.critical(self, "Hata", f"Sözlük kaydedilemedi:\n{exc}")
            return False

        self._set_dirty(False)
        if show_message:
            QMessageBox.information(self, "Tamam", "Sözlük kaydedildi.")
        return True

    def _maybe_save_before_close(self) -> bool:
        if not self._dirty:
            return True
        return self._save_scope(show_message=False)

    def reload_data(self):
        data = load_channel_dictionary(self.channel_name)
        self._loading_table = True
        try:
            self.table.setRowCount(0)
            for row, (wrong, correct) in enumerate(sorted(data.items(), key=lambda item: item[0].lower())):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(wrong))
                self.table.setItem(row, 1, QTableWidgetItem(correct))
        finally:
            self._loading_table = False

        self._set_dirty(False)

    def add_entry(self):
        wrong = self.wrong_input.text().strip().upper()
        correct = self.correct_input.text().strip()

        if not wrong or not correct:
            QMessageBox.information(self, "Bilgi", "Her iki alanı da doldur.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(wrong))
        self.table.setItem(row, 1, QTableWidgetItem(correct))

        self.wrong_input.clear()
        self.correct_input.clear()
        self._set_dirty(True)

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Bilgi", "Önce bir satır seç.")
            return
        self.table.removeRow(row)
        self._set_dirty(True)

    def save_data(self):
        self._save_scope(show_message=True)

    def accept(self):
        if not self._maybe_save_before_close():
            return
        super().accept()

    def reject(self):
        if not self._maybe_save_before_close():
            return
        super().reject()
