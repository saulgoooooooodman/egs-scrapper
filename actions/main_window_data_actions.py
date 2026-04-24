import logging
import sqlite3
import traceback
from pathlib import Path

from PySide6.QtWidgets import QCheckBox, QDialog, QMessageBox

from dialogs.backfill_dialog import BackfillDialog
from dialogs.startup_dialog import StartupDialog
from parsing.backfill_worker import BackfillWorker
from parsing.scanner import build_date_path, scan_news_files
from parsing.parser import _extract_news_code_and_title
from data.database import (
    connect_db,
    delete_news_for_paths,
    init_db,
    normalize_db_path,
)
from data.cache_manager import ensure_cache_table, is_cached, update_cache, clear_cache, delete_cache_paths
from data.news_repository import NewsRepository
from models.news_item import NewsItem
from parsing.news_worker import NewsLoadWorker
from parsing.worker_manager import WorkerManager
from parsing.news_service import NewsIngestService


logger = logging.getLogger("EGS.MainWindowData")


class MainWindowDataActions(WorkerManager):
    def _news_repository(self) -> NewsRepository:
        return NewsRepository(self.channel_name)

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

    def _refresh_list_titles(self, items):
        refreshed = []
        for item in items or []:
            current = item if isinstance(item, dict) else item.to_dict()
            file_name = str(current.get("file_name", "") or "").strip()
            title = str(current.get("title", "") or "").strip()
            list_title = str(current.get("list_title", "") or "").strip()

            try:
                _, extracted_title = _extract_news_code_and_title(file_name, self.channel_name)
            except Exception:
                extracted_title = ""

            candidate = extracted_title or title
            if candidate and list_title != candidate:
                current["list_title"] = candidate

            refreshed.append(current)
        return refreshed

    def _hide_previous_day_news_enabled(self) -> bool:
        if "hide_previous_day_news" in self.settings:
            return bool(self.settings.get("hide_previous_day_news", False))
        return not bool(self.settings.get("show_previous_day_news", True))

    def _set_load_metrics(self, *, scanned_count=0, to_process_count=0, cached_count=0):
        self._current_load_metrics = {
            "scanned_count": int(scanned_count or 0),
            "to_process_count": int(to_process_count or 0),
            "cached_count": int(cached_count or 0),
            "stale_deleted_count": 0,
            "stale_cache_deleted_count": 0,
        }

    def _warn_empty_source_folder(self, target_dir: Path, iso_date: str):
        if bool(self.settings.get("suppress_empty_folder_warning", False)):
            return

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle("Kaynak Klasör Boş")
        dialog.setText(
            "Kaynak klasör boş görünüyor.\n"
            "Güvenlik için o güne ait veritabanı kayıtları korunacak."
        )
        dialog.setInformativeText(
            f"Tarih: {iso_date}\n"
            f"Klasör: {target_dir}\n\n"
            "Bu boşluk geçiciyse veritabanı silinmez. Klasör tekrar dolunca liste geri gelir."
        )
        checkbox = QCheckBox("Bir daha gösterme")
        dialog.setCheckBox(checkbox)
        dialog.exec()
        if checkbox.isChecked():
            self.settings["suppress_empty_folder_warning"] = True
            self.schedule_settings_save()

    def _sync_removed_files(self, repository: NewsRepository, iso_date: str, scanned_files, target_exists: bool) -> tuple[int, int]:
        if not target_exists or not scanned_files:
            return 0, 0

        live_paths = {
            normalize_db_path(str(path))
            for path in scanned_files or []
            if normalize_db_path(str(path))
        }

        stale_paths = []
        for item in repository.fetch_by_date(iso_date):
            item_path = normalize_db_path(item.path)
            if item_path and item_path not in live_paths:
                stale_paths.append(item_path)

        if not stale_paths:
            return 0, 0

        conn = repository.connect(iso_date)
        try:
            deleted_news = delete_news_for_paths(
                self.channel_name,
                stale_paths,
                iso_date=iso_date,
                conn=conn,
            )
            deleted_cache = delete_cache_paths(conn, stale_paths)
            conn.commit()
            return deleted_news, deleted_cache
        finally:
            conn.close()

    def _should_hide_previous_day_item(self, item: dict) -> bool:
        if not self._hide_previous_day_news_enabled():
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
        except sqlite3.Error:
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
        self.save_settings_now()

        self.user_name = selected["user_name"]
        self.channel_name = selected["channel_name"]
        self.root_folder = selected["root_folder"]
        self.profile_avatar_path = selected.get("profile_avatar_path", "")

        self.profile_button.setText(self.user_name)
        self.profile_label.setText(self.channel_name)
        if hasattr(self, "channel_logo_label"):
            try:
                from ui.main_window_topbar import update_channel_logo, update_profile_avatar

                update_channel_logo(self)
                update_profile_avatar(self)
            except (ImportError, AttributeError, RuntimeError):
                traceback.print_exc()

        if hasattr(self, "_refresh_live_watch_paths"):
            self._refresh_live_watch_paths()
        if hasattr(self, "sync_symbol_prefixed_visibility_action"):
            self.sync_symbol_prefixed_visibility_action()

        self.load_news(force_refresh=True)

    def on_date_changed(self, date):
        if bool(self.settings.get("remember_last_date", False)):
            self.settings["last_selected_date"] = date.toString("yyyy-MM-dd")
            self.schedule_settings_save()
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
        repository = self._news_repository()
        self._set_load_metrics()

        try:
            if hasattr(self, "stop_all_workers"):
                self.stop_all_workers()
        except RuntimeError:
            pass

        self._close_active_connection()

        date_str = self.date_edit.date().toString("dd.MM.yyyy")
        iso_date = self.date_edit.date().toString("yyyy-MM-dd")

        repository.ensure_storage(iso_date)

        try:
            self.news_model.set_items([])
        except RuntimeError:
            pass

        self.preview_title.setText("Başlık:")
        self.preview_corrected_title.setText("")
        self.preview_info.setText("Bilgi:")
        self.preview_text.clear()
        self.news_items = []
        self.filtered_items = []

        try:
            files = scan_news_files(self.root_folder, date_str, self.channel_name)
        except (OSError, ValueError, RuntimeError) as e:
            QMessageBox.critical(self, "Hata", f"Tarama sırasında hata oluştu:\n{e}")
            return

        target_dir = build_date_path(self.root_folder, date_str)
        try:
            target_exists = target_dir.exists()
        except OSError:
            target_exists = False

        folder_is_empty = target_exists and not files

        if folder_is_empty:
            stale_deleted_count, stale_cache_deleted_count = 0, 0
            self._warn_empty_source_folder(target_dir, iso_date)
        else:
            stale_deleted_count, stale_cache_deleted_count = self._sync_removed_files(
                repository,
                iso_date,
                files,
                target_exists,
            )
        self._current_load_metrics["stale_deleted_count"] = stale_deleted_count
        self._current_load_metrics["stale_cache_deleted_count"] = stale_cache_deleted_count

        if not files:
            self.count_label.setText("Haber sayısı: 0")
            db_count = repository.count_for_month(iso_date)
            if folder_is_empty:
                self.status_label.setText(
                    f"Kaynak klasör boş | DB korundu: {db_count} | "
                    f"Tarih: {iso_date}"
                )
                self.progress_bar.setVisible(False)
                return
            self.status_label.setText(
                f"Hiç haber bulunamadı | DB: {db_count} | "
                f"Temizlenen kayıt: {stale_deleted_count}"
            )
            self.progress_bar.setVisible(False)
            return

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
            except (OSError, sqlite3.Error):
                filtered_files.append(f)

        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(max(1, len(filtered_files)))
        self.progress_bar.setValue(0)
        self._set_load_metrics(
            scanned_count=len(files),
            to_process_count=len(filtered_files),
            cached_count=cached_count,
        )
        self._current_load_metrics["stale_deleted_count"] = stale_deleted_count
        self._current_load_metrics["stale_cache_deleted_count"] = stale_cache_deleted_count

        self.status_label.setText(
            f"Yükleniyor... Taranan: {len(files)} | İşlenecek: {len(filtered_files)} | Önbellekten: {cached_count}"
        )

        self._close_active_connection()

        if not filtered_files:
            self.news_items = self._refresh_list_titles(repository.fetch_by_date(iso_date))
            self.progress_bar.setVisible(False)
            try:
                self.apply_filters()
            except RuntimeError:
                traceback.print_exc()

            total_db = repository.count_for_month(iso_date)
            metrics = getattr(self, "_current_load_metrics", {})
            self.status_label.setText(
                f"{len(self.news_items)} haber | DB: {total_db} | "
                f"Taranan: {metrics.get('scanned_count', 0)} | "
                f"Önbellekten: {metrics.get('cached_count', 0)} | "
                f"Temizlenen: {metrics.get('stale_deleted_count', 0)} | "
                f"{self._filter_summary_text()}"
            )

            try:
                self._close_active_connection()
            except sqlite3.Error:
                pass
            return

        worker = NewsLoadWorker(filtered_files, self.channel_name, force_refresh)
        worker._load_token = load_token
        worker._iso_date = iso_date
        worker._date_str = date_str
        worker._channel_name = self.channel_name
        worker._force_refresh = force_refresh
        self.start_worker(worker)

    def on_worker_progress(self, current, total):
        if not self._is_current_worker_signal():
            return

        try:
            self.progress_bar.setValue(current)
            metrics = getattr(self, "_current_load_metrics", {})
            self.status_label.setText(
                f"Yükleniyor... {current}/{total} | "
                f"Taranan: {metrics.get('scanned_count', 0)} | "
                f"Önbellekten: {metrics.get('cached_count', 0)}"
            )
        except RuntimeError:
            traceback.print_exc()

    def on_worker_error(self, message):
        if not self._is_current_worker_signal():
            return

        try:
            self.progress_bar.setVisible(False)
        except RuntimeError:
            pass
        self._close_active_connection()
        QMessageBox.critical(self, "Hata", message)

    def on_worker_finished(self, results):
        if not self._is_current_worker_signal():
            return

        try:
            channel_name, iso_date, date_str = self._get_sender_load_context()
            force_refresh = bool(getattr(self.sender(), "_force_refresh", False))
            indexed_count = 0
            deleted_count = 0
            repository = NewsRepository(channel_name)
            conn = repository.connect(iso_date)
            ensure_cache_table(conn)

            try:
                if force_refresh and results:
                    try:
                        deleted_count = delete_news_for_paths(
                            channel_name,
                            [NewsItem.from_dict(item).path for item in results],
                            iso_date=iso_date,
                            conn=conn,
                        )
                    except (sqlite3.Error, ValueError, TypeError):
                        logger.exception("Zorla yenileme öncesi eski kayıtlar silinemedi | kanal=%s | tarih=%s", channel_name, iso_date)

                for item in results:
                    news_item = NewsItem.from_dict(item)
                    news_item.iso_date = iso_date
                    news_item.date_str = date_str

                    try:
                        repository.save_item(news_item, conn=conn)
                        indexed_count += 1
                    except (sqlite3.Error, OSError, ValueError):
                        logger.exception("Haber veritabanına yazılamadı | kanal=%s | tarih=%s | yol=%s", channel_name, iso_date, news_item.path)

                    try:
                        update_cache(
                            conn,
                            news_item.path,
                            news_item.mtime,
                            news_item.size
                        )
                    except sqlite3.Error:
                        logger.exception("Önbellek kaydı güncellenemedi | kanal=%s | tarih=%s | yol=%s", channel_name, iso_date, news_item.path)

                try:
                    conn.commit()
                except sqlite3.Error:
                    logger.exception("Veritabanı commit başarısız | kanal=%s | tarih=%s", channel_name, iso_date)
            finally:
                try:
                    conn.close()
                except sqlite3.Error:
                    logger.exception("Veritabanı bağlantısı kapatılamadı | kanal=%s | tarih=%s", channel_name, iso_date)

            try:
                self.news_items = self._refresh_list_titles(repository.fetch_by_date(iso_date))
            except sqlite3.Error:
                logger.exception("Veritabanından liste başlıkları okunamadı | kanal=%s | tarih=%s", channel_name, iso_date)
                self.news_items = []

            try:
                self.progress_bar.setVisible(False)
            except RuntimeError:
                logger.exception("İlerleme çubuğu gizlenemedi")

            try:
                self.apply_filters()
            except RuntimeError:
                logger.exception("Filtreler uygulanamadı")

            try:
                total_db = repository.count_for_month(iso_date)
            except sqlite3.Error:
                logger.exception("Aylık veritabanı sayısı okunamadı | kanal=%s | tarih=%s", channel_name, iso_date)
                total_db = 0

            self.status_label.setText(
                f"{len(self.news_items)} haber | DB: {total_db} | "
                f"Taranan: {self._current_load_metrics.get('scanned_count', 0)} | "
                f"İşlenen: {self._current_load_metrics.get('to_process_count', 0)} | "
                f"Önbellekten: {self._current_load_metrics.get('cached_count', 0)} | "
                f"Temizlenen: {self._current_load_metrics.get('stale_deleted_count', 0)} | "
                f"Silinen: {deleted_count} | Yazılan: {indexed_count} | "
                f"{self._filter_summary_text()}"
            )

        except (sqlite3.Error, OSError, RuntimeError, ValueError, TypeError):
            logger.exception("Yükleme işçisi sonuçları ana ekrana işlenemedi")

    def start_backfill(self):
        if not self.backfill_dialog:
            return

        start_date = self.backfill_dialog.start_date.date()
        end_date = self.backfill_dialog.end_date.date()

        if start_date > end_date:
            QMessageBox.warning(self, "Uyarı", "Başlangıç tarihi bitiş tarihinden büyük olamaz.")
            return

        self.backfill_dialog.start_button.setEnabled(False)
        self.backfill_dialog.cancel_button.setEnabled(True)
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

        try:
            self.backfill_dialog.cancel_button.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        self.backfill_dialog.cancel_button.clicked.connect(self.cancel_backfill)

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
            self.backfill_dialog.cancel_button.setEnabled(False)

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
        except (sqlite3.Error, OSError, RuntimeError, ValueError):
            traceback.print_exc()

    def force_reload(self):
        self.load_news(force_refresh=True)

    def cancel_backfill(self):
        worker = getattr(self, "backfill_worker", None)
        if not worker:
            return

        try:
            worker.requestInterruption()
            if self.backfill_dialog:
                self.backfill_dialog.progress_label.setText("İptal ediliyor...")
                self.backfill_dialog.cancel_button.setEnabled(False)
        except RuntimeError:
            traceback.print_exc()

    def clear_cache(self):
        try:
            self._news_repository().clear_cache()
            QMessageBox.information(
                self,
                "Önbellek",
                "Kanal önbelleği temizlendi.\n\n"
                "Bu işlem haber metinlerini silmez. Yalnızca uygulamanın "
                "dosyayı yeniden okumadan önce baktığı hızlı kontrol kayıtlarını temizler.",
            )
        except (sqlite3.Error, OSError, RuntimeError) as exc:
            QMessageBox.critical(self, "Hata", f"Önbellek temizlenemedi:\n{exc}")

    def _push_code_filter_state(self):
        history = list(getattr(self, "_code_filter_history", []))
        history.append((sorted(self.selected_codes), bool(self.code_filter_hide_mode)))
        self._code_filter_history = history[-20:]

    def _apply_code_filter_state(self):
        self.apply_filters()
        self.save_main_ui_settings()

    def hide_news_code(self, code: str | None = None):
        target_code = self._normalize_news_code(code)
        if not target_code:
            self.status_label.setText("Gizlenecek haber kodu bulunamadı")
            return
        self._push_code_filter_state()
        self.selected_codes.add(target_code)
        self.code_filter_hide_mode = True
        self._apply_code_filter_state()
        self.status_label.setText(f"Haber kodu gizlendi: {target_code}")

    def show_only_news_code(self, code: str | None = None):
        target_code = self._normalize_news_code(code)
        if not target_code:
            self.status_label.setText("Filtrelenecek haber kodu bulunamadı")
            return
        self._push_code_filter_state()
        self.selected_codes = {target_code}
        self.code_filter_hide_mode = False
        self._apply_code_filter_state()
        self.status_label.setText(f"Yalnızca bu haber kodu gösteriliyor: {target_code}")

    def undo_code_filter(self):
        history = list(getattr(self, "_code_filter_history", []))
        if not history:
            self.status_label.setText("Geri alınacak filtre bulunamadı")
            return
        previous_codes, previous_hide_mode = history.pop()
        self._code_filter_history = history
        self.selected_codes = set(previous_codes)
        self.code_filter_hide_mode = bool(previous_hide_mode)
        self._apply_code_filter_state()
        self.status_label.setText("Son haber kodu filtresi geri alındı")

    def clear_code_filters(self):
        if not self.selected_codes and not self.code_filter_hide_mode:
            self.status_label.setText("Temizlenecek haber kodu filtresi yok")
            return
        self._push_code_filter_state()
        self.selected_codes = set()
        self.code_filter_hide_mode = False
        self._apply_code_filter_state()
        self.status_label.setText("Haber kodu filtreleri temizlendi")

    def refresh_selected_news_from_source(self):
        targets = self._selected_news_items() if hasattr(self, "_selected_news_items") else []
        if not targets:
            self.status_label.setText("Önce bir haber seç")
            return

        repository = self._news_repository()
        iso_date = self.date_edit.date().toString("yyyy-MM-dd")
        date_str = self.date_edit.date().toString("dd.MM.yyyy")
        service = NewsIngestService(self.channel_name)
        updated_count = 0
        skipped = []
        conn = repository.connect(iso_date)
        ensure_cache_table(conn)

        try:
            for item in targets:
                path = Path(str(item.get("path", "") or "").strip())
                if not path.exists():
                    skipped.append(path.name or str(path))
                    continue

                delete_news_for_paths(self.channel_name, [str(path)], iso_date=iso_date, conn=conn)
                news_item = service.build_news_item(path, iso_date=iso_date, date_str=date_str)
                repository.save_item(news_item, conn=conn)
                update_cache(conn, str(path), news_item.mtime, news_item.size)
                updated_count += 1
            conn.commit()
        finally:
            conn.close()

        self.load_news(force_refresh=False)
        if skipped:
            self.status_label.setText(
                f"Güncellenen haber: {updated_count} | Atlanan dosya: {len(skipped)}"
            )
        else:
            self.status_label.setText(f"Kaynaktan yeniden okunan haber: {updated_count}")

    def navigate_news_by_prefix(self, prefix: str):
        from core.text_utils import normalize_search_text

        normalized_prefix = normalize_search_text(prefix)
        if not normalized_prefix:
            return

        for row, item in enumerate(self.news_model.all_items()):
            title = self.news_model.display_title_for_item(item)
            if normalize_search_text(title).startswith(normalized_prefix):
                index = self.news_model.index(row, 2)
                self.news_view.setCurrentIndex(index)
                self.news_view.selectRow(row)
                self.news_view.scrollTo(index, self.news_view.ScrollHint.PositionAtCenter)
                self.status_label.setText(f"Hızlı seçim: {title}")
                return

    def _set_filter_status_text(self, message: str = ""):
        total_count = len(self.news_items or [])
        visible_count = len(self.filtered_items or [])
        hidden_count = max(total_count - visible_count, 0)
        details = f"Gösterilen: {visible_count} | Gizlenen: {hidden_count}"
        self.status_label.setText(f"{message} | {details}" if message else details)

    def _filter_summary_text(self) -> str:
        total_count = len(self.news_items or [])
        visible_count = len(self.filtered_items or [])
        hidden_count = max(total_count - visible_count, 0)
        return f"Gösterilen: {visible_count} | Gizlenen: {hidden_count} | Toplam: {total_count}"

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
                self._set_filter_status_text("Geçersiz regex ifadesi")
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
            corrected_title = item.get("corrected_title", "")
            item["_is_previous_day"] = self._should_hide_previous_day_item(item)
            title_text = normalize_search_text(title_raw)
            corrected_text = normalize_search_text(corrected_title)
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
                        matched = bool(regex.search(corrected_title or title_raw))
                    elif scope == "Haber Metni":
                        matched = bool(regex.search(content_raw))
                    else:
                        raw_content = f"{corrected_title or title_raw} {content_raw}"
                        matched = bool(regex.search(raw_content))
                else:
                    if scope == "Başlık":
                        matched = query in (corrected_text or title_text)
                    elif scope == "Haber Metni":
                        matched = query in content_text
                    else:
                        matched = query in ((corrected_text or title_text) + " " + content_text)

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
        self._set_filter_status_text()

    def fill_tree(self, items):
        try:
            self.news_model.set_items(items)
        except RuntimeError:
            traceback.print_exc()
            return

        if items:
            try:
                self.news_view.selectRow(0)
            except RuntimeError:
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
