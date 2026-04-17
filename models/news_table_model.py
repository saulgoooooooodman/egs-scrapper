from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class NewsTableModel(QAbstractTableModel):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self._items = list(items or [])
        self._headers = ["Kod", "Haber"]
        self._sort_column = 1
        self._sort_order = Qt.AscendingOrder

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._items)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 2

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = self._items[index.row()]

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.get("news_code", "")
            if index.column() == 1:
                corrected = (item.get("corrected_title") or "").strip()
                return corrected if corrected else item.get("title", "")

        if role == Qt.ToolTipRole:
            if index.column() == 0:
                code = item.get("news_code", "")
                cat = item.get("news_category", "")
                return f"{code} | {cat}"
            if index.column() == 1:
                original = item.get("title", "")
                corrected = (item.get("corrected_title") or "").strip()
                file_name = item.get("file_name", "")
                if corrected and corrected != original:
                    return f"Düzeltilmiş: {corrected}\nOrijinal: {original}\nDosya: {file_name}"
                return file_name

        if role == Qt.UserRole:
            return item

        if role == Qt.TextAlignmentRole:
            if index.column() == 0:
                return int(Qt.AlignLeft | Qt.AlignVCenter)
            return int(Qt.AlignLeft | Qt.AlignVCenter)

        return None

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
                key=lambda x: (
                    (x.get("news_code", "") or "").lower(),
                    ((x.get("corrected_title") or x.get("title", "")) or "").lower(),
                ),
                reverse=reverse,
            )
        else:
            self._items.sort(
                key=lambda x: (
                    ((x.get("corrected_title") or x.get("title", "")) or "").lower(),
                    (x.get("news_code", "") or "").lower(),
                ),
                reverse=reverse,
            )