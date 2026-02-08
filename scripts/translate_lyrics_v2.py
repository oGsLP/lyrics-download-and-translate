#!/usr/bin/env python3
"""
Translate lyrics to Chinese using multiple translation sources
Supports: Google Translate (free), Baidu API, Youdao API

Usage:
    python translate_lyrics_v2.py <input_file> [output_path] [--config config.json]
    python translate_lyrics_v2.py "lyrics/Song.txt" "output/"

Arguments:
    input_file: Path to lyrics file
    output_path: Optional output directory (default: same as input)
    --config: Optional config file with API keys for Baidu/Youdao

Output:
    Saves translated lyrics to: {output_path}/{Artist} - {Song} (translated chinese).txt
"""

import sys
import os
import re
import json
import io
import urllib.request
import urllib.parse
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def translate_with_google(text: str, source: str = 'auto', target: str = 'zh-CN') -> str:
    """Translate using Google Translate via deep_translator."""
    try:
        from deep_translator import GoogleTranslator
        
        max_chunk = 4000
        if len(text) <= max_chunk:
            translator = GoogleTranslator(source=source, target=target)
            return translator.translate(text)
        
        # Chunk translation
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_chunk:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        translator = GoogleTranslator(source=source, target=target)
        translated_chunks = []
        
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                try:
                    translated = translator.translate(chunk)
                    translated_chunks.append(translated)
                except Exception as e:
                    print(f"    Warning: Chunk {i+1} failed: {e}")
                    translated_chunks.append(f"[Translation error in section {i+1}]")
        
        return '\n\n'.join(translated_chunks)
        
    except ImportError:
        print("    [X] deep_translator not found. Install: pip install deep_translator")
        return None
    except Exception as e:
        print(f"    [X] Google Translate error: {e}")
        return None


def translate_with_baidu(text: str, config: dict, source: str = 'auto', target: str = 'zh') -> str:
    """Translate using Baidu Translate API."""
    import random
    import hashlib
    
    appid = config.get('appid')
    secret_key = config.get('secret_key')
    
    if not appid or not secret_key:
        print("    [X] Baidu API requires appid and secret_key in config")
        return None
    
    # Language mapping
    lang_map = {'auto': 'auto', 'en': 'en', 'zh': 'zh', 'zh-CN': 'zh', 'ja': 'jp', 'ko': 'kor', 'fr': 'fra', 'es': 'spa'}
    from_lang = lang_map.get(source, source)
    to_lang = lang_map.get(target, target)
    
    max_chunk = 6000
    if len(text) <= max_chunk:
        return _baidu_translate_chunk(text, appid, secret_key, from_lang, to_lang)
    
    # Chunk translation
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk:
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
            print(f"    Translating chunk {i+1}/{len(chunks)} with Baidu...")
            result = _baidu_translate_chunk(chunk, appid, secret_key, from_lang, to_lang)
            if result:
                translated_chunks.append(result)
            else:
                translated_chunks.append(f"[Translation error in section {i+1}]")
    
    return '\n\n'.join(translated_chunks)


