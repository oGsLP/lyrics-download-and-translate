#!/usr/bin/env python3
"""
Download lyrics from Genius.com

Usage:
    python download_lyrics.py "Artist Name" "Song Title" [output_path]
    python download_lyrics.py "Beyond Awareness" "Crime" "D:/Tools/BesLyric-for-X/lyrics/"

Arguments:
    artist: The artist name
    song: The song title
    output_path: Optional output directory (default: current directory)

Output:
    Saves lyrics to: {output_path}/{Artist} - {Song}.txt
"""

import sys
import os
import re
import json
import urllib.request
import urllib.parse
import urllib.error
import socket
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def search_genius(artist, song, max_retries=3):
    """
    Search for a song on Genius and return the song URL.
    
    Args:
        artist: Artist name
        song: Song title
        max_retries: Maximum number of retry attempts
        
    Returns:
        str: Genius song URL or None if not found
    """
    query = f"{artist} {song}"
    search_url = f"https://genius.com/api/search/multi?q={urllib.parse.quote(query)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(search_url, headers=headers)
            # Increase timeout and handle socket timeout specifically
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Look for song results in the response
                sections = data.get('response', {}).get('sections', [])
                for section in sections:
                    if section.get('type') == 'song':
                        hits = section.get('hits', [])
                        if hits:
                            # Return the URL of the first hit
                            return hits[0].get('result', {}).get('url')
                
                # If no song section found, try any hit
                for section in sections:
                    hits = section.get('hits', [])
                    for hit in hits:
                        url = hit.get('result', {}).get('url')
                        if url and 'genius.com' in url:
                            return url
                        
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"  Warning: Search attempt {attempt + 1} failed, retrying...")
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Error searching Genius: {e}")
                return None
        except socket.timeout as e:
            if attempt < max_retries - 1:
                print(f"  Warning: Search timeout (attempt {attempt + 1}), retrying...")
                import time
                time.sleep(2 ** attempt)
            else:
                print(f"Error: Search timed out after {max_retries} attempts")
                return None
        except Exception as e:
            print(f"Error searching Genius: {e}")
            return None
    
    return None


