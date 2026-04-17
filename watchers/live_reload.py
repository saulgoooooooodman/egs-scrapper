from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal, QFileSystemWatcher, QTimer


class LiveReloadWatcher(QObject):
    reload_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.watcher = QFileSystemWatcher(self)
        self.watcher.directoryChanged.connect(self._on_fs_changed)
        self.watcher.fileChanged.connect(self._on_fs_changed)

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(1200)
        self._debounce.timeout.connect(self.reload_requested.emit)

        self._watched_paths: list[str] = []

    def clear(self):
        try:
            if self._watched_paths:
                self.watcher.removePaths(self._watched_paths)
        except Exception:
            pass
        self._watched_paths = []

    def watch_paths(self, paths: list[str]):
        self.clear()

        valid_paths = []
        for path in paths:
            try:
                p = Path(path)
                if p.exists():
                    valid_paths.append(str(p))
            except Exception:
                pass

        if not valid_paths:
            return

        try:
            self.watcher.addPaths(valid_paths)
            self._watched_paths = valid_paths
        except Exception:
            self._watched_paths = []

    def current_paths(self) -> list[str]:
        return list(self._watched_paths)

    def _on_fs_changed(self, changed_path: str):
        # Aynı anda çok sayıda dosya değişirse tek yenilemeye düşür.
        self._debounce.start()