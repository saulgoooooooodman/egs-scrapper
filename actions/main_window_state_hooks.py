from core.window_state_manager import save_window_state


class MainWindowStateHooks:
    def closeEvent(self, event):
        try:
            if self.settings.get("remember_window_geometry", False):
                save_window_state(self)
        except Exception:
            pass

        try:
            if hasattr(self, "save_settings_now"):
                self.save_settings_now()
        except Exception:
            pass

        try:
            if hasattr(self, "stop_all_workers"):
                self.stop_all_workers()
        except Exception:
            pass

        super().closeEvent(event)
