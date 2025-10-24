#!/bin/bash

# Pi Menu インストーラー
# boss1 Agent による配布用インストールスクリプト

set -e  # エラー時に停止

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ロゴ表示
echo -e "${PURPLE}┌─────────────────────────────────────────┐${NC}"
echo -e "${PURPLE}│                                         │${NC}"
echo -e "${PURPLE}│            🍎 Pi Menu v2.0              │${NC}"
echo -e "${PURPLE}│      モダンな円形アプリランチャー         │${NC}"
echo -e "${PURPLE}│                                         │${NC}"
echo -e "${PURPLE}│           by boss1 Agent               │${NC}"
echo -e "${PURPLE}│                                         │${NC}"
echo -e "${PURPLE}└─────────────────────────────────────────┘${NC}"
echo ""

# 管理者権限チェック
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        echo -e "${YELLOW}⚠️  管理者権限で実行されています。通常ユーザーで実行してください。${NC}"
        echo "sudo なしで再実行してください。"
        exit 1
    fi
}

# macOSバージョンチェック
check_macos_version() {
    echo -e "${BLUE}🔍 macOSバージョンを確認中...${NC}"
    
    macos_version=$(sw_vers -productVersion)
    major_version=$(echo $macos_version | cut -d. -f1)
    minor_version=$(echo $macos_version | cut -d. -f2)
    
    echo "   検出されたバージョン: macOS $macos_version"
    
    # macOS 10.15 (Catalina) 以降が必要
    if (( major_version < 10 || (major_version == 10 && minor_version < 15) )); then
        echo -e "${RED}❌ macOS 10.15 (Catalina) 以降が必要です${NC}"
        echo "   現在のバージョン: $macos_version"
        exit 1
    fi
    
    echo -e "${GREEN}✅ macOSバージョン: OK${NC}"
}

# Homebrewの確認・インストール
install_homebrew() {
    echo -e "${BLUE}🍺 Homebrewを確認中...${NC}"
    
    if command -v brew >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Homebrew: インストール済み${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}📦 Homebrewをインストール中...${NC}"
    echo "   これには数分かかる場合があります..."
    
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # パスの追加
    if [[ -f /opt/homebrew/bin/brew ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f /usr/local/bin/brew ]]; then
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    echo -e "${GREEN}✅ Homebrew: インストール完了${NC}"
}

# PyQt6の確認・インストール
install_pyqt6() {
    echo -e "${BLUE}🐍 PyQt6を確認中...${NC}"
    
    if python3 -c "import PyQt6" 2>/dev/null; then
        echo -e "${GREEN}✅ PyQt6: インストール済み${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}📦 PyQt6をインストール中...${NC}"
    echo "   これには数分かかる場合があります..."
    
    # まずはbreawで試行
    if command -v brew >/dev/null 2>&1; then
        brew install pyqt@6 || {
            echo -e "${YELLOW}⚠️  brewでのインストールに失敗。pipxを試行中...${NC}"
            
            # pipxが無い場合はインストール
            if ! command -v pipx >/dev/null 2>&1; then
                brew install pipx
                pipx ensurepath
            fi
            
            pipx install PyQt6
        }
    else
        echo -e "${RED}❌ Homebrewがインストールされていません${NC}"
        exit 1
    fi
    
    # 再確認
    if python3 -c "import PyQt6" 2>/dev/null; then
        echo -e "${GREEN}✅ PyQt6: インストール完了${NC}"
    else
        echo -e "${RED}❌ PyQt6のインストールに失敗しました${NC}"
        echo "手動でインストールしてください:"
        echo "   brew install pyqt@6"
        echo "   または"
        echo "   pipx install PyQt6"
        exit 1
    fi
}

