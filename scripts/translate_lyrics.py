#!/usr/bin/env python3
"""
Translate lyrics to Chinese

Usage:
    python translate_lyrics.py <input_file> [output_path]
    python translate_lyrics.py "lyrics/Crime - Beyond Awareness.txt" "output/"

Arguments:
    input_file: Path to lyrics file
    output_path: Optional output directory (default: same as input)

Output:
    Saves translated lyrics to: {output_path}/{Artist} - {Song} (translated chinese).txt

Note:
    This script requires one of the following translation methods:
    1. Google Translate (default) - requires googletrans or deep_translator package
    2. Youdao Translate - requires API key
    3. Baidu Translate - requires API key
"""

import sys
import os
import re
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def translate_with_google(text, source='auto', target='zh-CN'):
    """
    Translate text using Google Translate via deep_translator library.
    
    Args:
        text: Text to translate
        source: Source language code (default: auto-detect)
        target: Target language code (default: zh-CN for Chinese)
        
    Returns:
        str: Translated text or None if failed
    """
    try:
        # Try deep_translator first (more reliable)
        from deep_translator import GoogleTranslator
        
        # GoogleTranslator has a character limit per request, so we need to chunk
        max_chunk = 4000
        chunks = []
        
        # Split by paragraphs to keep context
        paragraphs = text.split('\n\n')
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
        
        # Translate each chunk
        translated_chunks = []
        translator = GoogleTranslator(source=source, target=target)
        
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                try:
                    translated = translator.translate(chunk)
                    translated_chunks.append(translated)
                except Exception as e:
                    print(f"Warning: Failed to translate chunk {i+1}: {e}")
                    translated_chunks.append(f"[Translation error for section {i+1}]")
        
        return '\n\n'.join(translated_chunks)
        
    except ImportError:
        # Fallback to googletrans
        try:
            from googletrans import Translator
            translator = Translator()
            
            # googletrans also has limits, chunk if necessary
            max_chunk = 4000
            if len(text) <= max_chunk:
                result = translator.translate(text, src=source, dest=target)
                return result.text if result else None
            else:
                # Split and translate in chunks
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
                for chunk in chunks:
                    if chunk.strip():
                        result = translator.translate(chunk, src=source, dest=target)
                        if result:
                            translated_chunks.append(result.text)
                
                return '\n\n'.join(translated_chunks)
                
        except ImportError:
            print("[X] Translation library not found.")
            print("    Install one of the following:")
            print("    pip install deep_translator")
            print("    pip install googletrans==4.0.0-rc1")
            return None
        except Exception as e:
            print(f"[X] Translation error: {e}")
            return None
    except Exception as e:
        print(f"[X] Translation error: {e}")
        return None


def parse_lyrics_file(filepath):
    """
    Parse a lyrics file and extract metadata and lyrics.
    
    Args:
        filepath: Path to lyrics file
        
    Returns:
        tuple: (artist, song, lyrics) or None if failed
    """
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
        
        # Find the separator line and extract lyrics after it
        lyrics_start = 0
        for i, line in enumerate(lines):
            if '=' in line and len(line) > 20:  # Likely the separator
                lyrics_start = i + 1
                break
        
        if lyrics_start == 0:
            # Look for first empty line after header
            for i in range(1, min(len(lines), 5)):
                if lines[i].strip() == '':
                    lyrics_start = i + 1
                    break
        
        lyrics = '\n'.join(lines[lyrics_start:]).strip()
        
        return artist, song, lyrics
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None


def save_translated_lyrics(artist, song, original_lyrics, translated_lyrics, output_path):
    """
    Save translated lyrics to a file with both original and translation.
    
    Args:
        artist: Artist name
        song: Song title
        original_lyrics: Original lyrics text
        translated_lyrics: Translated lyrics text
        output_path: Output directory
        
    Returns:
        str: Path to saved file
    """
    # Clean filename
    safe_artist = re.sub(r'[<>:"/\\|?*]', '', artist).strip()
    safe_song = re.sub(r'[<>:"/\\|?*]', '', song).strip()
    
    filename = f"{safe_artist} - {safe_song} (translated chinese).txt"
    filepath = Path(output_path) / filename
    
    # Ensure output directory exists
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{artist} - {song}\n")
        f.write("=" * 50 + "\n")
        f.write("Original Lyrics | 中文翻译\n")
        f.write("=" * 50 + "\n\n")
        
        # Write original and translation side by side or interleaved
        # For better readability, we'll do paragraph by paragraph
        orig_paragraphs = original_lyrics.split('\n\n')
        trans_paragraphs = translated_lyrics.split('\n\n')
        
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
        print("Usage: python translate_lyrics.py <input_file> [output_path]")
        print("Example: python translate_lyrics.py \"lyrics/Song.txt\" \"output/\"")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Default output path is same as input file's directory
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = Path(input_file).parent
    
    print(f"Reading lyrics from: {input_file}")
    
    # Parse the lyrics file
    result = parse_lyrics_file(input_file)
    if not result:
        print("[X] Could not parse lyrics file")
        print("    Make sure the file follows the format:")
        print("    Artist Name - Song Title")
        print("    ==================================================")
        print("    Lyrics content...")
        sys.exit(1)
    
    artist, song, lyrics = result
    print(f"Found lyrics: {artist} - {song}")
    print(f"Lyrics length: {len(lyrics)} characters")
    
    # Translate
    print("Translating to Chinese...")
    print("(This may take a moment for longer songs)")
    
    translated = translate_with_google(lyrics)
    if not translated:
        print("[X] Translation failed")
        print("    Common causes:")
        print("    - No internet connection")
        print("    - Google Translate rate limit (wait a moment and retry)")
        print("    - Missing translation library (pip install deep_translator)")
        sys.exit(1)
    
    print("[OK] Translation completed")
    
    # Save translated lyrics
    filepath = save_translated_lyrics(artist, song, lyrics, translated, output_path)
    print(f"[OK] Saved translated lyrics to: {filepath}")


if __name__ == "__main__":
    main()
