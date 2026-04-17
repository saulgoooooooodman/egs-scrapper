import logging
import sqlite3
import traceback

from PySide6.QtWidgets import QDialog, QMessageBox

from dialogs.backfill_dialog import BackfillDialog
from dialogs.startup_dialog import StartupDialog
from core.settings_manager import save_settings
from parsing.backfill_worker import BackfillWorker
from parsing.scanner import scan_news_files
from data.database import (
    clear_cache_for_channel,
    connect_db,
    get_news_count_for_month,
    get_news_for_date,
    get_db_path,
    init_db,
    upsert_news,
)
from data.cache_manager import ensure_cache_table, is_cached, update_cache, clear_cache
from parsing.news_worker import NewsLoadWorker
from parsing.worker_manager import WorkerManager
from dictionaries.title_spellcheck import get_spell_backend_status_text


class MainWindowDataActions(WorkerManager):
    def _next_load_token(self) -> int:
        token = getattr(self, "_load_request_token", 0) + 1
        self._load_request_token = token
        self._active_load_token = token
        return token

    def _is_current_worker_signal(self) -> bool:
        sender = self.sender()
        sender_token = getattr(sender, "_load_token", None)
        active_token = getattr(self, "_active_load_token", None)
        if sender_token is None or active_token is None:
            return True
        return sender_token == active_token

    def _get_sender_load_context(self) -> tuple[str, str, str]:
        sender = self.sender()
        iso_date = getattr(sender, "_iso_date", self.date_edit.date().toString("yyyy-MM-dd"))
        date_str = getattr(sender, "_date_str", self.date_edit.date().toString("dd.MM.yyyy"))
        channel_name = getattr(sender, "_channel_name", self.channel_name)
        return channel_name, iso_date, date_str

    def _normalize_news_code(self, code) -> str:
        return str(code or "").strip().upper()

    def _should_hide_previous_day_item(self, item: dict) -> bool:
        if self.settings.get("show_previous_day_news", True):
            return False

        from parsing.parser import extract_story_day_from_name

        file_name = item.get("file_name", "") or item.get("path", "")
        story_day = extract_story_day_from_name(file_name)
        if not story_day:
            return False

        selected_date = self.date_edit.date()
        previous_day = selected_date.addDays(-1).day()
        return story_day == previous_day and story_day != selected_date.day()

    def _close_active_connection(self):
        conn = getattr(self, "conn", None)
        if not conn:
            return

        try:
            conn.close()
        except Exception:
            pass
        finally:
            self.conn = None

    def change_profile(self):
        current_settings = {
            "user_name": self.user_name,
            "channel_name": self.channel_name,
            "root_folder": self.root_folder,
            "profile_avatar_path": getattr(self, "profile_avatar_path", ""),
            "remember_me": self.settings.get("remember_me", True),
            "show_startup_wizard": self.settings.get("show_startup_wizard", True),
        }

        startup = StartupDialog(current_settings, self)
        if startup.exec() != QDialog.Accepted:
            return

        selected = startup.result_data
        self.settings.update(selected)

        if selected["remember_me"]:
            save_settings(self.settings)

        self.user_name = selected["user_name"]
        self.channel_name = selected["channel_name"]
        self.root_folder = selected["root_folder"]
        self.profile_avatar_path = selected.get("profile_avatar_path", "")

        self.profile_button.setText(self.user_name)
        self.profile_label.setText(f"{self.channel_name} | {self.root_folder}")
        if hasattr(self, "channel_logo_label"):
            try:
                from ui.main_window_topbar import update_channel_logo, update_profile_avatar

                update_channel_logo(self)
                update_profile_avatar(self)
            except Exception:
                traceback.print_exc()

        if hasattr(self, "_refresh_live_watch_paths"):
            self._refresh_live_watch_paths()

        self.load_news(force_refresh=True)

    def on_date_changed(self, date):
        if hasattr(self, "_refresh_live_watch_paths"):
            self._refresh_live_watch_paths()
        self.load_news()

    def go_previous_day(self):
        self.date_edit.setDate(self.date_edit.date().addDays(-1))

    def go_next_day(self):
        self.date_edit.setDate(self.date_edit.date().addDays(1))

    def run_history_scan(self):
        dialog = BackfillDialog(self)
        self.backfill_dialog = dialog
        dialog.start_button.clicked.connect(self.start_backfill)
        dialog.exec()

    def load_news(self, force_refresh=False):
        load_token = self._next_load_token()

        try:
            if hasattr(self, "stop_all_workers"):
                self.stop_all_workers()
        except Exception:
            pass

        self._close_active_connection()

        date_str = self.date_edit.date().toString("dd.MM.yyyy")
        iso_date = self.date_edit.date().toString("yyyy-MM-dd")

        init_db(self.channel_name, iso_date)

        try:
            self.news_model.set_items([])
        except Exception:
            pass

        self.preview_title.setText("Başlık:")
        self.preview_corrected_title.setText("")
        self.preview_info.setText("Bilgi:")
        self.preview_text.clear()
        self.news_items = []
        self.filtered_items = []

        try:
            files = scan_news_files(self.root_folder, date_str, self.channel_name)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Tarama sırasında hata oluştu:\n{e}")
            return

        if not files:
            self.count_label.setText("Haber sayısı: 0")
            db_count = get_news_count_for_month(self.channel_name, iso_date)
            self.status_label.setText(f"Hiç haber bulunamadı | DB: {db_count}")
            self.progress_bar.setVisible(False)
            return

        db_file = get_db_path(self.channel_name, iso_date)
        self.conn = connect_db(self.channel_name, iso_date)
        ensure_cache_table(self.conn)

        filtered_files = []
        cached_count = 0

        for f in files:
            try:
                stat = f.stat()
                if force_refresh or not is_cached(self.conn, str(f), stat.st_mtime, stat.st_size):
                    filtered_files.append(f)
                else:
                    cached_count += 1
            except Exception:
                filtered_files.append(f)

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(max(1, len(filtered_files)))
        self.progress_bar.setValue(0)

        self.status_label.setText(
            f"Yükleniyor... İşlenecek: {len(filtered_files)} | Önbellekten: {cached_count}"
        )

        self._close_active_connection()

        if not filtered_files:
            self.news_items = get_news_for_date(self.channel_name, iso_date)
            self.progress_bar.setVisible(False)
            try:
                self.apply_filters()
            except Exception:
                traceback.print_exc()

            total_db = get_news_count_for_month(self.channel_name, iso_date)
            self.status_label.setText(
                f"{len(self.news_items)} haber | DB: {total_db} | {get_spell_backend_status_text()}"
            )

            try:
                self._close_active_connection()
            except Exception:
                pass
            return

        worker = NewsLoadWorker(filtered_files, self.channel_name, force_refresh)
        worker._load_token = load_token
        worker._iso_date = iso_date
        worker._date_str = date_str
        worker._channel_name = self.channel_name
        self.start_worker(worker)

    def on_worker_progress(self, current, total):
        if not self._is_current_worker_signal():
            return

        try:
            self.progress_bar.setValue(current)
            self.status_label.setText(f"Yükleniyor... {current}/{total}")
        except Exception:
            traceback.print_exc()

    def on_worker_error(self, message):
        if not self._is_current_worker_signal():
            return

        try:
            self.progress_bar.setVisible(False)
        except Exception:
            pass
        self._close_active_connection()
        QMessageBox.critical(self, "Hata", message)

    def on_worker_finished(self, results):
        if not self._is_current_worker_signal():
            return

        try:
            channel_name, iso_date, date_str = self._get_sender_load_context()
            indexed_count = 0
            conn = connect_db(channel_name, iso_date)
            ensure_cache_table(conn)

            try:
                for item in results:
                    item["iso_date"] = iso_date
                    item["date_str"] = date_str

                    try:
                        upsert_news(channel_name, item, conn=conn)
                        indexed_count += 1
                    except Exception:
                        traceback.print_exc()

                    try:
                        update_cache(
                            conn,
                            item["path"],
                            item["mtime"],
                            item["size"]
                        )
                    except Exception:
                        traceback.print_exc()

                try:
                    conn.commit()
                except Exception:
                    traceback.print_exc()
            finally:
                try:
                    conn.close()
                except Exception:
                    traceback.print_exc()

            try:
                self.news_items = get_news_for_date(channel_name, iso_date)
            except Exception:
                traceback.print_exc()
                self.news_items = []

            try:
                self.progress_bar.setVisible(False)
            except Exception:
                traceback.print_exc()

            try:
                self.apply_filters()
            except Exception:
                traceback.print_exc()

            try:
                total_db = get_news_count_for_month(channel_name, iso_date)
            except Exception:
                traceback.print_exc()
                total_db = 0

            self.status_label.setText(
                f"{len(self.news_items)} haber | DB: {total_db} | Yazılan: {indexed_count} | {get_spell_backend_status_text()}"
            )

        except Exception:
            traceback.print_exc()

    def start_backfill(self):
        if not self.backfill_dialog:
            return

        start_date = self.backfill_dialog.start_date.date()
        end_date = self.backfill_dialog.end_date.date()

        if start_date > end_date:
            QMessageBox.warning(self, "Uyarı", "Başlangıç tarihi bitiş tarihinden büyük olamaz.")
            return

        self.backfill_dialog.start_button.setEnabled(False)
        self.backfill_dialog.progress_label.setText("Tarama başlatılıyor...")
        self.backfill_dialog.progress.setValue(0)

        self.backfill_worker = BackfillWorker(
            self.root_folder,
            self.channel_name,
            start_date,
            end_date,
        )
        self.backfill_worker.progress.connect(self.on_backfill_progress)
        self.backfill_worker.finished_report.connect(self.on_backfill_finished)
        self.backfill_worker.start()

        logging.getLogger("EGS").info(
            "Arşiv taraması başlatıldı | kanal=%s | başlangıç=%s | bitiş=%s",
            self.channel_name,
            start_date.toString("yyyy-MM-dd"),
            end_date.toString("yyyy-MM-dd"),
        )

    def on_backfill_progress(self, percent, text):
        if self.backfill_dialog:
            self.backfill_dialog.progress.setValue(percent)
            self.backfill_dialog.progress_label.setText(text)

    def on_backfill_finished(self, report: dict):
        if self.backfill_dialog:
            self.backfill_dialog.progress.setValue(100)
            self.backfill_dialog.progress_label.setText(
                f"Bitti | Gün: {report['days']} | Dosya: {report['files_found']} | "
                f"Yazılan: {report['indexed']} | Hata: {report['errors']} | "
                f"Süre: {report['seconds']:.1f} sn"
            )
            self.backfill_dialog.start_button.setEnabled(True)

        self.status_label.setText(
            f"Arşiv taraması tamamlandı | Gün: {report['days']} | Dosya: {report['files_found']} | "
            f"Yazılan: {report['indexed']} | Hata: {report['errors']} | "
            f"Süre: {report['seconds']:.1f} sn"
        )

        logging.getLogger("EGS").info(
            "Arşiv taraması tamamlandı | kanal=%s | gün=%s | dosya=%s | yazılan=%s | hata=%s | süre=%.1f",
            self.channel_name,
            report["days"],
            report["files_found"],
            report["indexed"],
            report["errors"],
            report["seconds"],
        )

        try:
            self.load_news(force_refresh=False)
        except Exception:
            traceback.print_exc()

    def force_reload(self):
        self.load_news(force_refresh=True)

    def clear_cache(self):
        try:
            clear_cache_for_channel(self.channel_name)
            QMessageBox.information(self, "Önbellek", "Kanal önbelleği temizlendi.")
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Önbellek temizlenemedi:\n{exc}")

    def apply_filters(self):
        import re

        from core.text_utils import normalize_search_text

        raw_query = self.search_input.text().strip()
        query = normalize_search_text(raw_query)
        scope = self.search_scope_combo.currentText()
        use_regex = bool(self.search_regex_checkbox.isChecked())
        regex = None

        if use_regex and raw_query:
            try:
                regex = re.compile(raw_query, re.IGNORECASE)
            except re.error:
                self.filtered_items = []
                self.fill_tree([])
                self.count_label.setText("Haber sayısı: 0")
                self.status_label.setText("Geçersiz regex ifadesi")
                return

        filtered = []
        selected_codes = {
            self._normalize_news_code(code)
            for code in self.selected_codes
            if self._normalize_news_code(code)
        }

        for item in self.news_items:
            if self._should_hide_previous_day_item(item):
                continue

            item_code = self._normalize_news_code(item.get("news_code"))

            if selected_codes:
                if self.code_filter_hide_mode:
                    if item_code in selected_codes:
                        continue
                else:
                    if item_code not in selected_codes:
                        continue

            title_raw = item.get("title", "")
            title_text = normalize_search_text(title_raw)
            content_raw = " ".join([
                item.get("summary", ""),
                item.get("body", ""),
                item.get("final_text", ""),
                item.get("file_name", ""),
                " ".join(item.get("editors", [])),
            ])
            content_text = normalize_search_text(content_raw)

            matched = True

            if raw_query:
                if use_regex and regex:
                    if scope == "Başlık":
                        matched = bool(regex.search(title_raw))
                    elif scope == "Haber Metni":
                        matched = bool(regex.search(content_raw))
                    else:
                        raw_content = f"{title_raw} {content_raw}"
                        matched = bool(regex.search(raw_content))
                else:
                    if scope == "Başlık":
                        matched = query in title_text
                    elif scope == "Haber Metni":
                        matched = query in content_text
                    else:
                        matched = query in (title_text + " " + content_text)

            if matched:
                filtered.append(item)

        duplicate_mode = self.settings.get("main_duplicate_mode", "off")

        if duplicate_mode != "off":
            grouped = {}
            for item in filtered:
                key = item.get("title", "").strip().lower()
                grouped.setdefault(key, []).append(item)

            resolved = []
            for _, items_for_title in grouped.items():
                items_for_title = sorted(
                    items_for_title,
                    key=lambda x: (x.get("iso_date", ""), x.get("file_name", "")),
                )

                if duplicate_mode == "latest":
                    resolved.append(items_for_title[-1])
                elif duplicate_mode == "oldest":
                    resolved.append(items_for_title[0])
                else:
                    resolved.extend(items_for_title)

            filtered = resolved

        self.filtered_items = filtered
        self.fill_tree(self.filtered_items)
        self.count_label.setText(f"Haber sayısı: {len(self.filtered_items)}")

    def fill_tree(self, items):
        try:
            self.news_model.set_items(items)
        except Exception:
            traceback.print_exc()
            return

        if items:
            try:
                self.news_view.selectRow(0)
            except Exception:
                traceback.print_exc()
        else:
            self.preview_title.setText("Başlık:")
            self.preview_corrected_title.setText("")
            self.preview_info.setText("Bilgi:")
            self.preview_text.clear()

    def on_news_row_changed(self, current, previous):
        if not current.isValid():
            self.preview_title.setText("Başlık:")
            self.preview_corrected_title.setText("")
            self.preview_info.setText("Bilgi:")
            self.preview_text.clear()
            return

        item = self.news_model.item_at(current.row())
        if not item:
            return

        corrected = item.get("corrected_title", "").strip()

        if corrected and corrected != item.get("title", ""):
            self.preview_title.setText(corrected)
            self.preview_corrected_title.setText(f"(Orijinal: {item.get('title', '')})")
        else:
            self.preview_title.setText(item.get("title", ""))
            self.preview_corrected_title.setText("")

        editors_text = ", ".join(item.get("editors", [])) if item.get("editors") else "-"
        info_text = (
            f"{item.get('news_code', '')} | "
            f"{item.get('news_category', '').upper()} | "
            f"{item.get('title', '')} | "
            f"{item.get('date_str', '')} | "
            f"Editör: {editors_text}"
        )
        self.preview_info.setText(info_text)
        self.preview_text.setPlainText(item.get("final_text", ""))

    def on_news_double_clicked(self, index):
        if not index.isValid():
            return

        item = self.news_model.item_at(index.row())
        if not item:
            return

        text = self.preview_text.toPlainText().strip() or item.get("final_text", "").strip()
        if self.safe_copy_to_clipboard(text):
            self.status_label.setText("Metin panoya kopyalandı")
