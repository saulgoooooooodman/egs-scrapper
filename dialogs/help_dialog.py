from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QTextEdit,
)

from core.app_paths import HELP_FILE


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Yardım")
        self.resize(900, 650)

        layout = QVBoxLayout(self)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Yardımda Ara:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Konu, komut ya da regex örneği ara...")
        self.search_input.returnPressed.connect(self.find_next)
        search_row.addWidget(self.search_input, 1)

        self.search_prev_btn = QPushButton("Önceki")
        self.search_prev_btn.clicked.connect(self.find_prev)
        search_row.addWidget(self.search_prev_btn)

        self.search_next_btn = QPushButton("Sonraki")
        self.search_next_btn.clicked.connect(self.find_next)
        search_row.addWidget(self.search_next_btn)

        self.search_status = QLabel("")
        search_row.addWidget(self.search_status)

        layout.addLayout(search_row)

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        if HELP_FILE.exists():
            try:
                content = HELP_FILE.read_text(encoding="utf-8")
            except Exception:
                content = "Yardım dosyası okunamadı."
        else:
            content = "Yardım dosyası bulunamadı."

        self.text.setMarkdown(content)
        layout.addWidget(self.text)

    def _find(self, backward: bool = False):
        needle = self.search_input.text().strip()
        if not needle:
            self.search_status.setText("Arama metni gir.")
            self.search_input.setFocus()
            return

        flags = QTextDocument.FindBackward if backward else QTextDocument.FindFlags()
        found = self.text.find(needle, flags)
        if not found:
            cursor = self.text.textCursor()
            cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start)
            self.text.setTextCursor(cursor)
            found = self.text.find(needle, flags)

        self.search_status.setText("Bulundu" if found else "Bulunamadı")

    def find_next(self):
        self._find(backward=False)

    def find_prev(self):
        self._find(backward=True)
