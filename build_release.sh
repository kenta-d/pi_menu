#!/bin/bash

# Pi Menu v2.0 Release Build Script
# Supports multiple distribution methods

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Version and build info
VERSION="2.0.0"
BUILD_DATE=$(date "+%Y.%m.%d")
PROJECT_NAME="pi-menu"

echo -e "${PURPLE}🚀 Pi Menu v${VERSION} Release Build${NC}"
echo "=========================================="

# Check Python and dependencies
echo -e "${BLUE}🔍 Checking environment...${NC}"
python3 --version
if command -v uv &> /dev/null; then
    echo "✅ uv package manager found"
    PACKAGE_MANAGER="uv"
else
    echo "❌ uv not found, using pip"
    PACKAGE_MANAGER="pip"
fi

# Install build dependencies
echo -e "${BLUE}📦 Installing build dependencies...${NC}"
if [ "$PACKAGE_MANAGER" = "uv" ]; then
    uv sync
else
    pip install -e .
fi

# Install additional build tools
echo -e "${BLUE}🔨 Installing build tools...${NC}"
pip install build wheel setuptools twine

# Clean previous builds
echo -e "${BLUE}🧹 Cleaning previous builds...${NC}"
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/

# Build wheel and source distribution
echo -e "${BLUE}⚙️  Building Python packages...${NC}"
python -m build

# Build standalone executable with PyInstaller
echo -e "${BLUE}📱 Building standalone executable...${NC}"
pip install pyinstaller

# Create PyInstaller spec
cat > pi_menu.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pi_menu/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('custom_icons.json', '.'),
        ('pi_menu/*.py', 'pi_menu'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pi_menu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pi_menu'
)

app = BUNDLE(
    coll,
    name='Pi Menu.app',
    icon=None,
    bundle_identifier='com.kenta-d.pi-menu',
    version='2.0.0',
    info_plist={
        'CFBundleDisplayName': 'Pi Menu',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundleVersion': '2.0.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': True,
    }
)
EOF

pyinstaller pi_menu.spec --clean

# Move built app to release directory
mkdir -p release
if [ -d "dist/Pi Menu.app" ]; then
    cp -R "dist/Pi Menu.app" release/
    echo -e "${GREEN}✅ macOS app bundle created${NC}"
fi

# Create release archive
echo -e "${BLUE}📦 Creating release archives...${NC}"
cd release

# Create installer script
cat > install.sh << 'EOF'
#!/bin/bash

echo "🍎 Pi Menu v2.0 Installer"
echo "========================="

# Check macOS version
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This installer is for macOS only"
    exit 1
fi

# Check if Applications directory is writable
if [ ! -w "/Applications" ]; then
    echo "⚠️  Administrator privileges required"
    sudo cp -R "Pi Menu.app" /Applications/
else
    cp -R "Pi Menu.app" /Applications/
fi

echo "✅ Pi Menu installed to /Applications/"
echo "🚀 You can now launch Pi Menu from Applications or Spotlight"
EOF

chmod +x install.sh

# Create release package
RELEASE_NAME="Pi_Menu_v${VERSION}_macOS"
tar -czf "${RELEASE_NAME}.tar.gz" "Pi Menu.app" install.sh
zip -r "${RELEASE_NAME}.zip" "Pi Menu.app" install.sh

# Generate checksums
echo -e "${BLUE}🔒 Generating checksums...${NC}"
shasum -a 256 "${RELEASE_NAME}.tar.gz" > "${RELEASE_NAME}.tar.gz.sha256"
shasum -a 256 "${RELEASE_NAME}.zip" > "${RELEASE_NAME}.zip.sha256"

cd ..

# Summary
echo ""
echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo ""
echo -e "${PURPLE}📦 Created packages:${NC}"
echo "   • Python wheel: dist/${PROJECT_NAME}-${VERSION}-py3-none-any.whl"
echo "   • Source dist: dist/${PROJECT_NAME}-${VERSION}.tar.gz"
echo "   • macOS app: release/Pi Menu.app"
echo "   • Release archive: release/${RELEASE_NAME}.tar.gz"
echo "   • Release archive: release/${RELEASE_NAME}.zip"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "   1. Test the built application: open 'release/Pi Menu.app'"
echo "   2. Upload to PyPI: twine upload dist/*"
echo "   3. Create GitHub release with release/ files"
echo "   4. Update Homebrew formula (if applicable)"
echo ""
echo -e "${CYAN}🔗 Distribution options:${NC}"
echo "   • PyPI: pip install pi-menu"
echo "   • Direct download: ${RELEASE_NAME}.zip"
echo "   • Homebrew: brew install --cask pi-menu"
echo ""