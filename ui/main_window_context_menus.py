from __future__ import annotations

import os
import subprocess

from PySide6.QtWidgets import QMenu, QMessageBox, QTextEdit
from PySide6.QtGui import QAction
from core.shell_utils import show_file_in_explorer
from core.text_utils import transform_case_for_channel


def show_header_context_menu(self, pos):
    header = self.news_view.horizontalHeader()
    global_pos = header.mapToGlobal(pos)

    menu = QMenu(self)
    columns = [
        (0, "Kod"),
        (1, "Açıklama"),
        (2, "Haber"),
    ]

    for column, label in columns:
        action = QAction(f"{label} sütununu göster", self)
        action.setCheckable(True)
        action.setChecked(not self.news_view.isColumnHidden(column))
        action.triggered.connect(
            lambda checked=False, column=column: self.set_column_visibility(column, checked)
        )
        menu.addAction(action)
    menu.exec(global_pos)


def show_news_context_menu(self, pos):
    index = self.news_view.indexAt(pos)
    if not index.isValid():
        return

    row = index.row()
    self.news_view.setCurrentIndex(self.news_model.index(row, 2))
    self.news_view.clearSelection()
    self.news_view.selectRow(row)

    data = self.news_model.item_at(row)
    if not data:
        return

    current_code = str(data.get("news_code", "") or "").strip()

    menu = QMenu(self)

    refresh_action = QAction("Sayfayı Yenile", self)
    refresh_action.triggered.connect(self.load_news)
    menu.addAction(refresh_action)

    force_refresh_action = QAction("Veritabanını Güncelle", self)
    force_refresh_action.triggered.connect(lambda: self.load_news(force_refresh=True))
    menu.addAction(force_refresh_action)

    refresh_selected_action = QAction("Seçili Haberi Güncelle", self)
    refresh_selected_action.triggered.connect(self.refresh_selected_news_from_source)
    menu.addAction(refresh_selected_action)

    menu.addSeparator()

    open_source_action = QAction("Kaynağı Klasörde Göster", self)
    open_source_action.triggered.connect(lambda: open_source_file(self, data))
    menu.addAction(open_source_action)

    copy_action = QAction("Metni Kopyala", self)
    copy_action.triggered.connect(self.copy_current_item)
    menu.addAction(copy_action)

    current_settings = getattr(self, "settings", {}) or {}
    spell_mode = str(current_settings.get("title_spellcheck_mode", "auto")).lower()

    if spell_mode in {"auto", "manual"} and hasattr(self, "apply_spellcheck_to_selected_news"):
        spell_action = QAction("Yazımı Düzelt", self)
        spell_action.triggered.connect(self.apply_spellcheck_to_selected_news)
        menu.addAction(spell_action)

    if spell_mode in {"auto", "manual"} and hasattr(self, "revert_spellcheck_for_selected_news"):
        revert_spell_action = QAction("Yazımı Geri Al", self)
        revert_spell_action.triggered.connect(self.revert_spellcheck_for_selected_news)
        menu.addAction(revert_spell_action)

    if current_code:
        menu.addSeparator()

        hide_code_action = QAction(f"Haber Kodunu Gizle ({current_code})", self)
        hide_code_action.triggered.connect(lambda _=False, code=current_code: self.hide_news_code(code))
        menu.addAction(hide_code_action)

        show_only_code_action = QAction(f"Yalnızca Bu Haber Kodunu Göster ({current_code})", self)
        show_only_code_action.triggered.connect(lambda _=False, code=current_code: self.show_only_news_code(code))
        menu.addAction(show_only_code_action)

        undo_filter_action = QAction("Filtreyi Geri Al", self)
        undo_filter_action.triggered.connect(self.undo_code_filter)
        menu.addAction(undo_filter_action)

        clear_filters_action = QAction("Filtreleri Temizle", self)
        clear_filters_action.triggered.connect(self.clear_code_filters)
        menu.addAction(clear_filters_action)

        color_menu = menu.addMenu("Renklendir")

        code_bg_action = QAction(f"{current_code} Satır Rengi...", self)
        code_bg_action.triggered.connect(lambda _=False, code=current_code: self.set_code_background_color(code))
        color_menu.addAction(code_bg_action)

        code_fg_action = QAction(f"{current_code} Yazı Rengi...", self)
        code_fg_action.triggered.connect(lambda _=False, code=current_code: self.set_code_foreground_color(code))
        color_menu.addAction(code_fg_action)

        clear_code_color_action = QAction(f"{current_code} Rengini Temizle", self)
        clear_code_color_action.triggered.connect(lambda _=False, code=current_code: self.clear_code_style(code))
        color_menu.addAction(clear_code_color_action)

        if data.get("_is_previous_day"):
            color_menu.addSeparator()

            old_bg_action = QAction("Eski Haber Satır Rengi...", self)
            old_bg_action.triggered.connect(self.set_old_news_background_color)
            color_menu.addAction(old_bg_action)

            old_fg_action = QAction("Eski Haber Yazı Rengi...", self)
            old_fg_action.triggered.connect(self.set_old_news_foreground_color)
            color_menu.addAction(old_fg_action)

            clear_old_color_action = QAction("Eski Haber Rengini Temizle", self)
            clear_old_color_action.triggered.connect(self.clear_old_news_style)
            color_menu.addAction(clear_old_color_action)

    menu.exec(self.news_view.viewport().mapToGlobal(pos))


