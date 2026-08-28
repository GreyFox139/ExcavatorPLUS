import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from config import ICON_PATH, F_Sml, F_Nrm_B
from services.log_service import load_logs

# Класс UI окна логов
class LogWindow(QDialog):
    # Метод инициализации формы и UI
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("История изменений")
        self.setFixedSize(550, 480)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. Заголовок
        title_label = QLabel("Что нового в программе:")
        title_label.setFont(F_Nrm_B)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 2. Текстовое поле для вывода логов
        self.text_edit = QTextEdit()
        self.text_edit.setFont(F_Sml)
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 10px;
            }
        """)

        # Загрузка содержимого файла logs.txt
        log_content = load_logs()
        self.text_edit.setPlainText(log_content)
        layout.addWidget(self.text_edit)

        # 3. Кнопка "Закрыть"
        btn_layout = QHBoxLayout()
        btn_close = QPushButton("Закрыть")
        btn_close.setFont(F_Sml)
        btn_close.setFixedSize(140, 40)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #4C82C1;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #3B6AA0; }
        """)
        btn_close.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)