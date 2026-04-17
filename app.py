import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from core.logger_setup import setup_logging, install_exception_hook
from main_window import MainWindow


APP_WINDOW = None


def main():
    global APP_WINDOW

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    try:
        setup_logging()
    except Exception:
        traceback.print_exc()

    try:
        install_exception_hook()
    except Exception:
        traceback.print_exc()

    try:
        APP_WINDOW = MainWindow()
        APP_WINDOW.show()
    except SystemExit:
        raise
    except Exception as exc:
        traceback.print_exc()
        QMessageBox.critical(
            None,
            "Başlatma Hatası",
            f"Program başlatılırken bir hata oluştu:\n\n{exc}"
        )
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())