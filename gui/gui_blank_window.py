from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QLineEdit, QPushButton, QFrame, 
    QTabWidget, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt

from config import F_Mid_B, F_Nrm, F_Sml, CHECKBOX_STYLE, TAB_STYLE
from services.blank_print_service import process_blank_print
from gui.gui_dialog_window import show_success_message, show_warning_message

# Класс UI окна печати пустых бланков
class GuiBlankWindow(QDialog):
    # Метод инициализации формы
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if parent:
            self.setWindowFlags(Qt.WindowType.Window)
            
        self.setWindowTitle("Печать пустых бланков")
        self.resize(820, 655)

        self.doc_inputs = {}
        self.init_ui()

    # Метод инициализации UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        # 1. Заголовок
        lbl_title = QLabel("Печать пустых бланков")
        lbl_title.setFont(F_Mid_B)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(lbl_title)

        # 2. Вкладки Открытие / Закрытие
        self.tab = QTabWidget()
        self.tab.setFont(F_Sml)
        self.tab.setStyleSheet(TAB_STYLE)
        
        # Данные вкладок
        open_docs = [
            ("open_zayava", "Заявление", "1"),
            ("open_adm_act", "Акт приёма-передачи (Адм.)", "1"),
            ("open_adm_garant", "Гарантийное письмо (Адм.)", "1"),
            ("open_zks_dopka", "Доп. соглашение (ЖКС)", "1"),
            ("open_zks_act", "Акт восстановления (ЖКС)", "1"),
            ("open_zks_dogovor", "Договор (ЖКС)", "1"),
            ("open_drs_dopka", "Доп. соглашение (ДРС)", "1"),
            ("open_drs_f2", "Форма 2 (ДРС)", "1"),
            ("open_drs_dogovor", "Договор (ДРС)", "1"),
            ("open_hzs_dopka", "Доп. соглашение (ЗС)", "1"),
            ("open_hzs_f2", "Форма 2 (ЗС)", "1"),
            ("open_hzs_dogovor", "Договор (ЗС)", "1"),
        ]

        close_docs = [
            ("close_adm_act2", "Акт комиссии (Адм.)", "1"),
            ("close_zks_act2", "Акт комиссии (ЖКС)", "1"),
            ("close_zks_prper", "Акт приёма-передачи (ЖКС)", "1"),
            ("close_drs_prper", "Акт приёма-передачи (ДРС)", "1"),
            ("close_hzs_prper", "Акт приёма-передачи (ЗС)", "1"),
            ("close_f7", "Форма 7", "1"),
        ]

        self.tab.addTab(self._create_doc_list_tab(open_docs, with_scroll=True), "Открытие")
        self.tab.addTab(self._create_doc_list_tab(close_docs, with_scroll=False), "Закрытие")

        main_layout.addWidget(self.tab)

        # 3. Кнопка «Напечатать выбранные бланки»
        self.btn_print = QPushButton("Напечатать выбранное")
        self.btn_print.setFont(F_Nrm)
        self.btn_print.setFixedHeight(55)
        self.btn_print.setStyleSheet("""
            QPushButton { background-color: green; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: darkgreen; }
        """)
        self.btn_print.clicked.connect(self.on_print_clicked)
        main_layout.addWidget(self.btn_print)

        # 4. Кнопка «Назад»
        self.btn_back = QPushButton("Назад")
        self.btn_back.setFont(F_Nrm)
        self.btn_back.setFixedSize(140, 50)
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

    # Вспомогательный метод для UI и сборки списка документов во вкладке
    def _create_doc_list_tab(self, docs_list: list, with_scroll: bool = False) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(10)

        for doc_id, doc_name, default_copies in docs_list:
            row_frame = QFrame()
            row_frame.setStyleSheet("background-color: #E0E0E0; border-radius: 6px;")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(15, 8, 15, 8)

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

            container_layout.addWidget(row_frame)
            self.doc_inputs[doc_id] = {"checkbox": cb, "input": inp_copies}

        container_layout.addStretch()

        if with_scroll:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(container)
            scroll.setStyleSheet("QScrollArea { border: none; }")
            return scroll

        return container

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
                    show_warning_message(self, f"Сколько-сколько копий?\nШифратор, что ли?")
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

    # Метод подключения сервиса печати пустых бланков (с сообщение после печати)
    def on_print_clicked(self):
        if not self.validate_selective_print():
            return

        selected_blanks = {}
        for doc_id, controls in self.doc_inputs.items():
            cb = controls["checkbox"]
            inp = controls["input"]
            if cb.isChecked():
                selected_blanks[doc_id] = int(inp.text().strip())

        process_blank_print(selected_blanks)
        show_success_message(self, "Напечатали!!!")