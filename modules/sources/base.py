"""
Base classes for lyrics fetchers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LyricsResult:
    """Result container for lyrics fetch operation."""
    success: bool
    title: Optional[str] = None
    artist: Optional[str] = None
    lyrics: Optional[str] = None
    source: Optional[str] = None
    error: Optional[str] = None


class BaseLyricsFetcher(ABC):
    """Abstract base class for lyrics fetchers."""

    def __init__(self, proxy_opener=None):
        """Initialize fetcher with optional proxy opener."""
        self._proxy_opener = proxy_opener
        self._name = self.__class__.__name__.replace('Fetcher', '')

    @property
    def name(self) -> str:
        """Return fetcher name."""
        return self._name

    @property
    @abstractmethod
    def priority(self) -> int:
        """Return priority (lower = try first)."""
        pass

    @abstractmethod
    def fetch(self, artist: str, song: str) -> LyricsResult:
        """
        Fetch lyrics for the given artist and song.

        Args:
            artist: The artist name
            song: The song title

        Returns:
            LyricsResult with success status and lyrics if found
        """
        pass

    def _make_request(self, url: str, headers: dict = None, timeout: int = 30):
        """
        Make HTTP request with proxy support.

        Args:
            url: URL to request
            headers: Optional headers dictionary
            timeout: Request timeout

        Returns:
            Response object
        """
        import urllib.request

        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

        req = urllib.request.Request(url, headers=headers)

        if self._proxy_opener:
            return self._proxy_opener.open(req, timeout=timeout)
        else:
            return urllib.request.urlopen(req, timeout=timeout)
