import json
import urllib.request
import webbrowser
from config import APP_VERSION, GITHUB_REPO
from gui.gui_dialog_window import show_update_dialog

def check_for_updates(parent_window=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get("tag_name")
                download_url = data.get("html_url")
                
                # Сравниваем версии
                if latest_version and latest_version != APP_VERSION:
                    if show_update_dialog(latest_version, APP_VERSION, parent_window):
                        webbrowser.open(download_url)
    except Exception as e:
        # Тихий пропуск при отсутствии интернета или ошибке запроса
        print(f"Не удалось проверить обновления: {e}")