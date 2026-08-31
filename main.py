import sys
from PyQt6.QtWidgets import QApplication
from gui.gui_main_window import MainWindow
from gui.gui_dialog_window import logo_warning_window
from updater import check_for_updates

def main():
    app = QApplication(sys.argv)

    # 1. Запускаем цепочку: Логотип (3 сек) -> Предупреждение о Word
    logo_warning_window("gui/graph/logo.png")

    # 2. Открываем главное окно программы
    window = MainWindow()
    window.show()

    # 3. Проверяем обновления
    check_for_updates(window)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()