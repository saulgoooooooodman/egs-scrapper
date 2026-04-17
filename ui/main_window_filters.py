from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QCheckBox,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
)


def build_filter_bar(self, main_layout):
    filter_widget = QWidget()
    filter_layout = QHBoxLayout(filter_widget)
    filter_layout.setContentsMargins(0, 0, 0, 0)
    filter_layout.setSpacing(6)

    filter_layout.addWidget(QLabel("Ara:"))

    self.search_input = QLineEdit()
    self.search_input.setPlaceholderText("Başlık veya haber metni ara...")
    self.search_input.setToolTip("Arama kutusu")
    self.search_input.textChanged.connect(self.apply_filters)
    filter_layout.addWidget(self.search_input, 1)

    filter_layout.addWidget(QLabel("Arama Alanı:"))

    self.search_scope_combo = QComboBox()
    self.search_scope_combo.addItems(["Tümü", "Başlık", "Haber Metni"])
    self.search_scope_combo.setToolTip("Arama alanını seç")
    self.search_scope_combo.currentIndexChanged.connect(self.apply_filters)
    filter_layout.addWidget(self.search_scope_combo)

    self.search_regex_checkbox = QCheckBox("Regex")
    self.search_regex_checkbox.setToolTip("Aramalarda düzenli ifade kullan")
    self.search_regex_checkbox.toggled.connect(self.apply_filters)
    filter_layout.addWidget(self.search_regex_checkbox)

    self.refresh_button = QPushButton("Yenile")
    self.refresh_button.setToolTip("Haber listesini yeniden yükle")
    self.refresh_button.clicked.connect(self.load_news)
    filter_layout.addWidget(self.refresh_button)

    self.save_profile_button = QPushButton("Profili Kaydet")
    self.save_profile_button.setToolTip("Geçerli görünüm ve filtre ayarlarını kaydet")
    self.save_profile_button.clicked.connect(self.save_main_ui_settings)
    filter_layout.addWidget(self.save_profile_button)

    main_layout.addWidget(filter_widget)
