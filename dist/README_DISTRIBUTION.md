# Pi Menu v2.0 - 配布パッケージ

## 📦 配布内容

```
Pi_Menu_v2.0_Distribution/
├── Pi Menu.app/                 # macOSアプリケーションバンドル
│   ├── Contents/
│   │   ├── Info.plist          # アプリメタデータ
│   │   ├── MacOS/
│   │   │   └── pi_menu         # 実行ランチャー
│   │   └── Resources/
│   │       ├── pi_menu/        # Pythonソースコード
│   │       ├── config.json     # 設定ファイル
│   │       └── version.json    # バージョン情報
├── install_pi_menu.sh          # 自動インストーラー
├── icon_source.svg             # アイコンソース（開発用）
└── README_DISTRIBUTION.md     # このファイル
```

## 🚀 インストール方法

### 自動インストール（推奨）
```bash
# ダウンロードしたフォルダで実行
./install_pi_menu.sh
```

### 手動インストール
1. **Pi Menu.app** を `/Applications` フォルダにドラッグ&ドロップ
2. 依存関係をインストール:
   ```bash
   brew install pyqt@6
   ```

## 📋 システム要件

- **OS**: macOS 10.15 (Catalina) 以降
- **アーキテクチャ**: Intel (x86_64) / Apple Silicon (arm64)
- **Python**: 3.8 以降（システム標準）
- **依存関係**: PyQt6

## 🔧 依存関係の管理

### PyQt6のインストール方法
1. **Homebrew（推奨）**:
   ```bash
   brew install pyqt@6
   ```

2. **pipx**:
   ```bash
   brew install pipx
   pipx install PyQt6
   ```

3. **仮想環境**:
   ```bash
   python3 -m venv pi_menu_env
   source pi_menu_env/bin/activate
   pip install PyQt6
   ```

## 📁 配布ファイルの説明

### Pi Menu.app
- 完全なmacOSアプリケーションバンドル
- ダブルクリックで起動可能
- Finderでの表示とSpotlight検索に対応

### install_pi_menu.sh
- 依存関係の自動確認・インストール
- システム要件チェック
- エラーハンドリング付きインストール
- カラフルなUI表示

### 設定ファイル
- `config.json`: アプリケーション設定
- `version.json`: バージョン情報とメタデータ

## 🎯 配布方法

### 1. GitHub Releases
```bash
# リリースパッケージ作成
tar -czf Pi_Menu_v2.0_macOS.tar.gz "Pi Menu.app" install_pi_menu.sh README_DISTRIBUTION.md

# GitHubにアップロード（手動またはGH CLI）
gh release create v2.0 Pi_Menu_v2.0_macOS.tar.gz --title "Pi Menu v2.0" --notes "モダンUIリニューアル版"
```

### 2. DMGイメージ（オプション）
```bash
# DMGの作成
hdiutil create -volname "Pi Menu v2.0" -srcfolder . -ov -format UDZO Pi_Menu_v2.0.dmg
```

### 3. Zip圧縮
```bash
# Zip形式での配布
zip -r Pi_Menu_v2.0_macOS.zip "Pi Menu.app" install_pi_menu.sh README_DISTRIBUTION.md
```

## 🛡️ セキュリティ考慮事項

### Code Signing（本格配布時）
```bash
# 開発者証明書でのコード署名
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" "Pi Menu.app"

# 公証（Notarization）
xcrun notarytool submit "Pi Menu.app" --keychain-profile "notarytool-profile" --wait
```

### Gatekeeper対応
- 初回起動時に「開発元不明」の警告が表示される場合
- ユーザーは「システム環境設定」→「セキュリティとプライバシー」で許可が必要

## 📊 配布統計（追跡用）

### ダウンロード方法の追跡
- GitHub Releases のダウンロード数
- ウェブサイトのアクセス統計
- ユーザーフィードバック

### 使用統計（オプション）
- アプリ起動回数（プライバシー配慮）
- エラーレポート（匿名）
- 機能使用頻度

## 🔄 アップデート戦略

### 自動更新チェック（将来実装）
```python
# version.json を使用したバージョンチェック
def check_for_updates():
    current_version = "2.0.0"
    # GitHub API でリリース情報を取得
    # ユーザーに更新通知を表示
```

### 手動更新
1. 新しいバージョンをダウンロード
2. 既存アプリを置き換え
3. 設定ファイルは自動で引き継ぎ

## 📞 サポート情報

- **Issues**: GitHub Issues ページ
- **Email**: support@boss1.dev（仮想）
- **ドキュメント**: README.md
- **FAQ**: よくある質問集

## 🏷️ ライセンス

MIT License - 自由な使用・配布・改変が可能

---

**配布準備者**: boss1 Agent  
**作成日**: 2025-06-27  
**バージョン**: 2.0.0