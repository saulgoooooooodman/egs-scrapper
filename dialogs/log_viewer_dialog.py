from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from core.app_paths import LOG_DIR


class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Günlük Görüntüleyici")
        self.resize(900, 650)

        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        buttons = QHBoxLayout()
        self.refresh_btn = QPushButton("Yenile")
        self.refresh_btn.clicked.connect(self.load_latest_log)
        buttons.addWidget(self.refresh_btn)

        self.open_folder_btn = QPushButton("Klasörü Aç")
        self.open_folder_btn.clicked.connect(self.open_folder)
        buttons.addWidget(self.open_folder_btn)

        buttons.addStretch(1)
        layout.addLayout(buttons)

        self.load_latest_log()

    def _latest_log_file(self):
        files = sorted(LOG_DIR.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        return files[0] if files else None

    def load_latest_log(self):
        log_file = self._latest_log_file()
        if not log_file:
            self.text.setPlainText("Henüz log dosyası bulunamadı.")
            return

        try:
            self.text.setPlainText(log_file.read_text(encoding="utf-8"))
        except Exception as exc:
            self.text.setPlainText(f"Log okunamadı:\n{exc}")

    def open_folder(self):
        try:
            import os
            os.startfile(str(LOG_DIR))
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Klasör açılamadı:\n{exc}")