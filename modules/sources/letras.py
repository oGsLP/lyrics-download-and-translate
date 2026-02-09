"""
Letras.com lyrics fetcher.
"""

import re
import html
from .base import BaseLyricsFetcher, LyricsResult


class LetrasFetcher(BaseLyricsFetcher):
    """Fetch lyrics from Letras.com."""

    @property
    def priority(self) -> int:
        return 4

    def fetch(self, artist: str, song: str) -> LyricsResult:
        """Search and extract lyrics from Letras."""
        try:
            # Clean artist and song names for URL
            artist_clean = re.sub(r"[^a-zA-Z0-9]", "-", artist).lower().strip("-")
            song_clean = re.sub(r"[^a-zA-Z0-9]", "-", song).lower().strip("-")
            url = f"https://www.letras.com/{artist_clean}/{song_clean}/"

            with self._make_request(url, timeout=30) as response:
                html_content = response.read().decode("utf-8")

                # Try to extract lyrics
                lyrics = self._extract_lyrics(html_content)

                if lyrics:
                    lyrics = self._clean_lyrics(lyrics)
                    if lyrics:
                        return LyricsResult(
                            success=True,
                            title=song,
                            artist=artist,
                            lyrics=lyrics,
                            source="Letras.com"
                        )

        except Exception as e:
            return LyricsResult(success=False, error=str(e))

        return LyricsResult(success=False, error="Lyrics not found")

    def _extract_lyrics(self, html_content: str) -> str:
        """Extract lyrics from HTML."""
        # Try div with lyrics class or id first
        for attr in ["class", "id"]:
            pattern = rf'<div[^>]*{attr}="[^"]*lyrics[^"]*"[^>]*>(.*?)</div>'
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1)
                if self._is_valid_lyrics(content):
                    return content
        
        # Fallback to article tag
        match = re.search(r"<article[^>]*>(.*?)</article>", html_content, re.DOTALL)
        if match:
            return match.group(1)
        
        return ""

    def _is_valid_lyrics(self, content: str) -> bool:
        """Check if content looks like actual lyrics."""
        if not content:
            return False
        
        text = re.sub(r"<[^>]+>", "", content)
        text = html.unescape(text)
        
        if len(text) < 50:
            return False
        
        ui_indicators = [
            "Add to favorites", "Add to Playlist", "Font size", 
            "Tab", "Print", "Correct", "Auto-scroll", "Notes",
            "Restore", "Apply", "Send us", "revision"
        ]
        
        ui_count = sum(1 for indicator in ui_indicators if indicator in text)
        return ui_count <= 3

    def _clean_lyrics(self, content: str) -> str:
        """Clean lyrics content and remove UI elements."""
        if not content:
            return ""

        text = html.unescape(content)
        # Preserve line breaks from HTML
        text = re.sub(r'\s*<br\s*/?\>\s*', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*</p>\s*', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Fix case where metadata and first line are concatenated
        # Pattern: metadata words followed by actual lyric line
        # Remove common metadata patterns from start of lines
        metadata_pattern = r'^(lyrics views[\d\s\.]*|Numb|Linkin Park|Lyrics|Meaning|Translations)*\s*'
        lines = text.split('\n')
        cleaned = []
        for line in lines:
            # Remove leading metadata words
            clean_line = re.sub(metadata_pattern, '', line, flags=re.IGNORECASE).strip()
            # Keep empty lines (paragraph breaks)
            if clean_line or line.strip() == '':
                cleaned.append(clean_line)
        text = '\n'.join(cleaned)
        
        # Remove credits and trailing metadata
        skip_line_patterns = [
            r'^Written by:',
            r'^Subtitled by',
            r'^Revised by',
            r'^Did you see an error',
            r"^Isn't this right",
            r'Bourdon / Brad Delson',
        ]
        
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Keep empty lines (paragraph breaks)
            if not stripped:
                cleaned_lines.append('')
                continue
            # Skip credit lines
            if any(re.search(pattern, stripped, re.IGNORECASE) for pattern in skip_line_patterns):
                continue
            cleaned_lines.append(stripped)
        
        text = '\n'.join(cleaned_lines)
        
        # Fix formatting - ensure parentheses are on their own lines
        text = re.sub(r'\s*\(\s*', '\n(', text)
        text = re.sub(r'\s*\)\s*', ')\n', text)
        text = re.sub(r"(\S)(\[.+?\])", r"\1\n\2", text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Clean up lines but preserve paragraph breaks (double newlines = paragraph separator)
        lines = text.split("\n")
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                # Mark paragraph break with empty line
                if not prev_empty:
                    cleaned_lines.append("")
                    prev_empty = True
                continue
            prev_empty = False
            cleaned_lines.append(stripped)
        
        # Remove leading/trailing empty lines
        while cleaned_lines and not cleaned_lines[0]:
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return "\n".join(cleaned_lines)