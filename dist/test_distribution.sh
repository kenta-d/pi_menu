#!/bin/bash

# Pi Menu 配布パッケージテストスクリプト
# boss1 Agent による最終検証

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🧪 Pi Menu 配布パッケージテスト${NC}"
echo "=" * 50

# テスト結果保存
TEST_RESULTS=()

# テスト関数
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}🔍 テスト: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        TEST_RESULTS+=("PASS: $test_name")
        return 0
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        TEST_RESULTS+=("FAIL: $test_name")
        return 1
    fi
}

# 1. ファイル構造テスト
test_file_structure() {
    echo "   アプリバンドル構造を確認中..."
    
    [[ -d "Pi Menu.app" ]] || { echo "   Pi Menu.app が見つかりません"; return 1; }
    [[ -f "Pi Menu.app/Contents/Info.plist" ]] || { echo "   Info.plist が見つかりません"; return 1; }
    [[ -f "Pi Menu.app/Contents/MacOS/pi_menu" ]] || { echo "   実行ファイルが見つかりません"; return 1; }
    [[ -x "Pi Menu.app/Contents/MacOS/pi_menu" ]] || { echo "   実行権限がありません"; return 1; }
    [[ -d "Pi Menu.app/Contents/Resources/pi_menu" ]] || { echo "   Pythonソースが見つかりません"; return 1; }
    [[ -f "Pi Menu.app/Contents/Resources/config.json" ]] || { echo "   設定ファイルが見つかりません"; return 1; }
    
    echo "   ✓ アプリバンドル構造: OK"
    return 0
}

# 2. 設定ファイルテスト
test_config_file() {
    echo "   設定ファイルの形式を確認中..."
    
    local config_file="Pi Menu.app/Contents/Resources/config.json"
    
    # JSON形式の確認
    python3 -c "import json; json.load(open('$config_file'))" || { echo "   無効なJSON形式"; return 1; }
    
    # 必要なキーの確認
    python3 -c "
import json
data = json.load(open('$config_file'))
assert 'apps' in data, 'apps キーがありません'
assert isinstance(data['apps'], list), 'apps は配列である必要があります'
assert len(data['apps']) > 0, 'アプリリストが空です'
for app in data['apps']:
    assert 'name' in app, 'name キーがありません'
    assert 'command' in app, 'command キーがありません'
    assert 'favorite' in app, 'favorite キーがありません'
print('   ✓ 設定ファイル形式: OK')
"
    return $?
}

# 3. Pythonソースコードテスト
test_python_source() {
    echo "   Pythonソースコードを確認中..."
    
    local source_dir="Pi Menu.app/Contents/Resources/pi_menu"
    
    # 必要なファイルの存在確認
    [[ -f "$source_dir/main_safe.py" ]] || { echo "   main_safe.py が見つかりません"; return 1; }
    [[ -f "$source_dir/icon_system.py" ]] || { echo "   icon_system.py が見つかりません"; return 1; }
    [[ -f "$source_dir/__init__.py" ]] || { echo "   __init__.py が見つかりません"; return 1; }
    
    # 構文チェック
    python3 -m py_compile "$source_dir/main_safe.py" || { echo "   main_safe.py の構文エラー"; return 1; }
    python3 -m py_compile "$source_dir/icon_system.py" || { echo "   icon_system.py の構文エラー"; return 1; }
    
    echo "   ✓ Pythonソースコード: OK"
    return 0
}

# 4. インストーラーテスト
test_installer() {
    echo "   インストーラースクリプトを確認中..."
    
    [[ -f "install_pi_menu.sh" ]] || { echo "   install_pi_menu.sh が見つかりません"; return 1; }
    [[ -x "install_pi_menu.sh" ]] || { echo "   install_pi_menu.sh に実行権限がありません"; return 1; }
    
    # スクリプトの構文チェック
    bash -n install_pi_menu.sh || { echo "   install_pi_menu.sh の構文エラー"; return 1; }
    
    echo "   ✓ インストーラースクリプト: OK"
    return 0
}

