from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core.rules_store import (
    DEFAULT_CODE_RULE,
    DEFAULT_SCAN_OPTIONS,
    DEFAULT_TITLE_CLEANUP,
    get_all_rules,
    normalize_rule_code,
    save_all_rules,
)
from core.settings_manager import load_settings, save_settings


DEFAULT_CHANNELS = [
    "A NEWS",
    "A HABER",
    "ATV",
    "A SPOR",
    "A PARA",
]


class ChannelTitleRulesDialog(QDialog):
    def __init__(self, cleanup: dict | None = None, scan_options: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kanal Geneli Başlık Kuralları")
        self.resize(620, 260)

        current_cleanup = dict(DEFAULT_TITLE_CLEANUP)
        if isinstance(cleanup, dict):
            current_cleanup.update(cleanup)

        current_scan_options = dict(DEFAULT_SCAN_OPTIONS)
        if isinstance(scan_options, dict):
            current_scan_options.update(scan_options)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Bu pencere seçili kanalın tüm haberlerine uygulanacak genel başlık kurallarını düzenler. "
            "Buradaki ayarlar tek tek kanal kodlarından bağımsız çalışır."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()

        self.prefix_input = QLineEdit(str(current_cleanup.get("prefix", "") or ""))
        self.prefix_input.setPlaceholderText("Haber metninde başlığa eklenecek ön ektir. Örnek: ÖZEL")
        self.prefix_input.setToolTip("Haber metninde başlığa eklenecek ön ektir.")
        form.addRow("Başlık Ön Eki:", self.prefix_input)

        self.suffix_input = QLineEdit(str(current_cleanup.get("suffix", "") or ""))
        self.suffix_input.setPlaceholderText("Haber metninde başlığa eklenecek son ektir. Örnek: -APR")
        self.suffix_input.setToolTip("Haber metninde başlığa eklenecek son ektir.")
        form.addRow("Başlık Son Eki:", self.suffix_input)

        self.remove_phrases_input = QLineEdit(", ".join(current_cleanup.get("remove_phrases", [])))
        self.remove_phrases_input.setPlaceholderText("Başlıktan otomatik silinecek ifadeler. Örnek: 1300, 1430")
        self.remove_phrases_input.setToolTip("Başlıktan otomatik silinecek ifadeleri virgülle ayır.")
        form.addRow("Başlıktan Sil:", self.remove_phrases_input)

        self.remove_trailing_numbers_checkbox = QCheckBox(
            "Başlığın sonundaki saat veya sayıyı otomatik kaldır"
        )
        self.remove_trailing_numbers_checkbox.setChecked(bool(current_cleanup.get("remove_trailing_numbers", False)))
        form.addRow("", self.remove_trailing_numbers_checkbox)

        self.hide_symbol_checkbox = QCheckBox("Sembol ile başlayan başlıkları gizle")
        self.hide_symbol_checkbox.setChecked(bool(current_scan_options.get("hide_symbol_prefixed_titles", True)))
        self.hide_symbol_checkbox.setToolTip(
            "İşaretliyse +, !, #, * ile başlayan başlıklar gizlenir. "
            "Ama gerçek haber kodu olarak tanımlanan sembollü kodlar bu kurala takılmaz."
        )
        form.addRow("", self.hide_symbol_checkbox)

        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch(1)

        save_btn = QPushButton("Tamam")
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)

        cancel_btn = QPushButton("Kapat")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def get_values(self) -> tuple[dict, dict]:
        cleanup = {
            "prefix": self.prefix_input.text().strip(),
            "suffix": self.suffix_input.text().strip(),
            "remove_phrases": [
                part.strip()
                for part in self.remove_phrases_input.text().split(",")
                if part.strip()
            ],
            "remove_trailing_numbers": self.remove_trailing_numbers_checkbox.isChecked(),
        }
        scan_options = {
            "hide_symbol_prefixed_titles": self.hide_symbol_checkbox.isChecked(),
        }
        return cleanup, scan_options


