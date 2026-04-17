from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QCheckBox,
    QMessageBox,
)


class FindReplaceDialog(QDialog):
    SCOPE_OPTIONS = [
        ("preview_text", "Önizleme Metni"),
        ("selected_text", "Seçili Haber Metinleri"),
        ("filtered_text", "Listelenen Haber Metinleri"),
        ("current_title", "Geçerli Haber Başlığı"),
        ("selected_title", "Seçili Haber Başlıkları"),
        ("all_titles", "Tüm Haber Başlıkları"),
    ]

    def __init__(self, scope_samples: dict[str, str], channel_name: str, parent=None, selected_count: int = 0, filtered_count: int = 0, total_count: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Bul / Değiştir")
        self.resize(760, 560)

        self.channel_name = channel_name
        self.scope_samples = {key: str(value or "") for key, value in (scope_samples or {}).items()}
        default_scope = self.SCOPE_OPTIONS[0][0]
        self._result_text = self.scope_samples.get(default_scope, "")
        self._original_text = self._result_text

        layout = QVBoxLayout(self)

        row_find = QHBoxLayout()
        row_find.addWidget(QLabel("Bul:"))
        self.find_input = QLineEdit()
        row_find.addWidget(self.find_input, 1)
        layout.addLayout(row_find)

        row_replace = QHBoxLayout()
        row_replace.addWidget(QLabel("Değiştir:"))
        self.replace_input = QLineEdit()
        row_replace.addWidget(self.replace_input, 1)
        layout.addLayout(row_replace)

        row_scope = QHBoxLayout()
        row_scope.addWidget(QLabel("Kapsam:"))
        self.scope_combo = QComboBox()
        for key, label in self.SCOPE_OPTIONS:
            self.scope_combo.addItem(label, key)
        self.scope_combo.currentIndexChanged.connect(self.on_scope_changed)
        row_scope.addWidget(self.scope_combo, 1)
        layout.addLayout(row_scope)

        self.regex_checkbox = QCheckBox("Regex kullan")
        layout.addWidget(self.regex_checkbox)

        self.add_to_dictionary_checkbox = QCheckBox("Sözlüğe ekle")
        layout.addWidget(self.add_to_dictionary_checkbox)

        self.scope_info = QLabel(
            f"Seçili: {selected_count} | Listelenen: {filtered_count} | Toplam: {total_count}"
        )
        layout.addWidget(self.scope_info)

        self.preview = QTextEdit()
        self.preview.setPlainText(self._result_text)
        layout.addWidget(self.preview, 1)

        buttons = QHBoxLayout()

        self.apply_btn = QPushButton("Önizlemeye Uygula")
        self.apply_btn.clicked.connect(self.apply_replace)
        buttons.addWidget(self.apply_btn)

        self.ok_btn = QPushButton("Tamam")
        self.ok_btn.clicked.connect(self.accept_dialog)
        buttons.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)

        buttons.addStretch(1)
        layout.addLayout(buttons)

    def on_scope_changed(self):
        scope = self.get_scope()
        self._original_text = self.scope_samples.get(scope, "")
        self.preview.setPlainText(self._original_text)

    def apply_replace(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()

        if not find_text:
            QMessageBox.information(self, "Bilgi", "Bul alanı boş olamaz.")
            return False

        import re

        text = self._original_text
        if self.regex_checkbox.isChecked():
            try:
                text = re.sub(find_text, replace_text, text, flags=re.IGNORECASE)
            except re.error as exc:
                QMessageBox.warning(self, "Regex", f"Geçersiz regex:\n{exc}")
                return False
        else:
            text = text.replace(find_text, replace_text)

        self.preview.setPlainText(text)
        return True

    def accept_dialog(self):
        if self.find_input.text():
            if not self.apply_replace():
                return
        self._result_text = self.preview.toPlainText()
        self.accept()

    def get_result_text(self) -> str:
        return self._result_text

    def get_scope(self) -> str:
        return self.scope_combo.currentData() or "preview_text"

    def get_find_text(self) -> str:
        return self.find_input.text()

    def get_replace_text(self) -> str:
        return self.replace_input.text()

    def use_regex(self) -> bool:
        return self.regex_checkbox.isChecked()

    def should_add_to_dictionary(self) -> bool:
        return self.add_to_dictionary_checkbox.isChecked()
