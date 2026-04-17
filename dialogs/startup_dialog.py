from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFileDialog,
    QCheckBox,
    QMessageBox,
)


class StartupDialog(QDialog):
    def __init__(self, settings: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Profil Seçimi")
        self.resize(620, 340)

        settings = settings or {}
        self.result_data = None

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        row_user = QHBoxLayout()
        row_user.addWidget(QLabel("Kullanıcı:"))
        self.user_input = QLineEdit(settings.get("user_name", ""))
        row_user.addWidget(self.user_input, 1)
        layout.addLayout(row_user)

        row_channel = QHBoxLayout()
        row_channel.addWidget(QLabel("Kanal:"))
        self.channel_combo = QComboBox()
        self.channel_combo.addItems([
            "A NEWS",
            "A HABER",
            "ATV",
            "A SPOR",
            "A PARA",
        ])
        channel_name = settings.get("channel_name", "A NEWS")
        idx = self.channel_combo.findText(channel_name)
        if idx >= 0:
            self.channel_combo.setCurrentIndex(idx)
        row_channel.addWidget(self.channel_combo, 1)
        layout.addLayout(row_channel)

        row_root = QHBoxLayout()
        row_root.addWidget(QLabel("Kök Klasör:"))
        self.root_input = QLineEdit(settings.get("root_folder", r"C:\DeeR"))
        row_root.addWidget(self.root_input, 1)

        self.browse_btn = QPushButton("Gözat")
        self.browse_btn.clicked.connect(self.browse_root)
        row_root.addWidget(self.browse_btn)
        layout.addLayout(row_root)

        self.remember_checkbox = QCheckBox("Profili hatırla")
        self.remember_checkbox.setChecked(bool(settings.get("remember_me", False)))
        layout.addWidget(self.remember_checkbox)

        row_avatar = QHBoxLayout()
        row_avatar.addWidget(QLabel("Profil Logosu:"))
        self.avatar_input = QLineEdit(settings.get("profile_avatar_path", ""))
        self.avatar_input.setPlaceholderText("İsteğe bağlı profil görseli seç...")
        row_avatar.addWidget(self.avatar_input, 1)

        self.avatar_browse_btn = QPushButton("Gözat")
        self.avatar_browse_btn.clicked.connect(self.browse_avatar)
        row_avatar.addWidget(self.avatar_browse_btn)

        self.avatar_clear_btn = QPushButton("Temizle")
        self.avatar_clear_btn.clicked.connect(lambda: self.avatar_input.setText(""))
        row_avatar.addWidget(self.avatar_clear_btn)
        layout.addLayout(row_avatar)

        self.show_wizard_checkbox = QCheckBox("Bu pencereyi açılışta göster")
        self.show_wizard_checkbox.setChecked(bool(settings.get("show_startup_wizard", True)))
        layout.addWidget(self.show_wizard_checkbox)

        info = QLabel(
            "İpucu: Gözat düğmesine bastığında varsayılan olarak C:\\DeeR klasörü açılır."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        buttons = QHBoxLayout()
        buttons.addStretch(1)

        self.ok_btn = QPushButton("Tamam")
        self.ok_btn.clicked.connect(self.accept_dialog)
        buttons.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(self.cancel_btn)

        layout.addStretch(1)
        layout.addLayout(buttons)

    def browse_root(self):
        start_dir = self.root_input.text().strip() or r"C:\DeeR"
        folder = QFileDialog.getExistingDirectory(self, "Kök klasör seç", start_dir)
        if folder:
            self.root_input.setText(folder)

    def browse_avatar(self):
        start_dir = self.avatar_input.text().strip()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Profil logosu seç",
            start_dir,
            "Görseller (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if file_path:
            self.avatar_input.setText(file_path)

    def accept_dialog(self):
        user_name = self.user_input.text().strip()
        channel_name = self.channel_combo.currentText().strip()
        root_folder = self.root_input.text().strip()

        if not user_name:
            QMessageBox.warning(self, "Uyarı", "Kullanıcı adı boş olamaz.")
            return

        if not root_folder:
            QMessageBox.warning(self, "Uyarı", "Kök klasör boş olamaz.")
            return

        self.result_data = {
            "user_name": user_name,
            "channel_name": channel_name,
            "root_folder": root_folder,
            "profile_avatar_path": self.avatar_input.text().strip(),
            "remember_me": self.remember_checkbox.isChecked(),
            "show_startup_wizard": self.show_wizard_checkbox.isChecked(),
        }
        self.accept()
