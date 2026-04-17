from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core.settings_manager import load_settings, save_settings


def _normalize_db_path(path) -> str:
    text = str(path or "").strip()
    if not text:
        return ""
    return os.path.normpath(text)


class ExternalDbManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dış Veritabanı Yönetimi")
        self.resize(720, 360)

        self.parent_window = parent
        parent_settings = getattr(parent, "settings", {}) if parent else {}
        self.settings = dict(parent_settings or load_settings())
        self.db_paths = self._load_paths()

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "Arşiv aramada kullanılacak dış veritabanlarını buradan ekleyebilirsin."
            )
        )

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(self.list_widget.SelectionMode.SingleSelection)
        layout.addWidget(self.list_widget, 1)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        buttons = QHBoxLayout()

        self.add_btn = QPushButton("Veritabanı Ekle")
        self.add_btn.clicked.connect(self.add_db)
        buttons.addWidget(self.add_btn)

        self.remove_btn = QPushButton("Seçileni Kaldır")
        self.remove_btn.clicked.connect(self.remove_selected)
        buttons.addWidget(self.remove_btn)

        self.open_folder_btn = QPushButton("Klasörde Göster")
        self.open_folder_btn.clicked.connect(self.open_selected_folder)
        buttons.addWidget(self.open_folder_btn)

        buttons.addStretch(1)

        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.accept)
        buttons.addWidget(self.close_btn)

        layout.addLayout(buttons)

        self.refresh_list()

    def _load_paths(self) -> list[str]:
        raw_paths = self.settings.get("external_databases", [])
        if not isinstance(raw_paths, list):
            raw_paths = []

        unique = []
        seen = set()
        for raw_path in raw_paths:
            normalized = _normalize_db_path(raw_path)
            if not normalized:
                continue

            key = normalized.casefold()
            if key in seen:
                continue
            seen.add(key)
            unique.append(normalized)

        return unique

    def _save_paths(self):
        self.settings["external_databases"] = list(self.db_paths)
        save_settings(self.settings)

        if self.parent_window and hasattr(self.parent_window, "settings"):
            self.parent_window.settings["external_databases"] = list(self.db_paths)

    def refresh_list(self):
        self.list_widget.clear()

        for path in self.db_paths:
            label = f"{Path(path).name} | {path}"
            self.list_widget.addItem(label)

        if not self.db_paths:
            self.status_label.setText("Henüz dış veritabanı eklenmedi.")
        else:
            self.status_label.setText(f"{len(self.db_paths)} dış veritabanı kayıtlı.")

    def add_db(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Veritabanı Seç",
            "",
            "SQLite Veritabanı (*.db);;Tüm Dosyalar (*.*)",
        )
        if not path:
            return

        normalized = _normalize_db_path(path)
        if not normalized:
            return

        if not Path(normalized).exists():
            QMessageBox.warning(self, "Uyarı", "Seçilen veritabanı dosyası bulunamadı.")
            return

        if normalized.casefold() in {item.casefold() for item in self.db_paths}:
            QMessageBox.information(self, "Bilgi", "Bu veritabanı zaten listede.")
            return

        self.db_paths.append(normalized)
        self._save_paths()
        self.refresh_list()

    def remove_selected(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.db_paths):
            QMessageBox.information(self, "Bilgi", "Önce listeden bir veritabanı seç.")
            return

        self.db_paths.pop(row)
        self._save_paths()
        self.refresh_list()

    def open_selected_folder(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.db_paths):
            QMessageBox.information(self, "Bilgi", "Önce listeden bir veritabanı seç.")
            return

        selected = Path(self.db_paths[row])
        if selected.exists():
            os.startfile(str(selected.parent))
        else:
            QMessageBox.warning(self, "Uyarı", "Seçilen veritabanı artık bulunamıyor.")
