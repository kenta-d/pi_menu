"""
Pi Menu アイコンシステム
アプリケーション名に基づいて適切なアイコンと色を自動選択
"""

import re
from typing import Tuple, Dict

class IconSystem:
    """アプリケーション名からアイコンと色を決定するシステム"""
    
    # アプリ名パターンとアイコンのマッピング
    ICON_PATTERNS = {
        # 開発系
        r'(visual studio|vs code|code)': '👨‍💻',
        r'(xcode)': '🔨',
        r'(cursor|windsurf)': '⚡',
        r'(zed)': '⚡',
        r'(jetbrains|toolbox)': '🧰',
        
        # ブラウザ系
        r'(chrome|google chrome)': '🌐',
        r'(safari)': '🧭',
        r'(firefox)': '🦊',
        r'(arc)': '🌈',
        
        # 通信系
        r'(discord)': '💬',
        r'(zoom)': '📹',
        r'(teams|microsoft teams)': '👥',
        r'(outlook)': '📧',
        
        # クリエイティブ系
        r'(imovie)': '🎬',
        r'(garageband)': '🎵',
        r'(keynote)': '📊',
        r'(pages)': '📝',
        r'(numbers)': '📈',
        
        # ユーティリティ系
        r'(raycast)': '🚀',
        r'(commander|finder)': '📁',
        r'(dropbox)': '📦',
        r'(onedrive|google drive)': '☁️',
        r'(defender|security)': '🛡️',
        
        # ドキュメント系
        r'(notion)': '📋',
        r'(obsidian)': '🧠',
        r'(kindle|amazon kindle)': '📚',
        r'(upnote)': '📝',
        
        # Google系
        r'(google docs)': '📝',
        r'(google sheets)': '📊',
        r'(google slides)': '🎯',
        
        # Microsoft Office系
        r'(word|microsoft word)': '📄',
        r'(excel|microsoft excel)': '📊',
        r'(powerpoint|microsoft powerpoint)': '🎯',
        r'(onenote|microsoft onenote)': '📝',
        
        # その他
        r'(docker)': '🐳',
        r'(chatgpt)': '🤖',
        r'(perplexity)': '🔍',
        r'(devtoys)': '🔧',
        r'(iterm|terminal)': '⌨️',
        r'(pgadmin)': '🗄️',
        r'(karabiner)': '⌨️',
        r'(logi)': '🖱️',
        r'(calendar|notion calendar)': '📅',
        r'(github)': '🐙',
        r'(anaconda)': '🐍',
        r'(hhkb)': '⌨️',
    }
    
    # カテゴリ別の色定義
    CATEGORY_COLORS = {
        'development': ('rgba(76, 175, 80, 0.8)', 'rgba(56, 142, 60, 1.0)'),    # Green
        'browser': ('rgba(33, 150, 243, 0.8)', 'rgba(25, 118, 210, 1.0)'),      # Blue
        'communication': ('rgba(156, 39, 176, 0.8)', 'rgba(123, 31, 162, 1.0)'), # Purple
        'creative': ('rgba(255, 152, 0, 0.8)', 'rgba(230, 126, 34, 1.0)'),      # Orange
        'utility': ('rgba(96, 125, 139, 0.8)', 'rgba(69, 90, 100, 1.0)'),       # Blue Grey
        'document': ('rgba(63, 81, 181, 0.8)', 'rgba(48, 63, 159, 1.0)'),       # Indigo
        'google': ('rgba(244, 67, 54, 0.8)', 'rgba(211, 47, 47, 1.0)'),         # Red
        'microsoft': ('rgba(0, 150, 136, 0.8)', 'rgba(0, 121, 107, 1.0)'),      # Teal
        'default': ('rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)')      # Default gradient
    }
    
    # アプリ名とカテゴリのマッピング
    CATEGORY_PATTERNS = {
        'development': [r'(visual studio|vs code|code|xcode|cursor|windsurf|zed|jetbrains|toolbox|docker|github|anaconda|iterm|terminal|devtoys|pgadmin)'],
        'browser': [r'(chrome|safari|firefox|arc)'],
        'communication': [r'(discord|zoom|teams|outlook)'],
        'creative': [r'(imovie|garageband|keynote|pages|numbers)'],
        'utility': [r'(raycast|commander|finder|dropbox|onedrive|google drive|defender|karabiner|logi|hhkb)'],
        'document': [r'(notion|obsidian|kindle|upnote)'],
        'google': [r'(google docs|google sheets|google slides|google drive)'],
        'microsoft': [r'(word|excel|powerpoint|onenote|teams|outlook|onedrive)']
    }
    
    @classmethod
    def get_app_icon(cls, app_name: str) -> str:
        """アプリ名からアイコンを取得"""
        app_name_lower = app_name.lower()
        
        for pattern, icon in cls.ICON_PATTERNS.items():
            if re.search(pattern, app_name_lower):
                return icon
        
        # デフォルトアイコン（アプリ名の最初の文字）
        return app_name[0].upper() if app_name else '📱'
    
    @classmethod
    def get_app_category(cls, app_name: str) -> str:
        """アプリ名からカテゴリを取得"""
        app_name_lower = app_name.lower()
        
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, app_name_lower):
                    return category
        
        return 'default'
    
    @classmethod
    def get_app_colors(cls, app_name: str) -> Tuple[str, str]:
        """アプリ名から色を取得（normal, hover）"""
        category = cls.get_app_category(app_name)
        return cls.CATEGORY_COLORS.get(category, cls.CATEGORY_COLORS['default'])
    
    @classmethod
    def get_display_name(cls, app_name: str, max_length: int = 12) -> str:
        """表示用の短縮名を取得"""
        if len(app_name) <= max_length:
            return app_name
        
        # 重要な単語を抽出
        important_words = ['VS', 'Code', 'Chrome', 'Safari', 'Firefox', 'Teams', 'Word', 'Excel']
        
        for word in important_words:
            if word.lower() in app_name.lower():
                return word
        
        # スペースで分割して最初の単語を使用
        first_word = app_name.split()[0]
        if len(first_word) <= max_length:
            return first_word
        
        # 文字数制限で切り詰め
        return app_name[:max_length-1] + '…'

    @classmethod
    def get_app_info(cls, app_name: str) -> Dict[str, str]:
        """アプリの完全な情報を取得"""
        return {
            'icon': cls.get_app_icon(app_name),
            'display_name': cls.get_display_name(app_name),
            'category': cls.get_app_category(app_name),
            'colors': cls.get_app_colors(app_name),
            'full_name': app_name
        }