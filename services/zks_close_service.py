import os
from docxtpl import DocxTemplate
from config import OUTPUT_DIR, ZKS_BLAGO_DB, SHURF_MAP
from utility.print_docx import print_batch_docx
from utility.rozpiska_text import get_rozpiska_text

# Метод создания аддресной строки
def build_address(data: dict) -> str:
    street = data.get("street", "")
    if data.get("is_cross"):
        cross = data.get("cross_street", "")
        return f"{street} ріг {cross}"
    
    house = data.get("house_num", "")
    return f"{street}, {house}" if house else street

# Метод создания второго типа покрытия (с приоритетом)
def determine_second_type(shurf_types: list[str]) -> str:
    asphalt_keys = {"Пр. внутр.", "Тротуар", "Отмостка", "нет данных"}
    
    # Ищем по высшему приоритету
    for st in shurf_types:
        if st in asphalt_keys:
            return "асфальтобетоні"
            
    for st in shurf_types:
        if st == "Трот. плитка":
            return "тротуарній плитці"
            
    for st in shurf_types:
        if st == "Грунтовка":
            return "грунтовій дорозі"
            
    return "асфальтобетоні"

# Метод вычисления площадей
def calculate_areas(shurf_items: list[dict]) -> tuple[str, str]:
    green_sum = 0.0
    abp_sum = 0.0

    for item in shurf_items:
        stype = item.get("type", "")
        try:
            val = float(item.get("area", 0) or 0)
        except ValueError:
            val = 0.0

        if stype == "Зеленая зона":
            green_sum += val
        else:
            abp_sum += val

    g_str = f"{green_sum:.2f}".rstrip('0').rstrip('.') if green_sum else "0"
    a_str = f"{abp_sum:.2f}".rstrip('0').rstrip('.') if abp_sum else "0"

    return g_str, a_str

# Метод создания перечня типов покрытия
def build_shurfs_string(shurf_types: list[str]) -> str:
    names = []
    for st in shurf_types:
        if not st or st == "нет данных":
            continue
        mapped_name = SHURF_MAP.get(st, {}).get("full", st)
        names.append(mapped_name)
    
    return " + ".join(names)

# Основной метод сервиса генерации документов на закрытие для Жилкомсервиса
def process_zks_close(data: dict, selected_docs: dict = None):
    full_address = build_address(data)
    order_num = data.get("order_num", "")
    order_date_str = f"{data.get('order_date', '')} р." if data.get('order_date') else ""

    shurf_items = data.get("shurfs", [])  # Ожидается список диктов: [{"type": "...", "area": "..."}]
    shurf_types = [item.get("type", "") for item in shurf_items]
    second_type = determine_second_type(shurf_types)
    green_area, abp_area = calculate_areas(shurf_items)
    shurfs_str = build_shurfs_string(shurf_types)

    jks_num = data.get("jks_num", 0)
    jks_info = ZKS_BLAGO_DB.get(jks_num, {})
    jks_name = jks_info.get("jks_fio", "")

    hbu_num_str = str(data.get("hbu_num", ""))
    hbu_name = ""
    for bu in jks_info.get("blago_units", []):
        if str(bu.get("num")) == hbu_num_str:
            hbu_name = bu.get("fio", "")
            break

    documents_config = [
        {
            "id": "zks_act",
            "enabled": True,
            "template": os.path.join("templates", "close", "zks_act.docx"),
            "output": os.path.join(OUTPUT_DIR, "zks_act_rendered.docx"),
            "default_copies": 2,
            "context": {
                "order": order_num,
                "address": full_address,
                "second_type": second_type,
                "green": green_area,
                "abp": abp_area,
                "zks_num": jks_num,
                "zks_name": jks_name,
                "blago_num": hbu_num_str,
                "blago_name": hbu_name,
            },
        },
        {
            "id": "zks_prper",
            "enabled": True,
            "template": os.path.join("templates", "close", "zks_prper.docx"),
            "output": os.path.join(OUTPUT_DIR, "zks_prper_rendered.docx"),
            "default_copies": 3,
            "context": {
                "order": order_num,
                "address": full_address,
                "shurfs": shurfs_str,
                "du_num": data.get("du_num", ""),
                "du_date": data.get("du_date", ""),  # Чистая дата без "р."
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