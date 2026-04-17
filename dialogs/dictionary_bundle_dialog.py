from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from dictionaries.dictionary_store import (
    load_common_dictionary,
    save_common_dictionary,
)


class DictionaryBundleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sözlük Paketi Yönet")
        self.resize(420, 160)

        layout = QVBoxLayout(self)

        self.export_btn = QPushButton("Ortak Sözlüğü Dışa Aktar")
        self.export_btn.clicked.connect(self.export_common_dictionary)
        layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("Ortak Sözlüğü İçe Aktar")
        self.import_btn.clicked.connect(self.import_common_dictionary)
        layout.addWidget(self.import_btn)

    def export_common_dictionary(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Sözlüğü dışa aktar",
            "common_dictionary_export.json",
            "JSON Files (*.json)"
        )
        if not path:
            return

        try:
            data = load_common_dictionary()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Tamam", "Sözlük dışa aktarıldı.")
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız:\n{exc}")

    def import_common_dictionary(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Sözlüğü içe aktar",
            "",
            "JSON Files (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Dosya sözlük yapısında değil.")
            save_common_dictionary(data)
            QMessageBox.information(self, "Tamam", "Sözlük içe aktarıldı.")
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"İçe aktarma başarısız:\n{exc}")