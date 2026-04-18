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
        find_label = QLabel("Bul:")
        find_label.setToolTip("Aranacak kelimeyi, ifadeyi veya regex desenini yaz.")
        row_find.addWidget(find_label)
        self.find_input = QLineEdit()
        self.find_input.setToolTip("Bulmak istediğin metni yaz. Regex açıksa bu alan desen olarak yorumlanır.")
        row_find.addWidget(self.find_input, 1)
        layout.addLayout(row_find)

        row_replace = QHBoxLayout()
        replace_label = QLabel("Değiştir:")
        replace_label.setToolTip("Bulunan metnin yerine yazılacak yeni ifadeyi gir.")
        row_replace.addWidget(replace_label)
        self.replace_input = QLineEdit()
        self.replace_input.setToolTip("Bulunan ifade bununla değiştirilir.")
        row_replace.addWidget(self.replace_input, 1)
        layout.addLayout(row_replace)

        row_scope = QHBoxLayout()
        scope_label = QLabel("Kapsam:")
        scope_label.setToolTip("Değiştirmenin hangi alanda uygulanacağını seç.")
        row_scope.addWidget(scope_label)
        self.scope_combo = QComboBox()
        for key, label in self.SCOPE_OPTIONS:
            self.scope_combo.addItem(label, key)
        self.scope_combo.currentIndexChanged.connect(self.on_scope_changed)
        self.scope_combo.setToolTip("Yalnızca önizleme, seçili haberler veya başlıklar gibi hedef alanı belirler.")
        row_scope.addWidget(self.scope_combo, 1)
        layout.addLayout(row_scope)

        self.regex_checkbox = QCheckBox("Regex kullan")
        self.regex_checkbox.setToolTip("İşaretlersen 'Bul' alanı normal metin yerine regex deseni olarak çalışır.")
        layout.addWidget(self.regex_checkbox)

        self.add_to_dictionary_checkbox = QCheckBox("Sözlüğe ekle")
        self.add_to_dictionary_checkbox.setToolTip("Başlık düzeltmelerinde yapılan değişikliği sözlüğe eklemek için işaretle.")
        layout.addWidget(self.add_to_dictionary_checkbox)

        self.scope_info = QLabel(
            f"Seçili: {selected_count} | Listelenen: {filtered_count} | Toplam: {total_count}"
        )
        self.scope_info.setToolTip("İşlemin etkileyebileceği haber sayısını özetler.")
        layout.addWidget(self.scope_info)

        self.preview = QTextEdit()
        self.preview.setPlainText(self._result_text)
        self.preview.setToolTip("Değişiklik uygulanınca ortaya çıkacak sonucu önizleme olarak gösterir.")
        layout.addWidget(self.preview, 1)

        buttons = QHBoxLayout()

        self.apply_btn = QPushButton("Önizlemeye Uygula")
        self.apply_btn.clicked.connect(self.apply_replace)
        self.apply_btn.setToolTip("Yazdığın bul/değiştir kuralını önce önizleme alanına uygular.")
        buttons.addWidget(self.apply_btn)

        self.ok_btn = QPushButton("Tamam")
        self.ok_btn.clicked.connect(self.accept_dialog)
        self.ok_btn.setToolTip("Önizlemedeki sonucu onaylayıp ana ekrana geri gönderir.")
        buttons.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setToolTip("Hiçbir değişikliği uygulamadan pencereyi kapatır.")
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