# 5. ドキュメントテスト
test_documentation() {
    echo "   ドキュメントファイルを確認中..."
    
    [[ -f "README_DISTRIBUTION.md" ]] || { echo "   README_DISTRIBUTION.md が見つかりません"; return 1; }
    [[ -f "USER_GUIDE.md" ]] || { echo "   USER_GUIDE.md が見つかりません"; return 1; }
    
    # ファイルが空でないことを確認
    [[ -s "README_DISTRIBUTION.md" ]] || { echo "   README_DISTRIBUTION.md が空です"; return 1; }
    [[ -s "USER_GUIDE.md" ]] || { echo "   USER_GUIDE.md が空です"; return 1; }
    
    echo "   ✓ ドキュメントファイル: OK"
    return 0
}

# 6. アプリサイズテスト
test_app_size() {
    echo "   アプリケーションサイズを確認中..."
    
    local app_size=$(du -sh "Pi Menu.app" | cut -f1)
    echo "   アプリサイズ: $app_size"
    
    # サイズが妥当な範囲内かチェック（1MB〜100MB）
    local size_bytes=$(du -s "Pi Menu.app" | cut -f1)
    
    if [[ $size_bytes -lt 1024 ]]; then
        echo "   アプリサイズが小さすぎます（1MB未満）"
        return 1
    elif [[ $size_bytes -gt 102400 ]]; then
        echo "   アプリサイズが大きすぎます（100MB以上）"
        return 1
    fi
    
    echo "   ✓ アプリサイズ: OK ($app_size)"
    return 0
}

# 7. メタデータテスト
test_metadata() {
    echo "   メタデータを確認中..."
    
    local info_plist="Pi Menu.app/Contents/Info.plist"
    local version_json="Pi Menu.app/Contents/Resources/version.json"
    
    # Info.plist の確認
    [[ -f "$info_plist" ]] || { echo "   Info.plist が見つかりません"; return 1; }
    
    # version.json の確認
    [[ -f "$version_json" ]] || { echo "   version.json が見つかりません"; return 1; }
    
    # version.json の形式確認
    python3 -c "
import json
data = json.load(open('$version_json'))
assert 'app_name' in data, 'app_name がありません'
assert 'version' in data, 'version がありません'
assert 'description' in data, 'description がありません'
print(f\"   アプリ名: {data['app_name']}\")
print(f\"   バージョン: {data['version']}\")
print(f\"   説明: {data['description']}\")
"
    
    echo "   ✓ メタデータ: OK"
    return 0
}

echo ""
echo -e "${BLUE}📋 テスト実行中...${NC}"
echo ""

# テスト実行
run_test "ファイル構造" "test_file_structure"
run_test "設定ファイル" "test_config_file"
run_test "Pythonソースコード" "test_python_source"
run_test "インストーラー" "test_installer"
run_test "ドキュメント" "test_documentation"
run_test "アプリサイズ" "test_app_size"
run_test "メタデータ" "test_metadata"

echo ""
echo -e "${PURPLE}📊 テスト結果サマリー${NC}"
echo "=" * 50

PASS_COUNT=0
FAIL_COUNT=0

for result in "${TEST_RESULTS[@]}"; do
    if [[ $result == PASS:* ]]; then
        echo -e "${GREEN}$result${NC}"
        ((PASS_COUNT++))
    else
        echo -e "${RED}$result${NC}"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo -e "${BLUE}合計: $((PASS_COUNT + FAIL_COUNT)) テスト${NC}"
echo -e "${GREEN}成功: $PASS_COUNT${NC}"
echo -e "${RED}失敗: $FAIL_COUNT${NC}"

if [[ $FAIL_COUNT -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}🎉 全テストが成功しました！${NC}"
    echo -e "${GREEN}配布パッケージの準備が完了しています。${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ 一部のテストが失敗しました。${NC}"
    echo -e "${YELLOW}失敗したテストを修正してから配布してください。${NC}"
    exit 1
fi