"""
Translators module - Multiple translation service support.
"""

from .base import BaseTranslator, TranslationResult
from .google import GoogleTranslator
from .baidu import BaiduTranslator
from .youdao import YoudaoTranslator
from .manager import TranslationManager

__all__ = [
    'BaseTranslator',
    'TranslationResult',
    'GoogleTranslator',
    'BaiduTranslator',
    'YoudaoTranslator',
    'TranslationManager',
]
