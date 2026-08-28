import os
from PyQt6.QtWidgets import QCompleter, QLineEdit
from PyQt6.QtCore import Qt, QStringListModel

from config import F_Sml, BASE_DIR

# Список "мусорных" слов
JUNK_WORDS = [
    "вул.", "вул ", "просп.", "пров.", "пров ", 
    "в-д", "пр-д", "з-д", "наб.", "шосе", "м-н", "у-з"
]

def load_streets_from_file() -> list:
    # Загрузка списка улиц из data/streets.txt
    path = os.path.join(BASE_DIR, "data", "streets.txt")
    if not os.path.exists(path):
        return []
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

# Кэш загруженных улиц при первом импорте модуля
STREETS_LIST = load_streets_from_file()

# Класс комплитера улиц
class StreetCompleter(QCompleter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.raw_streets = STREETS_LIST
        self.junk_words = JUNK_WORDS
        self.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.string_model = QStringListModel(self.raw_streets)
        self.setModel(self.string_model)

        popup_view = self.popup()
        popup_view.setFont(F_Sml)

    def splitPath(self, path):
        clean_path = path.lower()
        for junk in self.junk_words:
            clean_path = clean_path.replace(junk.lower(), "")
        clean_path = clean_path.strip()
        
        filtered = [
            st for st in self.raw_streets 
            if clean_path in self.get_clean_street(st)
        ]
        self.string_model.setStringList(filtered)
        return [path]

    def get_clean_street(self, street_name):
        clean = street_name.lower()
        for junk in self.junk_words:
            clean = clean.replace(junk.lower(), "")
        return clean.strip()

# Единый хелпер для передачи улиц и "мусорных" слов
def setup_street_completer(line_edit: QLineEdit) -> StreetCompleter:
    completer = StreetCompleter(line_edit)
    line_edit.setCompleter(completer)
    return completer