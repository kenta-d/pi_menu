import json
import math
import plistlib
import shlex
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import QFileInfo, QPoint, QPropertyAnimation, QSize, Qt, QTimer
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFileIconProvider,
    QGraphicsDropShadowEffect,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


def _config_file_path() -> Path:
    return Path.home() / "Library" / "Application Support" / "PiMenu" / "config.json"


def _theme_file_path() -> Path:
    return Path.home() / "Library" / "Application Support" / "PiMenu" / "theme.json"


def _load_theme() -> dict:
    default_theme = {
        "background_color": "rgba(30, 30, 40, 200)",
        "ring_color": "rgba(100, 180, 255, 80)",
        "ring_glow_color": "rgba(100, 180, 255, 40)",
        "center_gradient_start": "#667eea",
        "center_gradient_end": "#764ba2",
        "center_border_color": "rgba(255, 255, 255, 100)",
        "icon_bg": "rgba(40, 40, 50, 180)",
        "icon_bg_hover": "rgba(60, 60, 80, 220)",
        "icon_border": "rgba(100, 100, 120, 100)",
        "icon_shadow_color": "rgba(0, 0, 0, 80)",
    }

    theme_path = _theme_file_path()
    if not theme_path.exists():
        return default_theme

    try:
        with open(theme_path, "r") as f:
            user_theme = json.load(f)
    except Exception:
        return default_theme

    return {**default_theme, **user_theme}


def _app_bundle_from_command(command: str) -> Path | None:
    if not command.startswith("open "):
        return None
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
        self.setWindowTitle("Favorite Apps Settings")
        self.setGeometry(200, 200, 400, 500)
        self.setStyleSheet(
            """
            QDialog {
                background-color: rgba(30, 30, 40, 240);
                color: white;
            }
            QListWidget {
                background-color: rgba(40, 40, 50, 200);
                color: white;
                border: 1px solid rgba(100, 100, 120, 100);
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: rgba(60, 60, 80, 200);
            }
            QPushButton {
                background-color: rgba(100, 180, 255, 180);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(100, 180, 255, 220);
            }
            """
        )

        layout = QVBoxLayout()
        self.app_list = QListWidget()
        self.load_apps()
        layout.addWidget(self.app_list)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_favorites)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def load_apps(self):
        if not self.config_file.exists():
            print(f"Config file not found: {self.config_file}")
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        for app in data["apps"]:
            item = QListWidgetItem(app["name"])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked
                if app.get("favorite", False)
                else Qt.CheckState.Unchecked
            )
            self.app_list.addItem(item)

    def save_favorites(self):
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

        print("Favorites saved")
        self.accept()


class PiMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.favorite_buttons = []
        self.favorite_apps = []
        self.config_file = _config_file_path()
        self.theme = _load_theme()
        self.drag_position = None
        self.ring_animation_angle = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pi Menu")
        self.setFixedSize(500, 500)

        # Frameless transparent window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.favorite_buttons = []
        self.favorite_apps = []
        self.load_favorites()
        self.create_circle_buttons()

        # Ring animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_ring_animation)
        self.animation_timer.start(50)

        # Center the window on screen
        self.center_on_screen()

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_ring_animation(self):
        self.ring_animation_angle = (self.ring_animation_angle + 1) % 360
        self.update()

    def load_favorites(self):
        self.favorite_apps = []

        if not self.config_file.exists():
            print(f"Config file not found: {self.config_file}")
            return

        with open(self.config_file, "r") as file:
            data = json.load(file)

        self.favorite_apps = [
            app for app in data["apps"] if app.get("favorite", False)
        ]

    def create_circle_buttons(self):
        for btn in self.favorite_buttons:
            btn.deleteLater()
        self.favorite_buttons.clear()

        if not self.favorite_apps:
            return

        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 160
        button_size = 64

        for i, app in enumerate(self.favorite_apps):
            angle = (2 * math.pi * i / len(self.favorite_apps)) - (math.pi / 2)
            x = center_x + (radius * math.cos(angle)) - (button_size // 2)
            y = center_y + (radius * math.sin(angle)) - (button_size // 2)

            btn = QToolButton(self)
            btn.setFixedSize(button_size, button_size)
            btn.app_command = app["command"]
            btn.app_name = app["name"]
            btn.clicked.connect(self.handle_button_click)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            btn.setStyleSheet(
                f"""
                QToolButton {{
                    border-radius: {button_size // 2}px;
                    background-color: {self.theme['icon_bg']};
                    border: 1px solid {self.theme['icon_border']};
                }}
                QToolButton:hover {{
                    background-color: {self.theme['icon_bg_hover']};
                    border: 1px solid rgba(100, 180, 255, 150);
                }}
                """
            )

            # Add shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(0, 3)
            btn.setGraphicsEffect(shadow)

            icon = _qt_icon_for_app(app.get("command", ""))
            if icon:
                btn.setIcon(icon)
            btn.setIconSize(QSize(48, 48))
            btn.move(int(x), int(y))
            btn.setToolTip(app["name"])
            btn.setParent(self)
            btn.show()

            self.favorite_buttons.append(btn)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() // 2
        center_y = self.height() // 2
        window_radius = min(self.width(), self.height()) // 2 - 10

        # Draw circular background
        bg_path = QPainterPath()
        bg_path.addEllipse(
            center_x - window_radius,
            center_y - window_radius,
            window_radius * 2,
            window_radius * 2,
        )
        painter.fillPath(bg_path, QColor(30, 30, 40, 200))

        # Draw outer glow ring
        ring_radius = 170
        ring_width = 3

        # Animated gradient for the ring
        gradient = QLinearGradient(
            center_x - ring_radius,
            center_y - ring_radius,
            center_x + ring_radius,
            center_y + ring_radius,
        )

        angle_offset = self.ring_animation_angle / 360.0
        gradient.setColorAt((0 + angle_offset) % 1.0, QColor(100, 180, 255, 120))
        gradient.setColorAt((0.25 + angle_offset) % 1.0, QColor(130, 100, 255, 80))
        gradient.setColorAt((0.5 + angle_offset) % 1.0, QColor(100, 180, 255, 120))
        gradient.setColorAt((0.75 + angle_offset) % 1.0, QColor(180, 100, 255, 80))

        pen = QPen(QBrush(gradient), ring_width)
        painter.setPen(pen)
        painter.drawEllipse(
            int(center_x - ring_radius),
            int(center_y - ring_radius),
            int(ring_radius * 2),
            int(ring_radius * 2),
        )

        # Draw outer glow effect
        for i in range(5):
            glow_pen = QPen(QColor(100, 180, 255, 30 - i * 5), ring_width + i * 2)
            painter.setPen(glow_pen)
            painter.drawEllipse(
                int(center_x - ring_radius),
                int(center_y - ring_radius),
                int(ring_radius * 2),
                int(ring_radius * 2),
            )

        # Draw center circle with gradient
        center_radius = 50
        center_gradient = QRadialGradient(center_x, center_y, center_radius)
        center_gradient.setColorAt(0, QColor(102, 126, 234, 255))
        center_gradient.setColorAt(0.7, QColor(118, 75, 162, 255))
        center_gradient.setColorAt(1, QColor(90, 60, 140, 255))

        painter.setPen(QPen(QColor(255, 255, 255, 100), 2))
        painter.setBrush(QBrush(center_gradient))
        painter.drawEllipse(
            center_x - center_radius,
            center_y - center_radius,
            center_radius * 2,
            center_radius * 2,
        )

        # Draw "P" text with pi symbol
        painter.setPen(QColor(255, 255, 255, 230))
        font = painter.font()
        font.setPointSize(32)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            center_x - center_radius,
            center_y - center_radius,
            center_radius * 2,
            center_radius * 2,
            Qt.AlignmentFlag.AlignCenter,
            "P",
        )

        # Draw small pi symbol
        font.setPointSize(14)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.drawText(
            center_x + 8,
            center_y + 20,
            "\u03c0",
        )

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            center = QPoint(self.width() // 2, self.height() // 2)
            distance = (event.position().toPoint() - center).manhattanLength()

            # Click on center opens settings
            if distance < 50:
                self.open_favorite_settings()
            else:
                self.drag_position = event.globalPosition().toPoint() - self.pos()

        elif event.button() == Qt.MouseButton.RightButton:
            self.close()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def open_favorite_settings(self):
        settings = FavoriteSettings(self.config_file, self)
        if settings.exec():
            self.load_favorites()
            self.create_circle_buttons()

    def handle_button_click(self):
        button = self.sender()
        if not button:
            return

        if hasattr(button, "app_command") and button.app_command:
            self.launch_app(button.app_command)

    def launch_app(self, command):
        try:
            if command.startswith("open "):
                command = f"open {shlex.quote(command[5:])}"
                subprocess.run(command, shell=True, check=True, capture_output=True)
            else:
                subprocess.run(command.split(), check=True, capture_output=True)

        except subprocess.CalledProcessError as e:
            print(f"Failed to launch app: {e}")
        except Exception as e:
            print(f"Failed to launch app: {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PiMenu()
    ex.show()
    sys.exit(app.exec())
