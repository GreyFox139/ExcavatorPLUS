import os
from config import OUTPUT_DIR
from utility.print_docx import print_batch_docx


# Карта путей к шаблонам бланков
BLANK_TEMPLATES = {
    # Вкладка "Открытие"
    "open_zayava": os.path.join("templates", "empty", "zayava.docx"),
    "open_adm_act": os.path.join("templates", "empty", "adm_act.docx"),
    "open_adm_garant": os.path.join("templates", "empty", "adm_garant.docx"),
    "open_zks_dopka": os.path.join("templates", "empty", "zks_dopka.docx"),
    "open_zks_act": os.path.join("templates", "empty", "zks_act.docx"),
    "open_zks_dogovor": os.path.join("templates", "open", "zks_dogovor.docx"),
    "open_drs_dopka": os.path.join("templates", "empty", "drs_dopka.docx"),
    "open_drs_f2": os.path.join("templates", "empty", "drs_f2.docx"),
    "open_drs_dogovor": os.path.join("templates", "open", "drs_dogovor.docx"),
    "open_hzs_dopka": os.path.join("templates", "empty", "hzs_dopka.docx"),
    "open_hzs_f2": os.path.join("templates", "empty", "hzs_f2.docx"),
    "open_hzs_dogovor": os.path.join("templates", "open", "hzs_dogovor.docx"),

    # Вкладка "Закрытие"
    "close_adm_act2": os.path.join("templates", "empty", "adm_act2.docx"),
    "close_zks_act2": os.path.join("templates", "empty", "zks_act2.docx"),
    "close_zks_prper": os.path.join("templates", "empty", "zks_prper.docx"),
    "close_drs_prper": os.path.join("templates", "empty", "drs_prper.docx"),
    "close_hzs_prper": os.path.join("templates", "empty", "hzs_prper.docx"),
    "close_f7": os.path.join("templates", "empty", "f7.docx"),
}

# Метод отправик пустых шаблонов на печать
def process_blank_print(selected_blanks: dict[str, int]):
    """
    Отправка на печать чистых бланков.
    selected_blanks: dict { "blank_id": copies_count }
    """
    files_to_print = []

    for blank_id, copies in selected_blanks.items():
        if copies < 1:
            continue

        tpl_path = BLANK_TEMPLATES.get(blank_id)
        if not tpl_path or not os.path.exists(tpl_path):
            print(f"⚠️ Шаблон бланка не найден: {tpl_path}")
            continue

        # Бланки не требуют рендеринга в PDF, поэтому печать прямо из шаблона
        files_to_print.append((tpl_path, copies))

    # Пакетная печать
    if files_to_print:
        print_batch_docx(files_to_print)