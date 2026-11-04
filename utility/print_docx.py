import win32com.client
import os
from PyQt6.QtWidgets import QApplication
from gui.gui_dialog_window import PrintProgressDialog

def print_batch_docx(files_info: list, parent=None):
    total_steps = sum(copies for _, copies, _ in files_info)
    if total_steps == 0:
        return

    progress_dialog = PrintProgressDialog(total_steps, parent)
    progress_dialog.show()
    QApplication.processEvents()

    word = None
    current_step = 0

    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0

        for file_path, copies, doc_title in files_info:
            abs_path = os.path.abspath(file_path)
            if not os.path.exists(abs_path):
                continue

            doc = word.Documents.Open(
                FileName=abs_path,
                ConfirmConversions=False,
                ReadOnly=True,
                AddToRecentFiles=False
            )
            
            for copy_idx in range(copies):
                if progress_dialog.was_canceled():
                    break

                current_step += 1
                
                status_text = (
                    f"Печать документа:\n"
                    f"«{doc_title}»\n"
                    f"(копия {copy_idx + 1} из {copies})"
                )
                progress_dialog.update_progress(current_step, status_text)
                
                doc.PrintOut(Background=False)

            doc.Close(False)
            
            if progress_dialog.was_canceled():
                break

    except Exception as e:
        print(f"❌ Ошибка пакетной печати MS Word: {e}")
    finally:
        if word:
            word.Quit()
            del word
        progress_dialog.close()