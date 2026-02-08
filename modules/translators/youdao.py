"""
Youdao Translate API implementation.
"""

import time
import hashlib
import json
import uuid
import urllib.request
import urllib.parse
from .base import BaseTranslator


class YoudaoTranslator(BaseTranslator):
    """Youdao Translate API."""

    def __init__(self, appkey: str, secret_key: str):
        self.appkey = appkey
        self.secret_key = secret_key
        self.api_url = 'https://openapi.youdao.com/api'

    @property
    def name(self) -> str:
        return "Youdao Translate"

    @property
    def is_available(self) -> bool:
        return bool(self.appkey and self.secret_key)

    def _truncate(self, text: str) -> str:
        """Truncate text for sign generation."""
        if len(text) <= 20:
            return text
        return text[:10] + str(len(text)) + text[-10:]

    def translate(self, text: str, source: str = 'auto', target: str = 'zh') -> str:
        if not text.strip() or not self.is_available:
            return text

        # Language mapping
        lang_map = {'auto': 'auto', 'en': 'en', 'zh': 'zh-CHS', 'zh-CN': 'zh-CHS'}
        from_lang = lang_map.get(source, source)
        to_lang = lang_map.get(target, target)

        curtime = str(int(time.time()))
        salt = str(uuid.uuid1())
        sign_str = self.appkey + self._truncate(text) + salt + curtime + self.secret_key
        sign = hashlib.sha256(sign_str.encode()).hexdigest()

        params = {
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'appKey': self.appkey,
            'salt': salt,
            'sign': sign,
            'signType': 'v3',
            'curtime': curtime
        }

        try:
            data = urllib.parse.urlencode(params).encode('utf-8')
            req = urllib.request.Request(self.api_url, data=data, method='POST')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get('errorCode') == '0':
                    return result.get('translation', [text])[0]
        except Exception:
            pass

        return text
