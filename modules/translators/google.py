"""
Google Translate implementation.
"""

import re
import time
from typing import List, Dict
from .base import BaseTranslator
from ..proxy import get_config


class GoogleTranslator(BaseTranslator):
    """Google Translate via deep_translator (free)."""

    def __init__(self):
        self._translator = None
        self._init_translator()

    def _init_translator(self):
        try:
            from deep_translator import GoogleTranslator as GT
            
            # Get proxy configuration
            config = get_config()
            proxy_config = config.get("proxy", {})
            
            proxies = None
            if proxy_config.get("enabled", False):
                http_proxy = proxy_config.get("http", "")
                https_proxy = proxy_config.get("https", "")
                if http_proxy or https_proxy:
                    proxies = {
                        "http": http_proxy,
                        "https": https_proxy if https_proxy else http_proxy
                    }
            
            # Initialize translator with proxy
            if proxies:
                self._translator = GT(source='auto', target='zh-CN', proxies=proxies)
            else:
                self._translator = GT(source='auto', target='zh-CN')
        except ImportError:
            self._translator = None

    @property
    def name(self) -> str:
        return "Google Translate"

    @property
    def is_available(self) -> bool:
        return self._translator is not None

    def translate(self, text: str, source: str = 'auto', target: str = 'zh') -> str:
        if not text.strip():
            return text

        # Don't translate section markers
        if re.match(r'^\[.+\]$', text.strip()):
            return text.strip()

        if not self._translator:
            return text

        try:
            return self._translator.translate(text)
        except Exception:
            return text

    def translate_batch(self, texts: List[str], delay: float = 0.5) -> Dict[str, str]:
        """Translate multiple texts with rate limiting."""
        results = {}

        for i, text in enumerate(texts):
            if text.strip() and not re.match(r'^\[.+\]$', text.strip()):
                results[text] = self.translate(text)
                if i < len(texts) - 1:
                    time.sleep(delay)
            else:
                results[text] = text.strip() if text.strip() else text

        return results
