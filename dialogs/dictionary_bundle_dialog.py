from __future__ import annotations

import json

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QLabel,
)

from dictionaries.dictionary_store import (
    load_channel_dictionary,
    save_channel_dictionary,
)


class DictionaryBundleDialog(QDialog):
    def __init__(self, channel_name: str, parent=None):
        super().__init__(parent)
        self.channel_name = channel_name
        self.setWindowTitle("Sözlük Paketini Yönet")
        self.resize(460, 190)

        layout = QVBoxLayout(self)

        info = QLabel(
            f"`{channel_name}` kanal sözlüğünü başka kullanıcılara göndermek veya "
            "gelen bir sözlük paketini bu kanala eklemek için bu pencereyi kullan."
        )
        info.setWordWrap(True)
        info.setToolTip(
            "Dışa aktarma JSON dosyası üretir. İçe aktarma ise dosyadaki kayıtları "
            "mevcut kanal sözlüğüne ekler; var olan eşleşmeler korunarak gerekirse güncellenir."
        )
        layout.addWidget(info)

        self.export_btn = QPushButton("Bu Kanalın Sözlüğünü Dışa Aktar")
        self.export_btn.clicked.connect(self.export_channel_dictionary)
        self.export_btn.setToolTip("Aktif kanalın sözlüğünü JSON dosyası olarak dışarı kaydeder.")
        layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("Dosyadan Bu Kanala İçe Aktar")
        self.import_btn.clicked.connect(self.import_channel_dictionary)
        self.import_btn.setToolTip("Seçtiğin sözlük paketini aktif kanalın sözlüğüne ekler.")
        layout.addWidget(self.import_btn)

    def export_channel_dictionary(self):
        default_name = f"{self.channel_name.lower().replace(' ', '_')}_dictionary_export.json"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Sözlüğü dışa aktar",
            default_name,
            "JSON Files (*.json)"
        )
        if not path:
            return

        try:
            data = load_channel_dictionary(self.channel_name)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Tamam", "Kanal sözlüğü dışa aktarıldı.")
        except (OSError, TypeError, ValueError) as exc:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız:\n{exc}")

    def import_channel_dictionary(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Sözlüğü içe aktar",
            "",
            "JSON Files (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, dict):
                raise ValueError("Dosya sözlük yapısında değil.")

            existing = load_channel_dictionary(self.channel_name)
            merged = dict(existing)
            merged.update({
                str(key).upper().strip(): str(value).strip()
                for key, value in data.items()
                if str(key).strip()
            })
            save_channel_dictionary(self.channel_name, merged)
            QMessageBox.information(
                self,
                "Tamam",
                f"Sözlük içe aktarıldı.\n\nEklenen/güncellenen kayıt: {len(data)}"
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            QMessageBox.critical(self, "Hata", f"İçe aktarma başarısız:\n{exc}")
