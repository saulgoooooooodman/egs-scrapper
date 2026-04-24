from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QBrush, QColor

from core.title_rules import build_list_corrected_title
from core.text_utils import turkish_sort_key


class NewsTableModel(QAbstractTableModel):
    def __init__(self, items=None, channel_name: str = "", parent=None):
        super().__init__(parent)
        self._items = list(items or [])
        self._channel_name = str(channel_name or "").strip()
        self._headers = ["Kod", "Açıklama", "Haber"]
        self._sort_column = 2
        self._sort_order = Qt.AscendingOrder
        self._show_corrected_titles = False
        self._code_styles = {}
        self._old_news_style = {}
        self._sort_internal()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._items)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 3

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self._items[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.get("news_code", "")
            if index.column() == 1:
                return item.get("news_category", "")
            if index.column() == 2:
                return self._display_title(item)

        if role == Qt.ToolTipRole:
            if index.column() == 0:
                code = item.get("news_code", "")
                category = item.get("news_category", "")
                return f"{code} | {category}"
            if index.column() == 1:
                return item.get("news_category", "")
            if index.column() == 2:
                original = str(item.get("title", "") or "").strip()
                display_title = self._display_title(item)
                file_name = item.get("file_name", "")
                if display_title and display_title != original:
                    return f"Listede: {display_title}\nOrijinal: {original}\nDosya: {file_name}"
                return file_name

        if role == Qt.UserRole:
            return item

        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter)

        style = self._resolve_row_style(item)
        if role == Qt.BackgroundRole:
            background = style.get("background", "")
            if background:
                color = QColor(background)
                if color.isValid():
                    return QBrush(color)

        if role == Qt.ForegroundRole:
            foreground = style.get("foreground", "")
            if foreground:
                color = QColor(foreground)
                if color.isValid():
                    return QBrush(color)

        return None

    def _resolve_row_style(self, item: dict) -> dict:
        code = str(item.get("news_code", "") or "").strip().upper()
        if code:
            style = self._code_styles.get(code, {})
            if isinstance(style, dict) and (style.get("background") or style.get("foreground")):
                return style

        if item.get("_is_previous_day"):
            return self._old_news_style if isinstance(self._old_news_style, dict) else {}
        return {}

    def _display_title(self, item: dict) -> str:
        if self._show_corrected_titles:
            corrected = build_list_corrected_title(
                str(item.get("corrected_title", "") or "").strip(),
                self._channel_name,
                str(item.get("news_code", "") or "").strip(),
            )
            if corrected:
                return corrected
        return (
            str(item.get("list_title", "") or "").strip()
            or str(item.get("corrected_title", "") or "").strip()
            or str(item.get("title", "") or "").strip()
        )

    def display_title_for_item(self, item: dict) -> str:
        return self._display_title(item)

    def set_show_corrected_titles(self, enabled: bool):
        enabled = bool(enabled)
        if self._show_corrected_titles == enabled:
            return
        self.beginResetModel()
        self._show_corrected_titles = enabled
        self._sort_internal()
        self.endResetModel()

    def set_styles(self, code_styles: dict | None = None, old_news_style: dict | None = None):
        self.beginResetModel()
        self._code_styles = dict(code_styles or {})
        self._old_news_style = dict(old_news_style or {})
        self.endResetModel()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            try:
                return self._headers[section]
            except IndexError:
                return ""
        return str(section + 1)

    def set_items(self, items):
        self.beginResetModel()
        self._items = list(items or [])
        self._sort_internal()
        self.endResetModel()

    def item_at(self, row: int):
        if 0 <= row < len(self._items):
            return self._items[row]
        return None

    def items_at_rows(self, rows: list[int]):
        result = []
        seen = set()
        for row in rows:
            if row in seen:
                continue
            seen.add(row)
            if 0 <= row < len(self._items):
                result.append(self._items[row])
        return result

    def all_items(self):
        return list(self._items)

    def sort(self, column, order=Qt.AscendingOrder):
        self.beginResetModel()
        self._sort_column = column
        self._sort_order = order
        self._sort_internal()
        self.endResetModel()

    def _sort_internal(self):
        reverse = self._sort_order == Qt.DescendingOrder

        if self._sort_column == 0:
            self._items.sort(
                key=lambda item: (
                    str(item.get("news_code", "") or "").casefold(),
                    str(item.get("news_category", "") or "").casefold(),
                    turkish_sort_key(self._display_title(item)),
                ),
                reverse=reverse,
            )
            return

        if self._sort_column == 1:
            self._items.sort(
                key=lambda item: (
                    str(item.get("news_category", "") or "").casefold(),
                    turkish_sort_key(self._display_title(item)),
                    str(item.get("news_code", "") or "").casefold(),
                ),
                reverse=reverse,
            )
            return

        self._items.sort(
            key=lambda item: (
                turkish_sort_key(self._display_title(item)),
                str(item.get("news_category", "") or "").casefold(),
                str(item.get("news_code", "") or "").casefold(),
            ),
            reverse=reverse,
        )
