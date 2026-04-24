from __future__ import annotations

import base64
import binascii

from core.settings_manager import save_settings


def save_window_state(window):
    try:
        geometry = window.saveGeometry().data()
        encoded = base64.b64encode(bytes(geometry)).decode("ascii")
        window.settings["window_geometry"] = encoded
        save_settings(window.settings)
    except (AttributeError, TypeError, ValueError, OSError, RuntimeError):
        pass


def restore_window_state(window):
    try:
        if not window.settings.get("remember_window_geometry", False):
            return

        encoded = window.settings.get("window_geometry")
        if not encoded:
            return

        geometry = base64.b64decode(encoded.encode("ascii"))
        window.restoreGeometry(geometry)
    except (AttributeError, TypeError, ValueError, binascii.Error, RuntimeError):
        pass
