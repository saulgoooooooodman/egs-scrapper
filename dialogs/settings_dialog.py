from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class SettingsDialog(QDialog):
    def __init__(self, settings: dict, channel_name: str, channel_scan_options: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayarlar")
        self.resize(820, 520)

        self._settings = dict(settings or {})
        self._channel_name = str(channel_name or "").strip()
        self._channel_scan_options = dict(channel_scan_options or {})

        root = QVBoxLayout(self)

        info = QLabel(
            "Bu pencere, programın sık kullanılan ayarlarını tek yerde toplar. "
            "Sol taraftan kategori seçebilir, sağ tarafta ilgili ayarları değiştirebilirsin."
        )
        info.setWordWrap(True)
        root.addWidget(info)

        content = QHBoxLayout()
        self.category_list = QListWidget()
        self.category_list.setMaximumWidth(220)
        self.pages = QStackedWidget()
        content.addWidget(self.category_list)
        content.addWidget(self.pages, 1)
        root.addLayout(content, 1)

        self._build_general_page()
        self._build_view_page()
        self._build_scan_page()
        self._build_spell_page()

        self.category_list.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.category_list.setCurrentRow(0)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _add_page(self, title: str, widget: QWidget):
        self.category_list.addItem(QListWidgetItem(title))
        self.pages.addWidget(widget)

    def _build_general_page(self):
        page = QWidget()
        form = QFormLayout(page)

        self.remember_profile_checkbox = QCheckBox("Profili hatırla")
        self.remember_profile_checkbox.setChecked(bool(self._settings.get("remember_me", False)))
        form.addRow("", self.remember_profile_checkbox)

        self.show_startup_checkbox = QCheckBox("Açılışta profil penceresini göster")
        self.show_startup_checkbox.setChecked(bool(self._settings.get("show_startup_wizard", True)))
        form.addRow("", self.show_startup_checkbox)

        self.remember_last_date_checkbox = QCheckBox("Kaldığım günü hatırla")
        self.remember_last_date_checkbox.setChecked(bool(self._settings.get("remember_last_date", False)))
        form.addRow("", self.remember_last_date_checkbox)

        self.empty_folder_warning_checkbox = QCheckBox("Kaynak klasör boşsa uyar")
        self.empty_folder_warning_checkbox.setChecked(not bool(self._settings.get("suppress_empty_folder_warning", False)))
        form.addRow("", self.empty_folder_warning_checkbox)

        self.always_on_top_checkbox = QCheckBox("Pencereyi her zaman üstte göster")
        self.always_on_top_checkbox.setChecked(bool(self._settings.get("always_on_top", False)))
        form.addRow("", self.always_on_top_checkbox)

        self.remember_window_checkbox = QCheckBox("Pencere boyutu ve konumunu hatırla")
        self.remember_window_checkbox.setChecked(bool(self._settings.get("remember_window_geometry", False)))
        form.addRow("", self.remember_window_checkbox)

        self._add_page("Genel", page)

    def _build_view_page(self):
        page = QWidget()
        form = QFormLayout(page)

        self.hide_code_checkbox = QCheckBox("Haber kodu sütununu gizle")
        hidden_columns = self._settings.get("main_hidden_columns", [])
        if not isinstance(hidden_columns, list):
            hidden_columns = []
        self.hide_code_checkbox.setChecked(0 in hidden_columns or bool(self._settings.get("main_hide_code_column", False)))
        form.addRow("", self.hide_code_checkbox)

        self.hide_desc_checkbox = QCheckBox("Açıklama sütununu gizle")
        self.hide_desc_checkbox.setChecked(1 in hidden_columns)
        form.addRow("", self.hide_desc_checkbox)

        self.hide_title_checkbox = QCheckBox("Haber sütununu gizle")
        self.hide_title_checkbox.setChecked(2 in hidden_columns)
        form.addRow("", self.hide_title_checkbox)

        self.show_corrected_titles_checkbox = QCheckBox("Listede düzeltilmiş başlığı göster")
        self.show_corrected_titles_checkbox.setChecked(bool(self._settings.get("show_corrected_titles_in_list", False)))
        form.addRow("", self.show_corrected_titles_checkbox)

        self.hide_previous_checkbox = QCheckBox("Eski haberleri gizle")
        hide_previous = bool(self._settings.get("hide_previous_day_news", not bool(self._settings.get("show_previous_day_news", True))))
        self.hide_previous_checkbox.setChecked(hide_previous)
        form.addRow("", self.hide_previous_checkbox)

        self.duplicate_mode_combo = QComboBox()
        self.duplicate_mode_combo.addItem("Tümünü Göster", "off")
        self.duplicate_mode_combo.addItem("Aynı başlıklarda en yeniyi bırak", "latest")
        self.duplicate_mode_combo.addItem("Aynı başlıklarda en eskiyi bırak", "oldest")
        current_mode = str(self._settings.get("main_duplicate_mode", "off"))
        for index in range(self.duplicate_mode_combo.count()):
            if self.duplicate_mode_combo.itemData(index) == current_mode:
                self.duplicate_mode_combo.setCurrentIndex(index)
                break
        form.addRow("Aynı Haber Başlıkları:", self.duplicate_mode_combo)

        self.news_list_font_spin = QSpinBox()
        self.news_list_font_spin.setRange(9, 22)
        self.news_list_font_spin.setValue(int(self._settings.get("news_list_font_size", 11)))
        form.addRow("Haber Listesi Yazı Boyutu:", self.news_list_font_spin)

        self.preview_font_spin = QSpinBox()
        self.preview_font_spin.setRange(9, 22)
        self.preview_font_spin.setValue(int(self._settings.get("preview_text_font_size", 11)))
        form.addRow("Haber Metni Yazı Boyutu:", self.preview_font_spin)

        self._add_page("Görünüm", page)

    def _build_scan_page(self):
        page = QWidget()
        form = QFormLayout(page)

        self.live_watch_checkbox = QCheckBox("Canlı izlemeyi aç")
        self.live_watch_checkbox.setChecked(bool(self._settings.get("live_watch_enabled", False)))
        form.addRow("", self.live_watch_checkbox)

        self.symbol_hide_checkbox = QCheckBox(f"Sembol ile başlayan başlıkları gizle ({self._channel_name})")
        self.symbol_hide_checkbox.setChecked(bool(self._channel_scan_options.get("hide_symbol_prefixed_titles", True)))
        form.addRow("", self.symbol_hide_checkbox)

        note = QLabel(
            "Not: Bu bölümdeki sembol ayarı yalnızca seçili kanal için geçerlidir. "
            "Gerçek haber kodu olarak tanımlanmış sembollü kodlar bu gizleme kuralına takılmaz."
        )
        note.setWordWrap(True)
        form.addRow("", note)

        self._add_page("Tarama", page)

    def _build_spell_page(self):
        page = QWidget()
        form = QFormLayout(page)

        self.spell_mode_combo = QComboBox()
        self.spell_mode_combo.addItem("Kapalı", "off")
        self.spell_mode_combo.addItem("Elle", "manual")
        self.spell_mode_combo.addItem("Otomatik", "auto")

        current_mode = str(
            self._settings.get(
                "title_spellcheck_mode",
                "auto" if bool(self._settings.get("auto_title_spellcheck", True)) else "manual",
            )
        )
        for index in range(self.spell_mode_combo.count()):
            if self.spell_mode_combo.itemData(index) == current_mode:
                self.spell_mode_combo.setCurrentIndex(index)
                break

        form.addRow("Haber Başlığı Yazım Denetimi:", self.spell_mode_combo)

        note = QLabel(
            "Otomatik: yeni okunan başlıklara kendisi uygular. "
            "Elle: yalnızca sağ tık bağlam menüsünden siz istediğinizde çalışır. "
            "Kapalı: yazım denetimi uygulanmaz."
        )
        note.setWordWrap(True)
        form.addRow("", note)

        self._add_page("Yazım", page)

    def get_values(self) -> tuple[dict, dict]:
        updated_settings = dict(self._settings)
        updated_settings["remember_me"] = self.remember_profile_checkbox.isChecked()
        updated_settings["show_startup_wizard"] = self.show_startup_checkbox.isChecked()
        updated_settings["remember_last_date"] = self.remember_last_date_checkbox.isChecked()
        updated_settings["suppress_empty_folder_warning"] = not self.empty_folder_warning_checkbox.isChecked()
        updated_settings["always_on_top"] = self.always_on_top_checkbox.isChecked()
        updated_settings["remember_window_geometry"] = self.remember_window_checkbox.isChecked()
        hidden_columns = []
        if self.hide_code_checkbox.isChecked():
            hidden_columns.append(0)
        if self.hide_desc_checkbox.isChecked():
            hidden_columns.append(1)
        if self.hide_title_checkbox.isChecked():
            hidden_columns.append(2)
        updated_settings["main_hidden_columns"] = hidden_columns
        updated_settings["main_hide_code_column"] = 0 in hidden_columns
        updated_settings["show_corrected_titles_in_list"] = self.show_corrected_titles_checkbox.isChecked()
        updated_settings["hide_previous_day_news"] = self.hide_previous_checkbox.isChecked()
        updated_settings["show_previous_day_news"] = not self.hide_previous_checkbox.isChecked()
        updated_settings["main_duplicate_mode"] = self.duplicate_mode_combo.currentData()
        updated_settings["news_list_font_size"] = int(self.news_list_font_spin.value())
        updated_settings["preview_text_font_size"] = int(self.preview_font_spin.value())
        updated_settings["live_watch_enabled"] = self.live_watch_checkbox.isChecked()
        updated_settings["title_spellcheck_mode"] = str(self.spell_mode_combo.currentData() or "manual")
        updated_settings["auto_title_spellcheck"] = updated_settings["title_spellcheck_mode"] == "auto"

        channel_scan_options = dict(self._channel_scan_options)
        channel_scan_options["hide_symbol_prefixed_titles"] = self.symbol_hide_checkbox.isChecked()
        return updated_settings, channel_scan_options
