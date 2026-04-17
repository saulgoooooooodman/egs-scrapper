from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QWidget,
    QGridLayout,
    QCheckBox,
    QScrollArea,
    QFrame,
)


class CodeFilterWizardDialog(QDialog):
    def __init__(self, codes, selected_codes, hide_mode=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kodları Filtreleme")

        if isinstance(codes, dict):
            self.code_labels = {
                str(code).strip(): str(label or "").strip()
                for code, label in codes.items()
                if str(code).strip()
            }
            self.codes = sorted(self.code_labels)
        else:
            self.codes = sorted(str(code).strip() for code in codes if str(code).strip())
            self.code_labels = {code: "" for code in self.codes}
        self.selected_codes = set(selected_codes)
        self.hide_mode = hide_mode
        self.checkboxes = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 6, 6, 6)

        info = QLabel("Filtrelemek istediğin haber kodlarını seç. Yeni kodlar Kanal Kuralları ekranından eklenir.")
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()
        row.setSpacing(4)
        row.addWidget(QLabel("Biçim:"))

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Göster", "Gizle"])
        self.mode_combo.setCurrentIndex(1 if hide_mode else 0)
        row.addWidget(self.mode_combo)
        layout.addLayout(row)

        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(1, 1, 1, 1)
        frame_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(0)
        grid.setVerticalSpacing(0)
        grid.setHorizontalSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)

        columns = 2
        display_texts = []
        for i, code in enumerate(self.codes):
            r = i // columns
            c = i % columns

            label = self.code_labels.get(code, "")
            text = f"{code} - {label}" if label else code
            display_texts.append(text)

            cb = QCheckBox(text)
            cb.setChecked(code in self.selected_codes)
            cb.setStyleSheet("""
                QCheckBox {
                    margin: 0px;
                    padding: 0px;
                    spacing: 3px;
                    min-height: 20px;
                    max-height: 20px;
                }
            """)
            self.checkboxes[code] = cb
            grid.addWidget(cb, r, c, alignment=Qt.AlignLeft | Qt.AlignVCenter)

        scroll.setWidget(container)
        frame_layout.addWidget(scroll)
        layout.addWidget(frame, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        self.select_all_btn = QPushButton("Tümü")
        self.select_all_btn.clicked.connect(self.select_all)
        btn_row.addWidget(self.select_all_btn)

        self.clear_btn = QPushButton("Temizle")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_row.addWidget(self.clear_btn)

        self.ok_btn = QPushButton("Uygula")
        self.ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        layout.addLayout(btn_row)

        self._fit_to_contents(display_texts, columns)

    def _fit_to_contents(self, display_texts, columns: int):
        fm = self.fontMetrics()
        widest = max((fm.horizontalAdvance(text) for text in display_texts), default=280)
        width = min(980, max(560, (widest * columns) + 120))
        rows = max(1, (len(self.codes) + columns - 1) // columns)
        height = min(760, max(320, 170 + (rows * 24)))
        self.resize(width, height)

    def select_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(True)

    def clear_all(self):
        for cb in self.checkboxes.values():
            cb.setChecked(False)

    def get_selected_codes(self):
        return [code for code, cb in self.checkboxes.items() if cb.isChecked()]

    def is_hide_mode(self):
        return self.mode_combo.currentIndex() == 1