class CodeRuleDialog(QDialog):
    def __init__(self, code: str = "", config: dict | None = None, parent=None):
        super().__init__(parent)
        self.config = dict(DEFAULT_CODE_RULE)
        if isinstance(config, dict):
            self.config.update(config)

        self.setWindowTitle("Kanal Kodu Düzenle")
        self.resize(640, 360)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Bu pencere seçili kanal kodunun başlık davranışını düzenler. "
            "İstersen kodu ve açıklamayı burada ayrıntılı olarak girebilirsin."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()

        self.code_input = QLineEdit(normalize_rule_code(code))
        self.code_input.setPlaceholderText("Kanal kodu. Örnek: WEU, +SES, K-STD")
        self.code_input.setToolTip("Kanal kodu büyük harfe çevrilerek kaydedilir.")
        form.addRow("Kanal Kodu:", self.code_input)

        self.label_input = QLineEdit(str(self.config.get("label", "") or ""))
        self.label_input.setPlaceholderText("Açıklama. Örnek: AVRUPA KITASI")
        self.label_input.setToolTip("Bu açıklama haber bilgisi alanında kategori olarak görünür.")
        self.label_input.textChanged.connect(self._refresh_preview)
        form.addRow("Açıklama:", self.label_input)

        self.prepend_checkbox = QCheckBox("Açıklamayı başlığın başına otomatik yaz")
        self.prepend_checkbox.setChecked(bool(self.config.get("prepend_to_title", False)))
        self.prepend_checkbox.setToolTip("İşaretliyse açıklama haber metnindeki başlığın başına eklenir.")
        self.prepend_checkbox.toggled.connect(self._refresh_preview)
        form.addRow("", self.prepend_checkbox)

        self.append_checkbox = QCheckBox("Açıklamayı başlığın sonuna otomatik yaz")
        self.append_checkbox.setChecked(bool(self.config.get("append_to_title", False)))
        self.append_checkbox.setToolTip("İşaretliyse açıklama haber metnindeki başlığın sonuna eklenir.")
        self.append_checkbox.toggled.connect(self._refresh_preview)
        form.addRow("", self.append_checkbox)

        self.dedupe_input = QLineEdit(", ".join(self.config.get("dedupe_prefix_words", [])))
        self.dedupe_input.setPlaceholderText("Aynı önek tekrar eklenmesin diye kontrol edilir. Örnek: ÖZEL DOSYA")
        form.addRow("Tekrar Kontrolü:", self.dedupe_input)

        self.title_prefix_input = QLineEdit(str(self.config.get("title_prefix", "") or ""))
        self.title_prefix_input.setPlaceholderText("Haber metninde başlığa eklenecek ön ektir.")
        self.title_prefix_input.setToolTip("Haber metninde başlığa eklenecek ön ektir.")
        self.title_prefix_input.textChanged.connect(self._refresh_preview)
        form.addRow("Başlık Ön Eki:", self.title_prefix_input)

        self.title_suffix_input = QLineEdit(str(self.config.get("title_suffix", "") or ""))
        self.title_suffix_input.setPlaceholderText("Haber metninde başlığa eklenecek son ektir.")
        self.title_suffix_input.setToolTip("Haber metninde başlığa eklenecek son ektir.")
        self.title_suffix_input.textChanged.connect(self._refresh_preview)
        form.addRow("Başlık Son Eki:", self.title_suffix_input)

        self.remove_phrases_input = QLineEdit(", ".join(self.config.get("title_remove_phrases", [])))
        self.remove_phrases_input.setPlaceholderText("Bu koda özel olarak başlıktan silinecek ifadeler.")
        form.addRow("Başlıktan Sil:", self.remove_phrases_input)

        self.remove_trailing_numbers_checkbox = QCheckBox(
            "Bu koddaki haberlerde başlığın sonundaki saat veya sayıyı kaldır"
        )
        self.remove_trailing_numbers_checkbox.setChecked(bool(self.config.get("remove_trailing_numbers", False)))
        form.addRow("", self.remove_trailing_numbers_checkbox)

        self.row_background_input = QLineEdit(str(self.config.get("row_background", "") or ""))
        self.row_background_input.setPlaceholderText("Satır arka plan rengi. Örnek: #D9F99D")
        self.row_background_input.textChanged.connect(self._refresh_preview)
        row_bg_wrap = QHBoxLayout()
        row_bg_wrap.addWidget(self.row_background_input, 1)
        row_bg_pick = QPushButton("Seç")
        row_bg_pick.clicked.connect(lambda: self._pick_color(self.row_background_input))
        row_bg_wrap.addWidget(row_bg_pick)
        row_bg_clear = QPushButton("Temizle")
        row_bg_clear.clicked.connect(lambda: self.row_background_input.clear())
        row_bg_wrap.addWidget(row_bg_clear)
        form.addRow("Satır Rengi:", row_bg_wrap)

        self.row_foreground_input = QLineEdit(str(self.config.get("row_foreground", "") or ""))
        self.row_foreground_input.setPlaceholderText("Satır yazı rengi. Örnek: #1F2937")
        self.row_foreground_input.textChanged.connect(self._refresh_preview)
        row_fg_wrap = QHBoxLayout()
        row_fg_wrap.addWidget(self.row_foreground_input, 1)
        row_fg_pick = QPushButton("Seç")
        row_fg_pick.clicked.connect(lambda: self._pick_color(self.row_foreground_input))
        row_fg_wrap.addWidget(row_fg_pick)
        row_fg_clear = QPushButton("Temizle")
        row_fg_clear.clicked.connect(lambda: self.row_foreground_input.clear())
        row_fg_wrap.addWidget(row_fg_clear)
        form.addRow("Yazı Rengi:", row_fg_wrap)

        self.preview_label = QLabel("Canlı Önizleme")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(36)
        form.addRow("Önizleme:", self.preview_label)

        layout.addLayout(form)
        self._refresh_preview()

        buttons = QHBoxLayout()
        buttons.addStretch(1)

        save_btn = QPushButton("Tamam")
        save_btn.clicked.connect(self.accept)
        buttons.addWidget(save_btn)

        cancel_btn = QPushButton("Kapat")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)

        layout.addLayout(buttons)

    def get_rule_payload(self) -> tuple[str, dict]:
        code = normalize_rule_code(self.code_input.text())
        label = self.label_input.text().strip().upper()
        payload = {
            "label": label,
            "prepend_to_title": self.prepend_checkbox.isChecked(),
            "append_to_title": self.append_checkbox.isChecked(),
            "dedupe_prefix_words": [
                part.strip().upper()
                for part in self.dedupe_input.text().split(",")
                if part.strip()
            ],
            "title_prefix": self.title_prefix_input.text().strip(),
            "title_suffix": self.title_suffix_input.text().strip(),
            "title_remove_phrases": [
                part.strip()
                for part in self.remove_phrases_input.text().split(",")
                if part.strip()
            ],
            "remove_trailing_numbers": self.remove_trailing_numbers_checkbox.isChecked(),
            "row_background": self.row_background_input.text().strip(),
            "row_foreground": self.row_foreground_input.text().strip(),
            "dynamic_title_rules": list(self.config.get("dynamic_title_rules", []) or []),
        }
        return code, payload

    def _pick_color(self, target_input: QLineEdit):
        initial = QColor(target_input.text().strip())
        selected = QColorDialog.getColor(initial if initial.isValid() else QColor(), self, "Renk Seç")
        if not selected.isValid():
            return
        target_input.setText(selected.name())

    def _refresh_preview(self):
        sample_text = "ÖRNEK HABER BAŞLIĞI"
        label = self.label_input.text().strip()
        if self.prepend_checkbox.isChecked() and label:
            sample_text = f"{label}-{sample_text}".strip()
        if self.append_checkbox.isChecked() and label:
            sample_text = f"{sample_text}-{label}".strip()
        prefix = self.title_prefix_input.text().strip()
        suffix = self.title_suffix_input.text().strip()
        if prefix:
            sample_text = f"{prefix} {sample_text}".strip()
        if suffix:
            sample_text = f"{sample_text}{suffix}".strip()
        self.preview_label.setText(sample_text)

        background = self.row_background_input.text().strip()
        foreground = self.row_foreground_input.text().strip()
        style_parts = []
        if background and QColor(background).isValid():
            style_parts.append(f"background:{background};")
        if foreground and QColor(foreground).isValid():
            style_parts.append(f"color:{foreground};")
        style_parts.append("padding:6px; border:1px solid #cbd5e1;")
        self.preview_label.setStyleSheet(" ".join(style_parts))


