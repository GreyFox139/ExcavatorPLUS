from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QDateEdit, 
    QCheckBox, QPushButton, QFrame, QTabWidget, QWidget,
    QApplication, QStyle, QComboBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QPalette, QFont

from config import (
    F_Big_B, F_Nrm, F_Sml, 
    CHECKBOX_STYLE, RADIO_STYLE, TAB_STYLE_4,
    ZKS_BLAGO_DB, COMPANY_LIMITS, PRIORITY
)
from gui.gui_dialog_window import show_success_message, show_warning_message
from utility.clear_temp import cleanup_temp_files
from utility.street_completer import setup_street_completer
from gui.gui_rozpiska import RozpiskaTextDialog
from services.adm_close_service import process_adm_close, get_rozpiska_text
from services.zks_close_service import process_zks_close, get_rozpiska_text
from services.drs_close_service import process_drs_close, get_rozpiska_text
from services.hzs_close_service import process_hzs_close, get_rozpiska_text
from gui.extra.gui_adm_close_ex import GuiAdmCloseEx
from gui.extra.gui_zks_close_ex import GuiZksCloseEx
from gui.extra.gui_drs_close_ex import GuiDrsCloseEx
from gui.extra.gui_hzs_close_ex import GuiHzsCloseEx

# Класс UI окна для закрытия ордеров
class CloseWindow(QDialog):
    # Метод инициализации формы
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Закрытие ордеров")
        self.setFixedSize(900, 850)

        self.init_ui()
        self.setup_logic()

        font = QFont("Courier New", 18)

        for date_edit in self.findChildren(QDateEdit):
            date_edit.setCalendarPopup(True)
            date_edit.calendarWidget().setFont(font)

    # Метод инициализации UI (общий для вкладок)
    def init_ui(self):
        # 1. Заголовок
        lbl_title = QLabel("Закрытие ордеров", self)
        lbl_title.setFont(F_Big_B)
        lbl_title.setGeometry(0, 20, 900, 60)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 2. Область вкладок по организациям
        self.tabs = QTabWidget(self)
        self.tabs.setFont(F_Sml)
        self.tabs.setStyleSheet(TAB_STYLE_4)
        self.tabs.setGeometry(30, 105, 840, 630)

        # Создание 4 вкладок
        self.tab_adm = QWidget()
        self.tab_zks = QWidget()
        self.tab_drs = QWidget()
        self.tab_hzs = QWidget()

        self.tabs.addTab(self.tab_adm, "Администрация")
        self.tabs.addTab(self.tab_zks, "Житлокомсервис")
        self.tabs.addTab(self.tab_drs, "Дорремстрой")
        self.tabs.addTab(self.tab_hzs, "Зеленстрой")

        # Наполнение вкладок содержимым
        self.init_tab_adm()
        self.init_tab_zks()
        self.init_tab_drs()
        self.init_tab_hzs()

        self.btn_back = QPushButton("Назад", self)
        self.btn_back.setFont(F_Nrm)
        self.btn_back.setGeometry(35, 760, 200, 70)
        self.btn_back.setStyleSheet("""
            QPushButton { background-color: gray; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #666666; }
        """)

        # 3. Кнопка «Сброс»
        self.btn_reset = QPushButton(self)
        self.btn_reset.setGeometry(290, 760, 80, 70)
        
        style = QApplication.style()
        reload_icon = style.standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)
        self.btn_reset.setIcon(reload_icon)
        self.btn_reset.setIconSize(QSize(54, 54))
        self.btn_reset.setToolTip("Очистить все поля")
        self.btn_reset.setStyleSheet("""
            QPushButton { background-color: #A83232; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #7D2525; }
        """)

        # 4. Кнопка "Выборочная печать"
        self.btn_sel_print = QPushButton("Выборочная\n печать", self)
        self.btn_sel_print.setFont(F_Nrm)
        self.btn_sel_print.setGeometry(425, 760, 230, 70)
        self.btn_sel_print.setStyleSheet("""
            QPushButton { background-color: green; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: darkgreen; }
        """)

        # 5. Кнопка "Печать"
        self.btn_print = QPushButton("Печать", self)
        self.btn_print.setFont(F_Nrm)
        self.btn_print.setGeometry(665, 760, 200, 70)
        self.btn_print.setStyleSheet("""
            QPushButton { background-color: green; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: darkgreen; }
        """)

    # Метод инициализации UI (вкладка "Администрация")
    def init_tab_adm(self):
        parent = self.tab_adm

        # 1. Блок ордера
        lbl_order = QLabel("Ордер", parent)
        lbl_order.setFont(F_Sml)
        lbl_order.setGeometry(30, 15, 100, 30)

        lbl_ord_num = QLabel("#", parent)
        lbl_ord_num.setFont(F_Sml)
        lbl_ord_num.setGeometry(30, 50, 20, 35)

        self.adm_txt_order_num = QLineEdit(parent)
        self.adm_txt_order_num.setFont(F_Sml)
        self.adm_txt_order_num.setGeometry(55, 50, 200, 35)
        self.adm_txt_order_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ord_date = QLabel("дата", parent)
        lbl_ord_date.setFont(F_Sml)
        lbl_ord_date.setGeometry(270, 50, 55, 35)

        self.adm_date_order = QDateEdit(parent)
        self.adm_date_order.setFont(F_Sml)
        self.adm_date_order.setGeometry(335, 50, 190, 35)
        self.adm_date_order.setCalendarPopup(True)
        self.adm_date_order.setDate(QDate.currentDate())
        self.adm_date_order.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.adm_chk_no_order = QCheckBox("не использовать", parent)
        self.adm_chk_no_order.setFont(F_Sml)
        self.adm_chk_no_order.setGeometry(550, 50, 260, 35)
        self.adm_chk_no_order.setStyleSheet(CHECKBOX_STYLE)
        self.adm_chk_no_order.setChecked(True)

        # 2. Блок адреса
        lbl_addr = QLabel("Адрес", parent)
        lbl_addr.setFont(F_Sml)
        lbl_addr.setGeometry(30, 120, 100, 30)

        lbl_house = QLabel("# дома", parent)
        lbl_house.setFont(F_Sml)
        lbl_house.setGeometry(600, 120, 100, 30)

        self.adm_txt_address = QLineEdit(parent)
        self.adm_txt_address.setFont(F_Sml)
        self.adm_txt_address.setGeometry(30, 150, 540, 35)
        self.adm_txt_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.adm_txt_address)

        self.adm_txt_house = QLineEdit(parent)
        self.adm_txt_house.setFont(F_Sml)
        self.adm_txt_house.setGeometry(600, 150, 200, 35)
        self.adm_txt_house.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.adm_chk_cross = QCheckBox("пересечение", parent)
        self.adm_chk_cross.setFont(F_Sml)
        self.adm_chk_cross.setGeometry(30, 195, 190, 35)
        self.adm_chk_cross.setStyleSheet(CHECKBOX_STYLE)

        self.adm_txt_address_cross = QLineEdit(parent)
        self.adm_txt_address_cross.setFont(F_Sml)
        self.adm_txt_address_cross.setGeometry(230, 195, 570, 35)
        self.adm_txt_address_cross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.adm_txt_address_cross)
        self.adm_txt_address_cross.setEnabled(False)

        v_line = QFrame(parent)
        v_line.setGeometry(420, 260, 2, 305)
        v_line.setFrameShape(QFrame.Shape.VLine)

        # 3. Левый блок: Тип покрытия и его площадь
        lbl_cov_title = QLabel("Тип покрытия и его площадь", parent)
        lbl_cov_title.setFont(F_Sml)
        lbl_cov_title.setGeometry(30, 260, 365, 30)

        self.adm_chk_green_zone = QCheckBox("Зеленая зона", parent)
        self.adm_chk_green_zone.setFont(F_Sml)
        self.adm_chk_green_zone.setGeometry(30, 300, 210, 35)
        self.adm_chk_green_zone.setStyleSheet(CHECKBOX_STYLE)

        self.adm_txt_green_zone = QLineEdit(parent)
        self.adm_txt_green_zone.setFont(F_Sml)
        self.adm_txt_green_zone.setGeometry(250, 300, 140, 35)
        self.adm_txt_green_zone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adm_txt_green_zone.setEnabled(False)

        self.adm_chk_type2 = QCheckBox("Второй тип", parent)
        self.adm_chk_type2.setFont(F_Sml)
        self.adm_chk_type2.setGeometry(30, 340, 200, 35)
        self.adm_chk_type2.setStyleSheet(CHECKBOX_STYLE)

        self.adm_txt_type2 = QLineEdit(parent)
        self.adm_txt_type2.setFont(F_Sml)
        self.adm_txt_type2.setGeometry(250, 340, 140, 35)
        self.adm_txt_type2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adm_txt_type2.setEnabled(False)

        # Радиокнопки выбора второго типа покрытия
        self.adm_rb_asphalt = QRadioButton("Асфальт", parent)
        self.adm_rb_asphalt.setFont(F_Sml)
        self.adm_rb_asphalt.setGeometry(50, 395, 330, 32)
        self.adm_rb_asphalt.setStyleSheet(RADIO_STYLE)
        self.adm_rb_asphalt.setEnabled(False)

        self.adm_rb_tile = QRadioButton("Тротуарная плитка", parent)
        self.adm_rb_tile.setFont(F_Sml)
        self.adm_rb_tile.setGeometry(50, 430, 330, 32)
        self.adm_rb_tile.setStyleSheet(RADIO_STYLE)
        self.adm_rb_tile.setEnabled(False)

        self.adm_rb_dirt = QRadioButton("Грунтовая дорога", parent)
        self.adm_rb_dirt.setFont(F_Sml)
        self.adm_rb_dirt.setGeometry(50, 465, 330, 32)
        self.adm_rb_dirt.setStyleSheet(RADIO_STYLE)
        self.adm_rb_dirt.setEnabled(False)

        # Объединение радиокнопок в эксклюзивную группу
        self.adm_bg_type2 = QButtonGroup(parent)
        self.adm_bg_type2.addButton(self.adm_rb_asphalt)
        self.adm_bg_type2.addButton(self.adm_rb_tile)
        self.adm_bg_type2.addButton(self.adm_rb_dirt)
        self.adm_rb_asphalt.setChecked(True)

        self.adm_chk_form7 = QCheckBox("Печать Формы 7", parent)
        self.adm_chk_form7.setFont(F_Sml)
        self.adm_chk_form7.setGeometry(30, 525, 240, 35)
        self.adm_chk_form7.setStyleSheet(CHECKBOX_STYLE)

        # 4. Правый блок: Комиссия
        lbl_comm_title = QLabel("Комиссия", parent)
        lbl_comm_title.setFont(F_Sml)
        lbl_comm_title.setGeometry(450, 260, 350, 30)
        lbl_comm_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.adm_chk_jks_hbu = QCheckBox("Участки ЖКС и ХБУ", parent)
        self.adm_chk_jks_hbu.setFont(F_Sml)
        self.adm_chk_jks_hbu.setGeometry(450, 300, 350, 35)
        self.adm_chk_jks_hbu.setStyleSheet(CHECKBOX_STYLE)

        self.adm_lbl_jks = QLabel("Участок ЖКС", parent)
        self.adm_lbl_jks.setFont(F_Sml)
        self.adm_lbl_jks.setGeometry(450, 345, 180, 35)
        self.adm_lbl_jks.setEnabled(False)

        self.adm_cb_jks_unit = QComboBox(parent)
        self.adm_cb_jks_unit.setFont(F_Sml)
        self.adm_cb_jks_unit.setGeometry(650, 345, 150, 35)
        self.adm_cb_jks_unit.setEditable(True)
        self.adm_cb_jks_unit.lineEdit().setReadOnly(True)
        self.adm_cb_jks_unit.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adm_cb_jks_unit.setEnabled(False)

        for u in sorted(ZKS_BLAGO_DB.keys()):
            self.adm_cb_jks_unit.addItem(str(u))

        self.adm_lbl_hbu = QLabel("Участок ХБУ", parent)
        self.adm_lbl_hbu.setFont(F_Sml)
        self.adm_lbl_hbu.setGeometry(450, 390, 180, 35)
        self.adm_lbl_hbu.setEnabled(False)

        self.adm_txt_hbu_unit = QLineEdit(parent)
        self.adm_txt_hbu_unit.setFont(F_Sml)
        self.adm_txt_hbu_unit.setGeometry(650, 390, 150, 35)
        self.adm_txt_hbu_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adm_txt_hbu_unit.setEnabled(False)

        self.adm_chk_other = QCheckBox("Другие представители", parent)
        self.adm_chk_other.setFont(F_Sml)
        self.adm_chk_other.setGeometry(450, 445, 350, 35)
        self.adm_chk_other.setStyleSheet(CHECKBOX_STYLE)

        self.adm_chk_receipt = QCheckBox("Печать расписки", parent)
        self.adm_chk_receipt.setFont(F_Sml)
        self.adm_chk_receipt.setGeometry(450, 525, 250, 35)
        self.adm_chk_receipt.setStyleSheet(CHECKBOX_STYLE)

        self.adm_btn_txt_receipt = QPushButton("Текст", parent)
        self.adm_btn_txt_receipt.setFont(F_Sml)
        self.adm_btn_txt_receipt.setGeometry(710, 525, 100, 35)
        self.adm_btn_txt_receipt.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
            QPushButton:disabled { background-color: #7f7f7f; color: white; border: none; border-radius: 4px; }
        """)
        self.adm_btn_txt_receipt.setEnabled(False)

    # Метод инициализации UI (вкладка "Жилокомсервис")
    def init_tab_zks(self):
        parent = self.tab_zks

        # 1. Блок ордера
        lbl_order = QLabel("Ордер", parent)
        lbl_order.setFont(F_Sml)
        lbl_order.setGeometry(30, 15, 100, 30)

        lbl_ord_num = QLabel("#", parent)
        lbl_ord_num.setFont(F_Sml)
        lbl_ord_num.setGeometry(30, 50, 20, 35)

        self.zks_txt_order_num = QLineEdit(parent)
        self.zks_txt_order_num.setFont(F_Sml)
        self.zks_txt_order_num.setGeometry(55, 50, 200, 35)
        self.zks_txt_order_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ord_date = QLabel("дата", parent)
        lbl_ord_date.setFont(F_Sml)
        lbl_ord_date.setGeometry(270, 50, 55, 35)

        self.zks_date_order = QDateEdit(parent)
        self.zks_date_order.setFont(F_Sml)
        self.zks_date_order.setGeometry(335, 50, 190, 35)
        self.zks_date_order.setCalendarPopup(True)
        self.zks_date_order.setDate(QDate.currentDate())
        self.zks_date_order.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zks_chk_no_order = QCheckBox("не использовать", parent)
        self.zks_chk_no_order.setFont(F_Sml)
        self.zks_chk_no_order.setGeometry(550, 50, 260, 35)
        self.zks_chk_no_order.setStyleSheet(CHECKBOX_STYLE)
        self.zks_chk_no_order.setChecked(True)

        # 2. Доп. соглашение (без 5/в)
        lbl_dopka = QLabel("Доп. соглашение (без 5/в)", parent)
        lbl_dopka.setFont(F_Sml)
        lbl_dopka.setGeometry(30, 95, 400, 30)

        lbl_dop_num = QLabel("#", parent)
        lbl_dop_num.setFont(F_Sml)
        lbl_dop_num.setGeometry(30, 130, 20, 35)

        self.zks_txt_dop_num = QLineEdit(parent)
        self.zks_txt_dop_num.setFont(F_Sml)
        self.zks_txt_dop_num.setGeometry(55, 130, 200, 35)
        self.zks_txt_dop_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_dop_date = QLabel("дата", parent)
        lbl_dop_date.setFont(F_Sml)
        lbl_dop_date.setGeometry(270, 130, 55, 35)

        self.zks_date_dop = QDateEdit(parent)
        self.zks_date_dop.setFont(F_Sml)
        self.zks_date_dop.setGeometry(335, 130, 190, 35)
        self.zks_date_dop.setCalendarPopup(True)
        self.zks_date_dop.setDate(QDate.currentDate())
        self.zks_date_dop.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3. Адресный блок
        lbl_addr = QLabel("Адрес", parent)
        lbl_addr.setFont(F_Sml)
        lbl_addr.setGeometry(30, 175, 100, 30)

        lbl_house = QLabel("# дома", parent)
        lbl_house.setFont(F_Sml)
        lbl_house.setGeometry(600, 175, 100, 30)

        self.zks_txt_address = QLineEdit(parent)
        self.zks_txt_address.setFont(F_Sml)
        self.zks_txt_address.setGeometry(30, 205, 540, 35)
        self.zks_txt_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.zks_txt_address)

        self.zks_txt_house = QLineEdit(parent)
        self.zks_txt_house.setFont(F_Sml)
        self.zks_txt_house.setGeometry(600, 205, 200, 35)
        self.zks_txt_house.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zks_chk_cross = QCheckBox("пересечение", parent)
        self.zks_chk_cross.setFont(F_Sml)
        self.zks_chk_cross.setGeometry(30, 250, 190, 35)
        self.zks_chk_cross.setStyleSheet(CHECKBOX_STYLE)

        self.zks_txt_address_cross = QLineEdit(parent)
        self.zks_txt_address_cross.setFont(F_Sml)
        self.zks_txt_address_cross.setGeometry(230, 250, 570, 35)
        self.zks_txt_address_cross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.zks_txt_address_cross)
        self.zks_txt_address_cross.setEnabled(False)

        # 4. Шурфы и Площади (Левый блок)
        lbl_shurf_title = QLabel("Шурфы", parent)
        lbl_shurf_title.setFont(F_Sml)
        lbl_shurf_title.setGeometry(30, 320, 100, 30)

        lbl_sq_title = QLabel("Площадь, м²", parent)
        lbl_sq_title.setFont(F_Sml)
        lbl_sq_title.setGeometry(365, 320, 200, 30)

        self.zks_shurf_combos = []
        self.zks_dig_fields = []

        y_offset = 360
        for i in range(3):
            lbl_type = QLabel(f"Тип {i+1}", parent)
            lbl_type.setFont(F_Sml)
            lbl_type.setGeometry(30, y_offset, 80, 35)

            cb_type = QComboBox(parent)
            cb_type.setFont(F_Sml)
            cb_type.setGeometry(120, y_offset, 200, 35)
            cb_type.setEditable(True)
            cb_type.lineEdit().setReadOnly(True)
            cb_type.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.zks_shurf_combos.append(cb_type)

            txt_dig = QLineEdit(parent)
            txt_dig.setFont(F_Sml)
            txt_dig.setGeometry(350, y_offset, 180, 35)
            txt_dig.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_dig.setEnabled(i == 0)
            self.zks_dig_fields.append(txt_dig)

            y_offset += 45

        v_line = QFrame(parent)
        v_line.setGeometry(570, 325, 2, 175)
        v_line.setFrameShape(QFrame.Shape.VLine)

        # 5. Участки ЖКС и ХБУ (Правый блок)
        lbl_jks_unit = QLabel("Участок ЖКС", parent)
        lbl_jks_unit.setFont(F_Sml)
        lbl_jks_unit.setGeometry(585, 320, 200, 30)
        lbl_jks_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zks_cb_jks_unit = QComboBox(parent)
        self.zks_cb_jks_unit.setFont(F_Sml)
        self.zks_cb_jks_unit.setGeometry(610, 360, 150, 35)
        self.zks_cb_jks_unit.setEditable(True)
        self.zks_cb_jks_unit.lineEdit().setReadOnly(True)
        self.zks_cb_jks_unit.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for u in sorted(ZKS_BLAGO_DB.keys()):
            self.zks_cb_jks_unit.addItem(str(u))

        lbl_hbu_unit = QLabel("Участок ХБУ", parent)
        lbl_hbu_unit.setFont(F_Sml)
        lbl_hbu_unit.setGeometry(585, 405, 200, 30)
        lbl_hbu_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.zks_txt_hbu_unit = QLineEdit(parent)
        self.zks_txt_hbu_unit.setFont(F_Sml)
        self.zks_txt_hbu_unit.setGeometry(610, 445, 150, 35)
        self.zks_txt_hbu_unit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 6. Блок чекбоксов
        self.zks_chk_form7 = QCheckBox("Печать Формы 7", parent)
        self.zks_chk_form7.setFont(F_Sml)
        self.zks_chk_form7.setGeometry(30, 520, 240, 35)
        self.zks_chk_form7.setStyleSheet(CHECKBOX_STYLE)

        self.zks_chk_receipt = QCheckBox("Печать расписки", parent)
        self.zks_chk_receipt.setFont(F_Sml)
        self.zks_chk_receipt.setGeometry(330, 520, 250, 35)
        self.zks_chk_receipt.setStyleSheet(CHECKBOX_STYLE)

        self.zks_btn_txt_receipt = QPushButton("Текст", parent)
        self.zks_btn_txt_receipt.setFont(F_Sml)
        self.zks_btn_txt_receipt.setGeometry(595, 520, 100, 35)
        self.zks_btn_txt_receipt.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
            QPushButton:disabled { background-color: #7f7f7f; color: white; border: none; border-radius: 4px; }
        """)
        self.zks_btn_txt_receipt.setEnabled(False)

    # Метод инициализации UI (вкладка "Дорремстрой")
    def init_tab_drs(self):
        parent = self.tab_drs

        # 1. Блок ордера
        lbl_order = QLabel("Ордер", parent)
        lbl_order.setFont(F_Sml)
        lbl_order.setGeometry(30, 15, 100, 30)

        lbl_ord_num = QLabel("#", parent)
        lbl_ord_num.setFont(F_Sml)
        lbl_ord_num.setGeometry(30, 50, 20, 35)

        self.drs_txt_order_num = QLineEdit(parent)
        self.drs_txt_order_num.setFont(F_Sml)
        self.drs_txt_order_num.setGeometry(55, 50, 200, 35)
        self.drs_txt_order_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ord_date = QLabel("дата", parent)
        lbl_ord_date.setFont(F_Sml)
        lbl_ord_date.setGeometry(270, 50, 55, 35)

        self.drs_date_order = QDateEdit(parent)
        self.drs_date_order.setFont(F_Sml)
        self.drs_date_order.setGeometry(335, 50, 190, 35)
        self.drs_date_order.setCalendarPopup(True)
        self.drs_date_order.setDate(QDate.currentDate())
        self.drs_date_order.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.drs_chk_no_order = QCheckBox("не использовать", parent)
        self.drs_chk_no_order.setFont(F_Sml)
        self.drs_chk_no_order.setGeometry(550, 50, 260, 35)
        self.drs_chk_no_order.setStyleSheet(CHECKBOX_STYLE)
        self.drs_chk_no_order.setChecked(False)  # Выключен по умолчанию

        # 2. Блок адреса
        lbl_addr = QLabel("Адрес", parent)
        lbl_addr.setFont(F_Sml)
        lbl_addr.setGeometry(30, 120, 100, 30)

        lbl_house = QLabel("# дома", parent)
        lbl_house.setFont(F_Sml)
        lbl_house.setGeometry(600, 120, 100, 30)

        self.drs_txt_address = QLineEdit(parent)
        self.drs_txt_address.setFont(F_Sml)
        self.drs_txt_address.setGeometry(30, 150, 540, 35)
        self.drs_txt_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.drs_txt_address)

        self.drs_txt_house = QLineEdit(parent)
        self.drs_txt_house.setFont(F_Sml)
        self.drs_txt_house.setGeometry(600, 150, 200, 35)
        self.drs_txt_house.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.drs_chk_cross = QCheckBox("пересечение", parent)
        self.drs_chk_cross.setFont(F_Sml)
        self.drs_chk_cross.setGeometry(30, 195, 190, 35)
        self.drs_chk_cross.setStyleSheet(CHECKBOX_STYLE)

        self.drs_txt_address_cross = QLineEdit(parent)
        self.drs_txt_address_cross.setFont(F_Sml)
        self.drs_txt_address_cross.setGeometry(230, 195, 570, 35)
        self.drs_txt_address_cross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.drs_txt_address_cross)
        self.drs_txt_address_cross.setEnabled(False)

        # 3. Блок чекбоксов
        self.drs_chk_form7 = QCheckBox("Печать Формы 7", parent)
        self.drs_chk_form7.setFont(F_Sml)
        self.drs_chk_form7.setGeometry(30, 260, 240, 35)
        self.drs_chk_form7.setStyleSheet(CHECKBOX_STYLE)

        self.drs_chk_receipt = QCheckBox("Печать расписки", parent)
        self.drs_chk_receipt.setFont(F_Sml)
        self.drs_chk_receipt.setGeometry(435, 260, 250, 35)
        self.drs_chk_receipt.setStyleSheet(CHECKBOX_STYLE)

        self.drs_btn_txt_receipt = QPushButton("Текст", parent)
        self.drs_btn_txt_receipt.setFont(F_Sml)
        self.drs_btn_txt_receipt.setGeometry(700, 260, 100, 35)
        self.drs_btn_txt_receipt.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
            QPushButton:disabled { background-color: #7f7f7f; color: white; border: none; border-radius: 4px; }
        """)
        self.drs_btn_txt_receipt.setEnabled(False)

    # Метод инициализации UI (вкладка "Зеленстрой")
    def init_tab_hzs(self):
        parent = self.tab_hzs

        # 1. Блок ордера
        lbl_order = QLabel("Ордер", parent)
        lbl_order.setFont(F_Sml)
        lbl_order.setGeometry(30, 15, 100, 30)

        lbl_ord_num = QLabel("#", parent)
        lbl_ord_num.setFont(F_Sml)
        lbl_ord_num.setGeometry(30, 50, 20, 35)

        self.hzs_txt_order_num = QLineEdit(parent)
        self.hzs_txt_order_num.setFont(F_Sml)
        self.hzs_txt_order_num.setGeometry(55, 50, 200, 35)
        self.hzs_txt_order_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_ord_date = QLabel("дата", parent)
        lbl_ord_date.setFont(F_Sml)
        lbl_ord_date.setGeometry(270, 50, 55, 35)

        self.hzs_date_order = QDateEdit(parent)
        self.hzs_date_order.setFont(F_Sml)
        self.hzs_date_order.setGeometry(335, 50, 190, 35)
        self.hzs_date_order.setCalendarPopup(True)
        self.hzs_date_order.setDate(QDate.currentDate())
        self.hzs_date_order.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hzs_chk_no_order = QCheckBox("не использовать", parent)
        self.hzs_chk_no_order.setFont(F_Sml)
        self.hzs_chk_no_order.setGeometry(550, 50, 260, 35)
        self.hzs_chk_no_order.setStyleSheet(CHECKBOX_STYLE)
        self.hzs_chk_no_order.setChecked(True)

        # 2. Адресный блок
        lbl_addr = QLabel("Адрес", parent)
        lbl_addr.setFont(F_Sml)
        lbl_addr.setGeometry(30, 120, 100, 30)

        lbl_house = QLabel("# дома", parent)
        lbl_house.setFont(F_Sml)
        lbl_house.setGeometry(600, 120, 100, 30)

        self.hzs_txt_address = QLineEdit(parent)
        self.hzs_txt_address.setFont(F_Sml)
        self.hzs_txt_address.setGeometry(30, 150, 540, 35)
        self.hzs_txt_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.hzs_txt_address)

        self.hzs_txt_house = QLineEdit(parent)
        self.hzs_txt_house.setFont(F_Sml)
        self.hzs_txt_house.setGeometry(600, 150, 200, 35)
        self.hzs_txt_house.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hzs_chk_cross = QCheckBox("пересечение", parent)
        self.hzs_chk_cross.setFont(F_Sml)
        self.hzs_chk_cross.setGeometry(30, 195, 190, 35)
        self.hzs_chk_cross.setStyleSheet(CHECKBOX_STYLE)

        self.hzs_txt_address_cross = QLineEdit(parent)
        self.hzs_txt_address_cross.setFont(F_Sml)
        self.hzs_txt_address_cross.setGeometry(230, 195, 570, 35)
        self.hzs_txt_address_cross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.hzs_txt_address_cross)
        self.hzs_txt_address_cross.setEnabled(False)

        # 3. Блок шурфов и площадей
        lbl_shurf_title = QLabel("Шурфы", parent)
        lbl_shurf_title.setFont(F_Sml)
        lbl_shurf_title.setGeometry(30, 270, 100, 30)

        lbl_sq_title = QLabel("Площадь, м²", parent)
        lbl_sq_title.setFont(F_Sml)
        lbl_sq_title.setGeometry(365, 270, 200, 30)

        self.hzs_shurf_combos = []
        self.hzs_dig_fields = []

        y_offset = 305
        for i in range(3):
            lbl_type = QLabel(f"Тип {i+1}", parent)
            lbl_type.setFont(F_Sml)
            lbl_type.setGeometry(30, y_offset, 80, 35)

            cb_type = QComboBox(parent)
            cb_type.setFont(F_Sml)
            cb_type.setGeometry(120, y_offset, 200, 35)
            cb_type.setEditable(True)
            cb_type.lineEdit().setReadOnly(True)
            cb_type.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hzs_shurf_combos.append(cb_type)

            txt_dig = QLineEdit(parent)
            txt_dig.setFont(F_Sml)
            txt_dig.setGeometry(350, y_offset, 180, 35)
            txt_dig.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_dig.setEnabled(i == 0)
            self.hzs_dig_fields.append(txt_dig)

            y_offset += 45

        # 4. Блок чекбоксов
        self.hzs_chk_form7 = QCheckBox("Печать Формы 7", parent)
        self.hzs_chk_form7.setFont(F_Sml)
        self.hzs_chk_form7.setGeometry(30, 470, 240, 35)
        self.hzs_chk_form7.setStyleSheet(CHECKBOX_STYLE)

        self.hzs_chk_receipt = QCheckBox("Печать расписки", parent)
        self.hzs_chk_receipt.setFont(F_Sml)
        self.hzs_chk_receipt.setGeometry(330, 470, 250, 35)
        self.hzs_chk_receipt.setStyleSheet(CHECKBOX_STYLE)

        self.hzs_btn_txt_receipt = QPushButton("Текст", parent)
        self.hzs_btn_txt_receipt.setFont(F_Sml)
        self.hzs_btn_txt_receipt.setGeometry(595, 470, 100, 35)
        self.hzs_btn_txt_receipt.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
            QPushButton:disabled { background-color: #7f7f7f; color: white; border: none; border-radius: 4px; }
        """)
        self.hzs_btn_txt_receipt.setEnabled(False)

    # Метод подключения логики
    def setup_logic(self):
        self.btn_back.clicked.connect(self.reject)
        self.btn_reset.clicked.connect(self.reset_fields)

        self.btn_print.clicked.connect(self.on_print_clicked)
        self.btn_sel_print.clicked.connect(self.on_sel_print_clicked)

        self.setup_adm_logic()
        self.setup_zks_logic()
        self.setup_drs_logic()
        self.setup_hzs_logic()

    '''БЛОК ЛОГИКИ ДЛЯ АДМИНИСТРАЦИИ'''
    # Метод поключения логики
    def setup_adm_logic(self):
        self.adm_chk_no_order.toggled.connect(self.on_adm_no_order_toggled)
        self.on_adm_no_order_toggled(self.adm_chk_no_order.isChecked())

        self.adm_chk_cross.toggled.connect(self.on_adm_cross_toggled)

        self.adm_chk_green_zone.toggled.connect(self.on_adm_green_zone_toggled)
        self.adm_chk_type2.toggled.connect(self.on_adm_type2_toggled)

        self.adm_chk_jks_hbu.toggled.connect(self.on_adm_jks_hbu_toggled)
        self.adm_cb_jks_unit.currentTextChanged.connect(self.on_adm_unit_changed)
        self.on_adm_unit_changed(self.adm_cb_jks_unit.currentText())

        self.adm_chk_receipt.toggled.connect(self.adm_btn_txt_receipt.setEnabled)
        self.adm_btn_txt_receipt.clicked.connect(self.open_rozpiska_dialog)

    # Метод проверки надобности ордера
    def on_adm_no_order_toggled(self, checked: bool):
        self.adm_txt_order_num.setEnabled(not checked)
        self.adm_date_order.setEnabled(not checked)
        if checked:
            self.adm_txt_order_num.clear()

    # Метод проверки пересечения
    def on_adm_cross_toggled(self, checked: bool):
        self.adm_txt_house.setEnabled(not checked)
        if checked:
            self.adm_txt_house.clear()
        self.adm_txt_address_cross.setEnabled(checked)
        if not checked:
            self.adm_txt_address_cross.clear()

    # Метод проверки выбранной зеленой зоны
    def on_adm_green_zone_toggled(self, checked: bool):
        self.adm_txt_green_zone.setEnabled(checked)
        if not checked:
            self.adm_txt_green_zone.clear()

    # Метод проверки второго типа покрытия
    def on_adm_type2_toggled(self, checked: bool):
        self.adm_txt_type2.setEnabled(checked)
        self.adm_rb_asphalt.setEnabled(checked)
        self.adm_rb_tile.setEnabled(checked)
        self.adm_rb_dirt.setEnabled(checked)

        if not checked:
            self.adm_rb_asphalt.setChecked(True)

    # Метод подключение ЖКС и ХБУ в комиссию
    def on_adm_jks_hbu_toggled(self, checked: bool):
        self.adm_lbl_jks.setEnabled(checked)
        self.adm_cb_jks_unit.setEnabled(checked)
        self.adm_lbl_hbu.setEnabled(checked)
        self.adm_txt_hbu_unit.setEnabled(checked)

    # Метод подстановки участка ХБУ к участку ЖКС (вместе с начальниками)
    def on_adm_unit_changed(self, unit_str: str):
        try:
            unit_num = int(unit_str)
        except ValueError:
            return

        unit_info = ZKS_BLAGO_DB.get(unit_num)
        if not unit_info:
            return

        blago_units = unit_info.get("blago_units", [])

        if unit_num == 30:
            self.adm_txt_hbu_unit.setReadOnly(False)
            self.adm_txt_hbu_unit.clear()
            self.adm_txt_hbu_unit.setPlaceholderText("1 или 2")
        else:
            self.adm_txt_hbu_unit.setReadOnly(True)
            self.adm_txt_hbu_unit.setPlaceholderText("")
            if blago_units:
                self.adm_txt_hbu_unit.setText(str(blago_units[0]["num"]))
    '''КОНЕЦ БЛОКА'''

    '''БЛОК ЛОГИКИ ДЛЯ ЖИЛКОМСЕРВИСА'''
    # Метод подключения логики
    def setup_zks_logic(self):
        self.zks_chk_no_order.toggled.connect(self.on_zks_no_order_toggled)
        self.on_zks_no_order_toggled(self.zks_chk_no_order.isChecked())

        self.zks_chk_cross.toggled.connect(self.on_zks_cross_toggled)

        self.zks_cb_jks_unit.currentTextChanged.connect(self.on_zks_unit_changed)
        self.on_zks_unit_changed(self.zks_cb_jks_unit.currentText())

        # 4. Связка комбобоксов шурфов ЖКС
        for i in range(3):
            self.zks_shurf_combos[i].currentTextChanged.connect(
                lambda text, row=i: self.update_zks_shurf_options()
            )

        self.update_zks_shurf_options()

        self.zks_chk_receipt.toggled.connect(self.zks_btn_txt_receipt.setEnabled)
        self.zks_btn_txt_receipt.clicked.connect(self.open_rozpiska_dialog)

    # Метод проверки надобности ордера
    def on_zks_no_order_toggled(self, checked: bool):
        self.zks_txt_order_num.setEnabled(not checked)
        self.zks_date_order.setEnabled(not checked)
        if checked:
            self.zks_txt_order_num.clear()

    # Метод проверки пересечения
    def on_zks_cross_toggled(self, checked: bool):
        self.zks_txt_house.setEnabled(not checked)
        if checked:
            self.zks_txt_house.clear()
        self.zks_txt_address_cross.setEnabled(checked)
        if not checked:
            self.zks_txt_address_cross.clear()

    # Метод определения связи участка ЖКС и ХБУ
    def on_zks_unit_changed(self, unit_str: str):
        try:
            unit_num = int(unit_str)
        except ValueError:
            return

        unit_info = ZKS_BLAGO_DB.get(unit_num)
        if not unit_info:
            return

        blago_units = unit_info.get("blago_units", [])

        if unit_num == 30:
            self.zks_txt_hbu_unit.setReadOnly(False)
            self.zks_txt_hbu_unit.clear()
            self.zks_txt_hbu_unit.setPlaceholderText("1 или 2")
        else:
            self.zks_txt_hbu_unit.setReadOnly(True)
            self.zks_txt_hbu_unit.setPlaceholderText("")
            if blago_units:
                self.zks_txt_hbu_unit.setText(str(blago_units[0]["num"]))

    # Метод сортировки типа покрытия
    def update_zks_shurf_options(self):
        allowed_base = [item for item in COMPANY_LIMITS.get("Житлокомсервис", [])]
        asphalt_types = ["Пр. внутр.", "Тротуар", "Трот. плитка", "Отмостка"]

        for cb in self.zks_shurf_combos:
            cb.blockSignals(True)

        selected_type_1 = self.zks_shurf_combos[0].currentText()
        cb1_items = [item for item in allowed_base if item != "нет данных"]
        self.zks_shurf_combos[0].clear()
        self.zks_shurf_combos[0].addItems(cb1_items)
        if selected_type_1 in cb1_items:
            self.zks_shurf_combos[0].setCurrentText(selected_type_1)
        else:
            self.zks_shurf_combos[0].setCurrentIndex(0)

        val1 = self.zks_shurf_combos[0].currentText()

        cb2_items = []
        for item in allowed_base:
            if item == "нет данных":
                cb2_items.append(item)
                continue

            if val1 == "Грунтовка" and item in asphalt_types:
                continue
            if val1 in asphalt_types and item == "Грунтовка":
                continue

            if item == val1:
                continue

            if val1 in asphalt_types and item in asphalt_types:
                if PRIORITY.get(item, 99) <= PRIORITY.get(val1, 99):
                    continue

            cb2_items.append(item)

        old_val2 = self.zks_shurf_combos[1].currentText()
        self.zks_shurf_combos[1].clear()
        self.zks_shurf_combos[1].addItems(cb2_items)

        if old_val2 in cb2_items:
            self.zks_shurf_combos[1].setCurrentText(old_val2)
        else:
            self.zks_shurf_combos[1].setCurrentIndex(0)

        val2 = self.zks_shurf_combos[1].currentText()

        cb3_items = []
        if val2 in ["нет данных", ""]:
            cb3_items = ["нет данных"]
        else:
            has_grunt = (val1 == "Грунтовка" or val2 == "Грунтовка")
            has_asphalt = (val1 in asphalt_types or val2 in asphalt_types)

            for item in allowed_base:
                if item == "нет данных":
                    cb3_items.append(item)
                    continue

                if has_grunt and item in asphalt_types:
                    continue
                if has_asphalt and item == "Грунтовка":
                    continue

                if item in (val1, val2):
                    continue

                is_valid = True
                if item in asphalt_types:
                    for prev_val in (val1, val2):
                        if prev_val in asphalt_types:
                            if PRIORITY.get(item, 99) <= PRIORITY.get(prev_val, 99):
                                is_valid = False
                                break

                if is_valid:
                    cb3_items.append(item)

        old_val3 = self.zks_shurf_combos[2].currentText()
        self.zks_shurf_combos[2].clear()
        self.zks_shurf_combos[2].addItems(cb3_items)

        if old_val3 in cb3_items:
            self.zks_shurf_combos[2].setCurrentText(old_val3)
        else:
            self.zks_shurf_combos[2].setCurrentIndex(0)

        for cb in self.zks_shurf_combos:
            cb.blockSignals(False)

        for i in range(3):
            stype = self.zks_shurf_combos[i].currentText()
            has_data = bool(stype) and (stype != "нет данных")
            self.zks_dig_fields[i].setEnabled(has_data)
            if not has_data:
                self.zks_dig_fields[i].clear()
    '''КОНЕЦ БЛОКА'''

    '''БЛОК ЛОГИКИ ДЛЯ ДОРРЕМСТРОЯ'''
    # Метод подключения логики
    def setup_drs_logic(self):
        self.drs_chk_no_order.toggled.connect(self.on_drs_no_order_toggled)
        self.on_drs_no_order_toggled(self.drs_chk_no_order.isChecked())

        self.drs_chk_cross.toggled.connect(self.on_drs_cross_toggled)

        self.drs_chk_receipt.toggled.connect(self.drs_btn_txt_receipt.setEnabled)
        self.drs_btn_txt_receipt.clicked.connect(self.open_rozpiska_dialog)

    # Метод проверки надобности ордера
    def on_drs_no_order_toggled(self, checked: bool):
        self.drs_txt_order_num.setEnabled(not checked)
        self.drs_date_order.setEnabled(not checked)
        if checked:
            self.drs_txt_order_num.clear()

    # Метод проверки пересечения
    def on_drs_cross_toggled(self, checked: bool):
        self.drs_txt_house.setEnabled(not checked)
        if checked:
            self.drs_txt_house.clear()
        self.drs_txt_address_cross.setEnabled(checked)
        if not checked:
            self.drs_txt_address_cross.clear()
    '''КОНЕЦ БЛОКА'''

    '''БЛОК ЛОГИКИ ДЛЯ ЗЕЛЕНСТРОЯ'''
    # Метод подключения логики
    def setup_hzs_logic(self):
        self.hzs_chk_no_order.toggled.connect(self.on_hzs_no_order_toggled)
        self.on_hzs_no_order_toggled(self.hzs_chk_no_order.isChecked())

        self.hzs_chk_cross.toggled.connect(self.on_hzs_cross_toggled)

        for i in range(3):
            self.hzs_shurf_combos[i].currentTextChanged.connect(
                lambda text, row=i: self.update_hzs_shurf_options()
            )

        self.update_hzs_shurf_options()

        self.hzs_chk_receipt.toggled.connect(self.hzs_btn_txt_receipt.setEnabled)
        self.hzs_btn_txt_receipt.clicked.connect(self.open_rozpiska_dialog)

    # Метод проверки надобности ордера
    def on_hzs_no_order_toggled(self, checked: bool):
        self.hzs_txt_order_num.setEnabled(not checked)
        self.hzs_date_order.setEnabled(not checked)
        if checked:
            self.hzs_txt_order_num.clear()

    # Метод проверки пересечения
    def on_hzs_cross_toggled(self, checked: bool):
        self.hzs_txt_house.setEnabled(not checked)
        if checked:
            self.hzs_txt_house.clear()
        self.hzs_txt_address_cross.setEnabled(checked)
        if not checked:
            self.hzs_txt_address_cross.clear()

    # Метод сортировки типа покрытия
    def update_hzs_shurf_options(self):
        allowed_base = [item for item in COMPANY_LIMITS.get("Зеленстрой", [])]
        asphalt_types = ["Пр. внутр.", "Тротуар", "Трот. плитка", "А/б заезд"]

        for cb in self.hzs_shurf_combos:
            cb.blockSignals(True)

        selected_type_1 = self.hzs_shurf_combos[0].currentText()
        cb1_items = [item for item in allowed_base if item != "нет данных"]
        self.hzs_shurf_combos[0].clear()
        self.hzs_shurf_combos[0].addItems(cb1_items)
        if selected_type_1 in cb1_items:
            self.hzs_shurf_combos[0].setCurrentText(selected_type_1)
        else:
            self.hzs_shurf_combos[0].setCurrentIndex(0)

        val1 = self.hzs_shurf_combos[0].currentText()

        cb2_items = []
        for item in allowed_base:
            if item == "нет данных":
                cb2_items.append(item)
                continue

            if item == val1:
                continue

            if val1 in asphalt_types and item in asphalt_types:
                if PRIORITY.get(item, 99) <= PRIORITY.get(val1, 99):
                    continue

            cb2_items.append(item)

        old_val2 = self.hzs_shurf_combos[1].currentText()
        self.hzs_shurf_combos[1].clear()
        self.hzs_shurf_combos[1].addItems(cb2_items)

        if old_val2 in cb2_items:
            self.hzs_shurf_combos[1].setCurrentText(old_val2)
        else:
            self.hzs_shurf_combos[1].setCurrentIndex(0)

        val2 = self.hzs_shurf_combos[1].currentText()

        cb3_items = []
        if val2 in ["нет данных", ""]:
            cb3_items = ["нет данных"]
        else:
            for item in allowed_base:
                if item == "нет данных":
                    cb3_items.append(item)
                    continue

                if item in (val1, val2):
                    continue

                is_valid = True
                if item in asphalt_types:
                    for prev_val in (val1, val2):
                        if prev_val in asphalt_types:
                            if PRIORITY.get(item, 99) <= PRIORITY.get(prev_val, 99):
                                is_valid = False
                                break

                if is_valid:
                    cb3_items.append(item)

        old_val3 = self.hzs_shurf_combos[2].currentText()
        self.hzs_shurf_combos[2].clear()
        self.hzs_shurf_combos[2].addItems(cb3_items)

        if old_val3 in cb3_items:
            self.hzs_shurf_combos[2].setCurrentText(old_val3)
        else:
            self.hzs_shurf_combos[2].setCurrentIndex(0)

        for cb in self.hzs_shurf_combos:
            cb.blockSignals(False)

        for i in range(3):
            stype = self.hzs_shurf_combos[i].currentText()
            has_data = bool(stype) and (stype != "нет данных")
            self.hzs_dig_fields[i].setEnabled(has_data)
            if not has_data:
                self.hzs_dig_fields[i].clear()
    '''КОНЕЦ БЛОКА'''

    # Метод открытия окна расписки
    def open_rozpiska_dialog(self):
        dlg = RozpiskaTextDialog(self)
        dlg.exec()

    # Метод очистки всех полей до дефолтных значений
    def reset_fields(self):
        for line_edit in self.findChildren(QLineEdit):
            line_edit.clear()
        
        for chk in self.findChildren(QCheckBox):
            chk.setChecked(False)

        for date_edit in self.findChildren(QDateEdit):
            date_edit.setDate(QDate.currentDate())
            date_edit.lineEdit().deselect()

        self.adm_rb_asphalt.setChecked(True)
        self.adm_chk_no_order.setChecked(True)
        self.zks_chk_no_order.setChecked(True)
        self.hzs_chk_no_order.setChecked(True)
        self.adm_cb_jks_unit.setCurrentIndex(0)
        self.zks_cb_jks_unit.setCurrentIndex(0)

    # Метод сбора данных для Администрации        
    def collect_adm_data(self) -> dict:
        second_type_key = "asphalt"
        if self.adm_rb_tile.isChecked():
            second_type_key = "paving"
        elif self.adm_rb_dirt.isChecked():
            second_type_key = "dirt"

        second_area_raw = self.adm_txt_type2.text().strip()
        second_area_val = second_area_raw if (self.adm_chk_type2.isChecked() and second_area_raw) else "0"

        green_area_raw = self.adm_txt_green_zone.text().strip()
        green_area_val = green_area_raw if (self.adm_chk_green_zone.isChecked() and green_area_raw) else "0"

        jks_unit_str = self.adm_cb_jks_unit.currentText()
        jks_num = int(jks_unit_str) if jks_unit_str.isdigit() else 0
        jks_info = ZKS_BLAGO_DB.get(jks_num, {})
        jks_fio = jks_info.get("jks_fio", "")
        
        hbu_num_str = self.adm_txt_hbu_unit.text().strip()
        hbu_fio = ""
        for bu in jks_info.get("blago_units", []):
            if bu.get("num") == hbu_num_str:
                hbu_fio = bu.get("fio", "")
                break
        
        return {
            "order_num": "" if self.adm_chk_no_order.isChecked() else self.adm_txt_order_num.text().strip(),
            "order_date": "" if self.adm_chk_no_order.isChecked() else self.adm_date_order.date().toString("dd.MM.yyyy"),
            "street": self.adm_txt_address.text().strip(),
            "house_num": self.adm_txt_house.text().strip(),
            "is_cross": self.adm_chk_cross.isChecked(),
            "cross_street": self.adm_txt_address_cross.text().strip(),
            "green_area": green_area_val,
            "second_type_key": second_type_key if self.adm_chk_type2.isChecked() else "",
            "second_type_area": second_area_val,
            "chk_form7": self.adm_chk_form7.isChecked(),
            "chk_receipt": self.adm_chk_receipt.isChecked(),
            "chk_jks_hbu": self.adm_chk_jks_hbu.isChecked(),
            "chk_other_rep": self.adm_chk_other.isChecked(),
            "jks_num": jks_num,
            "jks_fio": jks_fio,
            "hbu_num": hbu_num_str,
            "hbu_fio": hbu_fio,
        }

    # Метод сбора данных для Жилкомсервиса
    def collect_zks_data(self) -> dict:
        shurf_items = []
        for i in range(3):
            stype = self.zks_shurf_combos[i].currentText()
            sdig = self.zks_dig_fields[i].text().strip()
            if stype and stype != "нет данных":
                shurf_items.append({"type": stype, "area": sdig})

        jks_unit_str = self.zks_cb_jks_unit.currentText()
        jks_num = int(jks_unit_str) if jks_unit_str.isdigit() else 0

        return {
            "order_num": "" if self.zks_chk_no_order.isChecked() else self.zks_txt_order_num.text().strip(),
            "order_date": "" if self.zks_chk_no_order.isChecked() else self.zks_date_order.date().toString("dd.MM.yyyy"),
            "du_num": self.zks_txt_dop_num.text().strip(),
            "du_date": self.zks_date_dop.date().toString("dd.MM.yyyy"),
            "street": self.zks_txt_address.text().strip(),
            "house_num": self.zks_txt_house.text().strip(),
            "is_cross": self.zks_chk_cross.isChecked(),
            "cross_street": self.zks_txt_address_cross.text().strip(),
            "shurfs": shurf_items,
            "jks_num": jks_num,
            "hbu_num": self.zks_txt_hbu_unit.text().strip(),
            "chk_form7": self.zks_chk_form7.isChecked(),
            "chk_receipt": self.zks_chk_receipt.isChecked(),
        }

    # Метод сбора данных для Дорремстроя
    def collect_drs_data(self) -> dict:
        return {
            "order_num": "" if self.drs_chk_no_order.isChecked() else self.drs_txt_order_num.text().strip(),
            "order_date": "" if self.drs_chk_no_order.isChecked() else self.drs_date_order.date().toString("dd.MM.yyyy"),
            "street": self.drs_txt_address.text().strip(),
            "house_num": self.drs_txt_house.text().strip(),
            "is_cross": self.drs_chk_cross.isChecked(),
            "cross_street": self.drs_txt_address_cross.text().strip(),
            "chk_form7": self.drs_chk_form7.isChecked(),
            "chk_receipt": self.drs_chk_receipt.isChecked(),
        }

    # Метод сбора данных для Зеленстроя
    def collect_hzs_data(self) -> dict:
        shurf_items = []
        for i in range(3):
            stype = self.hzs_shurf_combos[i].currentText()
            sdig = self.hzs_dig_fields[i].text().strip()
            if stype and stype != "нет данных":
                shurf_items.append({"type": stype, "area": sdig})

        return {
            "order_num": "" if self.hzs_chk_no_order.isChecked() else self.hzs_txt_order_num.text().strip(),
            "order_date": "" if self.hzs_chk_no_order.isChecked() else self.hzs_date_order.date().toString("dd.MM.yyyy"),
            "street": self.hzs_txt_address.text().strip(),
            "house_num": self.hzs_txt_house.text().strip(),
            "is_cross": self.hzs_chk_cross.isChecked(),
            "cross_street": self.hzs_txt_address_cross.text().strip(),
            "shurfs": shurf_items,
            "chk_form7": self.hzs_chk_form7.isChecked(),
            "chk_receipt": self.hzs_chk_receipt.isChecked(),
        }

    # Метод "Защита от дурака" для Администрации
    def validate_input_adm(self) -> bool:
        if not self.adm_chk_no_order.isChecked() and not self.adm_txt_order_num.text().strip():
            show_warning_message(self, "Номер ордера не нужен? Тогда поставь флажок. Нужен? Ну так, напиши.")
            return False

        street1 = self.adm_txt_address.text().strip()
        if not street1:
            show_warning_message(self, "А где мы копали-то?")
            return False

        if not self.adm_chk_cross.isChecked() and not self.adm_txt_house.text().strip():
            show_warning_message(self, "Где номер дома? Всю улицу перекопали?")
            return False

        street2 = self.adm_txt_address_cross.text().strip()
        if self.adm_chk_cross.isChecked() and not street2:
            show_warning_message(self, "С кем улица пересеклась? С пустотой бытия?")
            return False

        if self.adm_chk_cross.isChecked() and street1.lower() == street2.lower():
            show_warning_message(self, "Улица пересеклась сама с собой! Серъёзно?")
            return False

        if not self.adm_chk_green_zone.isChecked() and not self.adm_chk_type2.isChecked():
            show_warning_message(self, "Если не копали ни зелёнку, ни асфальт, то к чему сыр-бор?")
            return False

        if self.adm_chk_green_zone.isChecked() and not self.adm_txt_green_zone.text().strip():
            show_warning_message(self, "Площадь разрытия нам уже не нужна, да?")
            return False

        if self.adm_chk_type2.isChecked() and not self.adm_txt_type2.text().strip():
            show_warning_message(self, "Площадь разрытия нам уже не нужна, да?")
            return False

        if self.adm_chk_jks_hbu.isChecked():
            jks_unit_str = self.adm_cb_jks_unit.currentText()
            if jks_unit_str == "30":
                hbu_val = self.adm_txt_hbu_unit.text().strip()
                if hbu_val not in ("1", "2"):
                    show_warning_message(self, "У этого ЖКС только два варианта:\n1 или 2. Третьего не дано.")
                    return False

        if self.adm_chk_receipt.isChecked():
            if not get_rozpiska_text().strip():
                show_warning_message(self, "Напиши хоть что-нибудь в расписке!")
                return False

        return True

    # Метод "Защита от дурака" для Жилкомсервиса
    def validate_input_zks(self) -> bool:
        if not self.zks_chk_no_order.isChecked() and not self.zks_txt_order_num.text().strip():
            show_warning_message(self, "Номер ордера не нужен? Тогда поставь флажок. Нужен? Ну так, напиши.")
            return False

        if not self.zks_txt_dop_num.text().strip():
            show_warning_message(self, "Номер доп. соглашения КДЕ?")
            return False

        street1 = self.zks_txt_address.text().strip()
        if not street1:
            show_warning_message(self, "А где мы копали-то?")
            return False

        if not self.zks_chk_cross.isChecked() and not self.zks_txt_house.text().strip():
            show_warning_message(self, "Где номер дома? Всю улицу перекопали?")
            return False

        street2 = self.zks_txt_address_cross.text().strip()
        if self.zks_chk_cross.isChecked() and not street2:
            show_warning_message(self, "С кем улица пересеклась? С пустотой бытия?")
            return False

        if self.zks_chk_cross.isChecked() and street1.lower() == street2.lower():
            show_warning_message(self, "Улица пересеклась сама с собой! Серъёзно?")
            return False

        for i in range(3):
            stype = self.zks_shurf_combos[i].currentText()
            sq = self.zks_dig_fields[i].text().strip()
            
            if stype and stype != "нет данных" and not sq:
                show_warning_message(self, "Площадь разрытия нам уже не нужна, да?")
                return False

        jks_unit_str = self.zks_cb_jks_unit.currentText()
        if jks_unit_str == "30":
            hbu_val = self.zks_txt_hbu_unit.text().strip()
            if hbu_val not in ("1", "2"):
                show_warning_message(self, "У этого ЖКС только два варианта:\n1 или 2. Третьего не дано.")
                return False

        if self.zks_chk_receipt.isChecked() and not get_rozpiska_text():
            show_warning_message(self, "Напиши хоть что-нибудь в расписке!")
            return False

        return True

    # Метод "Защита от дурака" для Дорремстроя
    def validate_input_drs(self) -> bool:
        if not self.drs_chk_no_order.isChecked() and not self.drs_txt_order_num.text().strip():
            show_warning_message(self, "Номер ордера не нужен? Тогда поставь флажок. Нужен? Ну так, напиши.")
            return False

        street1 = self.drs_txt_address.text().strip()
        if not street1:
            show_warning_message(self, "А где мы копали-то?")
            return False

        if not self.drs_chk_cross.isChecked() and not self.drs_txt_house.text().strip():
            show_warning_message(self, "Где номер дома? Всю улицу перекопали?")
            return False

        street2 = self.drs_txt_address_cross.text().strip()
        if self.drs_chk_cross.isChecked() and not street2:
            show_warning_message(self, "С кем улица пересеклась? С пустотой бытия?")
            return False

        if self.drs_chk_cross.isChecked() and street1.lower() == street2.lower():
            show_warning_message(self, "Улица пересеклась сама с собой! Серъёзно?")
            return False

        if self.drs_chk_receipt.isChecked() and not get_rozpiska_text():
            show_warning_message(self, "Напиши хоть что-нибудь в расписке!")
            return False

        return True

    # Метод "защита от дурака" для Зеленстроя
    def validate_input_hzs(self) -> bool:
        if not self.hzs_chk_no_order.isChecked() and not self.hzs_txt_order_num.text().strip():
            show_warning_message(self, "Номер ордера не нужен? Тогда поставь флажок. Нужен? Ну так, напиши.")
            return False

        street1 = self.hzs_txt_address.text().strip()
        if not street1:
            show_warning_message(self, "А где мы копали-то?")
            return False

        if not self.hzs_chk_cross.isChecked() and not self.hzs_txt_house.text().strip():
            show_warning_message(self, "Где номер дома? Всю улицу перекопали?")
            return False

        street2 = self.hzs_txt_address_cross.text().strip()
        if self.hzs_chk_cross.isChecked() and not street2:
            show_warning_message(self, "С кем улица пересеклась? С пустотой бытия?")
            return False

        if self.hzs_chk_cross.isChecked() and street1.lower() == street2.lower():
            show_warning_message(self, "Улица пересеклась сама с собой! Серъёзно?")
            return False

        for i in range(3):
            stype = self.hzs_shurf_combos[i].currentText()
            sq = self.hzs_dig_fields[i].text().strip()
            
            if stype and stype != "нет данных" and not sq:
                show_warning_message(self, "Площадь разрытия нам уже не нужна, да?")
                return False

        if self.hzs_chk_receipt.isChecked() and not get_rozpiska_text():
            show_warning_message(self, "Напиши хоть что-нибудь в расписке!")
            return False

        return True

    # Метод сбора данных и подключения сервиса печати
    # (с сообщением после печати) при обычной печати
    def on_print_clicked(self):
        current_index = self.tabs.currentIndex()

        if current_index == 0:
            if not self.validate_input_adm():
                return

            data = self.collect_adm_data()
            try:
                process_adm_close(data)
                show_success_message(self, "Напечатали!!!")
                cleanup_temp_files()
            except Exception as e:
                show_warning_message(self, f"Ошибка при формировании документов: {e}")

        elif current_index == 1:
            if not self.validate_input_zks():
                return 

            data = self.collect_zks_data()
            try:
                process_zks_close(data)
                show_success_message(self, "Напечатали!!!")
                cleanup_temp_files()
            except Exception as e:
                show_warning_message(self, f"Ошибка при формировании документов: {e}")

        elif current_index == 2:
            if not self.validate_input_drs():
                return
            
            data = self.collect_drs_data()
            try:
                process_drs_close(data)
                show_success_message(self, "Напечатали!!!")
                cleanup_temp_files()
            except Exception as e:
                show_warning_message(self, f"Ошибка при формировании документов: {e}")

        elif current_index == 3:
            if not self.validate_input_hzs():
                return

            data = self.collect_hzs_data()
            try:
                process_hzs_close(data)
                show_success_message(self, "Напечатали!!!")
                cleanup_temp_files()
            except Exception as e:
                show_warning_message(self, f"Ошибка при формировании документов: {e}")

    # Метод сбора данных и подключения сервиса печати
    # (с сообщением после печати) при выборочной печати
    def on_sel_print_clicked(self):
        current_tab_index = self.tabs.currentIndex()

        if current_tab_index == 0:
            if not self.validate_input_adm():
                return
            data = self.collect_adm_data()
            dialog = GuiAdmCloseEx(parent=self, order_data=data)
            dialog.exec()

        elif current_tab_index == 1:
            if not self.validate_input_zks():
                return
            data = self.collect_zks_data()
            dialog = GuiZksCloseEx(parent=self, order_data=data)
            dialog.exec()

        elif current_tab_index == 2:
            if not self.validate_input_drs():
                return
            data = self.collect_drs_data()
            dialog = GuiDrsCloseEx(parent=self, order_data=data)
            dialog.exec()

        elif current_tab_index == 3:
            if not self.validate_input_hzs():
                return
            data = self.collect_hzs_data()
            dialog = GuiHzsCloseEx(parent=self, order_data=data)
            dialog.exec()

    # Метод ручного закрытия окна
    def closeEvent(self, event):
        cleanup_temp_files()
        event.accept()