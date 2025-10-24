#!/bin/bash

# Pi Menu v2.0 配布パッケージ作成スクリプト
# boss1 Agent による最終配布準備

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# バージョン情報
VERSION="2.0.0"
BUILD_DATE=$(date "+%Y.%m.%d")
DIST_NAME="Pi_Menu_v${VERSION}_macOS"

echo -e "${PURPLE}📦 Pi Menu v${VERSION} 配布パッケージ作成${NC}"
echo "=" * 60

# 1. 配布ディレクトリの確認
echo -e "${BLUE}🔍 配布ファイルを確認中...${NC}"

if [[ ! -d "dist" ]]; then
    echo -e "${RED}❌ distディレクトリが見つかりません${NC}"
    exit 1
fi

cd dist

# 必要なファイルの確認
REQUIRED_FILES=(
    "Pi Menu.app"
    "install_pi_menu.sh"
    "README_DISTRIBUTION.md"
    "USER_GUIDE.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -e "$file" ]]; then
        echo -e "${RED}❌ 必要なファイルが見つかりません: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ 必要なファイル: 確認完了${NC}"

# 2. アプリバンドルの検証
echo -e "${BLUE}🔍 アプリバンドルを検証中...${NC}"

if [[ ! -f "Pi Menu.app/Contents/Info.plist" ]]; then
    echo -e "${RED}❌ Info.plistが見つかりません${NC}"
    exit 1
fi

if [[ ! -x "Pi Menu.app/Contents/MacOS/pi_menu" ]]; then
    echo -e "${RED}❌ 実行ファイルが見つからないか実行権限がありません${NC}"
    exit 1
fi

echo -e "${GREEN}✅ アプリバンドル: 検証完了${NC}"

# 3. サイズ計算
echo -e "${BLUE}📊 パッケージサイズを計算中...${NC}"

TOTAL_SIZE=$(du -sh . | cut -f1)
APP_SIZE=$(du -sh "Pi Menu.app" | cut -f1)

echo "   Pi Menu.app: $APP_SIZE"
echo "   パッケージ全体: $TOTAL_SIZE"

# 4. 配布アーカイブの作成
echo -e "${BLUE}📦 配布アーカイブを作成中...${NC}"

# 作業ディレクトリの準備
TEMP_DIR="/tmp/${DIST_NAME}"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# ファイルのコピー
echo "   ファイルをコピー中..."
cp -R "Pi Menu.app" "$TEMP_DIR/"
cp install_pi_menu.sh "$TEMP_DIR/"
cp README_DISTRIBUTION.md "$TEMP_DIR/README.md"
cp USER_GUIDE.md "$TEMP_DIR/"

# ライセンスファイルの作成
cat > "$TEMP_DIR/LICENSE" << 'EOF'
MIT License

Copyright (c) 2025 boss1

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# 配布用READMEの作成
cat > "$TEMP_DIR/README_RELEASE.md" << EOF
# 🍎 Pi Menu v${VERSION}

**モダンな円形アプリケーションランチャー for macOS**

## 📥 インストール

### 自動インストール（推奨）
\`\`\`bash
./install_pi_menu.sh
\`\`\`

### 手動インストール
1. Pi Menu.app を Applications フォルダにドラッグ&ドロップ
2. PyQt6 をインストール: \`brew install pyqt@6\`

## 🌟 主な機能

- **48種類のアプリアイコン自動認識**
- **カテゴリ別色分け** (開発・ブラウザ・通信など)
- **Glassmorphism効果** のモダンUI
- **スムーズなアニメーション**
- **フレームレスウィンドウ** (ドラッグ移動可能)

## 📋 システム要件

- macOS 10.15 (Catalina) 以降
- Python 3.8 以降
- PyQt6

## 📞 サポート

- GitHub Issues: バグ報告・機能リクエスト
- ユーザーガイド: USER_GUIDE.md
- ライセンス: MIT License

---

**開発**: boss1 Agent  
**バージョン**: ${VERSION}  
**ビルド日**: ${BUILD_DATE}
EOF

# 5. アーカイブの作成
echo -e "${BLUE}🗜️  アーカイブを作成中...${NC}"

cd /tmp

# Tar.gz アーカイブ
echo "   .tar.gz アーカイブを作成中..."
tar -czf "${DIST_NAME}.tar.gz" "$DIST_NAME"

# Zip アーカイブ
echo "   .zip アーカイブを作成中..."
zip -r "${DIST_NAME}.zip" "$DIST_NAME" > /dev/null

# 6. アーカイブを元のディレクトリに移動
ORIGINAL_DIR=$(pwd)
cd - > /dev/null

mv "/tmp/${DIST_NAME}.tar.gz" "./"
mv "/tmp/${DIST_NAME}.zip" "./"

# 7. チェックサムの計算
echo -e "${BLUE}🔒 チェックサムを計算中...${NC}"

echo "   SHA256チェックサムを計算中..."
shasum -a 256 "${DIST_NAME}.tar.gz" > "${DIST_NAME}.tar.gz.sha256"
shasum -a 256 "${DIST_NAME}.zip" > "${DIST_NAME}.zip.sha256"

# 8. 結果の表示
echo ""
echo -e "${GREEN}🎉 配布パッケージの作成が完了しました！${NC}"
echo ""
echo -e "${PURPLE}📦 作成されたファイル:${NC}"
echo "   ${DIST_NAME}.tar.gz ($(du -sh "${DIST_NAME}.tar.gz" | cut -f1))"
echo "   ${DIST_NAME}.zip ($(du -sh "${DIST_NAME}.zip" | cut -f1))"
echo "   チェックサムファイル (.sha256)"
echo ""

echo -e "${BLUE}📊 パッケージ情報:${NC}"
echo "   バージョン: ${VERSION}"
echo "   ビルド日: ${BUILD_DATE}"
echo "   総サイズ: $TOTAL_SIZE"
echo "   対応OS: macOS 10.15+"
echo ""

echo -e "${CYAN}🚀 配布方法:${NC}"
echo "   1. GitHub Releases にアップロード"
echo "   2. ウェブサイトで公開"
echo "   3. ユーザーに直接配布"
echo ""

echo -e "${YELLOW}📝 次のステップ:${NC}"
echo "   • リリースノートの作成"
echo "   • GitHub Releases での公開"
echo "   • ユーザーテストの実施"
echo "   • フィードバックの収集"
echo ""

# クリーンアップ
rm -rf "$TEMP_DIR"

echo -e "${PURPLE}Thanks for using Pi Menu distribution builder! - boss1 Agent${NC}"