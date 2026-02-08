"""
Lyrics sources module - Modular lyrics fetchers for different services.
"""

from .base import BaseLyricsFetcher, LyricsResult
from .genius import GeniusFetcher
from .azlyrics import AZLyricsFetcher
from .musixmatch import MusixmatchFetcher
from .letras import LetrasFetcher
from .youtube import YouTubeFetcher
from .manager import LyricsSourceManager

__all__ = [
    'BaseLyricsFetcher',
    'LyricsResult',
    'GeniusFetcher',
    'AZLyricsFetcher',
    'MusixmatchFetcher',
    'LetrasFetcher',
    'YouTubeFetcher',
    'LyricsSourceManager',
]
