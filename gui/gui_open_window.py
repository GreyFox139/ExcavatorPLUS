import os
import json
from PyQt6.QtWidgets import (
    QDialog, QLabel, QComboBox, QLineEdit, QDateEdit, 
    QCheckBox, QPushButton, QFrame, QApplication, QStyle
)
from PyQt6.QtCore import Qt, QDate, QSize

from config import F_Big_B, F_Nrm, F_Mid_B, F_Sml, COMPANY_LIMITS, PRIORITY, CHECKBOX_STYLE
from gui.gui_winter_date import WinterDateWindow
from gui.extra.gui_adm_open_ex import GuiAdmOpenEx
from gui.extra.gui_drs_open_ex import GuiDrsOpenEx
from gui.extra.gui_hzs_open_ex import GuiHzsOpenEx
from gui.extra.gui_zks_open_ex import GuiZksOpenEx
from gui.gui_dialog_window import show_success_message, show_warning_message
from utility.clear_temp import cleanup_temp_files
from utility.street_completer import setup_street_completer

# Импорт сервисов печати
from services.adm_open_service import process_adm_open
from services.zks_open_service import process_zks_open
from services.drs_open_service import process_drs_open
from services.hzs_open_service import process_hzs_open

CONFIG_PATH = os.path.join("data", "app_config.json")

