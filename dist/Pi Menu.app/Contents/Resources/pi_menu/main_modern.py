import json
import math
import os
import subprocess
import sys
import shlex

from PyQt6.QtCore import QSize, Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty
from PyQt6.QtGui import QIcon, QPainter, QPen, QBrush, QRadialGradient, QColor, QFont
from PyQt6.QtWidgets import (QApplication, QPushButton, QVBoxLayout, QWidget, 
                           QDialog, QListWidget, QListWidgetItem, QCheckBox, QGraphicsDropShadowEffect)

CONFIG_FILE = "./config.json"

class ModernButton(QPushButton):
    """モダンなアニメーション付きボタン"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._scale = 1.0
        self.setFixedSize(80, 80)
        self.setup_animation()
        self.setup_shadow()
        
    def setup_animation(self):
        """ホバーアニメーションの設定"""
        self.animation = QPropertyAnimation(self, b"scale")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def setup_shadow(self):
        """ドロップシャドウ効果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)
        
    @pyqtProperty(float)
    def scale(self):
        return self._scale
        
    @scale.setter
    def scale(self, value):
        self._scale = value
        self.setFixedSize(int(80 * value), int(80 * value))
        
    def enterEvent(self, event):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(1.1)
        self.animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animation.setStartValue(1.1)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().leaveEvent(event)

