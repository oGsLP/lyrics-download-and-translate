#!/usr/bin/env python3
"""
Download lyrics from multiple sources (Genius, AZLyrics, Letras, Musixmatch, YouTube)
Uses modular sources from modules.sources

Usage:
    python download_lyrics.py "Artist Name" "Song Title" [output_path]
    python download_lyrics.py "Beyond Awareness" "Crime" "./lyrics/"
"""

import io
import sys
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Import from modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.sources import LyricsSourceManager
from modules.utils import load_config, save_lyrics
from modules.proxy import get_proxy_opener


def main():
    if len(sys.argv) < 3:
        print('Usage: python download_lyrics.py "Artist Name" "Song Title" [output_path]')
        print('       python download_lyrics.py "Beyond Awareness" "Crime" "./lyrics/"')
        print("")
        print("Proxy Configuration:")
        print("  Create config.json in the skill directory to enable proxy support.")
        print("  Clash default: http://127.0.0.1:7890")
        print("")
        print("Sources tried (in order):")
        print("  1. Genius.com")
        print("  2. AZLyrics.com")
        print("  3. Musixmatch.com")
        print("  4. Letras.com")
        print("  5. YouTube (video descriptions)")
        print("")
        print("Output format: Clean lyrics with [Verse], [Chorus] markers preserved")
        sys.exit(1)

    artist = sys.argv[1]
    song = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "."

    # Load config and initialize proxy
    possible_paths = [
        str(Path(__file__).parent.parent / "config.json"),
        str(Path.cwd() / "config.json"),
    ]
    config = load_config(possible_paths)

    # Initialize proxy
    proxy_opener = get_proxy_opener(possible_paths[0] if possible_paths else None)
    if proxy_opener:
        print("  [Proxy] Enabled")
        proxy_config = config.get("proxy", {})
        if proxy_config.get("http"):
            print(f"  [Proxy] HTTP: {proxy_config['http']}")
        if proxy_config.get("https"):
            print(f"  [Proxy] HTTPS: {proxy_config['https']}")

    print(f"Searching for: {artist} - {song}")
    print("Will try multiple sources...")
    print()

    # Use LyricsSourceManager to fetch lyrics
    manager = LyricsSourceManager(proxy_opener)
    result = manager.fetch_lyrics(artist, song)

    if not result.success or not result.lyrics:
        print("[X] Could not find lyrics from any source.")
        print("    Tips:")
        print("    - Check the spelling of artist and song title")
        print("    - Try using the original artist name")
        print("    - Some songs may not be available on any lyrics site")
        sys.exit(1)

    print()
    print(f"Extracted lyrics for: {result.artist} - {result.title}")
    print(f"Source: {result.source}")

    # Save lyrics
    filepath = save_lyrics(result.artist or artist, result.title or song, result.lyrics, output_path)
    print(f"[OK] Saved lyrics to: {filepath}")


if __name__ == "__main__":
    main()