# Класс UI окна открытия ордеров
class OpenWindow(QDialog):
    # Метод инициализации формы
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Открытие ордеров")
        self.setFixedSize(900, 850)

        self.winter_green_date = QDate.currentDate()
        self.winter_asphalt_date = QDate.currentDate()

        self.init_ui()
        self.load_config()
        self.setup_logic()

    # Загрузка настроек из файла app_config.json
    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    is_winter = data.get("is_winter_period", False)
                    self.chk_winter.setChecked(is_winter)

                    green_str = data.get("winter_date_green")
                    if green_str:
                        self.winter_green_date = QDate.fromString(green_str, "yyyy-MM-dd")

                    asphalt_str = data.get("winter_date_asphalt")
                    if asphalt_str:
                        self.winter_asphalt_date = QDate.fromString(asphalt_str, "yyyy-MM-dd")
            except Exception as e:
                print(f"Ошибка чтения JSON-конфига: {e}")

    # Сохранение настроек в файл app_config.json
    def save_config(self):
        data = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        data["is_winter_period"] = self.chk_winter.isChecked()
        data["winter_date_green"] = self.winter_green_date.toString("yyyy-MM-dd")
        data["winter_date_asphalt"] = self.winter_asphalt_date.toString("yyyy-MM-dd")

        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # Метод инициализации UI
    def init_ui(self):
        # 1. Заголовок
        lbl_title = QLabel("Открытие ордеров", self)
        lbl_title.setFont(F_Big_B)
        lbl_title.setGeometry(0, 20, 900, 60)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        line1 = QFrame(self)
        line1.setGeometry(30, 90, 840, 2)
        line1.setFrameShape(QFrame.Shape.HLine)

        # 2. Блок балансосодержателя
        lbl_holder = QLabel("Балансосодержатель:", self)
        lbl_holder.setFont(F_Sml)
        lbl_holder.setGeometry(50, 110, 290, 35)

        self.cb_holder = QComboBox(self)
        self.cb_holder.setFont(F_Sml)
        self.cb_holder.setGeometry(350, 110, 500, 35)
        self.cb_holder.setEditable(True)
        self.cb_holder.lineEdit().setReadOnly(True)
        self.cb_holder.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cb_holder.addItems(list(COMPANY_LIMITS.keys()))

        # 3. Блок карточки 1562
        lbl_card = QLabel("Карточка 1562", self)
        lbl_card.setFont(F_Sml)
        lbl_card.setGeometry(50, 160, 200, 30)

        lbl_num_sign = QLabel("#", self)
        lbl_num_sign.setFont(F_Sml)
        lbl_num_sign.setGeometry(50, 200, 20, 35)

        self.txt_card_num = QLineEdit(self)
        self.txt_card_num.setFont(F_Sml)
        self.txt_card_num.setGeometry(80, 200, 250, 35)
        self.txt_card_num.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_date_sign = QLabel("от", self)
        lbl_date_sign.setFont(F_Sml)
        lbl_date_sign.setGeometry(345, 200, 30, 35)

        self.date_card = QDateEdit(self)
        self.date_card.setFont(F_Sml)
        self.date_card.setGeometry(390, 200, 190, 35)
        self.date_card.setCalendarPopup(True)
        self.date_card.setDate(QDate.currentDate())
        self.date_card.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 4. Блок адресной строки
        lbl_addr = QLabel("Адрес", self)
        lbl_addr.setFont(F_Sml)
        lbl_addr.setGeometry(50, 250, 100, 30)

        lbl_house = QLabel("# дома", self)
        lbl_house.setFont(F_Sml)
        lbl_house.setGeometry(680, 250, 100, 30)

        self.txt_address = QLineEdit(self)
        self.txt_address.setFont(F_Sml)
        self.txt_address.setGeometry(50, 285, 600, 35)
        self.txt_address.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.txt_address)

        self.txt_house = QLineEdit(self)
        self.txt_house.setFont(F_Sml)
        self.txt_house.setGeometry(680, 285, 170, 35)
        self.txt_house.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.chk_cross = QCheckBox("пересечение", self)
        self.chk_cross.setFont(F_Sml)
        self.chk_cross.setGeometry(50, 330, 190, 35)
        self.chk_cross.setStyleSheet(CHECKBOX_STYLE)

        self.txt_address_cross = QLineEdit(self)
        self.txt_address_cross.setFont(F_Sml)
        self.txt_address_cross.setGeometry(250, 330, 600, 35)
        self.txt_address_cross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setup_street_completer(self.txt_address_cross)
        self.txt_address_cross.setEnabled(False)

        line2 = QFrame(self)
        line2.setGeometry(30, 380, 840, 2)
        line2.setFrameShape(QFrame.Shape.HLine)

        # 5. Блок типов покрытия и плоащдей
        lbl_shurf_title = QLabel("Шурфы", self)
        lbl_shurf_title.setFont(F_Sml)
        lbl_shurf_title.setGeometry(50, 395, 100, 30)

        lbl_sq_title = QLabel("Площадь, м²", self)
        lbl_sq_title.setFont(F_Sml)
        lbl_sq_title.setGeometry(550, 395, 200, 30)

        lbl_dig = QLabel("разрытие", self)
        lbl_dig.setFont(F_Sml)
        lbl_dig.setGeometry(450, 430, 150, 30)

        lbl_rec = QLabel("восстановление", self)
        lbl_rec.setFont(F_Sml)
        lbl_rec.setGeometry(640, 430, 200, 30)

        self.shurf_combos = []
        self.dig_fields = []
        self.rec_fields = []

        y_offset = 470
        for i in range(3):
            lbl_type = QLabel(f"Тип {i+1}", self)
            lbl_type.setFont(F_Sml)
            lbl_type.setGeometry(50, y_offset, 80, 35)

            cb_type = QComboBox(self)
            cb_type.setFont(F_Sml)
            cb_type.setGeometry(140, y_offset, 250, 35)
            cb_type.setEditable(True)
            cb_type.lineEdit().setReadOnly(True)
            cb_type.lineEdit().setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.shurf_combos.append(cb_type)

            txt_dig = QLineEdit(self)
            txt_dig.setFont(F_Sml)
            txt_dig.setGeometry(410, y_offset, 200, 35)
            txt_dig.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_dig.setEnabled(False)
            self.dig_fields.append(txt_dig)

            txt_rec = QLineEdit(self)
            txt_rec.setFont(F_Sml)
            txt_rec.setGeometry(630, y_offset, 220, 35)
            txt_rec.setAlignment(Qt.AlignmentFlag.AlignCenter)
            txt_rec.setEnabled(False)
            self.rec_fields.append(txt_rec)

            y_offset += 45

        line3 = QFrame(self)
        line3.setGeometry(30, 610, 840, 2)
        line3.setFrameShape(QFrame.Shape.HLine)

        # 6. Блок дополнительных параметров печати
        lbl_extra = QLabel("Дополнительные параметры печати", self)
        lbl_extra.setFont(F_Mid_B)
        lbl_extra.setGeometry(0, 625, 900, 40)
        lbl_extra.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.chk_winter = QCheckBox("Зимний период", self)
        self.chk_winter.setFont(F_Sml)
        self.chk_winter.setGeometry(50, 680, 220, 35)
        self.chk_winter.setStyleSheet(CHECKBOX_STYLE)
        self.chk_winter.setEnabled(False)

        self.btn_winter_dates = QPushButton("Задать даты", self)
        self.btn_winter_dates.setFont(F_Sml)
        self.btn_winter_dates.setGeometry(300, 680, 250, 35)
        self.btn_winter_dates.setEnabled(False)
        self.btn_winter_dates.setStyleSheet("""
            QPushButton { background-color: #4172A2; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #355E87; }
            QPushButton:disabled { background-color: #7f7f7f; color: white; border: none; border-radius: 4px; }
        """)

        # 7. Кнопка "Назад"
        self.btn_back = QPushButton("Назад", self)
        self.btn_back.setFont(F_Nrm)
        self.btn_back.setGeometry(35, 760, 200, 70)
        self.btn_back.setStyleSheet("""
            QPushButton { background-color: gray; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: #666666; }
        """)

        # 8. Кнопка "Очистить все поля"
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

        # 9. Кнопка "Выборочная печать"
        self.btn_sel_print = QPushButton("Выборочная\n печать", self)
        self.btn_sel_print.setFont(F_Nrm)
        self.btn_sel_print.setGeometry(425, 760, 230, 70)
        self.btn_sel_print.setStyleSheet("""
            QPushButton { background-color: green; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: darkgreen; }
        """)

        # 10. Кнопка "Печать"
        self.btn_print = QPushButton("Печать", self)
        self.btn_print.setFont(F_Nrm)
        self.btn_print.setGeometry(665, 760, 200, 70)
        self.btn_print.setStyleSheet("""
            QPushButton { background-color: green; color: white; border: none; border-radius: 4px; }
            QPushButton:hover { background-color: darkgreen; }
        """)

    # Метод подключения логики
    def setup_logic(self):
        self.chk_cross.toggled.connect(self.on_cross_toggled)
        self.cb_holder.currentTextChanged.connect(self.on_holder_changed)

        self.chk_winter.toggled.connect(self.on_winter_toggled)
        self.btn_winter_dates.clicked.connect(self.open_winter_dates_window)

        self.btn_back.clicked.connect(self.reject)
        self.btn_reset.clicked.connect(self.reset_fields)
        self.btn_sel_print.clicked.connect(self.on_selective_print_clicked)
        self.btn_print.clicked.connect(self.on_print_clicked)

        for i in range(3):
            self.shurf_combos[i].currentIndexChanged.connect(
                lambda idx, row=i: self.on_shurf_type_changed(row)
            )
            self.dig_fields[i].textChanged.connect(
                lambda text, row=i: self.on_dig_text_changed(row, text)
            )

        self.on_holder_changed(self.cb_holder.currentText())

    # Метод логики "Пересечение"
    def on_cross_toggled(self, checked):
        self.txt_house.setEnabled(not checked)
        if checked:
            self.txt_house.clear()
        self.txt_address_cross.setEnabled(checked)
        if not checked:
            self.txt_address_cross.clear()

    # Метод логики для смены балансосодержателя
    def on_holder_changed(self, holder_name: str = None):
        if holder_name is None:
            holder_name = self.cb_holder.currentText()

        is_admin = (holder_name == "Администрация")
        self.chk_winter.setEnabled(is_admin)
        self.btn_winter_dates.setEnabled(is_admin and self.chk_winter.isChecked())

        self.update_shurf_options()

        for i in range(3):
            self.update_fields_state(i)

    # Метод логики для элементов зимнего периода
    def on_winter_toggled(self, checked):
        is_admin = (self.cb_holder.currentText() == "Администрация")
        self.btn_winter_dates.setEnabled(is_admin and checked)
        self.save_config()

    # Метод открытия окна сроков зимнего периода
    def open_winter_dates_window(self):
        dialog = WinterDateWindow(
            current_green=self.winter_green_date,
            current_asphalt=self.winter_asphalt_date,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.winter_green_date, self.winter_asphalt_date = dialog.get_dates()
            self.save_config()

    # Метод реакции на смену значения в любом к-боксе
    def on_shurf_type_changed(self, row: int):
        self.update_shurf_options()

    # Метод пересчета доступных вариантов для всех к-боксов с учетом приоритетов
    def update_shurf_options(self):
        holder = self.cb_holder.currentText()
        allowed_base = COMPANY_LIMITS.get(holder, ["нет данных"])

        # Временное отключение сигналов, чтобы убрать рекурсию
        for cb in self.shurf_combos:
            cb.blockSignals(True)

        # Фиксация текстов, которые сейчас выбраны пользователем
        current_selections = [cb.currentText() for cb in self.shurf_combos]

        for i in range(3):
            cb = self.shurf_combos[i]
            old_val = current_selections[i]

            # Правила цепочки данных
            if i > 0 and current_selections[i - 1] in ["нет данных", ""]:
                valid_items = ["нет данных"]
            else:
                valid_items = []
                for item in allowed_base:
                    if i == 0 and item == "нет данных":
                        continue
                    
                    if item == "нет данных":
                        valid_items.append(item)
                        continue

                    is_valid = True

                    for prev_idx in range(0, i):
                        prev_val = current_selections[prev_idx]
                        if prev_val and prev_val != "нет данных":
                            if item == prev_val or PRIORITY.get(item, 99) <= PRIORITY.get(prev_val, 99):
                                is_valid = False
                                break

                    if not is_valid:
                        continue

                    for next_idx in range(i + 1, 3):
                        next_val = current_selections[next_idx]
                        if next_val and next_val != "нет данных":
                            if item == next_val or PRIORITY.get(item, 99) >= PRIORITY.get(next_val, 99):
                                is_valid = False
                                break

                    if is_valid:
                        valid_items.append(item)

            # Пересоздание списка элементов
            cb.clear()
            cb.addItems(valid_items)

            # Сброс индекса в -1, чтобы PyQt не считал 0-й элемент "уже выбранным"
            cb.setCurrentIndex(-1)

            # Установка значения заново
            if old_val in valid_items:
                cb.setCurrentText(old_val)
            else:
                new_val = valid_items[0] if valid_items else ""
                cb.setCurrentText(new_val)

            # Созранение реального выбранного текст для корректности следующих итераций цикла
            current_selections[i] = cb.currentText()

        # Включение сигналов обратно
        for cb in self.shurf_combos:
            cb.blockSignals(False)

        # Принудительное обновление полей для всех 3 шурфов
        for i in range(3):
            self.update_fields_state(i)

    # Метод управления активностью и содержимым полей разрытия и под восстановление
    def update_fields_state(self, row: int):
        holder = self.cb_holder.currentText()
        stype = self.shurf_combos[row].currentText()
        is_has_data = bool(stype) and (stype != "нет данных")

        # Для площадей разрытия
        if holder == "Администрация":
            # Для Администрации всегда заблокированы и пусты
            self.dig_fields[row].setEnabled(False)
            self.dig_fields[row].clear()
        else:
            # Активны только если выбран тип, отличный от "нет данных"
            self.dig_fields[row].setEnabled(is_has_data)
            if not is_has_data:
                self.dig_fields[row].clear()

        # Для площадей под восстановление
        if holder in ["Администрация", "Житлокомсервис"]:
            # Заблокированы и пусты для Администрации и Жилкомсервиса
            self.rec_fields[row].setEnabled(False)
            self.rec_fields[row].clear()

        elif holder in ["Дорремстрой", "Зеленстрой"]:
            if not is_has_data:
                # Заблокированы, если тип шурфа "нет данных"
                self.rec_fields[row].setEnabled(False)
                self.rec_fields[row].clear()
            elif stype in ["Зеленая зона", "Грунтовка"]:
                # Копируют разрытие, если Зеленая зона или Грунтовка (неактивны)
                self.rec_fields[row].setEnabled(False)
                self.rec_fields[row].setText(self.dig_fields[row].text())
            else:
                # Отличные от Зеленой зоны/Грунтовки — активны для редактирования
                self.rec_fields[row].setEnabled(True)

    # Метод проверки изменений в полях разрытия и под восстановление
    def on_dig_text_changed(self, row: int, text: str):
        holder = self.cb_holder.currentText()
        stype = self.shurf_combos[row].currentText()

        if holder in ["Дорремстрой", "Зеленстрой"]:
            if stype in ["Зеленая зона", "Грунтовка"]:
                self.rec_fields[row].setText(text)

    # Вспомагательный метод сбора данных с формы
    def collect_data(self) -> dict:
        shurfs_data = []
        for i in range(3):
            stype = self.shurf_combos[i].currentText()
            if stype and stype != "нет данных":
                shurfs_data.append({
                    "type": stype,
                    "dig_sq": self.dig_fields[i].text().strip(),
                    "rec_sq": self.rec_fields[i].text().strip()
                })

        return {
            "holder": self.cb_holder.currentText(),
            "card_num": self.txt_card_num.text().strip(),
            "card_date": self.date_card.date().toString("dd.MM.yyyy"),
            "address": self.txt_address.text().strip(),
            "house": self.txt_house.text().strip(),
            "is_cross": self.chk_cross.isChecked(),
            "address_cross": self.txt_address_cross.text().strip(),
            "shurfs": shurfs_data,
            "is_winter": self.chk_winter.isChecked(),
            "winter_date_green": self.winter_green_date.toString("dd.MM.yyyy"),
            "winter_date_asphalt": self.winter_asphalt_date.toString("dd.MM.yyyy")
        }

    # Метод "Защита от дурака"
    def validate_inputs(self) -> bool:
        if not self.txt_card_num.text().strip():
            show_warning_message(self, "Номер карточки КДЕ?")
            self.txt_card_num.setFocus()
            return False

        if not self.txt_address.text().strip():
            show_warning_message(self, "А где мы копали-то?")
            self.txt_address.setFocus()
            return False

        if self.chk_cross.isChecked():
            main_street = self.txt_address.text().strip().lower()
            cross_street = self.txt_address_cross.text().strip().lower()

            if not cross_street:
                show_warning_message(self, "С кем улица пересеклась? С пустотой бытия?")
                self.txt_address_cross.setFocus()
                return False

            if main_street == cross_street:
                show_warning_message(self, "Улица пересеклась сама с собой! Серъёзно?")
                self.txt_address_cross.setFocus()
                return False
        else:
            if not self.txt_house.text().strip():
                show_warning_message(self, "Где номер дома? Всю улицу перекопали?")
                self.txt_house.setFocus()
                return False 
        
        holder = self.cb_holder.currentText()
        
        if holder != "Администрация":
            for i in range(3):
                stype = self.shurf_combos[i].currentText()
                if stype and stype != "нет данных":
                    if not self.dig_fields[i].text().strip():
                        show_warning_message(self, f"Площадь разрытия нам уже не нужна, да?")
                        self.dig_fields[i].setFocus()
                        return False

                    if self.rec_fields[i].isEnabled() and not self.rec_fields[i].text().strip():
                        show_warning_message(self, f"Восстанавливать асфальт мы, по ходу, уже не будем...")
                        self.rec_fields[i].setFocus()
                        return False

        return True

    # Метод сбора данных и подключения сервиса печати
    # (с сообщением после печати) при обычной печати
    def on_print_clicked(self, *_):
        if not self.validate_inputs():
            return

        order_data = self.collect_data()

        services_map = {
            "Администрация": process_adm_open,
            "Житлокомсервис": process_zks_open,
            "Дорремстрой": process_drs_open,
            "Зеленстрой": process_hzs_open
        }

        current_holder = order_data["holder"]
        service = services_map.get(current_holder)

        if service:
            service(order_data)
            show_success_message(self, f"Напечатали!!!")
            cleanup_temp_files()

    # Метод сбора данных и подключения сервиса печати
    # (с сообщением после печати) при выборочной печати
    def on_selective_print_clicked(self):
        if not self.validate_inputs():
            return
        
        current_holder = self.cb_holder.currentText().strip()

        order_data = self.collect_data()

        if current_holder in ["Администрация"]:
            self.adm_ex_window = GuiAdmOpenEx(parent=self, order_data=order_data)
            self.adm_ex_window.show()
        elif current_holder in ["Житлокомсервис"]:
            self.drs_ex_window = GuiZksOpenEx(parent=self, order_data=order_data)
            self.drs_ex_window.show()
        elif current_holder in ["Дорремстрой"]:
            self.drs_ex_window = GuiDrsOpenEx(parent=self, order_data=order_data)
            self.drs_ex_window.show()
        elif current_holder in ["Зеленстрой"]:
            self.drs_ex_window = GuiHzsOpenEx(parent=self, order_data=order_data)
            self.drs_ex_window.show()

    # Метод очистки всех полей к дефолтным значениям
    def reset_fields(self):
        self.txt_card_num.clear()
        self.txt_address.clear()
        self.txt_house.clear()
        self.txt_address_cross.clear()
        
        self.chk_cross.setChecked(False)
        self.date_card.setDate(QDate.currentDate())

        if self.cb_holder.count() > 0:
            self.cb_holder.setCurrentIndex(0)

        for i in range(3):
            self.dig_fields[i].clear()
            self.rec_fields[i].clear()

        self.update_shurf_options()

        self.txt_card_num.setFocus()

    # Метод ручного закрытия окна
    def closeEvent(self, event):
        cleanup_temp_files()
        event.accept()