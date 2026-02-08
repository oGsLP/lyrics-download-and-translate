"""
Lyrics source manager - coordinates multiple lyrics fetchers.
"""

from typing import List

from .base import BaseLyricsFetcher, LyricsResult


class LyricsSourceManager:
    """Manages multiple lyrics fetchers with priority-based fallback."""

    def __init__(self, proxy_opener=None):
        """
        Initialize manager with fetcher instances.

        Args:
            proxy_opener: Optional proxy opener for HTTP requests
        """
        self._fetchers: List[BaseLyricsFetcher] = []
        self._init_fetchers(proxy_opener)

    def _init_fetchers(self, proxy_opener):
        """Initialize all available fetchers."""
        from .genius import GeniusFetcher
        from .azlyrics import AZLyricsFetcher
        from .musixmatch import MusixmatchFetcher
        from .letras import LetrasFetcher
        from .youtube import YouTubeFetcher

        self._fetchers = [
            GeniusFetcher(proxy_opener),
            AZLyricsFetcher(proxy_opener),
            MusixmatchFetcher(proxy_opener),
            LetrasFetcher(proxy_opener),
            YouTubeFetcher(proxy_opener),
        ]

        # Sort by priority (lower = try first)
        self._fetchers.sort(key=lambda f: f.priority)

    @property
    def sources(self) -> List[str]:
        """Return list of available source names."""
        return [f.name for f in self._fetchers]

    def fetch_lyrics(self, artist: str, song: str) -> LyricsResult:
        """
        Try all sources in priority order until lyrics are found.

        Args:
            artist: The artist name
            song: The song title

        Returns:
            LyricsResult with lyrics if found, or error status
        """
        for fetcher in self._fetchers:
            print(f"  Trying {fetcher.name}...")

            result = fetcher.fetch(artist, song)

            if result.success and result.lyrics:
                print(f"  [OK] Found lyrics on {fetcher.name}!")
                return result

        return LyricsResult(
            success=False,
            error="Could not find lyrics from any source"
        )

    def fetch_from_source(self, artist: str, song: str, source: str) -> LyricsResult:
        """
        Fetch lyrics from a specific source.

        Args:
            artist: The artist name
            song: The song title
            source: Source name to use

        Returns:
            LyricsResult from the specified source
        """
        for fetcher in self._fetchers:
            if fetcher.name.lower() == source.lower():
                return fetcher.fetch(artist, song)

        return LyricsResult(
            success=False,
            error=f"Unknown source: {source}"
        )
