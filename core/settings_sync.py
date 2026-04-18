from __future__ import annotations

from PySide6.QtCore import QObject, QTimer

from core.settings_manager import save_settings


class SettingsSync(QObject):
    def __init__(self, owner, delay_ms: int = 250):
        super().__init__(owner)
        self.owner = owner
        self.delay_ms = max(50, int(delay_ms or 250))
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.flush)

    def schedule(self, immediate: bool = False):
        if immediate:
            self.flush()
            return
        self._timer.start(self.delay_ms)

    def flush(self):
        self._timer.stop()
        settings = getattr(self.owner, "settings", None)
        if isinstance(settings, dict):
            save_settings(settings)
