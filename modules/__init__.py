"""
Lyrics Download and Translate - Modules
"""

from .config import config, Config
from .proxy import proxy_handler, ProxyHandler
from .translators import (
    TranslationManager,
    GoogleTranslator,
    BaiduTranslator,
    YoudaoTranslator
)
from .utils import clean_lyrics, is_section_marker

__all__ = [
    'config',
    'Config',
    'proxy_handler',
    'ProxyHandler',
    'TranslationManager',
    'GoogleTranslator',
    'BaiduTranslator',
    'YoudaoTranslator',
    'clean_lyrics',
    'is_section_marker'
]
