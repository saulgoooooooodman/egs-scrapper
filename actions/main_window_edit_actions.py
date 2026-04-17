import re

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QTextCursor, QTextDocument
from PySide6.QtCore import QItemSelectionModel

from dialogs.find_replace_dialog import FindReplaceDialog
from dialogs.title_dictionary_manager import TitleDictionaryManagerDialog
from dictionaries.dictionary_store import add_title_dictionary_entry
from data.database import upsert_news
from core.text_utils import lower_tr, title_tr, upper_tr


class MainWindowEditActions:
    def open_find_replace_dialog(self):
        selected_rows = self.news_view.selectionModel().selectedRows()
        selected_count = len(selected_rows)
        current_item = self.news_model.item_at(self.news_view.currentIndex().row()) if self.news_view.currentIndex().isValid() else None
        selected_items = self.news_model.items_at_rows([index.row() for index in selected_rows]) if selected_rows else []

        scope_samples = {
            "preview_text": self.preview_text.toPlainText(),
            "selected_text": "\n\n".join(item.get("final_text", "") for item in selected_items),
            "filtered_text": "\n\n".join(item.get("final_text", "") for item in self.filtered_items),
            "current_title": current_item.get("title", "") if current_item else "",
            "selected_title": "\n".join(item.get("title", "") for item in selected_items),
            "all_titles": "\n".join(item.get("title", "") for item in self.news_items),
        }
        dialog = FindReplaceDialog(
            scope_samples,
            self.channel_name,
            self,
            selected_count=selected_count,
            filtered_count=len(self.filtered_items),
            total_count=len(self.news_items),
        )
        if dialog.exec():
            find_text = dialog.get_find_text()
            replace_text = dialog.get_replace_text()
            scope = dialog.get_scope()
            use_regex = dialog.use_regex()

            if not find_text:
                self.status_label.setText("Bul alanı boş bırakılamaz")
                return

            try:
                changed = self._apply_find_replace(find_text, replace_text, scope, use_regex, dialog.get_result_text())
            except re.error as exc:
                QMessageBox.warning(self, "Regex", f"Geçersiz regex:\n{exc}")
                return

            if dialog.should_add_to_dictionary() and replace_text.strip():
                add_title_dictionary_entry(
                    self.channel_name,
                    find_text.strip(),
                    replace_text.strip(),
                    use_common=False,
                )

            self.status_label.setText(f"Bul / Değiştir uygulandı | Güncellenen: {changed}")

    def _replace_text_value(self, source_text: str, find_text: str, replace_text: str, use_regex: bool) -> str:
        if use_regex:
            return re.sub(find_text, replace_text, source_text, flags=re.IGNORECASE)
        return source_text.replace(find_text, replace_text)

    def _apply_title_replace(self, item: dict, find_text: str, replace_text: str, use_regex: bool) -> bool:
        original = item.get("title", "") or ""
        updated = self._replace_text_value(original, find_text, replace_text, use_regex)
        if updated == original:
            return False

        item["title"] = updated
        item["corrected_title"] = ""

        final_text = item.get("final_text", "") or ""
        if final_text:
            lines = final_text.splitlines()
            if lines:
                lines[0] = updated
                item["final_text"] = "\n".join(lines)

        return True

    def _apply_find_replace(self, find_text: str, replace_text: str, scope: str, use_regex: bool, preview_result: str) -> int:
        if scope == "preview_text":
            self.preview_text.setPlainText(preview_result)
            index = self.news_view.currentIndex()
            if index.isValid():
                item = self.news_model.item_at(index.row())
                if item:
                    item["final_text"] = preview_result
            return 1

        current_item = None
        current_index = self.news_view.currentIndex()
        if current_index.isValid():
            current_item = self.news_model.item_at(current_index.row())

        if scope == "selected_text":
            rows = [index.row() for index in self.news_view.selectionModel().selectedRows()]
            targets = self.news_model.items_at_rows(rows)
            field = "text"
        elif scope == "filtered_text":
            targets = list(self.filtered_items)
            field = "text"
        elif scope == "current_title":
            targets = [current_item] if current_item else []
            field = "title"
        elif scope == "selected_title":
            rows = [index.row() for index in self.news_view.selectionModel().selectedRows()]
            targets = self.news_model.items_at_rows(rows)
            field = "title"
        elif scope == "all_titles":
            targets = list(self.news_items)
            field = "title"
        else:
            targets = []
            field = "text"

        changed = 0

        for item in targets:
            if not item:
                continue

            if field == "title":
                was_changed = self._apply_title_replace(item, find_text, replace_text, use_regex)
            else:
                original = item.get("final_text", "") or ""
                updated = self._replace_text_value(original, find_text, replace_text, use_regex)
                if updated == original:
                    continue
                item["final_text"] = updated
                was_changed = True

            if not was_changed:
                continue

            upsert_news(self.channel_name, item)
            changed += 1

            if item is current_item:
                if field == "title":
                    corrected = item.get("corrected_title", "").strip()
                    if corrected and corrected != item.get("title", ""):
                        self.preview_title.setText(corrected)
                        self.preview_corrected_title.setText(f"(Orijinal: {item.get('title', '')})")
                    else:
                        self.preview_title.setText(item.get("title", ""))
                        self.preview_corrected_title.setText("")
                    self.preview_text.setPlainText(item.get("final_text", ""))
                else:
                    self.preview_text.setPlainText(item.get("final_text", ""))

        if changed:
            self.apply_filters()
        return changed

    def open_title_dictionary_manager(self):
        dialog = TitleDictionaryManagerDialog(self.channel_name, self)
        dialog.exec()
        self.load_news(force_refresh=True)

    def safe_copy_to_clipboard(self, text: str) -> bool:
        try:
            QApplication.clipboard().setText(text)
            return True
        except Exception:
            return False

    def copy_from_preview(self):
        cursor = self.preview_text.textCursor()
        selected_text = cursor.selectedText()

        if selected_text:
            QApplication.clipboard().setText(selected_text)
            self.status_label.setText("Seçili metin panoya kopyalandı")
        else:
            full_text = self.preview_text.toPlainText()
            if full_text.strip():
                QApplication.clipboard().setText(full_text)
                self.status_label.setText("Tüm metin panoya kopyalandı")

    def copy_full_current_news_from_title(self, event):
        selected_rows = self.news_view.selectionModel().selectedRows()

        if not selected_rows:
            return

        if len(selected_rows) == 1:
            item = self.news_model.item_at(selected_rows[0].row())
            if not item:
                return

            text = self.preview_text.toPlainText().strip() or item.get("final_text", "").strip()
            if text:
                QApplication.clipboard().setText(text)
                self.status_label.setText("Tüm haber metni panoya kopyalandı")
            return

        items = self.news_model.items_at_rows([idx.row() for idx in selected_rows])
        texts = [item.get("final_text", "").strip() for item in items if item.get("final_text", "").strip()]
        if texts:
            QApplication.clipboard().setText("\n\n".join(texts))
            self.status_label.setText(f"{len(texts)} haber metni panoya kopyalandı")

    def copy_current_item(self):
        selected_rows = self.news_view.selectionModel().selectedRows()

        if not selected_rows:
            self.status_label.setText("Önce bir haber seç")
            return

        if len(selected_rows) == 1:
            item = self.news_model.item_at(selected_rows[0].row())
            if not item:
                return

            if self.safe_copy_to_clipboard(item.get("final_text", "")):
                self.status_label.setText("Metin panoya kopyalandı")
            else:
                self.status_label.setText("Pano şu anda meşgul, tekrar deneyin")
            return

        items = self.news_model.items_at_rows([idx.row() for idx in selected_rows])
        texts = [item.get("final_text", "").strip() for item in items if item.get("final_text", "").strip()]
        joined = "\n\n".join(texts)

        if self.safe_copy_to_clipboard(joined):
            self.status_label.setText(f"{len(texts)} haber metni panoya kopyalandı")
        else:
            self.status_label.setText("Pano şu anda meşgul, tekrar deneyin")

    def copy_active_context(self):
        if self.preview_text.hasFocus():
            self.copy_from_preview()
        else:
            self.copy_current_item()

    def on_item_double_clicked_copy(self, item, column):
        pass

    def cut_text(self):
        if self.preview_text.hasFocus():
            self.preview_text.cut()

    def paste_text(self):
        if self.preview_text.hasFocus():
            self.preview_text.paste()

    def select_all_text(self):
        if self.preview_text.hasFocus():
            self.preview_text.selectAll()
        else:
            self.news_view.selectAll()

    def delete_selected_text(self):
        if self.preview_text.hasFocus():
            cursor = self.preview_text.textCursor()
            if cursor.hasSelection():
                cursor.removeSelectedText()

    def undo_text(self):
        if self.preview_text.hasFocus():
            self.preview_text.undo()

    def redo_text(self):
        if self.preview_text.hasFocus():
            self.preview_text.redo()

    def to_upper(self):
        if self.preview_text.hasFocus():
            cursor = self.preview_text.textCursor()
            text = cursor.selectedText() if cursor.hasSelection() else self.preview_text.toPlainText()
            text = upper_tr(text)
            if cursor.hasSelection():
                cursor.insertText(text)
            else:
                self.preview_text.setPlainText(text)

    def to_lower(self):
        if self.preview_text.hasFocus():
            cursor = self.preview_text.textCursor()
            text = cursor.selectedText() if cursor.hasSelection() else self.preview_text.toPlainText()
            text = lower_tr(text)
            if cursor.hasSelection():
                cursor.insertText(text)
            else:
                self.preview_text.setPlainText(text)

    def to_title_case(self):
        if self.preview_text.hasFocus():
            cursor = self.preview_text.textCursor()
            text = cursor.selectedText() if cursor.hasSelection() else self.preview_text.toPlainText()
            text = title_tr(text)
            if cursor.hasSelection():
                cursor.insertText(text)
            else:
                self.preview_text.setPlainText(text)

    def focus_preview_text(self):
        self.preview_text.setFocus()

    def _find_in_preview(self, backward: bool = False):
        needle = self.search_input.text().strip()
        if not needle:
            self.focus_search()
            return

        if bool(self.search_regex_checkbox.isChecked()):
            self._find_regex_in_preview(needle, backward)
            return

        flags = QTextDocument.FindBackward if backward else QTextDocument.FindFlags()
        found = self.preview_text.find(needle, flags)
        if not found:
            cursor = self.preview_text.textCursor()
            cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start)
            self.preview_text.setTextCursor(cursor)
            self.preview_text.find(needle, flags)

    def _find_regex_in_preview(self, needle: str, backward: bool = False):
        try:
            regex = re.compile(needle, re.IGNORECASE)
        except re.error:
            self.status_label.setText("Geçersiz regex ifadesi")
            return

        text = self.preview_text.toPlainText()
        cursor = self.preview_text.textCursor()
        current_pos = cursor.selectionStart() if backward else cursor.selectionEnd()

        matches = list(regex.finditer(text))
        if not matches:
            self.status_label.setText("Eşleşme bulunamadı")
            return

        target = None
        if backward:
            for match in reversed(matches):
                if match.start() < current_pos:
                    target = match
                    break
            if target is None:
                target = matches[-1]
        else:
            for match in matches:
                if match.start() > current_pos:
                    target = match
                    break
            if target is None:
                target = matches[0]

        highlight = self.preview_text.textCursor()
        highlight.setPosition(target.start())
        highlight.setPosition(target.end(), QTextCursor.KeepAnchor)
        self.preview_text.setTextCursor(highlight)

    def find_next_in_preview(self):
        self._find_in_preview(backward=False)

    def find_prev_in_preview(self):
        self._find_in_preview(backward=True)

    def save_edited_text(self):
        index = self.news_view.currentIndex()
        if not index.isValid():
            self.status_label.setText("Kaydetmek için önce bir haber seç")
            return

        data = self.news_model.item_at(index.row())
        if not data:
            return

        edited_text = self.preview_text.toPlainText().strip()
        if not edited_text:
            QMessageBox.warning(self, "Uyarı", "Boş metin kaydedilemez.")
            return

        data["final_text"] = edited_text
        upsert_news(self.channel_name, data)
        self.status_label.setText("Düzenlenmiş haber metni kaydedildi")

    def select_same_codes(self):
        selected_rows = self.news_view.selectionModel().selectedRows()
        if not selected_rows:
            self.status_label.setText("Önce bir haber seç")
            return

        first_item = self.news_model.item_at(selected_rows[0].row())
        if not first_item:
            return

        target_code = first_item.get("news_code", "")

        self.news_view.clearSelection()
        selection_model = self.news_view.selectionModel()
        model = self.news_view.model()

        for row in range(self.news_model.rowCount()):
            item = self.news_model.item_at(row)
            if item and item.get("news_code", "") == target_code:
                left_index = model.index(row, 0)
                selection_model.select(left_index, QItemSelectionModel.Select | QItemSelectionModel.Rows)

        self.status_label.setText(f"Aynı koda sahip haberler seçildi: {target_code}")

    def select_other_codes(self):
        selected_rows = self.news_view.selectionModel().selectedRows()
        if not selected_rows:
            self.status_label.setText("Önce bir haber seç")
            return

        first_item = self.news_model.item_at(selected_rows[0].row())
        if not first_item:
            return

        target_code = first_item.get("news_code", "")

        self.news_view.clearSelection()
        selection_model = self.news_view.selectionModel()
        model = self.news_view.model()

        for row in range(self.news_model.rowCount()):
            item = self.news_model.item_at(row)
            if item and item.get("news_code", "") != target_code:
                left_index = model.index(row, 0)
                selection_model.select(left_index, QItemSelectionModel.Select | QItemSelectionModel.Rows)

        self.status_label.setText(f"{target_code} dışındaki haberler seçildi")
