from __future__ import annotations

from pathlib import Path

from . import generate_configfile
from .main import PiMenu

from PyQt6.QtWidgets import QApplication
import sys


def _ensure_config_exists() -> None:
    config_path = Path.home() / "Library" / "Application Support" / "PiMenu" / "config.json"
    if config_path.exists():
        return
    generate_configfile.generate_config(config_path)


def main() -> int:
    _ensure_config_exists()
    app = QApplication(sys.argv)
    ex = PiMenu()
    ex.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
