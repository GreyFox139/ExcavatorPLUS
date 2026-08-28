import os
from docxtpl import DocxTemplate
from config import OUTPUT_DIR
from utility.print_docx import print_batch_docx
from utility.rozpiska_text import get_rozpiska_text

# Метод создания адресной строки
def build_address(data: dict) -> str:
    street = data.get("street", "")
    if data.get("is_cross"):
        cross = data.get("cross_street", "")
        return f"{street} ріг {cross}"
    house = data.get("house_num", "")
    return f"{street}, {house}" if house else street

# Метод маппинга второго типа покрытия
def build_second_type_text(type_key: str) -> str:
    mapping = {
        "asphalt": "асфальтобетоні",
        "paving": "тротуарній плитці",
        "dirt": "грунтовій дорозі",
    }
    return mapping.get(type_key, "асфальтобетоні")

# Метод создания списка комиссии
def build_commission_dict(data: dict) -> dict:
    chk_jks = data.get("chk_jks_hbu", False)
    chk_other = data.get("chk_other_rep", False)

    jks_num = data.get("jks_num", "")
    jks_regal = f"Начальник дільниці № {jks_num}\nСалтівського району\nКП «Житлокомсервис»" if jks_num else ""
    jks_name = data.get("jks_fio", "")

    hbu_num = data.get("hbu_num", "")
    hbu_regal = f"Начальник дільниці № {hbu_num}\nСалтівського району\nфілії «БЛАГОУСТРІЙ» КП «ШЛЯХРЕМБУД»" if hbu_num else ""
    hbu_name = data.get("hbu_fio", "")

    line1 = "\n_____________________________________\n_____________________________________"
    line2 = "_______________"

    r1, n1 = "", ""
    r2, n2 = "", ""
    r3, n3 = "", ""

    if chk_jks and not chk_other:
        r1, n1 = jks_regal, jks_name
        r2, n2 = hbu_regal, hbu_name
    elif chk_jks and chk_other:
        r1, n1 = jks_regal, jks_name
        r2, n2 = hbu_regal, hbu_name
        r3, n3 = line1, line2
    elif not chk_jks and chk_other:
        r1, n1 = line1, line2

    return {
        "regal1": r1, "name1": n1,
        "regal2": r2, "name2": n2,
        "regal3": r3, "name3": n3,
    }

# Метод расчета количества копий
def get_act_copies(data: dict) -> int:
    if data.get("chk_jks_hbu"):
        return 4
    if data.get("chk_other_rep"):
        return 3
    return 2

# Основной метод сервиса генерации документов на закрытие для Администрации
def process_adm_close(data: dict, selected_docs: dict = None):
    full_address = build_address(data)
    order_num = data.get("order_num", "")
    order_date_str = f"{data.get('order_date', '')} р." if data.get('order_date') else ""

    documents_config = [
        {
            "id": "adm_act",
            "enabled": True,
            "template": os.path.join("templates", "close", "adm_act.docx"),
            "output": os.path.join(OUTPUT_DIR, "adm_act_rendered.docx"),
            "default_copies": get_act_copies(data),
            "context": {
                "order": order_num,
                "address": full_address,
                "second_type": build_second_type_text(data.get("second_type_key")),
                "green": data.get("green_area", ""),
                "abp": data.get("second_type_area", ""),
                **build_commission_dict(data),
            },
        },
        {
            "id": "f7",
            "enabled": data.get("chk_form7", False),
            "template": os.path.join("templates", "close", "f7.docx"),
            "output": os.path.join(OUTPUT_DIR, "f7_rendered.docx"),
            "default_copies": 1,
            "context": {
                "address": full_address,
                "order": order_num,
                "order_date": order_date_str,
            },
        },
        {
            "id": "rozpiska",
            "enabled": data.get("chk_receipt", False),
            "template": os.path.join("templates", "close", "rozpiska.docx"),
            "output": os.path.join(OUTPUT_DIR, "rozpiska_rendered.docx"),
            "default_copies": 1,
            "context": {
                "address": full_address,
                "works": get_rozpiska_text(),
            },
        },
    ]

    files_to_print = []

    for doc_info in documents_config:
        doc_id = doc_info["id"]

        # Проверка типа печати для устновки количества копий
        if selected_docs is not None:
            if doc_id in selected_docs:
                doc_info["enabled"] = True
                copies_count = selected_docs[doc_id]
            else:
                doc_info["enabled"] = False
                copies_count = 0
        else:
            copies_count = doc_info["default_copies"]

        if not doc_info["enabled"]:
            continue

        tpl_path = doc_info["template"]
        out_path = doc_info["output"]

        if not os.path.exists(tpl_path):
            print(f"⚠️ Шаблон не найден: {tpl_path}")
            continue

        tpl = DocxTemplate(tpl_path)
        tpl.render(doc_info["context"])
        tpl.save(out_path)

        files_to_print.append((out_path, copies_count))

    # Пакетная печать
    if files_to_print:
        print_batch_docx(files_to_print)