class RulesManagerDialog(QDialog):
    def __init__(self, current_channel: str = "A NEWS", parent=None):
        super().__init__(parent)
        self.resize(980, 720)

        self.current_channel = current_channel
        self.rules_data = get_all_rules()
        self._dirty = False
        self._loading_table = False
        self._current_code_configs: dict[str, dict] = {}
        self._current_channel_cleanup = dict(DEFAULT_TITLE_CLEANUP)
        self._current_scan_options = dict(DEFAULT_SCAN_OPTIONS)
        self._sort_column = 0
        self._sort_order = Qt.AscendingOrder
        self._settings = self._load_dialog_settings()

        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Kanal:"))

        self.channel_combo = QComboBox()
        self.channel_combo.addItems(self._available_channels())
        idx = self.channel_combo.findText(current_channel)
        if idx >= 0:
            self.channel_combo.setCurrentIndex(idx)
        self.channel_combo.currentTextChanged.connect(self._on_channel_changed)
        top_row.addWidget(self.channel_combo, 1)
        layout.addLayout(top_row)

        quick_add_row = QHBoxLayout()
        quick_add_row.addWidget(QLabel("Hızlı Ekle:"))

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Kanal kodu. Örnek: K STD, +SES, WEU")
        self.code_input.setClearButtonEnabled(True)
        quick_add_row.addWidget(self.code_input, 1)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Açıklama. Örnek: KONUK STÜDYO")
        self.desc_input.setClearButtonEnabled(True)
        quick_add_row.addWidget(self.desc_input, 2)

        self.quick_add_btn = QPushButton("Hızlı Ekle")
        self.quick_add_btn.clicked.connect(self.add_entry)
        quick_add_row.addWidget(self.quick_add_btn)

        layout.addLayout(quick_add_row)

        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("Filtre:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Kod veya açıklama ara...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.apply_filter)
        search_row.addWidget(self.search_input, 1)
        layout.addLayout(search_row)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Kanal Kodu",
            "Açıklama",
            "Başlığa Ekle",
            "Başlıktan Sil",
            "Sayı Sil",
            "Başa Yaz",
            "Sona Yaz",
        ])
        self.table.horizontalHeader().setSectionsMovable(True)
        for column in range(self.table.columnCount()):
            self.table.horizontalHeader().setSectionResizeMode(column, QHeaderView.Interactive)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.setSortingEnabled(False)
        self.table.horizontalHeader().sectionClicked.connect(self._sort_by_column)
        self.table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self._open_header_context_menu)
        self.table.horizontalHeader().sectionResized.connect(lambda *_: self._save_table_preferences())
        self.table.horizontalHeader().sectionMoved.connect(lambda *_: self._save_table_preferences())
        self.table.itemChanged.connect(self._on_item_changed)
        self.table.itemDoubleClicked.connect(lambda *_: self.open_selected_rule_details())
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._open_context_menu)
        layout.addWidget(self.table, 1)

        btn_row = QHBoxLayout()

        self.add_btn = QPushButton("Yeni Kanal Kodu Ekle")
        self.add_btn.clicked.connect(self.add_entry)
        btn_row.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Düzenle")
        self.edit_btn.clicked.connect(self.open_selected_rule_details)
        btn_row.addWidget(self.edit_btn)

        self.channel_rules_btn = QPushButton("Kanal Geneli Başlık Kuralları")
        self.channel_rules_btn.clicked.connect(self.open_channel_cleanup_dialog)
        btn_row.addWidget(self.channel_rules_btn)

        self.delete_btn = QPushButton("Seçili Satırı Sil")
        self.delete_btn.clicked.connect(self.delete_selected_row)
        btn_row.addWidget(self.delete_btn)

        btn_row.addStretch(1)

        self.save_btn = QPushButton("Kaydet")
        self.save_btn.clicked.connect(self.save_rules)
        btn_row.addWidget(self.save_btn)

        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.close_btn)

        layout.addLayout(btn_row)
        self.reload_channel()
        self._apply_table_preferences()

    def _load_dialog_settings(self) -> dict:
        parent = self.parent()
        if parent is not None and hasattr(parent, "settings"):
            return parent.settings
        return load_settings()

    def _persist_dialog_settings(self):
        parent = self.parent()
        if parent is not None and hasattr(parent, "schedule_settings_save"):
            parent.schedule_settings_save()
        else:
            save_settings(self._settings)

    def _save_table_preferences(self):
        self._settings["rules_table_widths"] = [
            int(self.table.columnWidth(column))
            for column in range(self.table.columnCount())
        ]
        self._settings["rules_table_hidden_columns"] = [
            column
            for column in range(self.table.columnCount())
            if self.table.isColumnHidden(column)
        ]
        self._persist_dialog_settings()

    def _apply_table_preferences(self):
        default_widths = [120, 220, 160, 180, 90, 90, 90]
        widths = self._settings.get("rules_table_widths", default_widths)
        if not isinstance(widths, list):
            widths = default_widths
        for column in range(self.table.columnCount()):
            width = widths[column] if column < len(widths) else default_widths[min(column, len(default_widths) - 1)]
            self.table.setColumnWidth(column, int(width))

        hidden = self._settings.get("rules_table_hidden_columns", [])
        if not isinstance(hidden, list):
            hidden = []
        for column in range(self.table.columnCount()):
            self.table.setColumnHidden(column, column in hidden)

    def _open_header_context_menu(self, pos):
        menu = QMenu(self)
        labels = [self.table.horizontalHeaderItem(column).text() for column in range(self.table.columnCount())]
        for column, label in enumerate(labels):
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(not self.table.isColumnHidden(column))
            action.toggled.connect(lambda checked, col=column: self._set_column_visible(col, checked))
            menu.addAction(action)
        menu.exec(self.table.horizontalHeader().viewport().mapToGlobal(pos))

    def _set_column_visible(self, column: int, visible: bool):
        self.table.setColumnHidden(column, not visible)
        self._save_table_preferences()

    def _update_window_title(self):
        title = "Kanal Kuralları"
        if self._dirty:
            title += " *"
        self.setWindowTitle(title)

    def _set_dirty(self, value: bool):
        self._dirty = bool(value)
        self._update_window_title()

    def _available_channels(self):
        channels = set(DEFAULT_CHANNELS)
        channels.update(self.rules_data.keys())
        return sorted(channels)

    def _ensure_channel_container(self, channel: str):
        if channel not in self.rules_data or not isinstance(self.rules_data[channel], dict):
            self.rules_data[channel] = {
                "codes": {},
                "news_codes": {},
                "title_cleanup": dict(DEFAULT_TITLE_CLEANUP),
                "scan_options": dict(DEFAULT_SCAN_OPTIONS),
            }
            return

        current = self.rules_data[channel]
        current.setdefault("codes", {})
        current.setdefault("news_codes", {})
        current.setdefault("title_cleanup", dict(DEFAULT_TITLE_CLEANUP))
        current.setdefault("scan_options", dict(DEFAULT_SCAN_OPTIONS))

    def _get_channel_codes(self, channel: str) -> dict[str, dict]:
        self._ensure_channel_container(channel)
        codes = self.rules_data[channel].get("codes", {})
        return dict(codes if isinstance(codes, dict) else {})

    def _get_channel_cleanup(self, channel: str) -> dict:
        self._ensure_channel_container(channel)
        cleanup = self.rules_data[channel].get("title_cleanup", {})
        return dict(cleanup if isinstance(cleanup, dict) else DEFAULT_TITLE_CLEANUP)

    def _get_channel_scan_options(self, channel: str) -> dict:
        self._ensure_channel_container(channel)
        options = self.rules_data[channel].get("scan_options", {})
        return dict(options if isinstance(options, dict) else DEFAULT_SCAN_OPTIONS)

    def _build_rule_summary(self, config: dict) -> tuple[str, str, str, str, str]:
        title_prefix = str(config.get("title_prefix", "") or "").strip()
        title_suffix = str(config.get("title_suffix", "") or "").strip()
        prefix_suffix = " / ".join(part for part in (title_prefix, title_suffix) if part)
        remove_phrases = ", ".join(config.get("title_remove_phrases", []) or [])
        remove_numbers = "Evet" if config.get("remove_trailing_numbers") else ""
        prepend_to_title = "Evet" if config.get("prepend_to_title") else ""
        append_to_title = "Evet" if config.get("append_to_title") else ""
        return prefix_suffix, remove_phrases, remove_numbers, prepend_to_title, append_to_title

    def _append_table_row(self, code: str, desc: str, config: dict | None = None):
        row = self.table.rowCount()
        self.table.insertRow(row)

        prefix_suffix, remove_phrases, remove_numbers, prepend_to_title, append_to_title = self._build_rule_summary(config or {})
        items = [
            QTableWidgetItem(normalize_rule_code(code)),
            QTableWidgetItem(str(desc or "").upper()),
            QTableWidgetItem(prefix_suffix),
            QTableWidgetItem(remove_phrases),
            QTableWidgetItem(remove_numbers),
            QTableWidgetItem(prepend_to_title),
            QTableWidgetItem(append_to_title),
        ]

        for column, item in enumerate(items):
            if column >= 2:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, column, item)

    def _find_row_by_code(self, code: str) -> int:
        normalized_code = normalize_rule_code(code)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and normalize_rule_code(item.text()) == normalized_code:
                return row
        return -1

    def _collect_codes_from_table(self) -> dict[str, dict]:
        collected = {}
        for row in range(self.table.rowCount()):
            code_item = self.table.item(row, 0)
            desc_item = self.table.item(row, 1)

            code = normalize_rule_code(code_item.text() if code_item else "")
            if not code:
                continue

            config = dict(DEFAULT_CODE_RULE)
            config.update(self._current_code_configs.get(code, {}))
            config["label"] = str(desc_item.text() if desc_item else "").strip().upper()
            collected[code] = config
        return collected

    def _move_row_to_bottom(self, row: int) -> int:
        if row < 0 or row >= self.table.rowCount():
            return row
        if row == self.table.rowCount() - 1:
            return row

        items = [self.table.takeItem(row, column) for column in range(self.table.columnCount())]
        self.table.removeRow(row)
        new_row = self.table.rowCount()
        self.table.insertRow(new_row)
        for column, item in enumerate(items):
            if item is not None:
                self.table.setItem(new_row, column, item)
        return new_row

    def _sort_by_column(self, column: int):
        if column == self._sort_column:
            self._sort_order = (
                Qt.DescendingOrder
                if self._sort_order == Qt.AscendingOrder
                else Qt.AscendingOrder
            )
        else:
            self._sort_column = column
            self._sort_order = Qt.AscendingOrder
        self.table.sortItems(column, self._sort_order)
        self._save_table_preferences()

    def _save_channel(self, channel: str, *, show_message: bool) -> bool:
        self._ensure_channel_container(channel)

        codes = self._collect_codes_from_table()
        news_codes = {
            code: str(config.get("label", "") or "").strip()
            for code, config in codes.items()
            if str(config.get("label", "") or "").strip()
        }

        self.rules_data[channel]["codes"] = codes
        self.rules_data[channel]["news_codes"] = news_codes
        self.rules_data[channel]["title_cleanup"] = dict(self._current_channel_cleanup)
        self.rules_data[channel]["scan_options"] = dict(self._current_scan_options)

        try:
            save_all_rules(self.rules_data)
        except (OSError, TypeError, ValueError) as exc:
            QMessageBox.critical(self, "Hata", f"Kayıt başarısız:\n{exc}")
            return False

        self.rules_data = get_all_rules()
        self._current_code_configs = self._get_channel_codes(channel)
        self._set_dirty(False)
        if show_message:
            QMessageBox.information(self, "Tamam", "Kanal kuralları kaydedildi.")
        return True

    def _maybe_save_before_close(self) -> bool:
        if not self._dirty:
            return True
        return self._save_channel(self.current_channel, show_message=False)

    def _on_channel_changed(self, new_channel: str):
        new_channel = str(new_channel or "").strip()
        if not new_channel or new_channel == self.current_channel:
            return

        if self._dirty and not self._save_channel(self.current_channel, show_message=False):
            self.channel_combo.blockSignals(True)
            previous_index = self.channel_combo.findText(self.current_channel)
            if previous_index >= 0:
                self.channel_combo.setCurrentIndex(previous_index)
            self.channel_combo.blockSignals(False)
            return

        self.current_channel = new_channel
        self.reload_channel()

    def reload_channel(self):
        channel = self.current_channel
        self._current_code_configs = self._get_channel_codes(channel)
        self._current_channel_cleanup = dict(DEFAULT_TITLE_CLEANUP)
        self._current_channel_cleanup.update(self._get_channel_cleanup(channel))
        self._current_scan_options = dict(DEFAULT_SCAN_OPTIONS)
        self._current_scan_options.update(self._get_channel_scan_options(channel))

        self._loading_table = True
        try:
            self.table.setRowCount(0)
            for code, config in sorted(self._current_code_configs.items(), key=lambda item: item[0].lower()):
                self._append_table_row(code, str(config.get("label", "") or ""), config)
        finally:
            self._loading_table = False

        self._set_dirty(False)
        self.apply_filter()

    def _open_context_menu(self, pos):
        menu = QMenu(self)

        add_action = QAction("Yeni Kanal Kodu Ekle", self)
        add_action.triggered.connect(self.add_entry)
        menu.addAction(add_action)

        edit_action = QAction("Düzenle", self)
        edit_action.triggered.connect(self.open_selected_rule_details)
        menu.addAction(edit_action)

        menu.addSeparator()

        channel_rules_action = QAction("Kanal Geneli Başlık Kuralları", self)
        channel_rules_action.triggered.connect(self.open_channel_cleanup_dialog)
        menu.addAction(channel_rules_action)

        menu.addSeparator()

        delete_action = QAction("Seçili Satırı Sil", self)
        delete_action.triggered.connect(self.delete_selected_row)
        menu.addAction(delete_action)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._loading_table:
            return

        row = item.row()
        if item.column() == 0:
            new_code = normalize_rule_code(item.text())
            item.setText(new_code)

            config = self._current_code_configs.pop(new_code, None)
            if config is None:
                old_keys = list(self._current_code_configs.keys())
                if 0 <= row < len(old_keys):
                    old_code = old_keys[row]
                    config = self._current_code_configs.pop(old_code, dict(DEFAULT_CODE_RULE))
                else:
                    config = dict(DEFAULT_CODE_RULE)
            self._current_code_configs[new_code] = config

        elif item.column() == 1:
            item.setText(item.text().strip().upper())
            code_item = self.table.item(row, 0)
            code = normalize_rule_code(code_item.text() if code_item else "")
            if code:
                self._current_code_configs.setdefault(code, dict(DEFAULT_CODE_RULE))
                self._current_code_configs[code]["label"] = item.text().strip().upper()

        self._set_dirty(True)

    def add_entry(self):
        quick_code = normalize_rule_code(self.code_input.text())
        quick_label = self.desc_input.text().strip().upper()

        if quick_code or quick_label:
            code = quick_code
            payload = dict(DEFAULT_CODE_RULE)
            payload["label"] = quick_label
        else:
            dialog = CodeRuleDialog(parent=self)
            if dialog.exec() != QDialog.Accepted:
                return
            code, payload = dialog.get_rule_payload()

        if not code:
            QMessageBox.information(self, "Bilgi", "Kanal kodu boş olamaz.")
            return

        if self.search_input.text().strip():
            self.search_input.clear()

        row = self._find_row_by_code(code)
        self._current_code_configs[code] = payload
        if row >= 0:
            self._loading_table = True
            try:
                self.table.item(row, 0).setText(code)
                self.table.item(row, 1).setText(payload["label"])
                prefix_suffix, remove_phrases, remove_numbers, prepend_to_title, append_to_title = self._build_rule_summary(payload)
                self.table.item(row, 2).setText(prefix_suffix)
                self.table.item(row, 3).setText(remove_phrases)
                self.table.item(row, 4).setText(remove_numbers)
                self.table.item(row, 5).setText(prepend_to_title)
                self.table.item(row, 6).setText(append_to_title)
            finally:
                self._loading_table = False
            row = self._move_row_to_bottom(row)
        else:
            self._append_table_row(code, payload["label"], payload)
            row = self.table.rowCount() - 1
        self._set_dirty(True)
        self.apply_filter()
        self.code_input.clear()
        self.desc_input.clear()
        self._save_table_preferences()

        if row >= 0:
            self.table.setCurrentCell(row, 0)
            self.table.selectRow(row)
            item = self.table.item(row, 0)
            if item is not None:
                self.table.scrollToItem(item)

    def open_selected_rule_details(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Bilgi", "Önce bir satır seç.")
            return

        code_item = self.table.item(row, 0)
        code = normalize_rule_code(code_item.text() if code_item else "")
        if not code:
            QMessageBox.information(self, "Bilgi", "Geçerli bir kanal kodu seç.")
            return

        config = dict(DEFAULT_CODE_RULE)
        config.update(self._current_code_configs.get(code, {}))
        config["label"] = str(self.table.item(row, 1).text() if self.table.item(row, 1) else "").strip().upper()

        dialog = CodeRuleDialog(code, config, self)
        if dialog.exec() != QDialog.Accepted:
            return

        new_code, payload = dialog.get_rule_payload()
        if not new_code:
            QMessageBox.information(self, "Bilgi", "Kanal kodu boş olamaz.")
            return

        if new_code != code:
            self._current_code_configs.pop(code, None)
        self._current_code_configs[new_code] = payload

        self._loading_table = True
        try:
            self.table.item(row, 0).setText(new_code)
            self.table.item(row, 1).setText(payload["label"])
            prefix_suffix, remove_phrases, remove_numbers, prepend_to_title, append_to_title = self._build_rule_summary(payload)
            self.table.item(row, 2).setText(prefix_suffix)
            self.table.item(row, 3).setText(remove_phrases)
            self.table.item(row, 4).setText(remove_numbers)
            self.table.item(row, 5).setText(prepend_to_title)
            self.table.item(row, 6).setText(append_to_title)
        finally:
            self._loading_table = False

        self._set_dirty(True)
        self._save_table_preferences()

    def open_channel_cleanup_dialog(self):
        dialog = ChannelTitleRulesDialog(
            self._current_channel_cleanup,
            self._current_scan_options,
            self,
        )
        if dialog.exec() != QDialog.Accepted:
            return

        cleanup, scan_options = dialog.get_values()
        self._current_channel_cleanup = cleanup
        self._current_scan_options = scan_options
        self._set_dirty(True)

    def delete_selected_row(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Bilgi", "Önce bir satır seç.")
            return

        code_item = self.table.item(row, 0)
        code = normalize_rule_code(code_item.text() if code_item else "")
        if code:
            self._current_code_configs.pop(code, None)

        self.table.removeRow(row)
        self._set_dirty(True)
        self._save_table_preferences()

    def apply_filter(self):
        needle = self.search_input.text().strip().lower()

        for row in range(self.table.rowCount()):
            code = self.table.item(row, 0).text().strip() if self.table.item(row, 0) else ""
            desc = self.table.item(row, 1).text().strip() if self.table.item(row, 1) else ""
            matched = (not needle) or (needle in code.lower()) or (needle in desc.lower())
            self.table.setRowHidden(row, not matched)

    def save_rules(self):
        self._save_channel(self.current_channel, show_message=True)

    def accept(self):
        self._save_table_preferences()
        if not self._maybe_save_before_close():
            return
        super().accept()

    def reject(self):
        self._save_table_preferences()
        if not self._maybe_save_before_close():
            return
        super().reject()
