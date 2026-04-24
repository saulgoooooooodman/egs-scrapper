from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.rules_store import get_all_rules
from data.database import get_archive_statistics


class StatisticsDialog(QDialog):
    def __init__(self, current_channel: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İstatistikler")
        self.resize(860, 620)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Bu ekran seçilen kanal ve tarih aralığı için veritabanındaki haber sayıları ile editör dağılımını gösterir."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        filters = QHBoxLayout()

        form = QFormLayout()
        self.channel_combo = QComboBox()
        channels = sorted(get_all_rules().keys())
        self.channel_combo.addItems(channels)
        index = self.channel_combo.findText(current_channel)
        if index >= 0:
            self.channel_combo.setCurrentIndex(index)
        form.addRow("Kanal:", self.channel_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat("dd.MM.yyyy")
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        form.addRow("Başlangıç:", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat("dd.MM.yyyy")
        self.end_date.setDate(QDate.currentDate())
        form.addRow("Bitiş:", self.end_date)
        filters.addLayout(form, 1)

        button_col = QVBoxLayout()
        self.refresh_button = QPushButton("Getir")
        self.refresh_button.clicked.connect(self.reload_stats)
        button_col.addWidget(self.refresh_button)
        button_col.addStretch(1)
        filters.addLayout(button_col)
        layout.addLayout(filters)

        self.summary_label = QLabel("Hazır")
        layout.addWidget(self.summary_label)

        self.tabs = QTabWidget()
        self.year_table = self._build_table("Yıl", "Haber")
        self.month_table = self._build_table("Ay", "Haber")
        self.day_table = self._build_table("Gün", "Haber")
        self.editor_table = self._build_table("Editör", "Haber")
        self.tabs.addTab(self.year_table, "Yıllar")
        self.tabs.addTab(self.month_table, "Aylar")
        self.tabs.addTab(self.day_table, "Günler")
        self.tabs.addTab(self.editor_table, "Editörler")
        layout.addWidget(self.tabs, 1)

        self.reload_stats()

    def _build_table(self, first_header: str, second_header: str) -> QTableWidget:
        table = QTableWidget(0, 2, self)
        table.setHorizontalHeaderLabels([first_header, second_header])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(table.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
        return table

    def _fill_table(self, table: QTableWidget, rows: list[dict]):
        table.setRowCount(0)
        for row_data in rows:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(row_data.get("label", ""))))
            table.setItem(row, 1, QTableWidgetItem(str(row_data.get("count", 0))))
        table.resizeColumnsToContents()

    def reload_stats(self):
        start_iso = self.start_date.date().toString("yyyy-MM-dd")
        end_iso = self.end_date.date().toString("yyyy-MM-dd")
        channel_name = self.channel_combo.currentText().strip()

        result = get_archive_statistics(channel_name, start_iso, end_iso)
        self.summary_label.setText(
            f"Toplam haber: {result['total_news']} | Kanal: {channel_name} | Aralık: {start_iso} - {end_iso}"
        )
        self._fill_table(self.year_table, result["per_year"])
        self._fill_table(self.month_table, result["per_month"])
        self._fill_table(self.day_table, result["per_day"])
        self._fill_table(self.editor_table, result["per_editor"])
