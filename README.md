# Pi Menu

[English](README_EN.md) | 日本語

macOS用のアプリケーションランチャーです。お気に入りのアプリを円形レイアウトで表示し、簡単にアクセスできます。

## 特徴

- お気に入りアプリを円形レイアウトで表示
- GUIでお気に入りアプリの設定が可能
- macOSの/Applicationsフォルダから自動的にアプリ一覧を生成
- PyQt6を使用したモダンなUI

## 必要要件

- Python 3.x
- PyQt6

## インストール

```bash
pip install PyQt6
```

## 使い方

### 1. 設定ファイルの生成

初回起動時は、まず設定ファイルを生成します：

```bash
python pi_menu/generate_configfile.py
```

これにより、`config.json`ファイルが作成され、macOSの`/Applications`フォルダ内のすべてのアプリが登録されます。

### 2. アプリケーションの起動

```bash
python pi_menu/main.py
```

### 3. お気に入りの設定

アプリケーション起動後、左上の「⭐ お気に入り設定」ボタンをクリックして、お気に入りアプリを選択できます。

## GitHub Releases 版のインストール

1. GitHub Releases から `Pi Menu-0.1.0.app.zip` をダウンロード
2. ZIP を展開
3. `Pi Menu.app` を `/Applications` に移動
4. 初回起動は `右クリック > 開く` で許可

> 署名なし配布のため、初回は Gatekeeper の警告が出ます。

### テーマ設定（任意）

`~/Library/Application Support/PiMenu/theme.json` を作成すると、
色・透明度・文字サイズ・アイコンサイズなどを調整できます。

## 設定ファイル (config.json)

`config.json`には以下の形式でアプリ情報が保存されます：

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

- `name`: アプリケーション名
- `command`: 起動コマンド
- `icon`: 絵文字アイコン（任意）
- `favorite`: お気に入りフラグ（trueの場合、円形レイアウトに表示）

## プロジェクト構成

```
pi_menu/
├── pi_menu/
│   ├── __init__.py
│   ├── main.py              # メインアプリケーション
│   ├── generate_configfile.py  # 設定ファイル生成スクリプト
│   ├── main_modern.py       # バージョン別実装
│   ├── main_backup.py
│   ├── main_original.py
│   └── main_safe.py
└── config.json              # アプリ設定ファイル
```

## ライセンス

このプロジェクトはMIT Licenseの下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。
