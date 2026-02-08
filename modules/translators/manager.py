"""
Translation manager - coordinates multiple translation services.
"""

import time
from typing import List, Dict
from .base import BaseTranslator
from .google import GoogleTranslator
from .baidu import BaiduTranslator
from .youdao import YoudaoTranslator


class TranslationManager:
    """Manager for multiple translation services with fallback."""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.translators: List[BaseTranslator] = []
        self._init_translators()

    def _init_translators(self):
        """Initialize all available translators."""
        # Youdao (priority if available)
        youdao_config = self.config.get('youdao', {})
        youdao = YoudaoTranslator(
            youdao_config.get('appkey', ''),
            youdao_config.get('secret_key', '')
        )
        if youdao.is_available:
            self.translators.append(youdao)

        # Baidu
        baidu_config = self.config.get('baidu', {})
        baidu = BaiduTranslator(
            baidu_config.get('appid', ''),
            baidu_config.get('secret_key', '')
        )
        if baidu.is_available:
            self.translators.append(baidu)

        # Google Translate (fallback)
        google = GoogleTranslator()
        if google.is_available:
            self.translators.append(google)

    def translate(self, text: str, source: str = 'auto', target: str = 'zh') -> str:
        """Try translators in order until one succeeds."""
        for translator in self.translators:
            try:
                result = translator.translate(text, source, target)
                if result and result != text:
                    return result
            except Exception:
                continue
        return text

    def translate_batch(self, texts: List[str], delay: float = 0.5) -> Dict[str, str]:
        """Batch translate using the first available translator."""
        if not self.translators:
            return {text: text for text in texts}

        # Use first available (priority: Youdao > Baidu > Google)
        for translator in self.translators:
            if isinstance(translator, GoogleTranslator):
                return translator.translate_batch(texts, delay)
            else:
                # For API-based translators, translate one by one
                results = {}
                for i, text in enumerate(texts):
                    if text.strip():
                        results[text] = translator.translate(text)
                        if (i + 1) % 10 == 0:
                            print(f"    Progress: {i + 1}/{len(texts)}")
                        if i < len(texts) - 1:
                            time.sleep(delay)
                    else:
                        results[text] = text
                return results

        # Fallback
        return {text: text for text in texts}

    @property
    def available_translators(self) -> List[str]:
        """List names of available translators."""
        return [t.name for t in self.translators]

    @property
    def primary_translator(self) -> str:
        """Return the name of the primary (first) translator."""
        if self.translators:
            return self.translators[0].name
        return "None"
