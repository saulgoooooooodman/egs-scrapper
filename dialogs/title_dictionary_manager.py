from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QCheckBox,
)

from dictionaries.dictionary_store import (
    load_common_dictionary,
    save_common_dictionary,
    load_channel_dictionary,
    save_channel_dictionary,
)


class TitleDictionaryManagerDialog(QDialog):
    def __init__(self, channel_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Başlık Sözlüğü")
        self.resize(820, 620)

        self.channel_name = channel_name

        layout = QVBoxLayout(self)

        self.use_common_checkbox = QCheckBox("Ortak sözlüğü düzenle")
        self.use_common_checkbox.stateChanged.connect(self.reload_data)
        self.use_common_checkbox.setToolTip("İşaretlersen tüm kanalların ortak kullandığı sözlüğü, kapalıysa bu kanala özel sözlüğü düzenlersin.")
        layout.addWidget(self.use_common_checkbox)

        form = QHBoxLayout()
        wrong_label = QLabel("Yanlış:")
        wrong_label.setToolTip("Düzeltilmesini istediğin hatalı başlık parçasını yaz.")
        form.addWidget(wrong_label)
        self.wrong_input = QLineEdit()
        self.wrong_input.setToolTip("Program başlıkta bunu gördüğünde karşılığındaki doğru metni önerir.")
        form.addWidget(self.wrong_input, 1)

        correct_label = QLabel("Doğru:")
        correct_label.setToolTip("Hatalı ifadenin yerine kullanılacak doğru metni yaz.")
        form.addWidget(correct_label)
        self.correct_input = QLineEdit()
        self.correct_input.setToolTip("Başlık düzeltmede kullanılacak doğru ifade.")
        form.addWidget(self.correct_input, 1)

        self.add_btn = QPushButton("Ekle")
        self.add_btn.clicked.connect(self.add_entry)
        self.add_btn.setToolTip("Yazdığın yanlış-doğru eşlemesini tabloya ekler.")
        form.addWidget(self.add_btn)

        layout.addLayout(form)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Yanlış", "Doğru"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setToolTip("Kaydedilmiş başlık düzeltme eşleşmeleri. Hücreleri doğrudan düzenleyebilirsin.")
        layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        self.delete_btn = QPushButton("Seçiliyi Sil")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setToolTip("Tablodaki seçili sözlük kaydını siler.")
        actions.addWidget(self.delete_btn)

        self.save_btn = QPushButton("Kaydet")
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setToolTip("Tablodaki sözlük değişikliklerini kalıcı olarak kaydeder.")
        actions.addWidget(self.save_btn)

        actions.addStretch(1)
        layout.addLayout(actions)

        if self.channel_name == "A NEWS":
            self.use_common_checkbox.setChecked(False)
            self.use_common_checkbox.setEnabled(False)
            self.use_common_checkbox.setToolTip("A NEWS ortak sözlüğü kullanmaz; yalnızca kendi sözlüğü düzenlenir.")

        self.reload_data()

    def _is_common(self) -> bool:
        return self.use_common_checkbox.isChecked()

    def _load_current_dict(self) -> dict[str, str]:
        if self._is_common():
            return load_common_dictionary()
        return load_channel_dictionary(self.channel_name)

    def _save_current_dict(self, data: dict[str, str]):
        if self._is_common():
            save_common_dictionary(data)
        else:
            save_channel_dictionary(self.channel_name, data)

    def reload_data(self):
        data = self._load_current_dict()
        self.table.setRowCount(0)

        for row, (wrong, correct) in enumerate(sorted(data.items(), key=lambda x: x[0].lower())):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(wrong))
            self.table.setItem(row, 1, QTableWidgetItem(correct))

    def add_entry(self):
        wrong = self.wrong_input.text().strip().upper()
        correct = self.correct_input.text().strip()

        if not wrong or not correct:
            QMessageBox.information(self, "Bilgi", "Her iki alanı da doldur.")
            return

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(wrong))
        self.table.setItem(row, 1, QTableWidgetItem(correct))

        self.wrong_input.clear()
        self.correct_input.clear()

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Bilgi", "Önce bir satır seç.")
            return
        self.table.removeRow(row)

    def save_data(self):
        data = {}
        for row in range(self.table.rowCount()):
            wrong = self.table.item(row, 0).text().strip() if self.table.item(row, 0) else ""
            correct = self.table.item(row, 1).text().strip() if self.table.item(row, 1) else ""
            if wrong:
                data[wrong] = correct

        self._save_current_dict(data)
        QMessageBox.information(self, "Tamam", "Sözlük kaydedildi.")
