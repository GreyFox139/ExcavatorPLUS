import os
from config import BASE_DIR

# Метод обработки логов
def load_logs(filepath: str = None) -> str:
    # Загрузка текста логов из файла data/logs.txt
    if filepath is None:
        filepath = os.path.join(BASE_DIR, "data", "logs.txt")

    if not os.path.exists(filepath):
        return "Файл логов data/logs.txt не найден."

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Ошибка при чтении файла логов: {e}"