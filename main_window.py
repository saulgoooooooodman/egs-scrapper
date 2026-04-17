from PySide6.QtCore import QDate
from PySide6.QtWidgets import QMainWindow, QDialog

from version_info import APP_NAME, APP_VERSION
from dialogs.startup_dialog import StartupDialog
from core.settings_manager import load_settings, save_settings
from core.window_state_manager import restore_window_state

from ui.main_window_ui import build_main_window_ui, attach_ui_helpers
from ui.main_window_menu_builder import build_main_window_menu
from actions.main_window_actions import MainWindowActions
from actions.main_window_state_hooks import MainWindowStateHooks
from watchers.live_reload import LiveReloadWatcher


class MainWindow(MainWindowActions, MainWindowStateHooks, QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        remember_me = bool(self.settings.get("remember_me", False))
        show_startup_wizard = bool(self.settings.get("show_startup_wizard", True))
        has_minimum_profile = all([
            self.settings.get("user_name"),
            self.settings.get("channel_name"),
            self.settings.get("root_folder"),
        ])

        must_show_startup = (not remember_me) or show_startup_wizard or (not has_minimum_profile)

        if must_show_startup:
            startup = StartupDialog(self.settings, self)
            if startup.exec() != QDialog.Accepted:
                raise SystemExit(0)

            selected = startup.result_data
            self.settings.update(selected)

            if selected.get("remember_me", False):
                save_settings(self.settings)
        else:
            selected = {
                "user_name": self.settings.get("user_name", ""),
                "channel_name": self.settings.get("channel_name", "A NEWS"),
                "root_folder": self.settings.get("root_folder", ""),
                "profile_avatar_path": self.settings.get("profile_avatar_path", ""),
                "remember_me": self.settings.get("remember_me", True),
                "show_startup_wizard": self.settings.get("show_startup_wizard", False),
            }

        self.user_name = selected["user_name"]
        self.channel_name = selected["channel_name"]
        self.root_folder = selected["root_folder"]
        self.profile_avatar_path = selected.get("profile_avatar_path", "")

        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1450, 880)

        self.news_items = []
        self.filtered_items = []
        self.conn = None
        self._load_request_token = 0
        self._active_load_token = 0
        self.selected_codes = set()
        self.code_filter_hide_mode = bool(self.settings.get("main_code_filter_hide_mode", False))
        self.backfill_dialog = None
        self.backfill_worker = None

        attach_ui_helpers(self.__class__)
        build_main_window_ui(self)
        build_main_window_menu(self)
        self._apply_styles()

        self.live_reload_watcher = LiveReloadWatcher(self)
        self.live_reload_watcher.reload_requested.connect(self._on_live_reload_requested)

        self.date_edit.blockSignals(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.blockSignals(False)
        self.load_main_ui_settings()
        restore_window_state(self)

        self._apply_live_watch_setting()
        self.load_news()
        self.show()

    def _apply_live_watch_setting(self):
        enabled = bool(self.settings.get("live_watch_enabled", False))
        if hasattr(self, "action_live_watch"):
            self.action_live_watch.setChecked(enabled)
        if enabled:
            self._refresh_live_watch_paths()

    def _refresh_live_watch_paths(self):
        from parsing.scanner import build_date_path

        date = self.date_edit.date().toString("dd.MM.yyyy")
        target_dir = build_date_path(self.root_folder, date)

        paths = []
        try:
            if target_dir.exists():
                paths.append(str(target_dir))
        except Exception:
            pass

        self.live_reload_watcher.watch_paths(paths)

    def _on_live_reload_requested(self):
        if bool(self.settings.get("live_watch_enabled", False)):
            self.load_news()

    def toggle_live_watch(self):
        enabled = self.action_live_watch.isChecked()
        self.settings["live_watch_enabled"] = enabled
        save_settings(self.settings)

        if enabled:
            self._refresh_live_watch_paths()
            self.status_label.setText("Canlı izleme açıldı")
        else:
            self.live_reload_watcher.clear()
            self.status_label.setText("Canlı izleme kapatıldı")
