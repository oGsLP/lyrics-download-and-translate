#!/usr/bin/env python3
"""
Multi-source translation module.
Supports: Google Translate, Baidu Translate, Youdao Translate
"""

import re
import json
import urllib.request
import urllib.parse
import random
import hashlib
from typing import Optional
from abc import ABC, abstractmethod


class TranslationSource(ABC):
    """Base class for translation sources."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'zh') -> Optional[str]:
        """Translate text. Returns translated text or None if failed."""
        pass


class GoogleTranslateSource(TranslationSource):
    """Google Translate via deep_translator or googletrans."""
    
    def __init__(self):
        super().__init__("Google Translate")
        self.chunk_size = 4000
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'zh-CN') -> Optional[str]:
        try:
            # Try deep_translator first
            from deep_translator import GoogleTranslator
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            
            # Split text into chunks if too long
            if len(text) <= self.chunk_size:
                return translator.translate(text)
            
            # Chunk translation
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < self.chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            translated_chunks = []
            for chunk in chunks:
                if chunk.strip():
                    try:
                        translated = translator.translate(chunk)
                        translated_chunks.append(translated)
                    except Exception as e:
                        print(f"    Warning: Chunk translation failed: {e}")
                        translated_chunks.append(f"[Translation error: {e}]")
            
            return '\n\n'.join(translated_chunks)
            
        except ImportError:
            # Try googletrans as fallback
            try:
                from googletrans import Translator
                translator = Translator()
                
                if len(text) <= self.chunk_size:
                    result = translator.translate(text, src=source_lang, dest=target_lang)
                    return result.text if result else None
                
                # Chunk translation
                paragraphs = text.split('\n\n')
                chunks = []
                current_chunk = ""
                
                for para in paragraphs:
                    if len(current_chunk) + len(para) < self.chunk_size:
                        current_chunk += para + "\n\n"
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = para + "\n\n"
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                translated_chunks = []
                for chunk in chunks:
                    if chunk.strip():
                        result = translator.translate(chunk, src=source_lang, dest=target_lang)
                        if result:
                            translated_chunks.append(result.text)
                
                return '\n\n'.join(translated_chunks)
                
            except ImportError:
                print("    [X] No Google Translate library found.")
                return None
        except Exception as e:
            print(f"    [X] Google Translate error: {e}")
            return None


class BaiduTranslateSource(TranslationSource):
    """Baidu Translate API (requires appid and key)."""
    
    def __init__(self, appid: str = None, secret_key: str = None):
        super().__init__("Baidu Translate")
        self.appid = appid
        self.secret_key = secret_key
        self.api_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        self.chunk_size = 6000  # Baidu allows up to 6000 chars
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'zh') -> Optional[str]:
        if not self.appid or not self.secret_key:
            print("    [X] Baidu Translate requires appid and secret_key.")
            return None
        
        # Map language codes to Baidu format
        lang_map = {
            'auto': 'auto',
            'en': 'en',
            'zh': 'zh',
            'zh-CN': 'zh',
            'zh-TW': 'cht',
            'ja': 'jp',
            'ko': 'kor',
            'fr': 'fra',
            'es': 'spa',
            'de': 'de',
        }
        
        from_lang = lang_map.get(source_lang, source_lang)
        to_lang = lang_map.get(target_lang, target_lang)
        
        try:
            # Baidu has a 6000 char limit, so we may need to chunk
            if len(text) <= self.chunk_size:
                return self._translate_chunk(text, from_lang, to_lang)
            
            # Chunk translation
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < self.chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    print(f"    Translating chunk {i+1}/{len(chunks)}...")
                    result = self._translate_chunk(chunk, from_lang, to_lang)
                    if result:
                        translated_chunks.append(result)
                    else:
                        translated_chunks.append(f"[Translation error for chunk {i+1}]")
            
            return '\n\n'.join(translated_chunks)
            
        except Exception as e:
            print(f"    [X] Baidu Translate error: {e}")
            return None
    
    def _translate_chunk(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """Translate a single chunk using Baidu API."""
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
        
        url = self.api_url + '?' + urllib.parse.urlencode(params)
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'trans_result' in result:
                    translations = [item['dst'] for item in result['trans_result']]
                    return '\n'.join(translations)
                elif 'error_code' in result:
                    print(f"    Baidu API error: {result.get('error_msg', 'Unknown error')}")
                    return None
        except Exception as e:
            print(f"    Baidu request error: {e}")
        
        return None


class YoudaoTranslateSource(TranslationSource):
    """Youdao Translate API (requires appkey and key)."""
    
    def __init__(self, appkey: str = None, secret_key: str = None):
        super().__init__("Youdao Translate")
        self.appkey = appkey
        self.secret_key = secret_key
        self.api_url = 'https://openapi.youdao.com/api'
        self.chunk_size = 5000
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'zh-CHS') -> Optional[str]:
        if not self.appkey or not self.secret_key:
            print("    [X] Youdao Translate requires appkey and secret_key.")
            return None
        
        # Map language codes
        lang_map = {
            'auto': 'auto',
            'en': 'en',
            'zh': 'zh-CHS',
            'zh-CN': 'zh-CHS',
            'zh-TW': 'zh-CHT',
            'ja': 'ja',
            'ko': 'ko',
            'fr': 'fr',
            'es': 'es',
            'de': 'de',
        }
        
        from_lang = lang_map.get(source_lang, source_lang)
        to_lang = lang_map.get(target_lang, target_lang)
        
        try:
            if len(text) <= self.chunk_size:
                return self._translate_chunk(text, from_lang, to_lang)
            
            # Chunk translation
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) < self.chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    print(f"    Translating chunk {i+1}/{len(chunks)}...")
                    result = self._translate_chunk(chunk, from_lang, to_lang)
                    if result:
                        translated_chunks.append(result)
                    else:
                        translated_chunks.append(f"[Translation error for chunk {i+1}]")
            
            return '\n\n'.join(translated_chunks)
            
        except Exception as e:
            print(f"    [X] Youdao Translate error: {e}")
            return None
    
    def _translate_chunk(self, text: str, from_lang: str, to_lang: str) -> Optional[str]:
        """Translate a single chunk using Youdao API."""
        import time
        import uuid
        
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
                    return result.get('translation', [None])[0]
                else:
                    print(f"    Youdao API error: {result.get('errorCode')}")
                    return None
        except Exception as e:
            print(f"    Youdao request error: {e}")
        
        return None
    
    def _truncate(self, text: str) -> str:
        """Truncate text for Youdao sign generation (if >20 chars)."""
        if len(text) <= 20:
            return text
        return text[:10] + str(len(text)) + text[-10:]


class MultiSourceTranslator:
    """Translator that tries multiple sources."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.sources = self._init_sources()
    
    def _init_sources(self) -> list:
        """Initialize translation sources."""
        sources: list = [GoogleTranslateSource()]
        
        # Add Baidu if configured
        baidu_config = self.config.get('baidu', {})
        if baidu_config.get('appid') and baidu_config.get('secret_key'):
            sources.append(BaiduTranslateSource(
                baidu_config['appid'],
                baidu_config['secret_key']
            ))
        
        # Add Youdao if configured
        youdao_config = self.config.get('youdao', {})
        if youdao_config.get('appkey') and youdao_config.get('secret_key'):
            sources.append(YoudaoTranslateSource(
                youdao_config['appkey'],
                youdao_config['secret_key']
            ))
        
        return sources
    
    def translate(self, text: str, source_lang: str = 'auto', target_lang: str = 'zh-CN') -> Optional[str]:
        """
        Try to translate using multiple sources.
        Returns the first successful translation.
        """
        for source in self.sources:
            print(f"  Trying {source.name}...")
            try:
                result = source.translate(text, source_lang, target_lang)
                if result:
                    print(f"  [OK] Translation successful with {source.name}!")
                    return result
            except Exception as e:
                print(f"  [X] {source.name} failed: {e}")
                continue
        
        print("\n[X] All translation sources failed.")
        return None


# Convenience function
def translate_text(text: str, source_lang: str = 'auto', target_lang: str = 'zh-CN', 
                   config: dict = None) -> Optional[str]:
    """Translate text using multiple sources."""
    translator = MultiSourceTranslator(config)
    return translator.translate(text, source_lang, target_lang)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python translate_sources.py \"Text to translate\"")
        sys.exit(1)
    
    text = sys.argv[1]
    
    # Example config (replace with actual credentials)
    config = {
        # 'baidu': {
        #     'appid': 'your_appid',
        #     'secret_key': 'your_secret_key'
        # },
        # 'youdao': {
        #     'appkey': 'your_appkey',
        #     'secret_key': 'your_secret_key'
        # }
    }
    
    result = translate_text(text, config=config)
    
    if result:
        print("\n" + "="*60)
        print("Original:", text)
        print("Translated:", result)
    else:
        print("\nTranslation failed.")
