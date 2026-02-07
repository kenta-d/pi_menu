import json
from pathlib import Path


def get_mac_apps(apps_dir: Path):
    apps = []
    for app in apps_dir.iterdir():
        if app.name.endswith(".app"):
            app_name = app.name.replace(".app", "")
            app_path = f"open {app}"
            apps.append(
                {
                    "name": app_name,
                    "command": app_path,
                    "icon": "",
                    "favorite": False,  # デフォルトでは favorite ではない
                }
            )
    return apps


def _default_config_path() -> Path:
    return Path.home() / "Library" / "Application Support" / "PiMenu" / "config.json"


def generate_config(config_path: Path, apps_dir: Path | None = None):
    if apps_dir is None:
        apps_dir = Path("/Applications")

    if config_path.exists():
        print(f"{config_path} は既に存在します。")
        return

    config_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"apps": get_mac_apps(apps_dir)}

    # いくつかのアプリを「お気に入り」に設定
    if len(data["apps"]) >= 3:
        data["apps"][0]["favorite"] = True
        data["apps"][1]["favorite"] = True

    with open(config_path, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"{config_path} を生成しました！")


if __name__ == "__main__":
    generate_config(_default_config_path())
