"""
Baidu Translate API implementation.
"""

import hashlib
import json
import random
import urllib.request
import urllib.parse
from .base import BaseTranslator


class BaiduTranslator(BaseTranslator):
    """Baidu Translate API."""

    def __init__(self, appid: str, secret_key: str):
        self.appid = appid
        self.secret_key = secret_key
        self.api_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

    @property
    def name(self) -> str:
        return "Baidu Translate"

    @property
    def is_available(self) -> bool:
        return bool(self.appid and self.secret_key)

    def translate(self, text: str, source: str = 'auto', target: str = 'zh') -> str:
        if not text.strip() or not self.is_available:
            return text

        # Language mapping
        lang_map = {'auto': 'auto', 'en': 'en', 'zh': 'zh', 'zh-CN': 'zh', 'ja': 'jp', 'ko': 'kor'}
        from_lang = lang_map.get(source, source)
        to_lang = lang_map.get(target, target)

        salt = random.randint(32768, 65536)
        sign_str = self.appid + text + str(salt) + self.secret_key
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appid': self.appid,
            'salt': salt,
            'sign': sign
        }

        try:
            url = self.api_url + '?' + urllib.parse.urlencode(params)
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                if 'trans_result' in result:
                    return '\n'.join([item['dst'] for item in result['trans_result']])
        except Exception:
            pass

        return text
