from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidgetItem


class NewsListModel:
    @staticmethod
    def populate(tree_widget, items):
        """
        Geriye dönük uyumluluk için tutuluyor.
        Yeni mimaride ana liste yapısı news_view + NewsTableModel olmalıdır.
        """
        if tree_widget is None:
            return

        tree_widget.setUpdatesEnabled(False)
        tree_widget.clear()

        for item in items:
            display_title = (item.get("corrected_title") or "").strip() or item.get("title", "")
            tree_item = QTreeWidgetItem([
                item.get("news_code", ""),
                display_title,
            ])
            tree_item.setData(0, Qt.UserRole, item)
            tree_item.setToolTip(0, f"{item.get('news_code', '')} | {item.get('news_category', '')}")
            tree_item.setToolTip(1, item.get("file_name", ""))
            tree_widget.addTopLevelItem(tree_item)

        tree_widget.setUpdatesEnabled(True)

        if items and tree_widget.topLevelItemCount() > 0:
            tree_widget.setCurrentItem(tree_widget.topLevelItem(0))