from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QTextEdit, QVBoxLayout

from changelog import CHANGELOG
from version_info import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_RELEASE_DATE,
    APP_STAGE,
    APP_VERSION,
)


class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Sürüm Notları")
        self.resize(820, 620)

        layout = QVBoxLayout(self)

        summary = QLabel(
            f"{APP_NAME} {APP_VERSION} ({APP_STAGE})\n"
            f"Yayın tarihi: {APP_RELEASE_DATE}\n\n"
            f"{APP_DESCRIPTION}"
        )
        summary.setWordWrap(True)
        layout.addWidget(summary)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setPlainText(self._build_changelog_text())
        layout.addWidget(self.text, 1)

    def _build_changelog_text(self) -> str:
        blocks = []

        for entry in CHANGELOG:
            version = entry.get("version", "Bilinmeyen sürüm")
            date = entry.get("date", "Tarih yok")
            notes = entry.get("notes", [])

            lines = [f"{version} - {date}"]
            lines.extend(f"  - {note}" for note in notes)
            blocks.append("\n".join(lines))

        return "\n\n".join(blocks) if blocks else "Henüz sürüm notu yok."
