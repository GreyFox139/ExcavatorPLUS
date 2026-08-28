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

# Основной метод сервиса генерации документов на закрытие для Дорремстроя
def process_drs_close(data: dict, selected_docs: dict = None):
    full_address = build_address(data)
    order_num = data.get("order_num", "")
    raw_date = data.get("order_date", "")
    order_date_str = f"{raw_date} р." if raw_date else ""

    documents_config = [
        {
            "id": "drs_prper",
            "enabled": True,
            "template": os.path.join("templates", "close", "drs_prper.docx"),
            "output": os.path.join(OUTPUT_DIR, "drs_prper_rendered.docx"),
            "default_copies": 3,
            "context": {
                "order": order_num,
                "order_date": order_date_str,
                "address": full_address,
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

        # Проверка типа печати для установки количества копий
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