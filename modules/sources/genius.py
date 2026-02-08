"""
Genius.com lyrics fetcher.
"""

import json
import re
import html
from .base import BaseLyricsFetcher, LyricsResult


class GeniusFetcher(BaseLyricsFetcher):
    """Fetch lyrics from Genius.com."""

    @property
    def priority(self) -> int:
        return 1

    def fetch(self, artist: str, song: str) -> LyricsResult:
        """Search and extract lyrics from Genius."""
        import urllib.request
        import urllib.parse

        query = f"{artist} {song}"
        search_url = f"https://genius.com/api/search/multi?q={urllib.parse.quote(query)}"

        try:
            # Search for song
            with self._make_request(search_url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))

                song_url = self._find_song_url(data)

                if song_url:
                    return self._extract_lyrics(song_url)

        except Exception as e:
            return LyricsResult(success=False, error=str(e))

        return LyricsResult(success=False, error="Song not found")

    def _find_song_url(self, data: dict) -> str:
        """Find song URL from search results."""
        sections = data.get('response', {}).get('sections', [])

        for section in sections:
            if section.get('type') == 'song':
                hits = section.get('hits', [])
                if hits:
                    return hits[0].get('result', {}).get('url')

            # Fallback: look for any Genius URL
            for hit in section.get('hits', []):
                url = hit.get('result', {}).get('url')
                if url and 'genius.com' in url:
                    return url

        return None

    def _extract_lyrics(self, url: str) -> LyricsResult:
        """Extract lyrics from Genius page."""
        try:
            with self._make_request(url, timeout=30) as response:
                html_content = response.read().decode('utf-8')

                # Extract title
                title_match = re.search(
                    r'<meta property="og:title" content="([^"]+)"', html_content
                )
                song_title = title_match.group(1) if title_match else "Unknown"

                # Extract lyrics using multiple methods
                lyrics = self._extract_lyrics_from_html(html_content)

                if lyrics:
                    return LyricsResult(
                        success=True,
                        title=song_title,
                        artist="Unknown",
                        lyrics=lyrics,
                        source="Genius"
                    )

        except Exception as e:
            return LyricsResult(success=False, error=str(e))

        return LyricsResult(success=False, error="Failed to extract lyrics")

    def _extract_lyrics_from_html(self, html_content: str) -> str:
        """Extract lyrics from HTML content using multiple strategies."""
        lyrics = None

        # Method 1: JSON-LD
        json_ld = re.search(
            r'<script type="application/ld\+json">([^<]+)</script>', html_content
        )
        if json_ld:
            try:
                data = json.loads(json_ld.group(1))
                lyrics = data.get('recordingOf', {}).get('lyrics', {}).get('text')
            except:
                pass

        # Method 2: data-lyrics-container
        if not lyrics:
            containers = re.findall(
                r'<div[^>]*data-lyrics-container="true"[^>]*>(.*?)</div>',
                html_content, re.DOTALL
            )
            if containers:
                lyrics_html = '\n\n'.join(containers)
                lyrics = self._clean_html(lyrics_html)

        # Method 3: Lyrics__Container
        if not lyrics:
            containers = re.findall(
                r'<div[^>]*class="[^"]*Lyrics__Container[^"]*"[^>]*>(.*?)</div>',
                html_content, re.DOTALL
            )
            if containers:
                lyrics_html = '\n\n'.join(containers)
                lyrics = self._clean_html(lyrics_html)

        return lyrics

    def _clean_html(self, html_content: str) -> str:
        """Clean HTML from lyrics content."""
        if not html_content:
            return ""

        # Decode HTML entities
        text = html.unescape(html_content)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        return text.strip()
