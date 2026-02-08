"""
Musixmatch.com lyrics fetcher.
"""

import re
import html
from .base import BaseLyricsFetcher, LyricsResult


class MusixmatchFetcher(BaseLyricsFetcher):
    """Fetch lyrics from Musixmatch.com."""

    @property
    def priority(self) -> int:
        return 3

    def fetch(self, artist: str, song: str) -> LyricsResult:
        """Search and extract lyrics from Musixmatch."""
        try:
            # Clean artist and song names for URL
            artist_clean = re.sub(r'[^a-zA-Z0-9]', '-', artist).lower().strip('-')
            song_clean = re.sub(r'[^a-zA-Z0-9]', '-', song).lower().strip('-')
            url = f"https://www.musixmatch.com/lyrics/{artist_clean}/{song_clean}"

            with self._make_request(url, timeout=30) as response:
                html_content = response.read().decode('utf-8')

                # Extract lyrics spans
                lyrics_spans = re.findall(
                    r'<span[^>]*class="[^"]*lyrics[^"]*"[^>]*>(.*?)</span>',
                    html_content, re.DOTALL
                )

                if lyrics_spans:
                    lyrics = self._clean_lyrics('\n'.join(lyrics_spans))
                    if lyrics:
                        return LyricsResult(
                            success=True,
                            title=song,
                            artist=artist,
                            lyrics=lyrics,
                            source="Musixmatch"
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
