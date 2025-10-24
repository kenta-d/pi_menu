#!/usr/bin/env python3
"""
Pi Menu - セーフモード版
エラーハンドリングを強化した実行可能版
"""

import json
import math
import os
import subprocess
import sys
import shlex

# PyQt6のインポートを安全に実行
try:
    from PyQt6.QtCore import QSize, Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, QTimer
    from PyQt6.QtGui import QIcon, QPainter, QPen, QBrush, QRadialGradient, QColor, QFont
    from PyQt6.QtWidgets import (QApplication, QPushButton, QVBoxLayout, QWidget, 
                               QDialog, QListWidget, QListWidgetItem, QCheckBox, QGraphicsDropShadowEffect, QToolTip)
    PYQT6_AVAILABLE = True
except ImportError as e:
    print(f"❌ PyQt6のインポートに失敗しました: {e}")
    print("📥 PyQt6をインストールしてください:")
    print("   brew install pyqt@6")
    print("   または pipx install PyQt6")
    PYQT6_AVAILABLE = False
    sys.exit(1)

# アイコンシステムのインポート
try:
    try:
        from .icon_system import IconSystem
    except ImportError:
        # 直接実行時の絶対インポート
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        from icon_system import IconSystem
    ICON_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"❌ アイコンシステムのインポートに失敗しました: {e}")
    print("フォールバックモードで実行します...")
    ICON_SYSTEM_AVAILABLE = False
    
    # フォールバック用のダミーアイコンシステム
    class IconSystem:
        @staticmethod
        def get_app_info(app_name):
            return {
                'icon': '📱',
                'display_name': app_name[:8],
                'category': 'default',
                'colors': ('rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)'),
                'full_name': app_name
            }

# 設定ファイルパスを動的に設定
def get_config_path():
    if __name__ == "__main__":
        # 直接実行時: スクリプトの親ディレクトリのconfig.jsonを参照
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    else:
        # モジュールとして実行時
        return "./config.json"

CONFIG_FILE = get_config_path()

class SafeModernButton(QPushButton):
    """エラーハンドリング強化版モダンボタン"""
    
    def __init__(self, app_info, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self._scale = 1.0
        self.setFixedSize(90, 90)
        
        try:
            self.setup_content()
            self.setup_animation()
            self.setup_shadow()
            self.setup_tooltip()
        except Exception as e:
            print(f"⚠️ ボタン初期化エラー: {e}")
            self.setText(self.app_info.get('display_name', 'App'))
        
    def setup_content(self):
        """ボタンの内容を設定"""
        icon = self.app_info.get('icon', '📱')
        display_name = self.app_info.get('display_name', 'App')
        self.setText(f"{icon}\n{display_name}")
        
    def setup_animation(self):
        """ホバーアニメーションの設定"""
        try:
            self.animation = QPropertyAnimation(self, b"scale")
            self.animation.setDuration(200)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        except Exception as e:
            print(f"⚠️ アニメーション設定エラー: {e}")
        
    def setup_shadow(self):
        """ドロップシャドウ効果"""
        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 80))
            self.setGraphicsEffect(shadow)
        except Exception as e:
            print(f"⚠️ シャドウ設定エラー: {e}")
        
    def setup_tooltip(self):
        """ツールチップを設定"""
        try:
            self.setToolTip(self.app_info.get('full_name', 'アプリケーション'))
        except Exception as e:
            print(f"⚠️ ツールチップ設定エラー: {e}")
        
    def get_button_style(self):
        """カテゴリに応じたスタイルを生成"""
        try:
            colors = self.app_info.get('colors', ('rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)'))
            normal_color, hover_color = colors
            
            return f"""
                SafeModernButton {{
                    background: {normal_color};
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    border-radius: 45px;
                    color: white;
                    font-size: 12px;
                    font-weight: 600;
                    text-align: center;
                    padding: 8px;
                    line-height: 1.2;
                }}
                SafeModernButton:hover {{
                    background: {hover_color};
                    border: 2px solid rgba(255, 255, 255, 0.4);
                    color: rgba(255, 255, 255, 1.0);
                }}
                SafeModernButton:pressed {{
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 rgba(82, 106, 214, 0.9),
                        stop: 1 rgba(98, 55, 142, 0.9));
                    border: 2px solid rgba(255, 255, 255, 0.6);
                }}
            """
        except Exception as e:
            print(f"⚠️ スタイル生成エラー: {e}")
            return "SafeModernButton { background: blue; color: white; border-radius: 45px; }"
        
    @pyqtProperty(float)
    def scale(self):
        return self._scale
        
    @scale.setter
    def scale(self, value):
        self._scale = value
        try:
            self.setFixedSize(int(90 * value), int(90 * value))
        except Exception as e:
            print(f"⚠️ スケール設定エラー: {e}")
        
    def enterEvent(self, event):
        try:
            if hasattr(self, 'animation'):
                self.animation.setStartValue(1.0)
                self.animation.setEndValue(1.1)
                self.animation.start()
        except Exception as e:
            print(f"⚠️ ホバーエラー: {e}")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        try:
            if hasattr(self, 'animation'):
                self.animation.setStartValue(1.1)
                self.animation.setEndValue(1.0)
                self.animation.start()
        except Exception as e:
            print(f"⚠️ ホバー終了エラー: {e}")
        super().leaveEvent(event)

