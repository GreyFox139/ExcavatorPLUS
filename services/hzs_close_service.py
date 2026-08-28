import os
from docxtpl import DocxTemplate
from config import OUTPUT_DIR, SHURF_MAP
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

# Метод создания перечня типов покрытия
def build_shurfs_string(shurf_items: list[dict]) -> str:
    names = []
    for item in shurf_items:
        stype = item.get("type", "")
        if not stype or stype == "нет данных":
            continue
        mapped_name = SHURF_MAP.get(stype, {}).get("full", stype)
        names.append(mapped_name)
    
    return " + ".join(names)

# Основной метод сервиса генерации документов на закрытие для Зеленстроя
def process_hzs_close(data: dict, selected_docs: dict = None):
    full_address = build_address(data)
    order_num = data.get("order_num", "")
    
    raw_date = data.get("order_date", "")
    order_date_str = f"{raw_date} р." if raw_date else ""

    shurf_items = data.get("shurfs", [])
    shurfs_str = build_shurfs_string(shurf_items)

    prper_context = {
        "order": order_num,
        "address": full_address,
        "shurfs": shurfs_str,
    }

    for i in range(1, 4):
        if i <= len(shurf_items):
            item = shurf_items[i - 1]
            stype = item.get("type", "")
            
            mapped_type = SHURF_MAP.get(stype, {}).get("full", stype) if (stype and stype != "нет данных") else ""

            prper_context[f"type{i}"] = mapped_type
            prper_context[f"rest{i}"] = item.get("area", "")
            prper_context[f"state{i}"] = "стан добрий" if mapped_type else ""
        else:
            prper_context[f"type{i}"] = ""
            prper_context[f"rest{i}"] = ""
            prper_context[f"state{i}"] = ""

    documents_config = [
        {
            "id": "hzs_prper",
            "enabled": True,
            "template": os.path.join("templates", "close", "hzs_prper.docx"),
            "output": os.path.join(OUTPUT_DIR, "hzs_prper_rendered.docx"),
            "default_copies": 3,
            "context": prper_context,
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