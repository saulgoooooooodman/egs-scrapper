from __future__ import annotations

import re
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QTextBrowser,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QWidget,
    QSizePolicy,
)

from core.app_paths import HELP_FILE


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Yardım")
        self.resize(900, 650)
        self._sections: list[dict[str, Any]] = []
        self._section_markdown_by_title: dict[str, str] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)

        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(8)
        search_label = QLabel("Yardımda Ara:")
        search_label.setToolTip("Yardım metni içinde konu veya anahtar kelime arar.")
        search_row.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Konu, komut ya da regex örneği ara...")
        self.search_input.returnPressed.connect(self.find_next)
        self.search_input.setToolTip("Yardım içeriğinde aramak istediğin kelimeyi yaz.")
        search_row.addWidget(self.search_input, 1)

        self.search_prev_btn = QPushButton("Önceki")
        self.search_prev_btn.clicked.connect(self.find_prev)
        self.search_prev_btn.setToolTip("Bir önceki eşleşmeye gider.")
        search_row.addWidget(self.search_prev_btn)

        self.search_next_btn = QPushButton("Sonraki")
        self.search_next_btn.clicked.connect(self.find_next)
        self.search_next_btn.setToolTip("Bir sonraki eşleşmeye gider.")
        search_row.addWidget(self.search_next_btn)

        self.search_status = QLabel("")
        self.search_status.setToolTip("Aramanın bulundu veya bulunamadı bilgisini gösterir.")
        search_row.addWidget(self.search_status)

        search_container = QWidget(self)
        search_container.setLayout(search_row)
        search_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(search_container, 0, Qt.AlignTop)

        self.topic_list = QListWidget()
        self.topic_list.setMinimumWidth(250)
        self.topic_list.setToolTip("Yardım konuları burada listelenir. Bir başlığa tıklayarak ilgili bölüme gidebilirsin.")

        self.text = QTextBrowser()
        self.text.setReadOnly(True)
        self.text.setOpenExternalLinks(False)
        self.text.setToolTip("Programın kapsamlı yardım içeriği burada görüntülenir.")

        if HELP_FILE.exists():
            try:
                content = HELP_FILE.read_text(encoding="utf-8")
            except Exception:
                content = "Yardım dosyası okunamadı."
        else:
            content = "Yardım dosyası bulunamadı."

        self._build_sections(content)
        self._build_topic_list()
        self.topic_list.currentItemChanged.connect(self._go_to_topic)

        splitter = QSplitter()
        splitter.addWidget(self.topic_list)
        splitter.addWidget(self.text)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([260, 620])
        layout.addWidget(splitter, 1)

        if self.topic_list.count() > 0:
            self.topic_list.setCurrentRow(0)

    def _build_sections(self, markdown_text: str):
        lines = markdown_text.splitlines()
        headings = []

        for index, line in enumerate(lines):
            match = re.match(r"^(#{1,3})\s+(.*)$", line.strip())
            if not match:
                continue
            level = len(match.group(1))
            title = match.group(2).strip()
            if not title:
                continue
            headings.append({
                "index": index,
                "level": level,
                "title": title,
            })

        self._sections = []
        self._section_markdown_by_title = {}
        if not headings:
            self._section_markdown_by_title["Yardım"] = markdown_text
            self._sections.append({"level": 1, "title": "Yardım"})
            return

        for position, heading in enumerate(headings):
            start_index = heading["index"]
            end_index = len(lines)

            for later in headings[position + 1:]:
                if later["level"] <= heading["level"]:
                    end_index = later["index"]
                    break

            section_markdown = "\n".join(lines[start_index:end_index]).strip()
            self._sections.append({
                "level": heading["level"],
                "title": heading["title"],
            })
            self._section_markdown_by_title[heading["title"]] = section_markdown

    def _build_topic_list(self):
        self.topic_list.clear()

        for section in self._sections:
            level = int(section.get("level", 1))
            title = str(section.get("title", "")).strip()
            if not title:
                continue
            label = title if level <= 2 else f"    {title}"
            item = QListWidgetItem(label)
            item.setData(256, title)
            self.topic_list.addItem(item)

    def _go_to_topic(self, current, previous):
        if current is None:
            return
        title = str(current.data(256) or "").strip()
        if not title:
            return
        content = self._section_markdown_by_title.get(title, "")
        self.text.setMarkdown(content or f"## {title}\n\nİçerik bulunamadı.")
        cursor = self.text.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.text.setTextCursor(cursor)
        self.text.ensureCursorVisible()

    def _find(self, backward: bool = False):
        needle = self.search_input.text().strip()
        if not needle:
            self.search_status.setText("Arama metni gir.")
            self.search_input.setFocus()
            return

        flags = QTextDocument.FindBackward if backward else QTextDocument.FindFlags()
        found = self.text.find(needle, flags)
        if not found:
            cursor = self.text.textCursor()
            cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start)
            self.text.setTextCursor(cursor)
            found = self.text.find(needle, flags)

        self.search_status.setText("Bulundu" if found else "Bulunamadı")

    def find_next(self):
        self._find(backward=False)

    def find_prev(self):
        self._find(backward=True)
