import json
import math
import plistlib
import shlex
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QFileInfo, QSize, Qt
from PyQt6.QtGui import QIcon, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileIconProvider,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def _config_file_path() -> Path:
    # Resolve to a user-writable location, even inside a signed app bundle.
    return Path.home() / "Library" / "Application Support" / "PiMenu" / "config.json"

def _theme_file_path() -> Path:
    return Path.home() / "Library" / "Application Support" / "PiMenu" / "theme.json"


def _load_theme() -> dict:
    default_theme = {
        "background_gradient": ["#F8FAFF", "#E3EAF6"],
        "text_color": "#1B1F2A",
        "settings_button": {
            "bg": "rgba(255, 255, 255, 0.65)",
            "bg_hover": "rgba(255, 255, 255, 0.85)",
            "border": "rgba(255, 255, 255, 0.9)",
            "text": "#1B1F2A",
            "radius": 10,
        },
        "button": {
            "bg": "rgba(255, 255, 255, 0.55)",
            "bg_hover": "rgba(255, 255, 255, 0.8)",
            "border": "rgba(255, 255, 255, 0.9)",
            "border_hover": "rgba(255, 255, 255, 1)",
            "text": "#1B1F2A",
            "font_size": 10,
            "icon_size": 48,
        },
    }

    theme_path = _theme_file_path()
    if not theme_path.exists():
        return default_theme

    try:
        with open(theme_path, "r") as f:
            user_theme = json.load(f)
    except Exception:
        return default_theme

    # Shallow merge; nested dicts override defaults
    merged = {**default_theme, **user_theme}
    for key in ("settings_button", "button"):
        if key in user_theme and isinstance(user_theme[key], dict):
            merged[key] = {**default_theme[key], **user_theme[key]}
    return merged
def _app_bundle_from_command(command: str) -> Path | None:
    if not command.startswith("open "):
        return None
    # The config uses: "open /Applications/App Name.app" (not quoted).
    raw_path = command[5:].strip()
    if (raw_path.startswith('"') and raw_path.endswith('"')) or (
        raw_path.startswith("'") and raw_path.endswith("'")
    ):
        raw_path = raw_path[1:-1]
    bundle = Path(raw_path)
    if bundle.suffix != ".app":
        return None
    return bundle


def _icon_path_for_app(command: str) -> Path | None:
    bundle = _app_bundle_from_command(command)
    if bundle is None:
        return None
    info_plist = bundle / "Contents" / "Info.plist"
    resources_dir = bundle / "Contents" / "Resources"
    if not info_plist.exists():
        return None
    try:
        with open(info_plist, "rb") as f:
            plist = plistlib.load(f)
    except Exception:
        return None
    icon_name = plist.get("CFBundleIconFile")
    if icon_name:
        icon_path = resources_dir / icon_name
        if icon_path.suffix == "":
            icon_path = icon_path.with_suffix(".icns")
        if icon_path.exists():
            return icon_path
    # Fallback: first .icns in Resources
    for candidate in resources_dir.glob("*.icns"):
        return candidate
    return None


def _qt_icon_for_app(command: str) -> QIcon | None:
    icon_path = _icon_path_for_app(command)
    if icon_path:
        icon = QIcon(str(icon_path))
        if not icon.isNull():
            return icon

    bundle = _app_bundle_from_command(command)
    if bundle:
        provider = QFileIconProvider()
        icon = provider.icon(QFileInfo(str(bundle)))
        if not icon.isNull():
            return icon
    return None

