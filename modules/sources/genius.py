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
            # Search for song with proper headers for Genius API
            search_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://genius.com/',
                'X-Requested-With': 'XMLHttpRequest'
            }
            with self._make_request(search_url, headers=search_headers, timeout=30) as response:
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
                    lyrics = self._clean_lyrics(lyrics)
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

        text = html_content
        
        # Preserve line breaks from HTML
        text = re.sub(r'\s*<br\s*/?>\s*', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*</p>\s*', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*<div[^>]*>\s*', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*</div>\s*', '\n', text, flags=re.IGNORECASE)
        
        # Decode HTML entities
        text = html.unescape(text)

        # Remove remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)

        return text.strip()
    
    def _clean_lyrics(self, text: str) -> str:
        """Clean and format lyrics."""
        if not text:
            return ""
        
        # Remove UI elements
        text = re.sub(r'^\d+\s*Contributor', '', text)
        text = re.sub(r'Lyrics\s*$', '', text)
        
        # Normalize whitespace
        lines = text.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if not prev_empty:
                    cleaned_lines.append('')
                    prev_empty = True
                continue
            
            prev_empty = False
            cleaned_lines.append(stripped)
        
        # Remove leading/trailing empty lines
        while cleaned_lines and not cleaned_lines[0]:
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)