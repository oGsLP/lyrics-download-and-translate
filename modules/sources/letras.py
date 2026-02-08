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
        
        return None

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
        text = re.sub(r"<[^>]+>", "", text)
        
        # Remove UI elements
        ui_patterns = [
            r"Add to favorites.*?Add to Playlist",
            r"Font size.*?Tab.*?Print.*?Correct.*?Auto-scroll.*?Notes",
            r"Enabled.*?Disabled",
            r"Do you know who is the songwriter.*?Send us their name\.",
            r"Sent by.*?Did you see an error.*?Send us your revision\.",
            r"RestoreApply",
            r"lyrics views \d+",
            r"Are You Listening.*?Lyrics.*?Translations",
        ]
        
        for pattern in ui_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
        
        # Fix formatting
        text = re.sub(r"([.!?])([A-Z])", r"\1\n\2", text)
        text = re.sub(r"(\s*)(\[.+?\])", r"\n\2", text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Clean up lines
        lines = text.split("\n")
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
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