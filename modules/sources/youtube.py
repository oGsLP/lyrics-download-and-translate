"""
YouTube lyrics fetcher.
Extracts lyrics from YouTube video descriptions.
"""

import re
import html
import urllib.request
import urllib.parse
from .base import BaseLyricsFetcher, LyricsResult


class YouTubeFetcher(BaseLyricsFetcher):
    """Fetch lyrics from YouTube video descriptions."""

    @property
    def priority(self) -> int:
        return 5

    def fetch(self, artist: str, song: str) -> LyricsResult:
        """Search YouTube for lyrics in video descriptions."""
        query = f"{artist} {song} lyrics"
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }

        try:
            # Search for videos
            with self._make_request(search_url, headers=headers, timeout=30) as response:
                html_content = response.read().decode('utf-8')

                # Extract video IDs
                video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html_content)

                if not video_ids:
                    return LyricsResult(success=False, error="No videos found")

                # Try first few videos
                for video_id in video_ids[:3]:
                    result = self._try_video_description(video_id, headers)
                    if result.success:
                        return result

        except Exception as e:
            return LyricsResult(success=False, error=str(e))

        return LyricsResult(success=False, error="No lyrics found in YouTube descriptions")

    def _try_video_description(self, video_id: str, headers: dict) -> LyricsResult:
        """Try to extract lyrics from a video description."""
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            with self._make_request(video_url, headers=headers, timeout=30) as response:
                video_html = response.read().decode('utf-8')

                # Method 1: Look for lyrics markers in description
                lyrics_match = re.search(
                    r'(?:Lyrics|LYRICS|歌词)[:\s]*\n?(.*?)(?:\n\n|\Z|Subscribe|Follow|Instagram|Twitter)',
                    video_html,
                    re.IGNORECASE | re.DOTALL
                )

                if lyrics_match:
                    lyrics = self._clean_lyrics(lyrics_match.group(1))
                    if len(lyrics) > 100:
                        return LyricsResult(
                            success=True,
                            title=f"{video_id} (YouTube)",
                            artist="YouTube",
                            lyrics=lyrics,
                            source="YouTube"
                        )

                # Method 2: Look for description in meta tag
                desc_match = re.search(
                    r'<meta[^>]*name="description"[^>]*content="([^"]*)"',
                    video_html
                )

                if desc_match:
                    description = desc_match.group(1)
                    # Check if description contains lyrics markers
                    if '[' in description and len(description) > 200:
                        lyrics = self._clean_lyrics(description)
                        if lyrics:
                            return LyricsResult(
                                success=True,
                                title=f"{video_id} (YouTube)",
                                artist="YouTube",
                                lyrics=lyrics,
                                source="YouTube"
                            )

        except Exception:
            pass

        return LyricsResult(success=False, error="Failed to extract from video")

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
