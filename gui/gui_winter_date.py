from PyQt6.QtWidgets import QDialog, QLabel, QDateEdit, QPushButton
from PyQt6.QtCore import Qt, QDate

from config import F_Mid_B, F_Sml, F_Nrm

# Класс UI окна сроков для зимнего периода
class WinterDateWindow(QDialog):
    # Метод инициализации формы
    def __init__(self, current_green=None, current_asphalt=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Корректировка дат")
        self.setFixedSize(500, 300)

        self.green_date_val = current_green or QDate.currentDate()
        self.asphalt_date_val = current_asphalt or QDate.currentDate()

        self.init_ui()
        self.setup_logic()

    # Метод инициализации UI
    def init_ui(self):
        # 1. Заголовок
        lbl_title = QLabel("Корректировка дат", self)
        lbl_title.setFont(F_Mid_B)
        lbl_title.setGeometry(0, 25, 500, 40)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 2. Зеленая зона
        lbl_green = QLabel("Зеленая зона", self)
        lbl_green.setFont(F_Sml)
        lbl_green.setGeometry(40, 95, 200, 35)
        lbl_green.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.date_green = QDateEdit(self)
        self.date_green.setFont(F_Sml)
        self.date_green.setGeometry(260, 95, 200, 35)
        self.date_green.setCalendarPopup(True)
        self.date_green.setDate(self.green_date_val)
        self.date_green.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3. Асфальтобетон / Грунтовка
        lbl_asphalt = QLabel("Асфальтобетон\nГрунтовка", self)
        lbl_asphalt.setFont(F_Sml)
        lbl_asphalt.setGeometry(40, 150, 200, 50)
        lbl_asphalt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.date_asphalt = QDateEdit(self)
        self.date_asphalt.setFont(F_Sml)
        self.date_asphalt.setGeometry(260, 155, 200, 35)
        self.date_asphalt.setCalendarPopup(True)
        self.date_asphalt.setDate(self.asphalt_date_val)
        self.date_asphalt.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 4. Кнопка «Применить»
        self.btn_apply = QPushButton("Применить", self)
        self.btn_apply.setFont(F_Nrm)
        self.btn_apply.setGeometry(50, 230, 400, 45)
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

    # Метод подключения логики
    def setup_logic(self):
        self.btn_apply.clicked.connect(self.accept)

    # Метод возвращения данных
    def get_dates(self):
        return self.date_green.date(), self.date_asphalt.date()