def show_preview_context_menu(self, pos):
    text_edit = self.preview_text
    _show_text_context_menu(
        self,
        text_edit,
        text_edit.mapToGlobal(pos),
        include_save=True,
        include_find_replace=True,
    )


def show_readonly_text_context_menu(text_edit: QTextEdit, pos, parent=None):
    _show_text_context_menu(
        parent or text_edit,
        text_edit,
        text_edit.mapToGlobal(pos),
        include_save=False,
        include_find_replace=False,
    )


def _show_text_context_menu(self, text_edit: QTextEdit, global_pos, include_save=False, include_find_replace=False):
    menu = QMenu(self)

    undo_action = QAction("Geri Al", self)
    undo_action.setEnabled((not text_edit.isReadOnly()) and text_edit.document().isUndoAvailable())
    undo_action.triggered.connect(text_edit.undo)
    menu.addAction(undo_action)

    redo_action = QAction("Yinele", self)
    redo_action.setEnabled((not text_edit.isReadOnly()) and text_edit.document().isRedoAvailable())
    redo_action.triggered.connect(text_edit.redo)
    menu.addAction(redo_action)

    menu.addSeparator()

    cut_action = QAction("Kes", self)
    cut_action.setEnabled((not text_edit.isReadOnly()) and text_edit.textCursor().hasSelection())
    cut_action.triggered.connect(text_edit.cut)
    menu.addAction(cut_action)

    copy_action = QAction("Kopyala", self)
    copy_action.setEnabled(bool(text_edit.textCursor().hasSelection() or text_edit.toPlainText().strip()))
    copy_action.triggered.connect(lambda: _copy_text(text_edit))
    menu.addAction(copy_action)

    paste_action = QAction("Yapıştır", self)
    paste_action.setEnabled(not text_edit.isReadOnly())
    paste_action.triggered.connect(text_edit.paste)
    menu.addAction(paste_action)

    delete_action = QAction("Sil", self)
    delete_action.setEnabled((not text_edit.isReadOnly()) and text_edit.textCursor().hasSelection())
    delete_action.triggered.connect(lambda: _delete_selected_text(text_edit))
    menu.addAction(delete_action)

    menu.addSeparator()

    select_all_action = QAction("Tümünü Seç", self)
    select_all_action.triggered.connect(text_edit.selectAll)
    menu.addAction(select_all_action)

    if include_find_replace and hasattr(self, "open_find_replace_dialog"):
        menu.addSeparator()
        find_replace_action = QAction("Bul / Değiştir...", self)
        find_replace_action.triggered.connect(self.open_find_replace_dialog)
        menu.addAction(find_replace_action)

    if not text_edit.isReadOnly():
        case_menu = menu.addMenu("Harfleri Çevir")

        upper_action = QAction("TÜMÜNÜ BÜYÜK", self)
        upper_action.triggered.connect(lambda: _transform_text(self, text_edit, "upper"))
        case_menu.addAction(upper_action)

        lower_action = QAction("tümünü küçük", self)
        lower_action.triggered.connect(lambda: _transform_text(self, text_edit, "lower"))
        case_menu.addAction(lower_action)

        title_action = QAction("İlk Harfler Büyük", self)
        title_action.triggered.connect(lambda: _transform_text(self, text_edit, "title"))
        case_menu.addAction(title_action)

    if include_save and hasattr(self, "save_edited_text"):
        menu.addSeparator()
        save_action = QAction("Kaydet", self)
        save_action.triggered.connect(self.save_edited_text)
        menu.addAction(save_action)

    menu.exec(global_pos)


def _delete_selected_text(text_edit: QTextEdit):
    cursor = text_edit.textCursor()
    if cursor.hasSelection():
        cursor.removeSelectedText()


def _copy_text(text_edit: QTextEdit):
    cursor = text_edit.textCursor()
    if cursor.hasSelection():
        text_edit.copy()
        return

    text = text_edit.toPlainText()
    if text.strip():
        text_edit.selectAll()
        text_edit.copy()
        cursor.clearSelection()
        text_edit.setTextCursor(cursor)


def _transform_text(owner, text_edit: QTextEdit, mode: str):
    cursor = text_edit.textCursor()
    text = cursor.selectedText() if cursor.hasSelection() else text_edit.toPlainText()
    channel_name = getattr(owner, "channel_name", "")
    transformed = transform_case_for_channel(text, mode, channel_name)

    if cursor.hasSelection():
        cursor.insertText(transformed)
    else:
        text_edit.setPlainText(transformed)


def open_source_file(self, data: dict):
    path = (data.get("path") or "").strip()
    if not path:
        QMessageBox.warning(self, "Uyarı", "Kaynak dosya yolu bulunamadı.")
        return

    file_path = os.path.normpath(path)
    if not os.path.exists(file_path):
        QMessageBox.warning(self, "Uyarı", f"Dosya bulunamadı:\n{file_path}")
        return

    try:
        show_file_in_explorer(file_path)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        QMessageBox.critical(self, "Hata", f"Kaynak açılamadı:\n{exc}")
