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

    search_label = QLabel("Ara:")
    search_label.setToolTip("Yüklü listedeki haberleri başlık veya metin içinde anında filtreler.")
    filter_layout.addWidget(search_label)

    self.search_input = QLineEdit()
    self.search_input.setPlaceholderText("Başlık veya haber metni ara...")
    self.search_input.setToolTip(
        "Yüklü listedeki haberleri anında filtreler. "
        "Regex kapalıysa normal kelime araması, açıksa düzenli ifade araması yapılır."
    )
    self.search_input.textChanged.connect(self.apply_filters)
    filter_layout.addWidget(self.search_input, 1)

    scope_label = QLabel("Arama Alanı:")
    scope_label.setToolTip("Aramanın başlıkta mı, haber metninde mi, yoksa her ikisinde mi çalışacağını belirler.")
    filter_layout.addWidget(scope_label)

    self.search_scope_combo = QComboBox()
    self.search_scope_combo.addItems(["Tümü", "Başlık", "Haber Metni"])
    self.search_scope_combo.setToolTip("Aramanın hangi alanlarda yapılacağını seç.")
    self.search_scope_combo.currentIndexChanged.connect(self.apply_filters)
    filter_layout.addWidget(self.search_scope_combo)

    self.search_regex_checkbox = QCheckBox("Regex")
    self.search_regex_checkbox.setToolTip("İşaretlersen arama kutusundaki ifade regex olarak yorumlanır.")
    self.search_regex_checkbox.toggled.connect(self.apply_filters)
    filter_layout.addWidget(self.search_regex_checkbox)

    self.refresh_button = QPushButton("Yenile")
    self.refresh_button.setToolTip("Seçili tarihteki klasörü yeniden tarar ve listeyi günceller.")
    self.refresh_button.clicked.connect(self.load_news)
    filter_layout.addWidget(self.refresh_button)

    main_layout.addWidget(filter_widget)