class FavoriteSettings(QDialog):
    def __init__(self, config_file, parent=None):
        super().__init__(parent)
        self.config_file = config_file
        self.setWindowTitle("お気に入りアプリ設定")
        self.setGeometry(200, 200, 400, 500)

        layout = QVBoxLayout()
        self.app_list = QListWidget()
        self.load_apps()
        layout.addWidget(self.app_list)

        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_favorites)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def load_apps(self):
        """config.json からアプリを読み込み、リストに表示"""
        if not self.config_file.exists():
            print(f"⚠️ 設定ファイルが見つかりません: {self.config_file}")
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        for app in data["apps"]:
            item = QListWidgetItem(app["name"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if app.get("favorite", False) else Qt.CheckState.Unchecked)
            self.app_list.addItem(item)

    def save_favorites(self):
        """config.json を更新"""
        if not self.config_file.exists():
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            for app in data["apps"]:
                if app["name"] == item.text():
                    app["favorite"] = item.checkState() == Qt.CheckState.Checked

        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("✅ お気に入りアプリを保存しました")
        self.accept()

class PiMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)  # Define main_layout here
        self.favorite_buttons = []
        self.favorite_apps = []
        self.config_file = _config_file_path()
        self.theme = _load_theme()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pi Menu")
        self.setGeometry(100, 100, 800, 600)
        # High-contrast base theme
        bg0, bg1 = self.theme["background_gradient"]
        text_color = self.theme["text_color"]
        self.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 {bg0},
                    stop: 1 {bg1}
                );
                color: {text_color};
            }}
            """
        )

        self.favorite_buttons = []
        self.favorite_apps = []
        self.load_favorites()

        self.create_circle_buttons()

        # ⭐ **「お気に入り設定」ボタンを追加**
        settings_button = QPushButton("⭐ お気に入り設定", self)
        settings_button.setGeometry(10, 10, 150, 40)
        settings_button.clicked.connect(self.open_favorite_settings)
        sb = self.theme["settings_button"]
        settings_button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {sb['bg']};
                color: {sb['text']};
                border: 1px solid {sb['border']};
                border-radius: {sb['radius']}px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {sb['bg_hover']};
            }}
            """
        )
        settings_button.setParent(self)
        settings_button.show()

    def open_favorite_settings(self):
        """お気に入りアプリの設定ウィンドウを開く"""
        settings = FavoriteSettings(self.config_file, self)
        if settings.exec():  # ユーザーが「保存」した場合のみ
            self.load_favorites()
            self.create_circle_buttons()  # UI を更新
    

    def load_favorites(self):
        """お気に入りアプリを `config.json` から取得"""
        self.favorite_apps = []
        
        if not self.config_file.exists():
            print(f"⚠️ 設定ファイルが見つかりません: {self.config_file}")
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        self.favorite_apps = [app for app in data["apps"] if app.get("favorite", False)]

        print(f"✅ お気に入りアプリを更新: {self.favorite_apps}")
    
    def create_circle_buttons(self):
        """お気に入りアプリのボタンを円形レイアウトで作成"""
        # 既存のボタンを削除
        for btn in self.favorite_buttons:
            btn.deleteLater()
        self.favorite_buttons.clear()

        if not self.favorite_apps:
            print("⚠️ お気に入りアプリがありません")
            return

        # 円形レイアウトの中心と半径を計算
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 3
        button_size = 80

        for i, app in enumerate(self.favorite_apps):
            angle = (2 * math.pi * i / len(self.favorite_apps)) - (math.pi / 2)
            x = center_x + (radius * math.cos(angle)) - (button_size // 2)
            y = center_y + (radius * math.sin(angle)) - (button_size // 2)

            print(f"{app['name']} の位置: x={x}, y={y}")

            btn = QToolButton(self)
            btn.setText(app["name"])
            btn.setFixedSize(button_size, button_size)
            btn.app_command = app["command"]
            btn.clicked.connect(self.handle_button_click)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

            bt = self.theme["button"]
            btn.setStyleSheet(
                f"""
                QToolButton {{
                    border-radius: 40px;
                    background-color: {bt['bg']};
                    color: {bt['text']};
                    border: 1px solid {bt['border']};
                    font-size: {bt['font_size']}px;
                    text-align: center;
                }}
                QToolButton:hover {{
                    background-color: {bt['bg_hover']};
                    border: 1px solid {bt['border_hover']};
                }}
                """
            )
            icon = _qt_icon_for_app(app.get("command", ""))
            if icon:
                btn.setIcon(icon)
            btn.setIconSize(QSize(int(bt["icon_size"]), int(bt["icon_size"])))
            btn.move(int(x), int(y))
            btn.setParent(self)
            btn.show()

            self.favorite_buttons.append(btn)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 円の中心と半径
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 3  # 半径の設定

        # ガイドライン用の円を描画（デバッグ用）
        painter.setPen(Qt.PenStyle.DashLine)
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2))

        painter.end()

    def handle_button_click(self):
        # 送信者のボタンからコマンドを取得
        button = self.sender()
        if not button:
            print("⚠️ handle_button_click: クリックされたボタンが取得できませんでした")
            return

        print(
            f"クリックされたボタン: {button.text()}"
        )  # クリックされたボタンのテキストを表示

        if hasattr(button, "app_command") and button.app_command:
            print(f"実行するコマンド: {button.app_command}")  # 実行するコマンドを表示
            self.launch_app(button.app_command)
        else:
            print("⚠️ ボタンにコマンドが設定されていません")


    def launch_app(self, command):
        try:
            print(f"実行するコマンド: {command}")  # デバッグ出力

            if command.startswith("open "):
                # スペースを含むパスを適切に処理
                command = f'open {shlex.quote(command[5:])}'
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            else:
                result = subprocess.run(command.split(), check=True, capture_output=True, text=True)

            print(f"コマンド実行結果: {result.stdout}")  # 標準出力を表示
            print(f"エラー出力: {result.stderr}")  # 標準エラーを表示

        except subprocess.CalledProcessError as e:
            print(f"アプリの起動に失敗しました: {e}\nコマンド: {command}")
        except Exception as e:
            print(f"アプリの起動に失敗しました: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.create_circle_buttons()  # ウィンドウサイズ変更時にボタンを再配置


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PiMenu()
    ex.show()
    sys.exit(app.exec())
