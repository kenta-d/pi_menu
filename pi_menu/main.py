import json
import math
import os
import subprocess
import sys

import shlex

from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter


CONFIG_FILE = "./config.json"

import json
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QListWidgetItem, QCheckBox


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
        if not os.path.exists(self.config_file):
            print(f"⚠️ 設定ファイルが見つかりません: {self.config_file}")
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        for app in data["apps"]:
            item = QListWidgetItem(app["name"])
            checkbox = QCheckBox()
            checkbox.setChecked(app.get("favorite", False))
            checkbox.stateChanged.connect(lambda state, app=app: self.toggle_favorite(app, state))
            self.app_list.addItem(item)
            self.app_list.setItemWidget(item, checkbox)

    def toggle_favorite(self, app, state):
        """お気に入りフラグを変更"""
        app["favorite"] = state == 2  # Qt.Checked = 2

    def save_favorites(self):
        """config.json を更新"""
        if not os.path.exists(self.config_file):
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            checkbox = self.app_list.itemWidget(item)
            for app in data["apps"]:
                if app["name"] == item.text():
                    app["favorite"] = checkbox.isChecked()

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
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pi Menu")
        self.setGeometry(100, 100, 800, 600)

        self.favorite_buttons = []
        self.favorite_apps = []
        self.load_favorites()

        self.create_circle_buttons()

        # ⭐ **「お気に入り設定」ボタンを追加**
        settings_button = QPushButton("⭐ お気に入り設定", self)
        settings_button.setGeometry(10, 10, 150, 40)
        settings_button.clicked.connect(self.open_favorite_settings)
        settings_button.setParent(self)
        settings_button.show()

    def open_favorite_settings(self):
        """お気に入りアプリの設定ウィンドウを開く"""
        settings = FavoriteSettings(CONFIG_FILE, self)
        if settings.exec():  # ユーザーが「保存」した場合のみ
            self.load_favorites()
            self.create_circle_buttons()  # UI を更新
    

    def load_favorites(self):
        """お気に入りアプリを `config.json` から取得"""
        self.favorite_apps = []
        
        if not os.path.exists(CONFIG_FILE):
            print(f"⚠️ 設定ファイルが見つかりません: {CONFIG_FILE}")
            return

        with open(CONFIG_FILE, "r") as file:
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

            btn = QPushButton(app["name"], self)
            btn.setFixedSize(button_size, button_size)
            btn.app_command = app["command"]
            btn.clicked.connect(self.handle_button_click)

            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 40px;
                    background-color: #f0f0f0;
                    border: 2px solid #d0d0d0;
                    font-size: 10px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border: 2px solid #c0c0c0;
                }
            """)
            btn.setIcon(QIcon(app.get("icon", "")))
            btn.setIconSize(QSize(40, 40))
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
