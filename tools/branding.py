from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from version_info import APP_NAME, APP_VERSION
from core.app_paths import LOGO_FILE

try:
    from PySide6.QtSvgWidgets import QSvgWidget
except Exception:
    QSvgWidget = None


def build_brand_widget(parent=None):
    brand_layout = QHBoxLayout()
    brand_layout.setSpacing(8)
    brand_layout.setContentsMargins(0, 0, 0, 0)

    if QSvgWidget is not None and LOGO_FILE.exists():
        logo = QSvgWidget(str(LOGO_FILE))
        logo.setFixedSize(38, 38)
        logo.setToolTip(APP_NAME)
        brand_layout.addWidget(logo)

    title_label = QLabel(f"{APP_NAME} {APP_VERSION}")
    title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
    brand_layout.addWidget(title_label)

    container = QWidget(parent)
    container.setLayout(brand_layout)
    return container