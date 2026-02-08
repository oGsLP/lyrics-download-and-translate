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
            artist_clean = re.sub(r'[^a-zA-Z0-9]', '-', artist).lower().strip('-')
            song_clean = re.sub(r'[^a-zA-Z0-9]', '-', song).lower().strip('-')
            url = f"https://www.letras.com/{artist_clean}/{song_clean}/"

            with self._make_request(url, timeout=30) as response:
                html_content = response.read().decode('utf-8')

                # Extract from article tag
                match = re.search(
                    r'<article[^>]*>(.*?)</article>',
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
                            source="Letras.com"
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

        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # Remove excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Strip each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)

        return text.strip()