def _baidu_translate_chunk(text: str, appid: str, secret_key: str, from_lang: str, to_lang: str) -> str:
    """Translate a single chunk using Baidu API."""
    import random
    import hashlib
    
    salt = random.randint(32768, 65536)
    sign_str = appid + text + str(salt) + secret_key
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    params = {
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    
    try:
        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if 'trans_result' in result:
                return '\n'.join([item['dst'] for item in result['trans_result']])
            elif 'error_code' in result:
                print(f"    Baidu API error: {result.get('error_msg', 'Unknown')}")
    except Exception as e:
        print(f"    Baidu request error: {e}")
    
    return None


def translate_with_youdao(text: str, config: dict, source: str = 'auto', target: str = 'zh-CHS') -> str:
    """Translate using Youdao Translate API."""
    import time
    import uuid
    import hashlib
    
    appkey = config.get('appkey')
    secret_key = config.get('secret_key')
    
    if not appkey or not secret_key:
        print("    [X] Youdao API requires appkey and secret_key in config")
        return None
    
    # Language mapping
    lang_map = {'auto': 'auto', 'en': 'en', 'zh': 'zh-CHS', 'zh-CN': 'zh-CHS', 'ja': 'ja', 'ko': 'ko'}
    from_lang = lang_map.get(source, source)
    to_lang = lang_map.get(target, target)
    
    max_chunk = 5000
    if len(text) <= max_chunk:
        return _youdao_translate_chunk(text, appkey, secret_key, from_lang, to_lang)
    
    # Chunk translation
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk:
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
            print(f"    Translating chunk {i+1}/{len(chunks)} with Youdao...")
            result = _youdao_translate_chunk(chunk, appkey, secret_key, from_lang, to_lang)
            if result:
                translated_chunks.append(result)
            else:
                translated_chunks.append(f"[Translation error in section {i+1}]")
    
    return '\n\n'.join(translated_chunks)


def _youdao_translate_chunk(text: str, appkey: str, secret_key: str, from_lang: str, to_lang: str) -> str:
    """Translate a single chunk using Youdao API."""
    import time
    import uuid
    import hashlib
    
    curtime = str(int(time.time()))
    salt = str(uuid.uuid1())
    
    def truncate(s):
        if len(s) <= 20:
            return s
        return s[:10] + str(len(s)) + s[-10:]
    
    sign_str = appkey + truncate(text) + salt + curtime + secret_key
    sign = hashlib.sha256(sign_str.encode()).hexdigest()
    
    url = 'https://openapi.youdao.com/api'
    params = {
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'appKey': appkey,
        'salt': salt,
        'sign': sign,
        'signType': 'v3',
        'curtime': curtime
    }
    
    try:
        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('errorCode') == '0':
                return result.get('translation', [None])[0]
            else:
                print(f"    Youdao API error: {result.get('errorCode')}")
    except Exception as e:
        print(f"    Youdao request error: {e}")
    
    return None


def translate_multi_source(text: str, config: dict = None) -> str:
    """
    Try multiple translation sources.
    Order: Google (free) -> Baidu (if configured) -> Youdao (if configured)
    """
    config = config or {}
    
    # Try Google first (free)
    print("  Trying Google Translate...")
    result = translate_with_google(text)
    if result:
        print("  [OK] Translation successful with Google Translate!")
        return result
    
    # Try Baidu if configured
    baidu_config = config.get('baidu')
    if baidu_config:
        print("  Trying Baidu Translate...")
        result = translate_with_baidu(text, baidu_config)
        if result:
            print("  [OK] Translation successful with Baidu!")
            return result
    
    # Try Youdao if configured
    youdao_config = config.get('youdao')
    if youdao_config:
        print("  Trying Youdao Translate...")
        result = translate_with_youdao(text, youdao_config)
        if result:
            print("  [OK] Translation successful with Youdao!")
            return result
    
    print("\n[X] All translation sources failed.")
    return None


def parse_lyrics_file(filepath: str) -> tuple:
    """Parse a lyrics file and extract metadata and lyrics."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # First line should be "Artist - Song"
        header = lines[0].strip()
        header_match = re.match(r'(.+?)\s+-\s+(.+)', header)
        
        if header_match:
            artist = header_match.group(1).strip()
            song = header_match.group(2).strip()
        else:
            artist = "Unknown Artist"
            song = "Unknown Song"
        
        # Find the separator line
        lyrics_start = 0
        for i, line in enumerate(lines):
            if '=' in line and len(line) > 20:
                lyrics_start = i + 1
                break
        
        if lyrics_start == 0:
            for i in range(1, min(len(lines), 5)):
                if lines[i].strip() == '':
                    lyrics_start = i + 1
                    break
        
        lyrics = '\n'.join(lines[lyrics_start:]).strip()
        return artist, song, lyrics
    except Exception as e:
        print(f"[X] Error reading file: {e}")
        return None


def save_translated_lyrics(artist: str, song: str, original: str, translated: str, output_path: str):
    """Save translated lyrics to a file."""
    safe_artist = re.sub(r'[<>:"/\\|?*]', '', artist).strip()
    safe_song = re.sub(r'[<>:"/\\|?*]', '', song).strip()
    
    filename = f"{safe_artist} - {safe_song} (translated chinese).txt"
    filepath = Path(output_path) / filename
    
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{artist} - {song}\n")
        f.write("=" * 50 + "\n")
        f.write("Original Lyrics | 中文翻译\n")
        f.write("=" * 50 + "\n\n")
        
        orig_paragraphs = original.split('\n\n')
        trans_paragraphs = translated.split('\n\n')
        
        for i, orig in enumerate(orig_paragraphs):
            if orig.strip():
                f.write("【原文】\n")
                f.write(orig.strip() + "\n\n")
                
                if i < len(trans_paragraphs) and trans_paragraphs[i].strip():
                    f.write("【翻译】\n")
                    f.write(trans_paragraphs[i].strip() + "\n\n")
                
                f.write("-" * 30 + "\n\n")
    
    return str(filepath)


def main():
    if len(sys.argv) < 2:
        print("Usage: python translate_lyrics_v2.py <input_file> [output_path] [--config config.json]")
        print("Example: python translate_lyrics_v2.py \"lyrics/Song.txt\" \"output/\"")
        print("")
        print("Translation sources (in order):")
        print("  1. Google Translate (free, no API key needed)")
        print("  2. Baidu Translate (requires API key)")
        print("  3. Youdao Translate (requires API key)")
        print("")
        print("Config file format (config.json):")
        print('  {')
        print('    "baidu": {')
        print('      "appid": "your_appid",')
        print('      "secret_key": "your_secret_key"')
        print('    },')
        print('    "youdao": {')
        print('      "appkey": "your_appkey",')
        print('      "secret_key": "your_secret_key"')
        print('    }')
        print('  }')
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_path = Path(input_file).parent
    config_file = None
    
    # Parse arguments
    if len(sys.argv) > 2:
        if sys.argv[2] != '--config':
            output_path = sys.argv[2]
        if '--config' in sys.argv:
            config_idx = sys.argv.index('--config')
            if config_idx + 1 < len(sys.argv):
                config_file = sys.argv[config_idx + 1]
    
    # Load config if provided
    config = {}
    if config_file:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"Loaded config from: {config_file}")
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
    
    print(f"Reading lyrics from: {input_file}")
    
    result = parse_lyrics_file(input_file)
    if not result:
        print("[X] Could not parse lyrics file")
        sys.exit(1)
    
    artist, song, lyrics = result
    print(f"Found lyrics: {artist} - {song}")
    print(f"Lyrics length: {len(lyrics)} characters\n")
    
    # Translate
    print("Translating to Chinese...")
    print("(This may take a moment for longer songs)\n")
    
    translated = translate_multi_source(lyrics, config)
    if not translated:
        print("\n[X] Translation failed")
        print("    Common causes:")
        print("    - No internet connection")
        print("    - Google Translate rate limit (wait and retry)")
        print("    - Missing deep_translator library: pip install deep_translator")
        sys.exit(1)
    
    print("\n[OK] Translation completed")
    
    # Save
    filepath = save_translated_lyrics(artist, song, lyrics, translated, output_path)
    print(f"[OK] Saved to: {filepath}")


if __name__ == "__main__":
    main()
