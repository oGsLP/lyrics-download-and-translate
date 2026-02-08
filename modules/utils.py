"""
Utility functions for lyrics processing.
"""

import html
import re


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
    cleaned_lines = [line.strip() for line in lines]
    lyrics = '\n'.join(cleaned_lines)
    
    # Final cleanup
    lyrics = lyrics.strip()
    
    return lyrics


def is_section_marker(line: str) -> bool:
    """Check if a line is a section marker like [Verse 1], [Chorus]."""
    return bool(re.match(r'^\[.+\]$', line.strip()))
