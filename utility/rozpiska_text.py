import os
import json

# Пусть к файлу app_config.json
CONFIG_PATH = os.path.join("data", "app_config.json")

# Метод считывания текста из файла app_config.json
def get_rozpiska_text() -> str:
    """Считывание общего текста расписки из app_config.json"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("rozpiska_text", "")
        except Exception as e:
            print(f"❌ Ошибка чтения config.json: {e}")
    return ""