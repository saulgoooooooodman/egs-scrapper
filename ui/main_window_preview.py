from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QTableView,
    QAbstractItemView,
    QHeaderView,
)

from models.news_table_model import NewsTableModel


class NewsTableView(QTableView):
    prefixTyped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._typeahead_buffer = ""
        self._typeahead_timer = QTimer(self)
        self._typeahead_timer.setSingleShot(True)
        self._typeahead_timer.setInterval(900)
        self._typeahead_timer.timeout.connect(self._clear_typeahead_buffer)

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
            super().keyPressEvent(event)
            return

        if event.key() == Qt.Key_Backspace and self._typeahead_buffer:
            self._typeahead_buffer = self._typeahead_buffer[:-1]
            if self._typeahead_buffer:
                self.prefixTyped.emit(self._typeahead_buffer)
                self._typeahead_timer.start()
            else:
                self._clear_typeahead_buffer()
            event.accept()
            return

        text = event.text() or ""
        if len(text) == 1 and text.isprintable() and not text.isspace():
            self._typeahead_buffer += text
            self._typeahead_timer.start()
            self.prefixTyped.emit(self._typeahead_buffer)
            event.accept()
            return

        if event.key() == Qt.Key_Escape:
            self._clear_typeahead_buffer()

        super().keyPressEvent(event)

    def _clear_typeahead_buffer(self):
        self._typeahead_buffer = ""


def build_news_list_panel(self):
    left_widget = QWidget()
    left_widget.setMinimumWidth(320)
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(4)

    self.count_label = QLabel("Haber sayısı: 0")
    self.count_label.setToolTip("Filtrelerden sonra listede görünen haber sayısını gösterir.")

    self.news_model = NewsTableModel([], channel_name=self.channel_name)
    self.news_view = NewsTableView()
    self.news_view.setModel(self.news_model)
    self.news_view.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.news_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
    self.news_view.setAlternatingRowColors(False)
    self.news_view.setSortingEnabled(True)
    self.news_view.sortByColumn(2, Qt.AscendingOrder)
    self.news_view.verticalHeader().setVisible(False)
    self.news_view.horizontalHeader().setStretchLastSection(False)
    self.news_view.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
    self.news_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
    self.news_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    self.news_view.setShowGrid(True)
    self.news_view.setWordWrap(False)
    self.news_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
    self.news_view.verticalHeader().setDefaultSectionSize(22)
    self.news_view.setToolTip(
        "Listedeki haberi çift tıklarsan metin kopyalanır. "
        "Birden fazla satır seçip Ctrl+C ile toplu kopyalama yapabilirsin."
    )

    self.news_view.selectionModel().currentRowChanged.connect(self.on_news_row_changed)
    self.news_view.doubleClicked.connect(self.on_news_double_clicked)
    self.news_view.prefixTyped.connect(self.navigate_news_by_prefix)

    self.copy_shortcut_table = QShortcut(QKeySequence("Ctrl+C"), self.news_view)
    self.copy_shortcut_table.activated.connect(self.copy_current_item)

    left_layout.addWidget(self.count_label)
    left_layout.addWidget(self.news_view)

    return left_widget


def build_preview_panel(self):
    right_widget = QWidget()
    right_widget.setMinimumWidth(420)
    right_layout = QVBoxLayout(right_widget)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(4)

    self.preview_title = QLabel("Başlık:")
    self.preview_title.setStyleSheet("font-weight: bold;")
    self.preview_title.setToolTip("Başlığa çift tıklarsan haberin tüm metni panoya kopyalanır.")
    self.preview_title.mouseDoubleClickEvent = self.copy_full_current_news_from_title

    self.preview_corrected_title = QLabel("")
    self.preview_corrected_title.setWordWrap(True)
    self.preview_corrected_title.setStyleSheet("color:#9bd29b; font-weight:bold;")
    self.preview_corrected_title.setToolTip("Sözlük veya yazım denetimiyle düzeltilmiş başlık önerisini gösterir.")

    self.preview_info = QLabel("Bilgi:")
    self.preview_info.setWordWrap(True)
    self.preview_info.setToolTip("Seçili haberin kod, tarih, editör ve dosya bilgilerini gösterir.")

    self.preview_text = QTextEdit()
    self.preview_text.setReadOnly(False)
    self.preview_text.setToolTip(
        "Seçili haberin düzenlenebilir metni. "
        "Ctrl+S ile kaydedebilir, sağ tıkla düzenleme komutlarına ulaşabilirsin."
    )

    self.copy_shortcut_preview = QShortcut(QKeySequence("Ctrl+C"), self.preview_text)
    self.copy_shortcut_preview.activated.connect(self.copy_from_preview)

    self.save_shortcut_preview = QShortcut(QKeySequence("Ctrl+S"), self.preview_text)
    self.save_shortcut_preview.activated.connect(self.save_edited_text)

    self.save_text_button = QPushButton("Kaydet")
    self.save_text_button.clicked.connect(self.save_edited_text)
    self.save_text_button.setToolTip("Önizleme alanındaki değişiklikleri seçili haber kaydına yazar.")

    right_layout.addWidget(self.preview_title)
    right_layout.addWidget(self.preview_corrected_title)
    right_layout.addWidget(self.preview_info)
    right_layout.addWidget(self.preview_text, 1)
    right_layout.addWidget(self.save_text_button)

    return right_widget