class ModernFavoriteSettings(QDialog):
    """モダンな設定ダイアログ"""
    
    def __init__(self, config_file, parent=None):
        super().__init__(parent)
        self.config_file = config_file
        self.setWindowTitle("アプリ設定")
        self.setFixedSize(480, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()
        self.apply_modern_style()
        self.load_apps()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # タイトル
        title = QPushButton("⚙️ アプリケーション設定")
        title.setEnabled(False)
        title.setFixedHeight(60)
        layout.addWidget(title)
        
        # アプリリスト
        self.app_list = QListWidget()
        self.app_list.setFixedHeight(400)
        layout.addWidget(self.app_list)
        
        # 保存ボタン
        save_button = QPushButton("💾 保存")
        save_button.setFixedHeight(50)
        save_button.clicked.connect(self.save_favorites)
        layout.addWidget(save_button)
        
        # 閉じるボタン
        close_button = QPushButton("✕ 閉じる")
        close_button.setFixedHeight(40)
        close_button.clicked.connect(self.reject)
        layout.addWidget(close_button)

    def apply_modern_style(self):
        self.setStyleSheet("""
            QDialog {
                background: rgba(20, 25, 35, 0.95);
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.15);
            }
            QPushButton:disabled {
                background: transparent;
                border: none;
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
            }
            QListWidget {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: #ffffff;
                font-size: 13px;
                outline: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid rgba(255, 255, 255, 0.4);
                background: transparent;
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #667eea, stop: 1 #764ba2);
                border-color: #667eea;
            }
        """)

    def load_apps(self):
        if not os.path.exists(self.config_file):
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        for app in data["apps"]:
            item = QListWidgetItem(f"📱 {app['name']}")
            checkbox = QCheckBox()
            checkbox.setChecked(app.get("favorite", False))
            checkbox.stateChanged.connect(lambda state, app=app: self.toggle_favorite(app, state))
            self.app_list.addItem(item)
            self.app_list.setItemWidget(item, checkbox)

    def toggle_favorite(self, app, state):
        app["favorite"] = state == 2

    def save_favorites(self):
        if not os.path.exists(self.config_file):
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            checkbox = self.app_list.itemWidget(item)
            app_name = item.text().replace("📱 ", "")
            for app in data["apps"]:
                if app["name"] == app_name:
                    app["favorite"] = checkbox.isChecked()

        with open(self.config_file, "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        self.accept()

class ModernPiMenu(QWidget):
    """モダンなPi Menuメインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.favorite_buttons = []
        self.favorite_apps = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Pi Menu - Modern")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(600, 600)
        
        # フレームレスウィンドウ
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.apply_modern_style()
        self.load_favorites()
        self.create_settings_button()
        self.create_circle_buttons()

    def apply_modern_style(self):
        """モダンなスタイルを適用"""
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                color: #ffffff;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            }
        """)

    def create_settings_button(self):
        """設定ボタンの作成"""
        self.settings_button = QPushButton("⚙️", self)
        self.settings_button.setFixedSize(50, 50)
        self.settings_button.move(20, 20)
        self.settings_button.clicked.connect(self.open_favorite_settings)
        
        self.settings_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.15);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 25px;
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.5);
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.2);
            }
        """)
        
        # ドロップシャドウ
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.settings_button.setGraphicsEffect(shadow)

    def open_favorite_settings(self):
        settings = ModernFavoriteSettings(CONFIG_FILE, self)
        if settings.exec():
            self.load_favorites()
            self.create_circle_buttons()

    def load_favorites(self):
        """お気に入りアプリを読み込み"""
        self.favorite_apps = []
        
        if not os.path.exists(CONFIG_FILE):
            return

        with open(CONFIG_FILE, "r") as file:
            data = json.load(file)

        self.favorite_apps = [app for app in data["apps"] if app.get("favorite", False)]

    def create_circle_buttons(self):
        """円形レイアウトでボタンを配置"""
        for btn in self.favorite_buttons:
            btn.deleteLater()
        self.favorite_buttons.clear()

        if not self.favorite_apps:
            return

        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(self.width(), self.height()) // 3
        
        for i, app in enumerate(self.favorite_apps):
            angle = (2 * math.pi * i / len(self.favorite_apps)) - (math.pi / 2)
            x = center_x + (radius * math.cos(angle)) - 40
            y = center_y + (radius * math.sin(angle)) - 40

            btn = ModernButton(app["name"][:8], self)
            btn.app_command = app["command"]
            btn.clicked.connect(self.handle_button_click)
            btn.move(int(x), int(y))
            
            # モダンなボタンスタイル
            btn.setStyleSheet("""
                ModernButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(102, 126, 234, 0.8),
                        stop: 1 rgba(118, 75, 162, 0.8));
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    border-radius: 40px;
                    color: white;
                    font-size: 10px;
                    font-weight: 600;
                    text-align: center;
                }
                ModernButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(102, 126, 234, 1.0),
                        stop: 1 rgba(118, 75, 162, 1.0));
                    border: 2px solid rgba(255, 255, 255, 0.4);
                }
                ModernButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(82, 106, 214, 0.9),
                        stop: 1 rgba(98, 55, 142, 0.9));
                }
            """)

            btn.show()
            self.favorite_buttons.append(btn)

    def paintEvent(self, event):
        """モダンな背景描画"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景グラデーション
        gradient = QRadialGradient(self.width()/2, self.height()/2, self.width()/2)
        gradient.setColorAt(0.0, QColor(30, 40, 60, 220))
        gradient.setColorAt(0.7, QColor(20, 25, 35, 240))
        gradient.setColorAt(1.0, QColor(10, 15, 25, 250))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        
        # 中央の装飾的な円
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 外側の薄い円
        painter.setPen(QPen(QColor(255, 255, 255, 30), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        outer_radius = min(self.width(), self.height()) // 2.5
        painter.drawEllipse(int(center_x - outer_radius), int(center_y - outer_radius),
                          int(outer_radius * 2), int(outer_radius * 2))
        
        # 内側のアクセント円
        painter.setPen(QPen(QColor(102, 126, 234, 80), 1))
        inner_radius = min(self.width(), self.height()) // 4
        painter.drawEllipse(int(center_x - inner_radius), int(center_y - inner_radius),
                          int(inner_radius * 2), int(inner_radius * 2))
        
        # 中央のドット
        painter.setBrush(QBrush(QColor(102, 126, 234, 150)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(int(center_x - 4), int(center_y - 4), 8, 8)

    def handle_button_click(self):
        button = self.sender()
        if hasattr(button, "app_command") and button.app_command:
            self.launch_app(button.app_command)

    def launch_app(self, command):
        try:
            if command.startswith("open "):
                command = f'open {shlex.quote(command[5:])}'
                subprocess.run(command, shell=True, check=True)
            else:
                subprocess.run(command.split(), check=True)
        except subprocess.CalledProcessError as e:
            print(f"アプリの起動に失敗しました: {e}")
        except Exception as e:
            print(f"アプリの起動に失敗しました: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 設定ボタンの位置を調整
        self.settings_button.move(20, 20)
        # アプリボタンを再配置
        self.create_circle_buttons()

    def mousePressEvent(self, event):
        """ウィンドウドラッグ機能"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """ウィンドウドラッグ機能"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ModernPiMenu()
    ex.show()
    sys.exit(app.exec())