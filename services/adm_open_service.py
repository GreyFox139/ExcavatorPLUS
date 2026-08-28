import os
from docxtpl import DocxTemplate
from config import SHURF_MAP, PRIORITY, OUTPUT_DIR
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
        if stype in SHURF_MAP and mode in SHURF_MAP[stype]:
            names.append(SHURF_MAP[stype][mode])
        else:
            names.append(stype)
    return " + ".join(names)

# Метод проверки приоритета типа покрытия (выше, чем "Зеленая зона")
def has_higher_than_green_zone(shurfs: list) -> bool:
    green_priority = PRIORITY.get("Зеленая зона", 7)
    for s in shurfs:
        stype = s.get("type")
        if PRIORITY.get(stype, 99) < green_priority:
            return True
    return False

# Метод установки дат восстановления в зимний период
def get_recovery_term(data: dict) -> str:
    is_winter = data.get("is_winter", False)
    shurfs = data.get("shurfs", [])
    has_hard_cover = has_higher_than_green_zone(shurfs)

    if is_winter:
        raw_date = data.get("winter_date_asphalt", "") if has_hard_cover else data.get("winter_date_green", "")
        return f"{raw_date} р." if raw_date else ""
    else:
        return "20 днів" if has_hard_cover else "14 днів"

# Основной метод сервсиа генерации документов на открытие для Администрации
def process_adm_open(data: dict, selected_docs: dict = None):
    full_address = build_address(data)
    shurfs_list = data.get("shurfs", [])
    garant_shurf_mode = "short" if len(full_address) > 40 else "normal"

    card_num = data.get("card_num", "")
    card_date = data.get("card_date", "")
    card_str = f"№ {card_num} від {card_date} р." if card_num else ""

    documents_config = [
        {
            "id": "zayava",
            "template": "templates/open/zayava.docx",
            "output": os.path.join(OUTPUT_DIR, "zayava_rendered.docx"),
            "default_copies": 1,
            "context": {
                "address": full_address,
                "shurfs": build_shurfs(shurfs_list, mode="normal")
            }
        },
        {
            "id": "act",
            "template": "templates/open/adm_act.docx",
            "output": os.path.join(OUTPUT_DIR, "adm_act_rendered.docx"),
            "default_copies": 1,
            "context": {
                "address": full_address
            }
        },
        {
            "id": "garant",
            "template": "templates/open/adm_garant.docx",
            "output": os.path.join(OUTPUT_DIR, "adm_garant_rendered.docx"),
            "default_copies": 1,
            "context": {
                "address": full_address,
                "shurfs": build_shurfs(shurfs_list, mode=garant_shurf_mode),
                "recovery": get_recovery_term(data),
                "card": card_str
            }
        }
    ]

    files_to_print = []
    for doc_info in documents_config:
        doc_id = doc_info["id"]

        # Проверка типа печати для установки количества копий
        if selected_docs is not None:
            if doc_id not in selected_docs:
                continue
            copies = selected_docs[doc_id]
        else:
            copies = doc_info["default_copies"]

        tpl_path = doc_info["template"]
        out_path = doc_info["output"]
        
        if not os.path.exists(tpl_path):
            continue

        tpl = DocxTemplate(tpl_path)
        tpl.render(doc_info["context"])
        tpl.save(out_path)
        files_to_print.append((out_path, copies))

    # Пакетная печать
    if files_to_print:
        print_batch_docx(files_to_print)