"""
Translation module supporting multiple translation services.
Supports: Google Translate (free), Baidu API, Youdao API
"""

import re
import time
import hashlib
import random
import urllib.request
import urllib.parse
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional


class BaseTranslator(ABC):
    """Abstract base class for translators."""
    
    @abstractmethod
    def translate(self, text: str, source: str = 'auto', target: str = 'zh') -> str:
        """Translate text and return result."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return translator name."""
        pass
    
    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if translator is properly configured."""
        pass


class GoogleTranslator(BaseTranslator):
    """Google Translate via deep_translator (free)."""
    
    def __init__(self):
        self._translator = None
        self._init_translator()
    
    def _init_translator(self):
        try:
            from deep_translator import GoogleTranslator as GT
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
        
        import uuid
        
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


class MultiTranslator:
    """Manager for multiple translation services with fallback."""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.translators: List[BaseTranslator] = []
        self._init_translators()
    
    def _init_translators(self):
        """Initialize all available translators."""
        # Google Translate (always try first)
        google = GoogleTranslator()
        if google.is_available:
            self.translators.append(google)
        
        # Baidu Translate
        baidu_config = self.config.get('baidu', {})
        baidu = BaiduTranslator(
            baidu_config.get('appid', ''),
            baidu_config.get('secret_key', '')
        )
        if baidu.is_available:
            self.translators.append(baidu)
        
        # Youdao Translate
        youdao_config = self.config.get('youdao', {})
        youdao = YoudaoTranslator(
            youdao_config.get('appkey', ''),
            youdao_config.get('secret_key', '')
        )
        if youdao.is_available:
            self.translators.append(youdao)
    
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
        
        # Use Google for batch translation (most reliable)
        for translator in self.translators:
            if isinstance(translator, GoogleTranslator):
                return translator.translate_batch(texts, delay)
        
        # Fallback to individual translations
        results = {}
        for text in texts:
            results[text] = self.translate(text)
            time.sleep(delay)
        return results
    
    @property
    def available_translators(self) -> List[str]:
        """List names of available translators."""
        return [t.name for t in self.translators]