class SafeFavoriteSettings(QDialog):
    """エラーハンドリング強化版設定ダイアログ"""
    
    def __init__(self, config_file, parent=None):
        super().__init__(parent)
        self.config_file = config_file
        self.setWindowTitle("アプリケーション設定")
        self.setFixedSize(480, 600)
        
        try:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        except Exception as e:
            print(f"⚠️ ウィンドウ設定エラー: {e}")
        
        self.setup_ui()
        self.apply_modern_style()
        self.load_apps()

    def setup_ui(self):
        """UI要素のセットアップ"""
        try:
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
            
        except Exception as e:
            print(f"⚠️ UI設定エラー: {e}")

    def apply_modern_style(self):
        """モダンなスタイルを適用"""
        try:
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
        except Exception as e:
            print(f"⚠️ スタイル適用エラー: {e}")

    def load_apps(self):
        """アプリリストを読み込み"""
        try:
            if not os.path.exists(self.config_file):
                print(f"⚠️ 設定ファイルが見つかりません: {self.config_file}")
                return

            with open(self.config_file, "r", encoding='utf-8') as file:
                data = json.load(file)

            for app in data["apps"]:
                try:
                    app_info = IconSystem.get_app_info(app['name'])
                    icon = app_info['icon']
                    display_name = app_info['display_name']
                    
                    item = QListWidgetItem(f"{icon} {display_name}")
                    # アプリデータを項目に関連付け
                    item.setData(Qt.ItemDataRole.UserRole, app)
                    
                    checkbox = QCheckBox()
                    checkbox.setChecked(app.get("favorite", False))
                    checkbox.stateChanged.connect(lambda state, item=item: self.toggle_favorite(item, state))
                    
                    self.app_list.addItem(item)
                    self.app_list.setItemWidget(item, checkbox)
                    
                except Exception as e:
                    print(f"⚠️ アプリ項目作成エラー ({app.get('name', 'Unknown')}): {e}")
                    
        except Exception as e:
            print(f"⚠️ アプリリスト読み込みエラー: {e}")

    def toggle_favorite(self, item, state):
        """お気に入り状態を切り替え"""
        try:
            app = item.data(Qt.ItemDataRole.UserRole)
            if app:
                app["favorite"] = (state == 2)  # Qt.Checked = 2
                print(f"🔄 {app['name']}: favorite = {app['favorite']}")
        except Exception as e:
            print(f"⚠️ お気に入り切り替えエラー: {e}")

    def save_favorites(self):
        """お気に入り設定を保存"""
        try:
            if not os.path.exists(self.config_file):
                print(f"⚠️ 設定ファイルが見つかりません: {self.config_file}")
                return

            # 現在の設定ファイルを読み込み
            with open(self.config_file, "r", encoding='utf-8') as file:
                data = json.load(file)

            # 各アプリのお気に入り状態を更新
            for i in range(self.app_list.count()):
                try:
                    item = self.app_list.item(i)
                    checkbox = self.app_list.itemWidget(item)
                    app_data = item.data(Qt.ItemDataRole.UserRole)
                    
                    if app_data and checkbox:
                        # 元のデータでアプリを見つけて更新
                        for app in data["apps"]:
                            if app["name"] == app_data["name"]:
                                app["favorite"] = checkbox.isChecked()
                                print(f"💾 保存: {app['name']} = {app['favorite']}")
                                break
                                
                except Exception as e:
                    print(f"⚠️ 個別アプリ保存エラー: {e}")

            # ファイルに書き込み
            with open(self.config_file, "w", encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            print("✅ お気に入り設定を保存しました")
            self.accept()
            
        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")

class SafePiMenu(QWidget):
    """エラーハンドリング強化版Pi Menu"""
    
    def __init__(self):
        super().__init__()
        self.favorite_buttons = []
        self.favorite_apps = []
        
        try:
            self.init_ui()
        except Exception as e:
            print(f"❌ UI初期化エラー: {e}")
            self.show_error_message()

    def show_error_message(self):
        """エラーメッセージを表示"""
        self.setWindowTitle("Pi Menu - エラー")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout(self)
        
        error_label = QPushButton("❌ Pi Menu の初期化中にエラーが発生しました")
        error_label.setEnabled(False)
        layout.addWidget(error_label)
        
        info_label = QPushButton("設定ファイルとPyQt6を確認してください")
        info_label.setEnabled(False)
        layout.addWidget(info_label)

    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("Pi Menu - Modern Safe Edition")
        self.setGeometry(100, 100, 900, 700)
        self.setMinimumSize(600, 600)
        
        try:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        except Exception as e:
            print(f"⚠️ ウィンドウ設定エラー: {e}")
        
        self.apply_modern_style()
        self.load_favorites()
        self.create_settings_button()
        self.create_circle_buttons()

    def apply_modern_style(self):
        """モダンなスタイルを適用"""
        try:
            self.setStyleSheet("""
                QWidget {
                    background: transparent;
                    color: #ffffff;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                }
            """)
        except Exception as e:
            print(f"⚠️ スタイル適用エラー: {e}")

    def create_settings_button(self):
        """設定ボタンの作成"""
        try:
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
                }
            """)
        except Exception as e:
            print(f"⚠️ 設定ボタン作成エラー: {e}")

    def open_favorite_settings(self):
        """お気に入りアプリの設定ウィンドウを開く"""
        try:
            settings = SafeFavoriteSettings(CONFIG_FILE, self)
            if settings.exec():
                self.load_favorites()
                self.create_circle_buttons()
        except Exception as e:
            print(f"⚠️ 設定ダイアログエラー: {e}")

    def load_favorites(self):
        """お気に入りアプリを読み込み"""
        self.favorite_apps = []
        
        try:
            if not os.path.exists(CONFIG_FILE):
                print(f"⚠️ 設定ファイルが見つかりません: {CONFIG_FILE}")
                return

            with open(CONFIG_FILE, "r", encoding='utf-8') as file:
                data = json.load(file)

            self.favorite_apps = [app for app in data["apps"] if app.get("favorite", False)]
            print(f"✅ お気に入りアプリを読み込み: {len(self.favorite_apps)} 件")
            
        except Exception as e:
            print(f"⚠️ お気に入り読み込みエラー: {e}")

    def create_circle_buttons(self):
        """円形レイアウトでボタンを配置"""
        try:
            for btn in self.favorite_buttons:
                btn.deleteLater()
            self.favorite_buttons.clear()

            if not self.favorite_apps:
                print("⚠️ お気に入りアプリがありません")
                return

            center_x = self.width() // 2
            center_y = self.height() // 2
            radius = min(self.width(), self.height()) // 3
            
            for i, app in enumerate(self.favorite_apps):
                angle = (2 * math.pi * i / len(self.favorite_apps)) - (math.pi / 2)
                x = center_x + (radius * math.cos(angle)) - 45
                y = center_y + (radius * math.sin(angle)) - 45

                try:
                    app_info = IconSystem.get_app_info(app["name"])
                    btn = SafeModernButton(app_info, self)
                    btn.app_command = app["command"]
                    btn.clicked.connect(self.handle_button_click)
                    btn.move(int(x), int(y))
                    btn.setStyleSheet(btn.get_button_style())
                    btn.show()
                    self.favorite_buttons.append(btn)
                except Exception as e:
                    print(f"⚠️ ボタン作成エラー ({app['name']}): {e}")
                    
        except Exception as e:
            print(f"⚠️ 円形ボタン作成エラー: {e}")

    def handle_button_click(self):
        """ボタンクリック処理"""
        try:
            button = self.sender()
            if hasattr(button, "app_command") and button.app_command:
                print(f"🚀 アプリ起動: {button.app_info['full_name']}")
                self.launch_app(button.app_command)
        except Exception as e:
            print(f"⚠️ ボタンクリックエラー: {e}")

    def launch_app(self, command):
        """アプリケーション起動"""
        try:
            if command.startswith("open "):
                command = f'open {shlex.quote(command[5:])}'
                subprocess.run(command, shell=True, check=True)
            else:
                subprocess.run(command.split(), check=True)
            print(f"✅ アプリ起動成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ アプリの起動に失敗しました: {e}")
        except Exception as e:
            print(f"❌ アプリ起動エラー: {e}")

    def paintEvent(self, event):
        """モダンな背景描画"""
        try:
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
            
        except Exception as e:
            print(f"⚠️ 描画エラー: {e}")

    def resizeEvent(self, event):
        """リサイズイベント"""
        try:
            super().resizeEvent(event)
            if hasattr(self, 'settings_button'):
                self.settings_button.move(20, 20)
            self.create_circle_buttons()
        except Exception as e:
            print(f"⚠️ リサイズエラー: {e}")

    def mousePressEvent(self, event):
        """ウィンドウドラッグ機能"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        except Exception as e:
            print(f"⚠️ マウスプレスエラー: {e}")

    def mouseMoveEvent(self, event):
        """ウィンドウドラッグ機能"""
        try:
            if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
        except Exception as e:
            print(f"⚠️ マウスムーブエラー: {e}")

def main():
    """メイン実行関数"""
    try:
        if not PYQT6_AVAILABLE:
            print("❌ PyQt6が利用できません。終了します。")
            return
            
        app = QApplication(sys.argv)
        
        # macOS用の設定
        app.setStyle('Fusion')
        
        menu = SafePiMenu()
        menu.show()
        
        print("✅ Pi Menu が起動しました")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ 起動エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()