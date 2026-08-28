import json
import os
from PyQt6.QtWidgets import QDialog, QLabel, QTextEdit, QPushButton, QVBoxLayout
from config import F_Sml
from gui.gui_dialog_window import show_warning_message

CONFIG_PATH = os.path.join("data", "app_config.json")

# Класс UI окна для расписки
class RozpiskaTextDialog(QDialog):
    # Метод инициализации формы
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Текст расписки")
        self.setFixedSize(500, 320)

        self.init_ui()
        self.load_text()

    # Метод инициализации UI
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        lbl_title = QLabel("Введи виды работ", self)
        lbl_title.setFont(F_Sml)
        layout.addWidget(lbl_title)

        self.txt_input = QTextEdit(self)
        self.txt_input.setFont(F_Sml)
        self.txt_input.setPlaceholderText("зеленої зони на прилеглій території")
        layout.addWidget(self.txt_input)

        self.btn_apply = QPushButton("Применить", self)
        self.btn_apply.setFont(F_Sml)
        self.btn_apply.setFixedHeight(35)
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #4172A2;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #355E87;
            }
        """)
        self.btn_apply.clicked.connect(self.save_and_close)
        layout.addWidget(self.btn_apply)

    # Метод загрузки текста из файла app_config.json
    def load_text(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.txt_input.setPlainText(config.get("rozpiska_text", ""))
            except Exception as e:
                print(f"Ошибка чтения конфигурации: {e}")

    # Метод сохранения текста в файл app_config.json
    # с последующим закрытием окна
    def save_and_close(self):
        text_val = self.txt_input.toPlainText().strip()

        # Защита от дурака: не дает сохранить пустое значение
        if not text_val:
            show_warning_message(self, "Напиши хоть что-нибудь!")
            return

        config = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception:
                config = {}

        config["rozpiska_text"] = text_val

        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

        self.accept()