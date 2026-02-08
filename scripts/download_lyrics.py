#!/usr/bin/env python3
"""
Download lyrics from multiple sources (Genius, AZLyrics, Letras, Musixmatch)

Usage:
    python download_lyrics.py "Artist Name" "Song Title" [output_path]
    python download_lyrics.py "Beyond Awareness" "Crime" "./lyrics/"

Arguments:
    artist: The artist name
    song: The song title
    output_path: Optional output directory (default: current directory)

Output:
    Saves lyrics to: {output_path}/{Artist} - {Song}.txt
    Format: Clean lyrics with section markers [Verse], [Chorus], etc.
"""

import sys
import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error
import socket
import html
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def clean_lyrics(lyrics: str) -> str:
    """
    Clean and format lyrics while preserving structure.
    Keeps [Verse], [Chorus], [Bridge] markers and maintains line breaks.
    """
    if not lyrics:
        return ""
    
    # Decode HTML entities
    lyrics = html.unescape(lyrics)
    
    # Remove HTML tags but preserve content
    lyrics = re.sub(r'<[^>]+>', '', lyrics)
    
    # Normalize line endings
    lyrics = lyrics.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove excessive blank lines (more than 2 consecutive)
    lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)
    
    # Remove leading/trailing whitespace from each line but keep structure
    lines = lyrics.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_line = line.strip()
        cleaned_lines.append(cleaned_line)
    
    lyrics = '\n'.join(cleaned_lines)
    
    # Final cleanup
    lyrics = lyrics.strip()
    
    return lyrics


def search_genius(artist: str, song: str, max_retries: int = 3) -> tuple:
    """
    Search Genius.com for lyrics.
    Returns: (success: bool, title: str, artist_name: str, lyrics: str, source: str)
    """
    query = f"{artist} {song}"
    search_url = f"https://genius.com/api/search/multi?q={urllib.parse.quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                sections = data.get('response', {}).get('sections', [])
                song_url = None
                
                for section in sections:
                    if section.get('type') == 'song':
                        hits = section.get('hits', [])
                        if hits:
                            song_url = hits[0].get('result', {}).get('url')
                            break
                    
                    if not song_url:
                        for hit in section.get('hits', []):
                            url = hit.get('result', {}).get('url')
                            if url and 'genius.com' in url:
                                song_url = url
                                break
                
                if song_url:
                    return extract_genius_lyrics(song_url)
                else:
                    return False, None, None, None, None
                        
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"    Warning: Search attempt {attempt + 1} failed, retrying...")
                import time
                time.sleep(2 ** attempt)
            else:
                print(f"    Genius error: {e}")
                return False, None, None, None, None
        except socket.timeout:
            if attempt < max_retries - 1:
                print(f"    Warning: Search timeout (attempt {attempt + 1}), retrying...")
                import time
                time.sleep(2 ** attempt)
            else:
                print(f"    Error: Search timed out after {max_retries} attempts")
                return False, None, None, None, None
        except Exception as e:
            print(f"    Genius error: {e}")
            return False, None, None, None, None
    
    return False, None, None, None, None


