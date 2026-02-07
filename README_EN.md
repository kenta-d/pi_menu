# Pi Menu

A macOS application launcher that displays your favorite apps in a circular layout for easy access.

## Features

- Display favorite apps in a circular layout
- GUI-based favorite app configuration
- Automatic app list generation from macOS /Applications folder
- Modern UI built with PyQt6

## Requirements

- Python 3.x
- PyQt6

## Installation

```bash
pip install PyQt6
```

## Usage

### 1. Generate Configuration File

On first run, generate the configuration file:

```bash
python pi_menu/generate_configfile.py
```

This creates a `config.json` file with all applications from your macOS `/Applications` folder.

### 2. Launch Application

```bash
python pi_menu/main.py
```

### 3. Configure Favorites

After launching the application, click the "⭐ お気に入り設定" (Favorite Settings) button in the top-left corner to select your favorite apps.

## Install (GitHub Releases)

1. Download `Pi Menu-0.1.0.app.zip` from GitHub Releases
2. Unzip it
3. Move `Pi Menu.app` to `/Applications`
4. First launch: `Right click > Open`

> Because this build is unsigned, Gatekeeper will show a warning on first launch.

### Theme (Optional)

Create `~/Library/Application Support/PiMenu/theme.json` to customize
colors, transparency, font size, and icon size.

## Configuration File (config.json)

The `config.json` file stores app information in the following format:

```json
{
    "apps": [
        {
            "name": "Visual Studio Code",
            "command": "open /Applications/Visual Studio Code.app",
            "icon": "👨‍💻",
            "favorite": true
        }
    ]
}
```

- `name`: Application name
- `command`: Launch command
- `icon`: Emoji icon (optional)
- `favorite`: Favorite flag (if true, displayed in circular layout)

## Project Structure

```
pi_menu/
├── pi_menu/
│   ├── __init__.py
│   ├── main.py              # Main application
│   ├── generate_configfile.py  # Config file generator
│   ├── main_modern.py       # Version-specific implementations
│   ├── main_backup.py
│   ├── main_original.py
│   └── main_safe.py
└── config.json              # App configuration file
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
