from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
)


class BackfillDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Arşiv Taraması")
        self.resize(430, 180)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        info = QLabel(
            "Belirli bir tarih aralığını tarayıp veritabanına ekleyebilirsin.\n"
            "Bu işlem eski günleri arşive almak için kullanılır."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()
        row.addWidget(QLabel("Başlangıç:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        row.addWidget(self.start_date)

        row.addWidget(QLabel("Bitiş:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.setDate(QDate.currentDate())
        row.addWidget(self.end_date)
        layout.addLayout(row)

        self.progress_label = QLabel("Hazır")
        layout.addWidget(self.progress_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        buttons = QHBoxLayout()
        self.start_button = QPushButton("Taramayı Başlat")
        self.cancel_button = QPushButton("İptal")
        self.cancel_button.setEnabled(False)
        self.close_button = QPushButton("Kapat")
        buttons.addWidget(self.start_button)
        buttons.addWidget(self.cancel_button)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

        self.close_button.clicked.connect(self.reject)
