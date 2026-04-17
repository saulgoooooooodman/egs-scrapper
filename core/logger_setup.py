from __future__ import annotations

import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.app_paths import LOG_DIR


LOG_FILE = LOG_DIR / f"egs_scrapper_{datetime.now().strftime('%Y%m%d')}.log"
LOG_RETENTION_FILES = 30
LOG_MAX_BYTES = 2_000_000


def _cleanup_old_logs():
    files = sorted(
        LOG_DIR.glob("egs_scrapper_*.log*"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for stale in files[LOG_RETENTION_FILES:]:
        try:
            stale.unlink()
        except Exception:
            pass


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _cleanup_old_logs()

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    for handler in list(root.handlers):
        root.removeHandler(handler)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_MAX_BYTES,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    logging.getLogger("EGS").info("Logging başlatıldı")
    logging.getLogger("EGS").info("Log dosyası: %s", LOG_FILE)


def install_exception_hook():
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logging.getLogger("EGS").exception(
            "Yakalanmamış hata",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception
