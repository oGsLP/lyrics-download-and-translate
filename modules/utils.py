"""
Utility functions for lyrics processing.
"""

import json
import re
from pathlib import Path
from typing import Optional, Tuple, List


def is_section_marker(line: str) -> bool:
    """Check if a line is a section marker like [Verse 1], [Chorus]."""
    return bool(re.match(r'^\[.+\]$', line.strip()))


def sanitize_filename(name: str) -> str:
    """Remove invalid characters from filename."""
    return re.sub(r'[<>："/\\|?*]', '', name).strip()


def parse_lyrics_file(filepath: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    """
    Parse lyrics file and return (artist, song, lines).
    
    Returns:
        Tuple of (artist, song, lines) or (None, None, []) on error
    """
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
        return None, None, []


def save_lyrics(artist: str, song: str, lyrics: str, output_path: str) -> str:
    """
    Save lyrics to a file in clean format.
    
    Args:
        artist: Artist name
        song: Song title
        lyrics: Lyrics content
        output_path: Output directory path
        
    Returns:
        Full filepath of saved file
    """
    safe_artist = sanitize_filename(artist)
    safe_song = sanitize_filename(song)

    filename = f"{safe_artist} - {safe_song}.txt"
    filepath = Path(output_path) / filename

    Path(output_path).mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(lyrics)

    return str(filepath)


def load_config(config_paths: Optional[List[str]] = None) -> dict:
    """
    Load configuration from config.json files.
    
    Args:
        config_paths: List of possible config file paths
        
    Returns:
        Configuration dictionary
    """
    if config_paths is None:
        config_paths = [
            str(Path.cwd() / "config.json"),
        ]

    for path in config_paths:
        path_obj = Path(path)
        if path_obj.exists():
            try:
                with open(path_obj, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

    return {"proxy": {"enabled": False}, "translation": {}}
