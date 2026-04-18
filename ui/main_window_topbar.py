from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QDateEdit,
)

from core.app_paths import LOGO_ICO_FILE, LOGO_PNG_FILE, channel_logo_file


def _build_icon():
    if LOGO_ICO_FILE.exists():
        return QIcon(str(LOGO_ICO_FILE))
    if LOGO_PNG_FILE.exists():
        return QIcon(str(LOGO_PNG_FILE))
    return QIcon()


def update_channel_logo(self):
    logo_path = channel_logo_file(self.channel_name)
    if not logo_path.exists():
        self.channel_logo_label.clear()
        self.channel_logo_label.setVisible(False)
        return

    pixmap = QPixmap(str(logo_path))
    if pixmap.isNull():
        self.channel_logo_label.clear()
        self.channel_logo_label.setVisible(False)
        return

    scaled = pixmap.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    self.channel_logo_label.setPixmap(scaled)
    self.channel_logo_label.setVisible(True)


def update_profile_avatar(self):
    avatar_path = Path(str(getattr(self, "profile_avatar_path", "") or "").strip())
    if not avatar_path.exists():
        self.profile_avatar_label.clear()
        self.profile_avatar_label.setVisible(False)
        return

    pixmap = QPixmap(str(avatar_path))
    if pixmap.isNull():
        self.profile_avatar_label.clear()
        self.profile_avatar_label.setVisible(False)
        return

    scaled = pixmap.scaled(30, 30, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    self.profile_avatar_label.setPixmap(scaled)
    self.profile_avatar_label.setVisible(True)


def build_topbar(self, main_layout):
    top_widget = QWidget()
    top_layout = QHBoxLayout(top_widget)
    top_layout.setContentsMargins(0, 0, 0, 0)
    top_layout.setSpacing(6)

    self.channel_logo_label = QLabel()
    self.channel_logo_label.setFixedSize(36, 36)
    self.channel_logo_label.setToolTip("Seçili kanal logosu")
    self.channel_logo_label.setScaledContents(False)
    top_layout.addWidget(self.channel_logo_label)

    self.profile_avatar_label = QLabel()
    self.profile_avatar_label.setFixedSize(32, 32)
    self.profile_avatar_label.setToolTip("Kullanıcı profil logosu")
    self.profile_avatar_label.setScaledContents(False)
    self.profile_avatar_label.setStyleSheet("border: 1px solid #666; border-radius: 4px;")
    top_layout.addWidget(self.profile_avatar_label)

    self.profile_button = QPushButton(self.user_name or "Profil")
    self.profile_button.setToolTip("Kullanıcı, kanal ve kök klasör ayarlarını değiştirmek için profil ekranını açar.")
    self.profile_button.clicked.connect(self.change_profile)
    top_layout.addWidget(self.profile_button)

    self.profile_label = QLabel(self.channel_name)
    self.profile_label.setToolTip("Şu an açık olan kanal.")
    self.profile_label.setWordWrap(False)
    top_layout.addWidget(self.profile_label, 1)

    top_layout.addSpacing(6)

    self.prev_day_btn = QPushButton("◀")
    self.prev_day_btn.setFixedWidth(32)
    self.prev_day_btn.setToolTip("Bir gün geri gider ve o tarihin haberlerini yükler.")
    self.prev_day_btn.clicked.connect(self.go_previous_day)
    top_layout.addWidget(self.prev_day_btn)

    self.date_edit = QDateEdit()
    self.date_edit.setCalendarPopup(True)
    self.date_edit.setDisplayFormat("dd.MM.yyyy")
    self.date_edit.setToolTip("Yüklenecek haber tarihini seç. Tarih değişince liste otomatik yenilenir.")
    self.date_edit.dateChanged.connect(self.on_date_changed)
    top_layout.addWidget(self.date_edit)

    self.next_day_btn = QPushButton("▶")
    self.next_day_btn.setFixedWidth(32)
    self.next_day_btn.setToolTip("Bir gün ileri gider ve o tarihin haberlerini yükler.")
    self.next_day_btn.clicked.connect(self.go_next_day)
    top_layout.addWidget(self.next_day_btn)

    icon = _build_icon()
    if not icon.isNull():
        self.setWindowIcon(icon)

    update_channel_logo(self)
    update_profile_avatar(self)

    main_layout.addWidget(top_widget)
