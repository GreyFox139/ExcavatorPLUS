import win32com.client
import os

# Метод обращения в MS Word для пакетной печати
def print_batch_docx(files_info: list):
    
    word = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0

        for file_path, copies in files_info:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                continue

            doc = word.Documents.Open(
                FileName=abs_path,
                ConfirmConversions=False,
                ReadOnly=True,
                AddToRecentFiles=False
            )
            doc.PrintOut(Background=False, Copies=copies)
            doc.Close(False)
    except Exception as e:
        print(f"❌ Ошибка пакетной печати MS Word: {e}")
    finally:
        if word:
            word.Quit()
            del word