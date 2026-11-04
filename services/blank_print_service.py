import os
from config import BASE_DIR
from utility.print_docx import print_batch_docx

# Карта путей к шаблонам бланков
BLANK_TEMPLATES = {
    # Вкладка "Открытие"
    "open_zayava": os.path.join(BASE_DIR, "templates", "empty", "zayava.docx"),
    "open_adm_act": os.path.join(BASE_DIR, "templates", "empty", "adm_act.docx"),
    "open_adm_garant": os.path.join(BASE_DIR, "templates", "empty", "adm_garant.docx"),
    "open_zks_dopka": os.path.join(BASE_DIR, "templates", "empty", "zks_dopka.docx"),
    "open_zks_act": os.path.join(BASE_DIR, "templates", "empty", "zks_act.docx"),
    "open_zks_dogovor": os.path.join(BASE_DIR, "templates", "open", "zks_dogovor.docx"),
    "open_drs_dopka": os.path.join(BASE_DIR, "templates", "empty", "drs_dopka.docx"),
    "open_drs_f2": os.path.join(BASE_DIR, "templates", "empty", "drs_f2.docx"),
    "open_drs_dogovor": os.path.join(BASE_DIR, "templates", "open", "drs_dogovor.docx"),
    "open_hzs_dopka": os.path.join(BASE_DIR, "templates", "empty", "hzs_dopka.docx"),
    "open_hzs_f2": os.path.join(BASE_DIR, "templates", "empty", "hzs_f2.docx"),
    "open_hzs_dogovor": os.path.join(BASE_DIR, "templates", "open", "hzs_dogovor.docx"),

    # Вкладка "Закрытие"
    "close_adm_act2": os.path.join(BASE_DIR, "templates", "empty", "adm_act2.docx"),
    "close_zks_act2": os.path.join(BASE_DIR, "templates", "empty", "zks_act2.docx"),
    "close_zks_prper": os.path.join(BASE_DIR, "templates", "empty", "zks_prper.docx"),
    "close_drs_prper": os.path.join(BASE_DIR, "templates", "empty", "drs_prper.docx"),
    "close_hzs_prper": os.path.join(BASE_DIR, "templates", "empty", "hzs_prper.docx"),
    "close_f7": os.path.join(BASE_DIR, "templates", "empty", "f7.docx"),
}

# Человекочитаемые названия бланков для окна прогресса
BLANK_TITLES = {
    "open_zayava": "Заявление",
    "open_adm_act": "Акт приёма-передачи(адм.)",
    "open_adm_garant": "Гарантийное письмо (адм.)",
    "open_zks_dopka": "Доп. соглашение (ЖКС)",
    "open_zks_act": "Акт восстановления (ЖКС)",
    "open_zks_dogovor": "Договор (ЖКС)",
    "open_drs_dopka": "Доп. соглашение (ДРС)",
    "open_drs_f2": "Форма 2 (ДРС)",
    "open_drs_dogovor": "Договор (ДРС)",
    "open_hzs_dopka": "Доп. соглашение (ЗС)",
    "open_hzs_f2": "Форма 2 (ЗС)",
    "open_hzs_dogovor": "Договор (ЗС)",
    "close_adm_act2": "Акт комиссии (адм.)",
    "close_zks_act2": "Акт комиссии (ЖКС)",
    "close_zks_prper": "Акт приёма-передачи (ЖКС)",
    "close_drs_prper": "Акт приёма-передачи (ДРС)",
    "close_hzs_prper": "Акт приёма-передачи (ЗС)",
    "close_f7": "Форма 7",
}

# Метод отправки пустых шаблонов на печать
def process_blank_print(selected_blanks: dict[str, int]):
    """
    Отправка на печать чистых бланков.
    selected_blanks: dict { "blank_id": copies_count }
    """
    files_to_print = []

    for blank_id, copies_count in selected_blanks.items():
        if copies_count < 1:
            continue

        tpl_path = BLANK_TEMPLATES.get(blank_id)
        if not tpl_path or not os.path.exists(tpl_path):
            print(f"⚠️ Шаблон бланка не найден: {tpl_path}")
            continue

        doc_title = BLANK_TITLES.get(blank_id, "Чистый бланк")

        # Передаем кортеж из трех элементов: (путь, копии, название для UI)
        files_to_print.append((tpl_path, copies_count, doc_title))

    # Пакетная печать с отображением нашего красивого окна прогресса
    if files_to_print:
        print_batch_docx(files_to_print)