import sys
import traceback
import logging

from PySide6.QtWidgets import QApplication, QMessageBox

from core.logger_setup import setup_logging, install_exception_hook
from main_window import MainWindow


APP_WINDOW = None
logger = logging.getLogger("EGS.App")


def main():
    global APP_WINDOW

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    try:
        setup_logging()
    except (OSError, RuntimeError):
        traceback.print_exc()

    try:
        install_exception_hook()
    except RuntimeError:
        logger.exception("Global exception hook kurulamadı")

    try:
        APP_WINDOW = MainWindow()
        APP_WINDOW.show()
    except SystemExit:
        raise
    except (ImportError, OSError, RuntimeError, ValueError, AttributeError) as exc:
        logger.exception("Uygulama başlatılamadı")
        QMessageBox.critical(
            None,
            "Başlatma Hatası",
            f"Program başlatılırken bir hata oluştu:\n\n{exc}"
        )
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
