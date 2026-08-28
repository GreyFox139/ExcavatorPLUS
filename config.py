import os
from PyQt6.QtGui import QFont

# --- Пути к ресурсам ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "icon.ico")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_temp")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Базовая семейство шрифтов ---
FONT_FAMILY = "Courier New"

# --- Реестр шрифтов ---
# 12 кегль (Tiny)
F_Tiny = QFont(FONT_FAMILY, 12)

# 18 кегль (Small)
F_Sml = QFont(FONT_FAMILY, 18)
F_Sml_B = QFont(FONT_FAMILY, 18, QFont.Weight.Bold)

# 24 кегль (Normal)
F_Nrm = QFont(FONT_FAMILY, 24)
F_Nrm_B = QFont(FONT_FAMILY, 24, QFont.Weight.Bold)

# 36 кегль (Middle)
F_Mid = QFont(FONT_FAMILY, 32)
F_Mid_B = QFont(FONT_FAMILY, 32, QFont.Weight.Bold)

# 48 кегль (Big)
F_Big = QFont(FONT_FAMILY, 40)
F_Big_B = QFont(FONT_FAMILY, 40, QFont.Weight.Bold)

# --- Перечень типов шурфов по организациям ---
COMPANY_LIMITS = {
    "Администрация": ["нет данных", "Зеленая зона", "Грунтовка", "Пр. внутр.", "Тротуар", "Трот. плитка", "Отмостка"],
    "Житлокомсервис": ["нет данных", "Зеленая зона", "Грунтовка", "Пр. внутр.", "Тротуар", "Трот. плитка", "Отмостка"],
    "Дорремстрой": ["нет данных", "Зеленая зона", "Грунтовка", "Пр. часть", "Тротуар", "Трот. плитка", "А/б заезд"],
    "Зеленстрой": ["нет данных", "Зеленая зона", "Грунтовка", "Пр. внутр.", "Тротуар", "Трот. плитка", "А/б заезд"]
}

# --- Перечень приоритетов отображения типов шурфов ---
PRIORITY = {
    "Пр. часть": 1,
    "Пр. внутр.": 2,
    "А/б заезд": 2,
    "Тротуар": 3,
    "Трот. плитка": 4,
    "Отмостка": 5,
    "Грунтовка": 6,
    "Зеленая зона": 7,
    "нет данных": 99
}

# --- Перечень изменения названий типов шурфов для конкретных организаций ---
SHURF_MAP = {
    "Зеленая зона": {
        "normal": "зел. зона",
        "short": "з/з",
        "full": "зелена зона"
    },
    "Грунтовка": {
        "normal": "грунт. дор.",
        "short": "грунт.",
        "full": "грунт. дор."
    },
    "Пр. внутр.": {
        "normal": "пр. внутр.",
        "short": "пр. внутр.",
        "full": "пр. внутр."
    },
    "Пр. часть": {
        "normal": "пр. частина",
        "short": "пр. частина",
        "full": "пр. частина"
    },
    "Тротуар": {
        "normal": "тротуар",
        "short": "тр-р",
        "full": "тротуар"
    },
    "Трот. плитка": {
        "normal": "трот. плитка",
        "short": "тр. пл.",
        "full": "трот. плитка"
    },
    "Отмостка": {
        "normal": "вимощ.",
        "short": "вимощ.",
        "full": "вимощ."
    },
    "А/б заезд": {
        "normal": "а/б заїзд",
        "short": "а/б заїзд",
        "full": "а/б заїзд"
    }
}

ZKS_BLAGO_DB = {
    30: {
        "jks_fio": "М.М. Масіч",
        "blago_units": [
            {"num": "1", "fio": "С.В. Колесник"},
            {"num": "2", "fio": "Л.В. Цеменко"},
        ]
    },
    31: {
        "jks_fio": "С.П. Ляшенко",
        "blago_units": [
            {"num": "5", "fio": "О.В. Петрук"}
        ]
    },
    32: {
        "jks_fio": "Н.І. Долгова",
        "blago_units": [
            {"num": "7", "fio": "С.Є. Ільєнко"}
        ]
    },
    33: {
        "jks_fio": "Л.М. Кулабухова",
        "blago_units": [
            {"num": "6", "fio": "О.В. Калашников"}
        ]
    },
    34: {
        "jks_fio": "П.О. Воронцов",
        "blago_units": [
            {"num": "3", "fio": "Є.Б. Волинчик"}
        ]
    },
    35: {
        "jks_fio": "Т.І. Шелепіна",
        "blago_units": [
            {"num": "4", "fio": "Б.В. Фартушний"}
        ]
    },
    36: {
        "jks_fio": "Д.В. Андрукович",
        "blago_units": [
            {"num": "9", "fio": "Т.В. Краченко"}
        ]
    },
    37: {
        "jks_fio": "О.І. Головчанська",
        "blago_units": [
            {"num": "10", "fio": "О.А. Перетяченко"}
        ]
    },
    38: {
        "jks_fio": "А.С. Кріпінєвич",
        "blago_units": [
            {"num": "11", "fio": "С.В. Косенко"}
        ]
    },
    39: {
        "jks_fio": "А.О. Демидюк",
        "blago_units": [
            {"num": "12", "fio": "О.І. Овечко"}
        ]
    },
    40: {
        "jks_fio": "О.В. Босенко",
        "blago_units": [
            {"num": "10", "fio": "О.А. Перетяченко"}
        ]
    },
    41: {
        "jks_fio": "С.Ю. Шиндель",
        "blago_units": [
            {"num": "8", "fio": "І.В. Семененко"}
        ]
    },
}

CHECKBOX_STYLE = """
    QCheckBox::indicator {
        width: 28px;
        height: 28px;
        border: 2px solid #7f7f7f;
        background-color: white;
        border-radius: 3px;
    }
    QCheckBox::indicator:checked {
        background-color: #4172A2;
        border-color: #355E87;
        image: url("gui/graph/checkbox_wing.png");
        image-position: center;
    }
    QCheckBox::indicator:hover {
        border-color: #253E67;
    }
    QCheckBox::indicator:disabled {
        border-color: #b0b0b0;
        background-color: #e0e0e0;
    }
"""

RADIO_STYLE = """
    QRadioButton::indicator {
        width: 28px;
        height: 28px;
        border: 2px solid #7f7f7f;
        background-color: white;
        border-radius: 16px;
    }
    QRadioButton::indicator:checked {
        background-color: #4172A2;
        border-color: #355E87;
        image: url("gui/graph/radio_dot.png");
        image-position: center;
    }
    QRadioButton::indicator:hover {
        border-color: #253E67;
    }
    QRadioButton::indicator:disabled {
        border-color: #b0b0b0;
        background-color: #e0e0e0;
    }
"""

TAB_STYLE = """
    /* Внешняя граница внутренней панели */
    QTabWidget::pane {
        border: 2px solid #8F8F8F;
        top: -1px;
    }

    /* Ярлыки вкладок на всю ширину (840px / 4 = 210px) */
    QTabBar::tab {
        width: 378px;
        height: 38px;
        background-color: #D6D6D6;
        border: 1px solid #8F8F8F;
        border-bottom: none;
    }

    /* Активная вкладка */
    QTabBar::tab:selected {
        background-color: #E8E8E8;
        border-bottom: 2px solid #E8E8E8;
        font-weight: bold;
    }

    /* Наведение на неактивную вкладку */
    QTabBar::tab:hover:!selected {
        background-color: #C5C5C5;
    }
"""