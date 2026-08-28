from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QLineEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt

from config import F_Mid_B, F_Nrm, F_Sml, CHECKBOX_STYLE
from services.hzs_close_service import process_hzs_close
from utility.clear_temp import cleanup_temp_files
from gui.gui_dialog_window import show_success_message, show_warning_message

# Класс UI окна выборочной печати на закрытие (Зеленстрой)
class GuiHzsCloseEx(QDialog):
    # Метод инициализации формы
    def __init__(self, parent=None, order_data: dict = None):
        super().__init__(parent)
        self.order_data = order_data or {}
        
        if parent:
            self.setWindowFlags(Qt.WindowType.Window)
            
        self.setWindowTitle("Выборочная печать — Зеленстрой")
        self.resize(800, 550)

        self.init_ui()

    # Метод инициализации UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)

        # 1. Заголовок
        lbl_title = QLabel("Выбери документы и\nколичество копий")
        lbl_title.setFont(F_Mid_B)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_title)

        # 2. Список документов
        docs_data = [
            ("hzs_prper", "Акт приёма-передачи", "1"),
            ("f7", "Форма 7", "1"),
            ("rozpiska", "Расписка", "1")
        ]

        self.doc_inputs = {}

        for doc_id, doc_name, default_copies in docs_data:
            row_frame = QFrame()
            row_frame.setStyleSheet("background-color: #E0E0E0; border-radius: 6px;")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(20, 10, 20, 10)

            cb = QCheckBox(doc_name)
            cb.setFont(F_Sml)
            cb.setStyleSheet(CHECKBOX_STYLE)

            lbl_copies = QLabel("копий:")
            lbl_copies.setFont(F_Sml)

            inp_copies = QLineEdit(default_copies)
            inp_copies.setFont(F_Sml)
            inp_copies.setFixedWidth(50)
            inp_copies.setAlignment(Qt.AlignmentFlag.AlignCenter)
            inp_copies.setStyleSheet("background-color: white; border: 1px solid #7f7f7f; border-radius: 3px;")

            row_layout.addWidget(cb)
            row_layout.addStretch()
            row_layout.addWidget(lbl_copies)
            row_layout.addWidget(inp_copies)

            main_layout.addWidget(row_frame)
            self.doc_inputs[doc_id] = {"checkbox": cb, "input": inp_copies}

        main_layout.addStretch()

        # 3. Кнопка «Напечатать выбранное»
        self.btn_print = QPushButton("Напечатать выбранное")
        self.btn_print.setFont(F_Nrm)
        self.btn_print.setFixedHeight(60)
        self.btn_print.setStyleSheet("""
            QPushButton { background-color: green; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: darkgreen; }
        """)
        self.btn_print.clicked.connect(self.on_print_clicked)
        main_layout.addWidget(self.btn_print)

        # 4. Кнопка «Назад»
        self.btn_back = QPushButton("Назад")
        self.btn_back.setFont(F_Nrm)
        self.btn_back.setFixedSize(140, 60)
        self.btn_back.setStyleSheet("""
            QPushButton { background-color: gray; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #666666; }
        """)
        self.btn_back.clicked.connect(self.close)

        btn_back_layout = QHBoxLayout()
        btn_back_layout.addStretch()
        btn_back_layout.addWidget(self.btn_back)
        btn_back_layout.addStretch()
        main_layout.addLayout(btn_back_layout)

    # Метод "Защита от дурака"
    def validate_selective_print(self) -> bool:
        has_checked = False

        for doc_id, controls in self.doc_inputs.items():
            cb = controls["checkbox"]
            inp = controls["input"]

            if cb.isChecked():
                has_checked = True
                copies_raw = inp.text().strip()

                if not copies_raw:
                    show_warning_message(self, "Где копии?\nСколько вешать в граммах?")
                    inp.setFocus()
                    return False

                if not copies_raw.isdigit():
                    show_warning_message(self, "Сколько-сколько копий?\nШифратор, что ли?")
                    inp.setFocus()
                    return False

                copies_num = int(copies_raw)

                if copies_num == 0:
                    show_warning_message(self, "Ноль копий? Ты чё, Кернес, что ли?\nКого собрался множить на ноль?")
                    inp.setFocus()
                    return False

                if copies_num > 10:
                    show_warning_message(self, "Не многовато ли копий?\nТуалетная бумага закончилась?")
                    inp.setFocus()
                    return False

        if not has_checked:
            show_warning_message(self, "Поставь хоть один флажок!\nЧё печатать-то собрался?")
            return False

        return True

    # Метод подключения сервиса печати (с сообщением после печати)
    def on_print_clicked(self):
        if not self.validate_selective_print():
            return

        selected_docs = {}
        for doc_id, controls in self.doc_inputs.items():
            cb = controls["checkbox"]
            inp = controls["input"]
            if cb.isChecked():
                selected_docs[doc_id] = int(inp.text().strip())

        process_hzs_close(self.order_data, selected_docs=selected_docs)
        cleanup_temp_files()
        show_success_message(self, "Напечатали!!!")