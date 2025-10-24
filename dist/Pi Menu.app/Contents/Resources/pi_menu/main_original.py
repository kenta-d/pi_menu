import json
import math
import os
import subprocess
import sys

import shlex

from PyQt6.QtCore import QSize
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
        
        # ダークテーマのスタイルシートを適用
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #1a1a2e, stop: 1 #16213e);
                color: #ffffff;
                font-family: "Segoe UI", "San Francisco", "Helvetica Neue", Arial, sans-serif;
            }
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, 
                    stop: 0 #1a1a2e, stop: 1 #16213e);
                color: #ffffff;
            }
            QListWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #ffffff;
                alternate-background-color: rgba(255, 255, 255, 0.02);
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border-color: #4a9eff;
            }
            QCheckBox::indicator:checked::after {
                content: "✓";
                color: white;
                font-weight: bold;
            }
        """)

        self.favorite_buttons = []
        self.favorite_apps = []
        self.load_favorites()

        self.create_circle_buttons()

        # ⭐ **「お気に入り設定」ボタンを追加**
        settings_button = QPushButton("⭐ お気に入り設定", self)
        settings_button.setGeometry(10, 10, 180, 45)
        settings_button.clicked.connect(self.open_favorite_settings)
        settings_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #4a9eff, stop: 1 #0066cc);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #5aa8ff, stop: 1 #1a75d9);
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #3a8eef, stop: 1 #0056b3);
            }
        """)
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
        radius = min(self.width(), self.height()) // 2.5 - 80  # メインベゼルに合わせて調整
        button_size = 60

        for i, app in enumerate(self.favorite_apps):
            angle = (2 * math.pi * i / len(self.favorite_apps)) - (math.pi / 2)
            x = center_x + (radius * math.cos(angle)) - (button_size // 2)
            y = center_y + (radius * math.sin(angle)) - (button_size // 2)

            print(f"{app['name']} の位置: x={x}, y={y}")

            btn = QPushButton(app["name"], self)
            btn.setFixedSize(button_size, button_size)
            btn.setIconSize(QSize(30, 30))
            btn.app_command = app["command"]
            btn.clicked.connect(self.handle_button_click)

            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 30px;
                    background: qradialgradient(cx: 0.3, cy: 0.3, radius: 1.2,
                        stop: 0 rgba(100, 100, 120, 0.8),
                        stop: 0.7 rgba(60, 60, 80, 0.9),
                        stop: 1 rgba(30, 30, 50, 1));
                    border: 2px solid rgba(0, 150, 255, 0.5);
                    color: #ffffff;
                    font-size: 8px;
                    font-weight: 600;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qradialgradient(cx: 0.3, cy: 0.3, radius: 1.2,
                        stop: 0 rgba(120, 120, 140, 0.9),
                        stop: 0.7 rgba(80, 80, 100, 1),
                        stop: 1 rgba(40, 40, 60, 1));
                    border: 2px solid rgba(0, 200, 255, 0.8);
                    color: rgba(0, 200, 255, 1);
                }
                QPushButton:pressed {
                    background: qradialgradient(cx: 0.7, cy: 0.7, radius: 1.2,
                        stop: 0 rgba(40, 40, 60, 1),
                        stop: 0.7 rgba(20, 20, 40, 1),
                        stop: 1 rgba(10, 10, 30, 1));
                    border: 2px solid rgba(0, 100, 180, 1);
                }
            """)
            btn.setIcon(QIcon(app.get("icon", "")))
            btn.setIconSize(QSize(40, 40))
            btn.move(int(x), int(y))
            btn.setParent(self)
            btn.show()

            self.favorite_buttons.append(btn)


    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 円の中心と半径
        center_x = self.width() // 2
        center_y = self.height() // 2
        main_radius = min(self.width(), self.height()) // 2.5
        
        from PyQt6.QtCore import Qt, QRect
        from PyQt6.QtGui import QPen, QBrush, QRadialGradient, QConicalGradient, QColor
        
        # メインの円形ベゼル（3D効果）
        for i in range(8):
            offset = i * 2
            alpha = 255 - (i * 25)
            pen = QPen(QColor(100, 100, 120, alpha))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(int(center_x - main_radius - offset), int(center_y - main_radius - offset),
                              int((main_radius + offset) * 2), int((main_radius + offset) * 2))
        
        # メインの金属ベゼル
        bezel_gradient = QConicalGradient(center_x, center_y, 0)
        bezel_gradient.setColorAt(0.0, QColor(80, 80, 100))
        bezel_gradient.setColorAt(0.25, QColor(120, 120, 140))
        bezel_gradient.setColorAt(0.5, QColor(60, 60, 80))
        bezel_gradient.setColorAt(0.75, QColor(100, 100, 120))
        bezel_gradient.setColorAt(1.0, QColor(80, 80, 100))
        
        painter.setBrush(QBrush(bezel_gradient))
        painter.setPen(QPen(QColor(40, 40, 60), 3))
        painter.drawEllipse(int(center_x - main_radius), int(center_y - main_radius),
                          int(main_radius * 2), int(main_radius * 2))
        
        # 青いネオンリング
        neon_pen = QPen(QColor(0, 200, 255, 200))
        neon_pen.setWidth(4)
        painter.setPen(neon_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(int(center_x - main_radius + 10), int(center_y - main_radius + 10),
                          int((main_radius - 10) * 2), int((main_radius - 10) * 2))
        
        # 内側のネオンリング
        inner_neon_pen = QPen(QColor(0, 150, 255, 150))
        inner_neon_pen.setWidth(2)
        painter.setPen(inner_neon_pen)
        inner_radius = main_radius - 80
        painter.drawEllipse(int(center_x - inner_radius), int(center_y - inner_radius),
                          int(inner_radius * 2), int(inner_radius * 2))
        
        # 中央の電源ボタン
        center_button_radius = 50
        
        # 電源ボタンの3D効果
        power_gradient = QRadialGradient(center_x, center_y - 5, center_button_radius)
        power_gradient.setColorAt(0.0, QColor(60, 60, 80))
        power_gradient.setColorAt(0.7, QColor(40, 40, 60))
        power_gradient.setColorAt(1.0, QColor(20, 20, 40))
        
        painter.setBrush(QBrush(power_gradient))
        painter.setPen(QPen(QColor(0, 150, 255), 2))
        painter.drawEllipse(int(center_x - center_button_radius), int(center_y - center_button_radius),
                          int(center_button_radius * 2), int(center_button_radius * 2))
        
        # 電源アイコン描画
        power_pen = QPen(QColor(0, 200, 255), 4)
        power_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(power_pen)
        
        # 電源アイコンの円弧
        power_arc_rect = QRect(center_x - 20, center_y - 20, 40, 40)
        painter.drawArc(power_arc_rect, 30 * 16, 300 * 16)  # 300度の円弧
        
        # 電源アイコンの縦線
        painter.drawLine(center_x, center_y - 20, center_x, center_y - 5)
        
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
