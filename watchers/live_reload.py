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

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(2000)
        self._poll_timer.timeout.connect(self._poll_for_changes)

        self._watched_paths: list[str] = []
        self._requested_paths: list[str] = []
        self._last_signature: tuple | None = None

    def clear(self):
        try:
            if self._watched_paths:
                self.watcher.removePaths(self._watched_paths)
        except Exception:
            pass
        self._watched_paths = []
        self._requested_paths = []
        self._last_signature = None
        self._poll_timer.stop()

    def watch_paths(self, paths: list[str]):
        self._requested_paths = [str(path) for path in paths if str(path or "").strip()]
        self._sync_watchers()
        self._last_signature = self._build_signature()
        if self._requested_paths:
            self._poll_timer.start()
        else:
            self._poll_timer.stop()

    def _resolve_watch_targets(self) -> list[str]:
        valid_paths = []
        seen = set()

        for path in self._requested_paths:
            try:
                current = Path(path)
            except Exception:
                continue

            while not current.exists() and current.parent != current:
                current = current.parent

            if not current.exists():
                continue

            normalized = str(current)
            key = normalized.casefold()
            if key in seen:
                continue
            seen.add(key)
            valid_paths.append(normalized)
        return valid_paths

    def _sync_watchers(self):
        try:
            if self._watched_paths:
                self.watcher.removePaths(self._watched_paths)
        except Exception:
            pass

        valid_paths = self._resolve_watch_targets()
        self._watched_paths = []
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
        self._sync_watchers()
        # Aynı anda çok sayıda dosya değişirse tek yenilemeye düşür.
        self._debounce.start()

    def _build_signature(self) -> tuple:
        signatures = []
        for path in self._watched_paths or self._resolve_watch_targets():
            current = Path(path)
            if current.is_file():
                try:
                    stat = current.stat()
                    signatures.append((str(current), stat.st_mtime_ns, stat.st_size))
                except OSError:
                    continue
                continue

            if not current.is_dir():
                continue

            try:
                dir_stat = current.stat()
                entries = []
                for item in current.iterdir():
                    try:
                        if item.is_dir():
                            child_stat = item.stat()
                            entries.append((item.name.casefold(), "dir", child_stat.st_mtime_ns))
                        else:
                            stat = item.stat()
                            entries.append((item.name.casefold(), "file", stat.st_mtime_ns, stat.st_size))
                    except OSError:
                        continue
                entries.sort()
                signatures.append((str(current), dir_stat.st_mtime_ns, tuple(entries)))
            except OSError:
                continue
        return tuple(signatures)

    def _poll_for_changes(self):
        current_signature = self._build_signature()
        if self._last_signature is None:
            self._last_signature = current_signature
            return
        if current_signature != self._last_signature:
            self._last_signature = current_signature
            self._sync_watchers()
            self._debounce.start()
