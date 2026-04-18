from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from data.database import merge_external_database_into_channel


class DbMergeDialog(QDialog):
    def __init__(self, current_channel: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Veritabanı İçe Aktar / Birleştir")
        self.resize(560, 180)

        self.current_channel = current_channel

        layout = QVBoxLayout(self)

        info = QLabel(
            f"Birleştirilecek hedef kanal: {current_channel}\n"
            "Harici SQLite veritabanını seçip mevcut kanal veritabanına aktar."
        )
        info.setWordWrap(True)
        info.setToolTip("Bu işlem seçtiğin dış veritabanındaki kayıtları aktif kanalın veritabanına kopyalar.")
        layout.addWidget(info)

        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setPlaceholderText("Harici veritabanı seçilmedi")
        self.path_input.setToolTip("Birleştirilecek veritabanı dosyasının tam yolunu gösterir.")
        path_row.addWidget(self.path_input, 1)

        self.browse_btn = QPushButton("Gözat")
        self.browse_btn.clicked.connect(self.pick_db)
        self.browse_btn.setToolTip("Birleştirmek istediğin dış SQLite veritabanını seç.")
        path_row.addWidget(self.browse_btn)
        layout.addLayout(path_row)

        action_row = QHBoxLayout()
        action_row.addStretch(1)

        self.merge_btn = QPushButton("Birleştir")
        self.merge_btn.clicked.connect(self.run_merge)
        self.merge_btn.setToolTip("Seçili veritabanındaki kayıtları mevcut kanal veritabanına aktarır.")
        action_row.addWidget(self.merge_btn)

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setToolTip("İşlemi başlatmadan pencereyi kapatır.")
        action_row.addWidget(self.cancel_btn)
        layout.addLayout(action_row)

    def pick_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Harici veritabanı seç",
            "",
            "SQLite Veritabanı (*.db *.sqlite *.sqlite3);;Tüm Dosyalar (*.*)",
        )
        if path:
            self.path_input.setText(path)

    def run_merge(self):
        external_db_path = self.path_input.text().strip()
        if not external_db_path:
            QMessageBox.information(self, "Bilgi", "Önce bir veritabanı seç.")
            return

        db_path = Path(external_db_path)
        if not db_path.exists():
            QMessageBox.critical(self, "Hata", "Seçilen veritabanı dosyası bulunamadı.")
            return

        try:
            merge_external_database_into_channel(self.current_channel, str(db_path))
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Birleştirme başarısız:\n{exc}")
            return

        QMessageBox.information(self, "Tamam", "Veritabanı birleştirme tamamlandı.")
        self.accept()
