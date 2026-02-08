#!/usr/bin/env python3
"""
Translate lyrics to Chinese with line-by-line format
Supports: Google Translate (free), Baidu API, Youdao API
"""

import sys
import os
import re
import json
import io
import time
import hashlib
import random
import urllib.request
import urllib.parse
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def load_config():
    """Load configuration from config.json."""
    possible_paths = [
        Path(__file__).parent.parent / "config.json",
        Path.cwd() / "config.json",
    ]
    
    for path in possible_paths:
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    
    return {"proxy": {"enabled": False}, "translation": {}}


def is_section_marker(line):
    """Check if line is a section marker like [Verse 1]."""
    return bool(re.match(r'^\[.+\]$', line.strip()))


def translate_with_google(texts, delay=0.1):
    """Translate texts using Google Translate."""
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target='zh-CN')
        
        results = {}
        total = len(texts)
        for i, text in enumerate(texts):
            if text.strip():
                try:
                    results[text] = translator.translate(text)
                    if (i + 1) % 10 == 0:
                        print(f"    Progress: {i + 1}/{total}")
                except Exception as e:
                    print(f"    Warning: Failed to translate line {i + 1}: {e}")
                    results[text] = text
                if i < len(texts) - 1:
                    time.sleep(delay)
            else:
                results[text] = text
        return results
    except ImportError:
        print("    [X] deep_translator not found. Install: pip install deep_translator")
        return {text: text for text in texts}


def translate_with_baidu(text, appid, secret_key):
    """Translate using Baidu API."""
    if not text.strip():
        return text
    
    salt = random.randint(32768, 65536)
    sign_str = appid + text + str(salt) + secret_key
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    params = {
        'q': text,
        'from': 'auto',
        'to': 'zh',
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    
    try:
        url = 'https://fanyi-api.baidu.com/api/trans/vip/translate?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
    except Exception:
        pass
    
    return text


def parse_lyrics_file(filepath):
    """Parse lyrics file and return (artist, song, lines)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = Path(filepath).stem
        if ' - ' in filename:
            artist, song = filename.split(' - ', 1)
        else:
            artist, song = "Unknown Artist", "Unknown Song"
        
        return artist.strip(), song.strip(), content.split('\n')
    except Exception as e:
        print(f"[X] Error reading file: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python translate_lyrics.py <input_file> [output_path]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else Path(input_file).parent
    config = load_config()
    
    print(f"Reading: {input_file}")
    
    result = parse_lyrics_file(input_file)
    if not result:
        sys.exit(1)
    
    artist, song, lines = result
    print(f"Found: {artist} - {song}")
    print(f"Lines: {len(lines)}")
    
    # Filter lines to translate (skip empty and section markers)
    to_translate = []
    for line in lines:
        stripped = line.strip()
        if stripped and not is_section_marker(stripped):
            to_translate.append(stripped)
    
    print(f"Translatable: {len(to_translate)}")
    
    # Translate
    print("Translating with Google...")
    translations = translate_with_google(to_translate, delay=0.3)
    
    # Build output - FIX: section markers only appear once
    output_lines = []
    trans_idx = 0
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            output_lines.append('')  # Empty line for paragraph break
        elif is_section_marker(stripped):
            output_lines.append(stripped)  # Section marker - only once!
            output_lines.append('')  # Empty line after marker
        else:
            orig = to_translate[trans_idx]
            trans = translations.get(orig, orig)
            output_lines.append(orig)
            output_lines.append(trans)
            trans_idx += 1
    
    # Save
    safe_artist = re.sub(r'[<>:"/\\|?*]', '', artist).strip()
    safe_song = re.sub(r'[<>:"/\\|?*]', '', song).strip()
    filename = f"{safe_artist} - {safe_song} (translated chinese).txt"
    filepath = Path(output_path) / filename
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"[OK] Saved: {filepath}")


if __name__ == "__main__":
    main()