# Pi Menuのインストール
install_pi_menu() {
    echo -e "${BLUE}🎯 Pi Menuをインストール中...${NC}"
    
    # インストール先の確認
    INSTALL_DIR="/Applications"
    APP_NAME="Pi Menu.app"
    FULL_PATH="$INSTALL_DIR/$APP_NAME"
    
    # 既存のアプリがある場合は削除確認
    if [[ -d "$FULL_PATH" ]]; then
        echo -e "${YELLOW}⚠️  既存のPi Menuが見つかりました${NC}"
        read -p "   既存のアプリを置き換えますか? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "   既存のアプリを削除中..."
            rm -rf "$FULL_PATH"
        else
            echo "   インストールをキャンセルしました"
            exit 1
        fi
    fi
    
    # アプリケーションバンドルをコピー
    if [[ -d "./$APP_NAME" ]]; then
        echo "   Pi Menuを/Applicationsにコピー中..."
        cp -R "./$APP_NAME" "$INSTALL_DIR/"
        
        # 実行権限を設定
        chmod +x "$FULL_PATH/Contents/MacOS/pi_menu"
        
        echo -e "${GREEN}✅ Pi Menu: インストール完了${NC}"
    else
        echo -e "${RED}❌ Pi Menu.appが見つかりません${NC}"
        echo "   インストーラーが正しいディレクトリで実行されているか確認してください"
        exit 1
    fi
}

# アクセシビリティ権限の確認
check_accessibility() {
    echo -e "${BLUE}🔒 アクセシビリティ権限を確認中...${NC}"
    echo ""
    echo -e "${YELLOW}📋 重要: アクセシビリティ権限について${NC}"
    echo "   Pi Menuが他のアプリケーションを起動するには、"
    echo "   システム環境設定でアクセシビリティ権限が必要な場合があります。"
    echo ""
    echo "   アプリ起動時に権限を求められた場合は許可してください。"
    echo ""
}

# インストール完了メッセージ
installation_complete() {
    echo ""
    echo -e "${GREEN}┌─────────────────────────────────────────┐${NC}"
    echo -e "${GREEN}│                                         │${NC}"
    echo -e "${GREEN}│        🎉 インストール完了！             │${NC}"
    echo -e "${GREEN}│                                         │${NC}"
    echo -e "${GREEN}│   Pi Menu が正常にインストールされました  │${NC}"
    echo -e "${GREEN}│                                         │${NC}"
    echo -e "${GREEN}└─────────────────────────────────────────┘${NC}"
    echo ""
    echo -e "${CYAN}🚀 Pi Menuを起動するには:${NC}"
    echo "   • Finderで「アプリケーション」フォルダを開く"
    echo "   • 「Pi Menu」をダブルクリック"
    echo "   • または Spotlight で「Pi Menu」を検索"
    echo ""
    echo -e "${CYAN}⚙️  設定方法:${NC}"
    echo "   • アプリ起動後、左上の⚙️ボタンをクリック"
    echo "   • お気に入りアプリを選択して保存"
    echo ""
    echo -e "${CYAN}🌟 主な機能:${NC}"
    echo "   • 48種類のアプリアイコン自動認識"
    echo "   • カテゴリ別色分け（開発・ブラウザ・通信など）"
    echo "   • Glassmorphism効果のモダンUI"
    echo "   • ホバー時のアニメーション"
    echo "   • フレームレスウィンドウ（ドラッグ移動可能）"
    echo ""
    
    # 起動オプション
    read -p "Pi Menuを今すぐ起動しますか? (Y/n): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${BLUE}🚀 Pi Menuを起動中...${NC}"
        open "/Applications/Pi Menu.app"
    fi
    
    echo ""
    echo -e "${PURPLE}Thanks for using Pi Menu! - boss1 Agent${NC}"
}

# メイン実行
main() {
    echo -e "${CYAN}📋 システム要件をチェック中...${NC}"
    echo ""
    
    check_permissions
    check_macos_version
    
    echo ""
    echo -e "${CYAN}📦 依存関係をインストール中...${NC}"
    echo ""
    
    install_homebrew
    install_pyqt6
    
    echo ""
    echo -e "${CYAN}🎯 Pi Menuをインストール中...${NC}"
    echo ""
    
    install_pi_menu
    check_accessibility
    installation_complete
}

# エラーハンドリング
trap 'echo -e "${RED}❌ インストール中にエラーが発生しました${NC}"; exit 1' ERR

# メイン実行
main "$@"