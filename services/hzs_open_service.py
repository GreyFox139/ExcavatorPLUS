import os
from docxtpl import DocxTemplate
from config import SHURF_MAP, OUTPUT_DIR
from utility.print_docx import print_batch_docx

# Метод создания адресной строки
def build_address(data: dict) -> str:
    main_addr = data.get("address", "")
    house = data.get("house", "")
    is_cross = data.get("is_cross", False)
    address_cross = data.get("address_cross", "")

    if is_cross:
        return f"{main_addr} ріг {address_cross}"
    if house:
        return f"{main_addr}, {house}"
    return main_addr

# Метод создания перечня типов покрытия
def build_shurfs(shurfs: list, mode: str = "normal") -> str:
    names = []
    for s in shurfs:
        stype = s.get("type")
        if not stype or stype == "нет данных":
            continue
        if stype in SHURF_MAP and mode in SHURF_MAP[stype]:
            names.append(SHURF_MAP[stype][mode])
        else:
            names.append(stype)
    return " + ".join(names)

# Основной метод сервиса генерации документов на открытие для Зеленстроя
def process_hzs_open(data: dict, selected_docs: dict = None):
    full_address = build_address(data)
    shurfs_list = data.get("shurfs", [])
    shurfs_normal = build_shurfs(shurfs_list, mode="normal")
    shurfs_full = build_shurfs(shurfs_list, mode="full")

    card_num = data.get("card_num", "")
    card_date = data.get("card_date", "")
    card_str = f"№ {card_num} від {card_date} р." if card_num else ""

    table_context = {}
    for i in range(1, 4):
        table_context[f"type{i}"] = ""
        table_context[f"state{i}"] = ""
        table_context[f"area{i}"] = ""
        table_context[f"rest{i}"] = ""

    for idx, s in enumerate(shurfs_list[:3], start=1):
        stype = s.get("type")
        dig_sq = s.get("dig_sq", "")

        if not stype or stype == "нет данных":
            continue

        name = SHURF_MAP[stype]["full"] if (stype in SHURF_MAP and "full" in SHURF_MAP[stype]) else stype
        sq_str = f"{dig_sq} м²" if dig_sq else ""

        table_context[f"type{idx}"] = name
        table_context[f"state{idx}"] = "стан добрий"
        table_context[f"area{idx}"] = sq_str
        table_context[f"rest{idx}"] = sq_str

    f2_context = {
        "address": full_address,
        "shurfs": shurfs_full,
        "card": card_str,
        **table_context
    }

    base_dir = os.path.dirname(os.path.dirname(__file__))

    documents_config = [
        {
            "id": "zayava",
            "template": os.path.join(base_dir, "templates", "open", "zayava.docx"),
            "output": os.path.join(OUTPUT_DIR, "hzs_zayava_rendered.docx"),
            "default_copies": 1,
            "context": {
                "address": full_address,
                "shurfs": shurfs_normal
            }
        },
        {
            "id": "dopka",
            "template": os.path.join(base_dir, "templates", "open", "hzs_dopka.docx"),
            "output": os.path.join(OUTPUT_DIR, "hzs_dopka_rendered.docx"),
            "default_copies": 3,
            "context": {
                "address": full_address,
                "shurfs": shurfs_full,
                "card": card_str
            }
        },
        {
            "id": "f2",
            "template": os.path.join(base_dir, "templates", "open", "hzs_f2.docx"),
            "output": os.path.join(OUTPUT_DIR, "hzs_f2_rendered.docx"),
            "default_copies": 2,
            "context": f2_context
        },
        {
            "id": "dogovor",
            "template": os.path.join(base_dir, "templates", "open", "hzs_dogovor.docx"),
            "output": os.path.join(OUTPUT_DIR, "hzs_dogovor_rendered.docx"),
            "default_copies": 1,
            "context": {}
        }
    ]

    files_to_print = []
    for doc_info in documents_config:
        doc_id = doc_info["id"]

        # Проверка типа печати для установки количества копий
        if selected_docs is not None:
            if doc_id not in selected_docs:
                continue
            copies_count = selected_docs[doc_id]
        else:
            copies_count = doc_info["default_copies"]

        tpl_path = doc_info["template"]
        out_path = doc_info["output"]
        
        if not os.path.exists(tpl_path):
            continue

        tpl = DocxTemplate(tpl_path)
        tpl.render(doc_info["context"])
        tpl.save(out_path)
        files_to_print.append((out_path, copies_count))

    # Пакетная печать
    if files_to_print:
        print_batch_docx(files_to_print)