def extract_lyrics_from_page(url, max_retries=3):
    """
    Extract lyrics from a Genius song page.
    
    Args:
        url: Genius song URL
        max_retries: Maximum number of retry attempts
        
    Returns:
        tuple: (song_title, artist_name, lyrics_text) or None if failed
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8')
                
                # Extract song title from meta tags or title
                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                song_title = title_match.group(1) if title_match else "Unknown Song"
                
                # Extract artist name
                artist_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
                artist_name = "Unknown Artist"
                if artist_match:
                    desc = artist_match.group(1)
                    # Try to extract artist from description like "Read the lyrics to Song by Artist..."
                    artist_extract = re.search(r'by\s+([^"]+?)\s+on Genius', desc)
                    if artist_extract:
                        artist_name = artist_extract.group(1).strip()
                
                # Try multiple methods to extract lyrics
                lyrics = None
                
                # Method 1: Look for lyrics in JSON-LD script tag
                json_ld_match = re.search(r'<script type="application/ld\+json">([^<]+)</script>', html)
                if json_ld_match:
                    try:
                        json_data = json.loads(json_ld_match.group(1))
                        if isinstance(json_data, dict):
                            lyrics = json_data.get('recordingOf', {}).get('lyrics', {}).get('text')
                    except:
                        pass
                
                # Method 2: Look for lyrics in the new Genius format (data-lyrics-container)
                if not lyrics:
                    lyrics_container = re.findall(r'<div[^>]*data-lyrics-container="true"[^>]*>(.*?)</div>', html, re.DOTALL)
                    if lyrics_container:
                        # Combine all lyrics containers
                        lyrics_html = ' '.join(lyrics_container)
                        # Remove HTML tags
                        lyrics = re.sub(r'<[^>]+>', '', lyrics_html)
                        lyrics = re.sub(r'\n\s*\n', '\n\n', lyrics)
                
                # Method 3: Look for the old lyrics div
                if not lyrics:
                    lyrics_div = re.search(r'<div class="lyrics">(.*?)</div>', html, re.DOTALL)
                    if lyrics_div:
                        lyrics = re.sub(r'<[^>]+>', '', lyrics_div.group(1))
                
                # Method 4: Search for lyrics in page data
                if not lyrics:
                    # Look for lyrics in window.__INITIAL_STATE__ or similar
                    state_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?});', html)
                    if state_match:
                        try:
                            state_data = json.loads(state_match.group(1))
                            # Navigate through the state to find lyrics
                            songs = state_data.get('songs', {})
                            for song_id, song_data in songs.items():
                                if 'lyrics' in song_data:
                                    lyrics = song_data['lyrics']
                                    break
                        except:
                            pass
                
                # Method 5: New method - look for lyrics in div with class containing 'Lyrics__Container'
                if not lyrics:
                    lyrics_container = re.findall(r'<div[^>]*class="[^"]*Lyrics__Container[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
                    if lyrics_container:
                        lyrics_html = ' '.join(lyrics_container)
                        lyrics = re.sub(r'<[^>]+>', '', lyrics_html)
                        lyrics = re.sub(r'\n\s*\n', '\n\n', lyrics)
                
                if lyrics:
                    # Clean up lyrics
                    lyrics = lyrics.strip()
                    lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remove [Chorus], [Verse] etc.
                    lyrics = re.sub(r'\n\s*\n\s*\n', '\n\n', lyrics)  # Remove excessive newlines
                    
                    return song_title, artist_name, lyrics.strip()
                    
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                print(f"  Warning: Extraction attempt {attempt + 1} failed, retrying...")
                import time
                time.sleep(2 ** attempt)
            else:
                print(f"Error extracting lyrics: {e}")
                return None
        except socket.timeout as e:
            if attempt < max_retries - 1:
                print(f"  Warning: Extraction timeout (attempt {attempt + 1}), retrying...")
                import time
                time.sleep(2 ** attempt)
            else:
                print(f"Error: Extraction timed out after {max_retries} attempts")
                return None
        except Exception as e:
            print(f"Error extracting lyrics: {e}")
            return None
    
    return None


def save_lyrics(artist, song, lyrics, output_path):
    """
    Save lyrics to a file.
    
    Args:
        artist: Artist name
        song: Song title
        lyrics: Lyrics text
        output_path: Output directory
        
    Returns:
        str: Path to saved file
    """
    # Clean filename
    safe_artist = re.sub(r'[<>:"/\\|?*]', '', artist).strip()
    safe_song = re.sub(r'[<>:"/\\|?*]', '', song).strip()
    
    filename = f"{safe_artist} - {safe_song}.txt"
    filepath = Path(output_path) / filename
    
    # Ensure output directory exists
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{artist} - {song}\n")
        f.write("=" * 50 + "\n\n")
        f.write(lyrics)
    
    return str(filepath)


def main():
    if len(sys.argv) < 3:
        print("Usage: python download_lyrics.py \"Artist Name\" \"Song Title\" [output_path]")
        print("Example: python download_lyrics.py \"Beyond Awareness\" \"Crime\" \"./lyrics/\"")
        sys.exit(1)
    
    artist = sys.argv[1]
    song = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "."
    
    print(f"Searching for: {artist} - {song}")
    
    # Search for the song
    song_url = search_genius(artist, song)
    if not song_url:
        print("[X] Song not found on Genius")
        print("    Tips:")
        print("    - Check the spelling of artist and song title")
        print("    - Try using the original artist name")
        print("    - Some songs may not be available on Genius")
        sys.exit(1)
    
    print(f"Found song page: {song_url}")
    
    # Extract lyrics
    result = extract_lyrics_from_page(song_url)
    if not result:
        print("[X] Could not extract lyrics from the page")
        print("    This might be because:")
        print("    - Genius page structure has changed")
        print("    - The page has anti-scraping protection")
        print("    - Try accessing the song page manually to verify it exists")
        sys.exit(1)
    
    actual_title, actual_artist, lyrics = result
    print(f"Extracted lyrics for: {actual_artist} - {actual_title}")
    
    # Save lyrics
    filepath = save_lyrics(actual_artist, actual_title, lyrics, output_path)
    print(f"[OK] Saved lyrics to: {filepath}")


if __name__ == "__main__":
    main()