def extract_genius_lyrics(url: str) -> tuple:
    """Extract lyrics from Genius page."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
            song_title = title_match.group(1) if title_match else "Unknown"
            
            lyrics = None
            
            # Method 1: JSON-LD
            json_ld = re.search(r'<script type="application/ld\+json">([^<]+)</script>', html_content)
            if json_ld:
                try:
                    data = json.loads(json_ld.group(1))
                    lyrics = data.get('recordingOf', {}).get('lyrics', {}).get('text')
                except:
                    pass
            
            # Method 2: data-lyrics-container
            if not lyrics:
                containers = re.findall(r'<div[^>]*data-lyrics-container="true"[^>]*>(.*?)</div>', 
                                      html_content, re.DOTALL)
                if containers:
                    # Keep paragraph structure
                    lyrics_html = '\n\n'.join(containers)
                    lyrics = re.sub(r'<[^>]+>', '', lyrics_html)
            
            # Method 3: Lyrics__Container
            if not lyrics:
                containers = re.findall(r'<div[^>]*class="[^"]*Lyrics__Container[^"]*"[^>]*>(.*?)</div>',
                                      html_content, re.DOTALL)
                if containers:
                    lyrics_html = '\n\n'.join(containers)
                    lyrics = re.sub(r'<[^>]+>', '', lyrics_html)
            
            if lyrics:
                lyrics = clean_lyrics(lyrics)
                if lyrics:
                    return True, song_title, "Unknown", lyrics, "Genius"
    except Exception as e:
        print(f"    Genius extraction error: {e}")
    
    return False, None, None, None, None


def search_azlyrics(artist: str, song: str) -> tuple:
    """Search AZLyrics.com for lyrics."""
    artist_clean = re.sub(r'[^a-zA-Z0-9]', '', artist).lower()
    song_clean = re.sub(r'[^a-zA-Z0-9]', '', song).lower()
    url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{song_clean}.html"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            match = re.search(r'<!-- Usage of azlyrics\.com content.*?-->(.*?)<!--', 
                            html_content, re.DOTALL)
            if match:
                lyrics = match.group(1)
                lyrics = clean_lyrics(lyrics)
                
                if lyrics:
                    return True, song, artist, lyrics, "AZLyrics"
    except Exception as e:
        print(f"    AZLyrics error: {e}")
    
    return False, None, None, None, None


def search_musixmatch(artist: str, song: str) -> tuple:
    """Search Musixmatch.com for lyrics."""
    artist_clean = re.sub(r'[^a-zA-Z0-9]', '-', artist).lower().strip('-')
    song_clean = re.sub(r'[^a-zA-Z0-9]', '-', song).lower().strip('-')
    url = f"https://www.musixmatch.com/lyrics/{artist_clean}/{song_clean}"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            lyrics_spans = re.findall(r'<span[^>]*class="[^"]*lyrics[^"]*"[^>]*>(.*?)</span>', 
                                    html_content, re.DOTALL)
            if lyrics_spans:
                lyrics = '\n'.join(lyrics_spans)
                lyrics = clean_lyrics(lyrics)
                
                if lyrics:
                    return True, song, artist, lyrics, "Musixmatch"
    except Exception as e:
        print(f"    Musixmatch error: {e}")
    
    return False, None, None, None, None


def search_letras(artist: str, song: str) -> tuple:
    """Search Letras.com for lyrics."""
    artist_clean = re.sub(r'[^a-zA-Z0-9]', '-', artist).lower().strip('-')
    song_clean = re.sub(r'[^a-zA-Z0-9]', '-', song).lower().strip('-')
    url = f"https://www.letras.com/{artist_clean}/{song_clean}/"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
            
            match = re.search(r'<article[^>]*>(.*?)</article>', html_content, re.DOTALL)
            if match:
                lyrics = match.group(1)
                lyrics = clean_lyrics(lyrics)
                
                if lyrics:
                    return True, song, artist, lyrics, "Letras.com"
    except Exception as e:
        print(f"    Letras error: {e}")
    
    return False, None, None, None, None


def find_lyrics_multi_source(artist: str, song: str) -> tuple:
    """
    Try multiple sources to find lyrics.
    Returns: (success: bool, title: str, artist_name: str, lyrics: str, source: str)
    """
    sources = [
        ("Genius", search_genius),
        ("AZLyrics", search_azlyrics),
        ("Musixmatch", search_musixmatch),
        ("Letras.com", search_letras),
    ]
    
    for source_name, source_func in sources:
        print(f"  Trying {source_name}...")
        try:
            success, title, artist_name, lyrics, source = source_func(artist, song)
            if success and lyrics:
                print(f"  [OK] Found lyrics on {source}!")
                return True, title or song, artist_name or artist, lyrics, source
        except Exception as e:
            print(f"  [X] {source_name} failed: {e}")
            continue
    
    return False, None, None, None, None


def save_lyrics(artist: str, song: str, lyrics: str, output_path: str):
    """
    Save lyrics to a file in clean format (matching reference style).
    Format: Pure lyrics only, no metadata headers.
    """
    safe_artist = re.sub(r'[<>:"/\\|?*]', '', artist).strip()
    safe_song = re.sub(r'[<>:"/\\|?*]', '', song).strip()
    
    filename = f"{safe_artist} - {safe_song}.txt"
    filepath = Path(output_path) / filename
    
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(lyrics)
    
    return str(filepath)


def main():
    if len(sys.argv) < 3:
        print("Usage: python download_lyrics.py \"Artist Name\" \"Song Title\" [output_path]")
        print("Example: python download_lyrics.py \"Beyond Awareness\" \"Crime\" \"./lyrics/\"")
        print("")
        print("Sources tried (in order):")
        print("  1. Genius.com")
        print("  2. AZLyrics.com")
        print("  3. Musixmatch.com")
        print("  4. Letras.com")
        print("")
        print("Output format: Clean lyrics with [Verse], [Chorus] markers preserved")
        sys.exit(1)
    
    artist = sys.argv[1]
    song = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "."
    
    print(f"Searching for: {artist} - {song}")
    print(f"Will try multiple sources...\n")
    
    success, title, artist_name, lyrics, source = find_lyrics_multi_source(artist, song)
    
    if not success:
        print("\n[X] Could not find lyrics from any source.")
        print("    Tips:")
        print("    - Check the spelling of artist and song title")
        print("    - Try using the original artist name")
        print("    - Some songs may not be available on any lyrics site")
        sys.exit(1)
    
    print(f"\nExtracted lyrics for: {artist_name} - {title}")
    print(f"Source: {source}")
    
    # Save lyrics in clean format (no metadata headers)
    filepath = save_lyrics(artist_name or artist, title or song, lyrics, output_path)
    print(f"[OK] Saved lyrics to: {filepath}")


if __name__ == "__main__":
    main()
