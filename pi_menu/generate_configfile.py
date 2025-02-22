import json
import os

CONFIG_FILE = "config.json"
MAC_APPS_DIR = "/Applications/"


def get_mac_apps():
    apps = []
    for app in os.listdir(MAC_APPS_DIR):
        if app.endswith(".app"):
            app_name = app.replace(".app", "")
            app_path = f"open {MAC_APPS_DIR}{app}"
            apps.append(
                {
                    "name": app_name,
                    "command": app_path,
                    "icon": "",
                    "favorite": False,  # デフォルトでは favorite ではない
                }
            )
    return apps


def generate_config():
    if os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} は既に存在します。")
        return

    data = {"apps": get_mac_apps()}

    # いくつかのアプリを「お気に入り」に設定
    if len(data["apps"]) >= 3:
        data["apps"][0]["favorite"] = True
        data["apps"][1]["favorite"] = True

    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"{CONFIG_FILE} を生成しました！")
