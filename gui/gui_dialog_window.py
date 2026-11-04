import os
import json
from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QProgressBar,
    QPushButton, QApplication, QStyle, QWidget, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QEventLoop, QPropertyAnimation, QSequentialAnimationGroup, QPauseAnimation
from PyQt6.QtGui import QIcon, QPixmap

from config import ICON_PATH, F_Sml, CHECKBOX_STYLE

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
        btn_yes.setDefault(True)
        btn_yes.clicked.connect(self.accept)

        btn_no = QPushButton("Нет")
        btn_no.setFont(F_Sml)
        btn_no.setFixedSize(180, 35)
        btn_no.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)

        layout.addLayout(btn_layout)

# Диалог прогресса печати
class PrintProgressDialog(QDialog):
    def __init__(self, max_steps: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Печать документов")
        self.setFixedSize(550, 220)  # Увеличили высоту окна для трех строк текста
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        # Текст состояния
        self.lbl_status = QLabel("Подготовка к печати...\n\n", self)
        self.lbl_status.setFont(F_Sml)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        # Прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFont(F_Sml)
        self.progress_bar.setRange(0, max_steps)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(36)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        # Кнопка отмены
        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setFont(F_Sml)
        self.btn_cancel.setFixedSize(140, 35)
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self._is_canceled = False
        self.btn_cancel.clicked.connect(lambda: setattr(self, '_is_canceled', True))

    def update_progress(self, current_step: int, text: str):
        self.progress_bar.setValue(current_step)
        self.lbl_status.setText(text)
        QApplication.processEvents()

    def was_canceled(self) -> bool:
        return self._is_canceled

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
        self.setWindowTitle("АХТУНГ!!!")
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

        # Чекбокс "Больше не показывать"
        self.chk_dont_show = QCheckBox("Хватит напоминать, достал!", self)
        self.chk_dont_show.setFont(F_Sml)
        self.chk_dont_show.setStyleSheet(CHECKBOX_STYLE)
        layout.addWidget(self.chk_dont_show)

        layout.addSpacing(10)

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

    # Метод для получения состояния чекбокса
    def is_dont_show_checked(self) -> bool:
        return self.chk_dont_show.isChecked()
    
# Метод цепочки: Логотип -> Предупреждение
def logo_warning_window(logo_path: str, parent=None):
    splash = LogoSplashDialog(logo_path, parent)
    splash.show()
    
    loop = QEventLoop()
    splash.anim_group.finished.connect(loop.quit)
    splash.start_animation()
    loop.exec()
    splash.close()

    config_path = os.path.join("data", "app_config.json")
    show_warning = True
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                show_warning = config_data.get("show_word_warning", True)
        except Exception:
            pass

    if not show_warning:
        return

    # Открытие окна предупреждения
    dialog = WordWarningDialog(parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        if dialog.is_dont_show_checked():
            try:
                config_data = {}
                if os.path.exists(config_path):
                    with open(config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                
                config_data["show_word_warning"] = False
                
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"Не удалось сохранить настройку предупреждения Word: {e}")

# Диалог предложения обновиться
class UpdateAvailableDialog(QDialog):
    def __init__(self, latest_version: str, current_version: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вышло обновление!")
        self.setMinimumWidth(460)
        self.adjustSize()
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 25, 25, 15)
        
        # Блок значка и текста
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        icon_label = QLabel()
        style = QApplication.style()
        info_icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        icon_label.setPixmap(info_icon.pixmap(64, 64))
        
        text_label = QLabel(
            f"Доступна новая версия: {latest_version}\n"
            f"Текущая версия: {current_version}\n\n"
            f"Перейти к скачиванию?\n"
        )
        text_label.setFont(F_Sml)
        text_label.setWordWrap(True)

        content_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(content_layout)
        layout.addStretch()

        # Блок кнопок
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        btn_yes = QPushButton("Давай!")
        btn_yes.setFont(F_Sml)
        btn_yes.setFixedSize(160, 35)
        btn_yes.clicked.connect(self.accept)

        btn_no = QPushButton("Позже")
        btn_no.setFont(F_Sml)
        btn_no.setFixedSize(160, 35)
        btn_no.setDefault(True)
        btn_no.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)

        layout.addLayout(btn_layout)

# Вспомогательный метод вызова окна обновления
def show_update_dialog(latest_version: str, current_version: str, parent: QWidget = None) -> bool:
    dialog = UpdateAvailableDialog(latest_version, current_version, parent)
    return dialog.exec() == QDialog.DialogCode.Accepted