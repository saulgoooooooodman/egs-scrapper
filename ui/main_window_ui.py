from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QLabel,
    QProgressBar,
)

from data.database import init_db, get_news_count_for_month
from ui.main_window_context_menus import (
    show_header_context_menu,
    show_news_context_menu,
    show_preview_context_menu,
)
from ui.main_window_topbar import build_topbar
from ui.main_window_filters import build_filter_bar
from ui.main_window_preview import build_news_list_panel, build_preview_panel


def build_main_window_ui(self):
    central = QWidget()
    self.setCentralWidget(central)

    main_layout = QVBoxLayout(central)
    main_layout.setContentsMargins(6, 6, 6, 6)
    main_layout.setSpacing(6)

    build_topbar(self, main_layout)
    build_filter_bar(self, main_layout)

    self.progress_bar = QProgressBar()
    self.progress_bar.setVisible(False)
    self.progress_bar.setMinimum(0)
    self.progress_bar.setValue(0)
    self.progress_bar.setTextVisible(True)
    self.progress_bar.setToolTip("Tarama ve yükleme ilerlemesi.")
    main_layout.addWidget(self.progress_bar)

    splitter = QSplitter()
    splitter.setChildrenCollapsible(False)

    left_widget = build_news_list_panel(self)
    right_widget = build_preview_panel(self)

    self.news_view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
    self.news_view.horizontalHeader().customContextMenuRequested.connect(
        lambda pos: show_header_context_menu(self, pos)
    )

    self.news_view.setContextMenuPolicy(Qt.CustomContextMenu)
    self.news_view.customContextMenuRequested.connect(
        lambda pos: show_news_context_menu(self, pos)
    )
    self.preview_text.setContextMenuPolicy(Qt.CustomContextMenu)
    self.preview_text.customContextMenuRequested.connect(
        lambda pos: show_preview_context_menu(self, pos)
    )

    splitter.addWidget(left_widget)
    splitter.addWidget(right_widget)
    splitter.setSizes([450, 980])

    main_layout.addWidget(splitter, 1)

    current_iso = self.date_edit.date().toString("yyyy-MM-dd")
    init_db(self.channel_name, current_iso)
    db_count = get_news_count_for_month(self.channel_name, current_iso)

    self.status_label = self._build_status_label(f"Hazır | DB: {db_count}")
    main_layout.addWidget(self.status_label)


def _build_status_label_impl(self, text: str):
    label = QLabel(text)
    label.setToolTip("Geçerli veritabanı durumu.")
    return label


def attach_ui_helpers(cls):
    cls._build_status_label = _build_status_label_impl
