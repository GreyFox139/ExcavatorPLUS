import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QDialog
)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QIcon, QDesktopServices

from config import ICON_PATH, F_Tiny, F_Nrm, F_Mid, F_Big_B
from gui.gui_open_window import OpenWindow
from gui.gui_close_window import CloseWindow
from gui.gui_log_window import LogWindow
from gui.gui_dialog_window import ConfirmExitDialog
from gui.gui_blank_window import GuiBlankWindow

# Класс UI гланого окна
class MainWindow(QMainWindow):
    # Метод инициализации формы и UI
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Экскаватор Плюс")
        self.setFixedSize(800, 675)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 20, 30, 15)

        # 1. Заголовок
        title_label = QLabel("Давай печатать\nдокументы!")
        title_label.setFont(F_Big_B)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #1A1A1A; margin-bottom: 24px;")
        main_layout.addWidget(title_label)

        # 2. Блок основных центральных кнопок
        center_layout = QVBoxLayout()
        center_layout.setSpacing(24)

        btn_w, btn_h = 660, 85

        btn_open = QPushButton("Открытие ордеров")
        btn_open.setFont(F_Mid)
        btn_open.setFixedSize(btn_w, btn_h)
        btn_open.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
        """)
        btn_open.clicked.connect(self.open_orders_window)

        btn_close = QPushButton("Закрытие ордеров")
        btn_close.setFont(F_Mid)
        btn_close.setFixedSize(btn_w, btn_h)
        btn_close.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
        """)
        btn_close.clicked.connect(self.close_orders_window)

        btn_blank = QPushButton("Печать пустых бланков")
        btn_blank.setFont(F_Mid)
        btn_blank.setFixedSize(btn_w, btn_h)
        btn_blank.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
        """)
        btn_blank.clicked.connect(self.blank_window_stub)

        center_layout.addWidget(btn_open, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(btn_blank, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        # 3. Нижний блок (кнопки логов, мануала и выхода + лейбл версии)
        bottom_layout = QHBoxLayout()

        # Левая нижняя группа: горизонтальный ряд кнопок логов и мануала
        left_bottom_layout = QVBoxLayout()
        
        tools_layout = QHBoxLayout()
        tools_layout.setSpacing(10)

        # Кнопка логов
        btn_log = QPushButton()
        btn_log.setFixedSize(50, 50)
        log_img_path = os.path.join("gui", "graph", "log.png")
        if os.path.exists(log_img_path):
            btn_log.setIcon(QIcon(log_img_path))
            btn_log.setIconSize(QSize(40, 40))
            
        btn_log.setStyleSheet("""
            QPushButton { background-color: #E0E0E0; border: 1px solid #B0B0B0; border-radius: 4px; }
            QPushButton:hover { background-color: #D0D0D0; }
        """)
        btn_log.clicked.connect(self.log_window_stub)

        # Кнопка мануала
        btn_manual = QPushButton()
        btn_manual.setFixedSize(50, 50)
        manual_img_path = os.path.join("gui", "graph", "manual.png")
        if os.path.exists(manual_img_path):
            btn_manual.setIcon(QIcon(manual_img_path))
            btn_manual.setIconSize(QSize(40, 40))
        
        btn_manual.setStyleSheet("""
            QPushButton { background-color: #E0E0E0; border: 1px solid #B0B0B0; border-radius: 4px; }
            QPushButton:hover { background-color: #D0D0D0; }
        """)
        btn_manual.clicked.connect(self.open_manual)

        tools_layout.addWidget(btn_log)
        tools_layout.addWidget(btn_manual)

        left_bottom_layout.addStretch()
        left_bottom_layout.addLayout(tools_layout)

        bottom_layout.addLayout(left_bottom_layout)
        bottom_layout.addStretch()

        # Правая нижняя группа: кнопка выхода и версия
        right_bottom_layout = QVBoxLayout()
        right_bottom_layout.setSpacing(16)

        btn_exit = QPushButton("Выход")
        btn_exit.setFont(F_Nrm)
        btn_exit.setFixedSize(200, 75)
        btn_exit.setStyleSheet("""
            QPushButton { background-color: #A83232; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #7D2525; }
        """)
        btn_exit.clicked.connect(self.close)

        version_label = QLabel("ver. 1.0.1")
        version_label.setFont(F_Tiny)
        version_label.setStyleSheet("color: #333333;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        right_bottom_layout.addWidget(btn_exit, alignment=Qt.AlignmentFlag.AlignRight)
        right_bottom_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignRight)

        bottom_layout.addLayout(right_bottom_layout)
        main_layout.addLayout(bottom_layout)

    # Метод вызова окна выхода
    def closeEvent(self, event):
        dialog = ConfirmExitDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            event.accept()
        else:
            event.ignore()

    # Метод вызова окна открытия ордеров
    def open_orders_window(self):
        dialog = OpenWindow(self)
        dialog.exec()

    # Метод вызова окна закрытия ордеров
    def close_orders_window(self):
        dialog = CloseWindow(self)
        dialog.exec()

    # Метод вызова окна печати пустых бланков
    def blank_window_stub(self):
        dialog = GuiBlankWindow(self)
        dialog.exec()

    # Метод вызова окна логов
    def log_window_stub(self):
        dialog = LogWindow(self)
        dialog.exec()

    # Метод открытия файла мануала системным просмотрщиком PDF
    def open_manual(self):
        manual_path = os.path.abspath("manual.pdf")
        if os.path.exists(manual_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(manual_path))