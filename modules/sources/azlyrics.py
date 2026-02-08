"""
AZLyrics.com lyrics fetcher.
"""

import html
import re

from .base import BaseLyricsFetcher, LyricsResult


class AZLyricsFetcher(BaseLyricsFetcher):
    """Fetch lyrics from AZLyrics.com."""

    @property
    def priority(self) -> int:
        return 2

    def fetch(self, artist: str, song: str) -> LyricsResult:
        """Search and extract lyrics from AZLyrics."""
        try:
            # Clean artist and song names for URL
            artist_clean = re.sub(r'[^a-zA-Z0-9]', '', artist).lower()
            song_clean = re.sub(r'[^a-zA-Z0-9]', '', song).lower()
            url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{song_clean}.html"

            with self._make_request(url, timeout=30) as response:
                html_content = response.read().decode('utf-8')

                # Extract lyrics from comment
                match = re.search(
                    r'<!-- Usage of azlyrics\.com content.*?-->(.*?)<!--',
                    html_content, re.DOTALL
                )

                if match:
                    lyrics = self._clean_lyrics(match.group(1))
                    if lyrics:
                        return LyricsResult(
                            success=True,
                            title=song,
                            artist=artist,
                            lyrics=lyrics,
                            source="AZLyrics"
                        )

        except Exception as e:
            return LyricsResult(success=False, error=str(e))

        return LyricsResult(success=False, error="Lyrics not found")

    def _clean_lyrics(self, content: str) -> str:
        """Clean lyrics content."""
        if not content:
            return ""

        # Decode HTML entities
        text = html.unescape(content)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text
