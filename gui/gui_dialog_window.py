import os
from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, 
    QPushButton, QApplication, QStyle, QWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QEventLoop, QPropertyAnimation, QSequentialAnimationGroup, QPauseAnimation
from PyQt6.QtGui import QIcon, QPixmap

from config import ICON_PATH, F_Sml

# Диалог подтверждения выхода из программы
class ConfirmExitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Уже всё?!")
        self.setFixedSize(440, 170)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 25, 15)
        
        # Блок значка и текста
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        icon_label = QLabel()
        style = QApplication.style()
        question_icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        icon_label.setPixmap(question_icon.pixmap(64, 64))
        
        text_label = QLabel("Хочешь выйти? Уверен?")
        text_label.setFont(F_Sml)

        content_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(content_layout)
        layout.addStretch()

        # Блок кнопок
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(30)

        btn_yes = QPushButton("Да")
        btn_yes.setFont(F_Sml)
        btn_yes.setFixedSize(180, 35)
        btn_yes.clicked.connect(self.accept)

        btn_no = QPushButton("Нет")
        btn_no.setFont(F_Sml)
        btn_no.setFixedSize(180, 35)
        btn_no.setDefault(True)
        btn_no.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)

        layout.addLayout(btn_layout)

# Диалог завершения печати
class SuccessPrintDialog(QDialog):
    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Печать")
        self.setFixedSize(300, 170)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 25, 15)
        
        # Блок значка и текста
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        icon_label = QLabel()
        style = QApplication.style()
        info_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
        icon_label.setPixmap(info_icon.pixmap(64, 64))
        
        text_label = QLabel(message)
        text_label.setFont(F_Sml)
        text_label.setWordWrap(True)

        content_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(content_layout)
        layout.addStretch()

        # Блок кнопки
        btn_layout = QHBoxLayout()

        btn_ok = QPushButton("ОК")
        btn_ok.setFont(F_Sml)
        btn_ok.setFixedSize(180, 35)
        btn_ok.setStyleSheet("margin-left: 100px;")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)
# Метод вызова окна диалога завершения печати
def show_success_message(parent: QWidget, message: str):
    dialog = SuccessPrintDialog(message, parent)
    dialog.exec()

# Окно "Защита от дурака"
class WarningDialog(QDialog):
    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Стопэ?!")
        self.setMinimumWidth(400)
        self.adjustSize()
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 25, 15)
        
        # Блок значка и текста
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        icon_label = QLabel()
        style = QApplication.style()
        warning_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        icon_label.setPixmap(warning_icon.pixmap(64, 64))
        
        text_label = QLabel(message)
        text_label.setFont(F_Sml)
        text_label.setWordWrap(True)

        content_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(content_layout)
        layout.addStretch()

        # Блок кнопки
        btn_layout = QHBoxLayout()

        btn_ok = QPushButton("Упс...")
        btn_ok.setFont(F_Sml)
        btn_ok.setFixedSize(180, 35)
        btn_ok.setStyleSheet("margin-left: 70px;")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)
# Метод вызова окна "Защита от дурака"
def show_warning_message(parent: QWidget, message: str):
    dialog = WarningDialog(message, parent)
    dialog.exec()

# Окно логотипа (анимация)
class LogoSplashDialog(QDialog):
    def __init__(self, logo_path: str, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        lbl_logo = QLabel()
        if os.path.exists(logo_path):
            lbl_logo.setPixmap(QPixmap(logo_path))
        
        layout.addWidget(lbl_logo)

        # Создание эффекта прозрачности
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # 1. Анимация появления (от 0.0 до 1.0) — 500 мс - 0.5 сек
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(500)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)

        # 2. Пауза во время полной видимости — 2000 мс - 2 сек
        self.pause = QPauseAnimation(2000)

        # 3. Анимация исчезновения (от 1.0 до 0.0) — 500 мс - 0.5 сек
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(500)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)

        # Последовательность воспроизведения анимаций логотипа
        self.anim_group = QSequentialAnimationGroup(self)
        self.anim_group.addAnimation(self.fade_in)
        self.anim_group.addAnimation(self.pause)
        self.anim_group.addAnimation(self.fade_out)

    # Метод запуска анимации логотипа
    def start_animation(self):
        self.anim_group.start()
# Окно предупреждения о MS Word
class WordWarningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("АНТУНГ!!!")
        self.setMinimumWidth(600)
        self.adjustSize()
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 25, 15)
        
        # Блок значка и текста
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        icon_label = QLabel()
        style = QApplication.style()
        warning_icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        icon_label.setPixmap(warning_icon.pixmap(128, 128))
        
        text_label = QLabel(
            "Рекомендую сохранить все открытые документы MS Word!\n\n"
            "Программа жестко эксплуатирует оболочку текстового редактора.\n"
            "Если не хочешь потерять данные, лучше сохранись.\n"
            "Я предупредил...\n"
        )
        text_label.setFont(F_Sml)
        text_label.setWordWrap(True)

        content_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(content_layout)
        layout.addStretch()

        # Блок кнопки
        btn_layout = QHBoxLayout()

        btn_ok = QPushButton("Всё закрыто, давай начинать")
        btn_ok.setFont(F_Sml)
        btn_ok.setFixedSize(400, 35)
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)

        layout.addLayout(btn_layout)
# Метод цепочки: Логотип -> Предупреждение
def logo_warning_window(logo_path: str, parent=None):
    splash = LogoSplashDialog(logo_path, parent)
    splash.show()
    
    loop = QEventLoop()
    # Закрытие логотип и выход из цикла ожидания сразу после завершения всей цепочки анимации
    splash.anim_group.finished.connect(loop.quit)
    
    # Запуска анимацию
    splash.start_animation()
    loop.exec()
    
    splash.close()

    # Открытие окна предупреждения после окончания анимации
    dialog = WordWarningDialog(parent)
    dialog.exec()