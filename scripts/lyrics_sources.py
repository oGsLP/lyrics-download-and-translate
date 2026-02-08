#!/usr/bin/env python3
"""
Multi-source lyrics search module.
Supports: Genius, YouTube (transcript), Web Search, Letras, Musixmatch
"""

import re
import json
import urllib.request
import urllib.parse
import urllib.error
import socket
import html
from typing import Optional, List, Dict, Tuple
from pathlib import Path


class LyricsSource:
    """Base class for lyrics sources."""
    
    def __init__(self, name: str):
        self.name = name
        self.timeout = 30
    
    def search(self, artist: str, song: str) -> Optional[Dict]:
        """Search for lyrics. Returns dict with 'title', 'artist', 'lyrics', 'source'."""
        raise NotImplementedError


class GeniusSource(LyricsSource):
    """Genius.com lyrics source."""
    
    def __init__(self):
        super().__init__("Genius")
    
    def search(self, artist: str, song: str) -> Optional[Dict]:
        query = f"{artist} {song}"
        search_url = f"https://genius.com/api/search/multi?q={urllib.parse.quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                sections = data.get('response', {}).get('sections', [])
                song_url = None
                
                for section in sections:
                    if section.get('type') == 'song':
                        hits = section.get('hits', [])
                        if hits:
                            song_url = hits[0].get('result', {}).get('url')
                            break
                    
                    if not song_url:
                        for hit in section.get('hits', []):
                            url = hit.get('result', {}).get('url')
                            if url and 'genius.com' in url:
                                song_url = url
                                break
                
                if song_url:
                    return self._extract_lyrics(song_url)
                    
        except Exception as e:
            print(f"  Genius error: {e}")
        
        return None
    
    def _extract_lyrics(self, url: str) -> Optional[Dict]:
        """Extract lyrics from Genius page."""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8')
                
                # Extract title
                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
                song_title = title_match.group(1) if title_match else "Unknown"
                
                # Try multiple methods to extract lyrics
                lyrics = None
                
                # Method 1: JSON-LD
                json_ld = re.search(r'<script type="application/ld\+json">([^<]+)</script>', html_content)
                if json_ld:
                    try:
                        data = json.loads(json_ld.group(1))
                        lyrics = data.get('recordingOf', {}).get('lyrics', {}).get('text')
                    except:
                        pass
                
                # Method 2: data-lyrics-container
                if not lyrics:
                    containers = re.findall(r'<div[^>]*data-lyrics-container="true"[^>]*>(.*?)</div>', 
                                          html_content, re.DOTALL)
                    if containers:
                        lyrics_html = ' '.join(containers)
                        lyrics = re.sub(r'<[^>]+>', '', lyrics_html)
                
                # Method 3: Lyrics__Container
                if not lyrics:
                    containers = re.findall(r'<div[^>]*class="[^"]*Lyrics__Container[^"]*"[^>]*>(.*?)</div>',
                                          html_content, re.DOTALL)
                    if containers:
                        lyrics_html = ' '.join(containers)
                        lyrics = re.sub(r'<[^>]+>', '', lyrics_html)
                
                if lyrics:
                    lyrics = lyrics.strip()
                    lyrics = re.sub(r'\[.*?\]', '', lyrics)
                    lyrics = re.sub(r'\n\s*\n\s*\n', '\n\n', lyrics)
                    
                    return {
                        'title': song_title,
                        'artist': 'Unknown',
                        'lyrics': lyrics.strip(),
                        'source': 'Genius'
                    }
        except Exception as e:
            print(f"  Genius extraction error: {e}")
        
        return None


class WebSearchSource(LyricsSource):
    """Web search for lyrics using DuckDuckGo or other search engines."""
    
    def __init__(self):
        super().__init__("Web Search")
    
    def search(self, artist: str, song: str) -> Optional[Dict]:
        # Try to find lyrics through web search
        query = f"{artist} {song} lyrics"
        
        # Try multiple lyric sites
        sources = [
            self._try_azlyrics,
            self._try_letras,
            self._try_musixmatch,
        ]
        
        for source_func in sources:
            try:
                result = source_func(artist, song)
                if result:
                    return result
            except Exception as e:
                print(f"  {source_func.__name__} error: {e}")
                continue
        
        return None
    
    def _try_azlyrics(self, artist: str, song: str) -> Optional[Dict]:
        """Try AZLyrics.com"""
        # Format: https://www.azlyrics.com/lyrics/[artist]/[song].html
        artist_clean = re.sub(r'[^a-zA-Z0-9]', '', artist).lower()
        song_clean = re.sub(r'[^a-zA-Z0-9]', '', song).lower()
        url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{song_clean}.html"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8')
                
                # AZLyrics puts lyrics in a div with no class after the copyright comment
                match = re.search(r'<!-- Usage of azlyrics\.com content.*?-->(.*?)<!--', 
                                html_content, re.DOTALL)
                if match:
                    lyrics = match.group(1)
                    lyrics = re.sub(r'<[^>]+>', '', lyrics)
                    lyrics = html.unescape(lyrics)
                    
                    if lyrics.strip():
                        return {
                            'title': song,
                            'artist': artist,
                            'lyrics': lyrics.strip(),
                            'source': 'AZLyrics'
                        }
        except:
            pass
        
        return None
    
    def _try_letras(self, artist: str, song: str) -> Optional[Dict]:
        """Try Letras.com (Portuguese/Spanish lyrics)"""
        # Format: https://www.letras.com/[artist]/[song]/
        artist_clean = re.sub(r'[^a-zA-Z0-9]', '-', artist).lower().strip('-')
        song_clean = re.sub(r'[^a-zA-Z0-9]', '-', song).lower().strip('-')
        url = f"https://www.letras.com/{artist_clean}/{song_clean}/"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8')
                
                # Look for lyrics in the article tag
                match = re.search(r'<article[^>]*>(.*?)</article>', html_content, re.DOTALL)
                if match:
                    lyrics = match.group(1)
                    lyrics = re.sub(r'<[^>]+>', '', lyrics)
                    lyrics = html.unescape(lyrics)
                    
                    if lyrics.strip():
                        return {
                            'title': song,
                            'artist': artist,
                            'lyrics': lyrics.strip(),
                            'source': 'Letras.com'
                        }
        except:
            pass
        
        return None
    
    def _try_musixmatch(self, artist: str, song: str) -> Optional[Dict]:
        """Try Musixmatch"""
        # Format: https://www.musixmatch.com/lyrics/[artist]/[song]
        artist_clean = re.sub(r'[^a-zA-Z0-9]', '-', artist).lower().strip('-')
        song_clean = re.sub(r'[^a-zA-Z0-9]', '-', song).lower().strip('-')
        url = f"https://www.musixmatch.com/lyrics/{artist_clean}/{song_clean}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8')
                
                # Look for lyrics in span elements with class containing 'lyrics'
                lyrics_spans = re.findall(r'<span[^>]*class="[^"]*lyrics[^"]*"[^>]*>(.*?)</span>', 
                                        html_content, re.DOTALL)
                if lyrics_spans:
                    lyrics = '\n'.join(lyrics_spans)
                    lyrics = re.sub(r'<[^>]+>', '', lyrics)
                    lyrics = html.unescape(lyrics)
                    
                    if lyrics.strip():
                        return {
                            'title': song,
                            'artist': artist,
                            'lyrics': lyrics.strip(),
                            'source': 'Musixmatch'
                        }
        except:
            pass
        
        return None


class MultiSourceLyricsFinder:
    """Finds lyrics from multiple sources."""
    
    def __init__(self):
        self.sources: List[LyricsSource] = [
            GeniusSource(),
            WebSearchSource(),
        ]
    
    def find_lyrics(self, artist: str, song: str) -> Optional[Dict]:
        """
        Try to find lyrics from multiple sources.
        Returns the first successful result.
        """
        print(f"Searching for lyrics: {artist} - {song}")
        print(f"Trying {len(self.sources)} sources...\n")
        
        for source in self.sources:
            print(f"  Trying {source.name}...")
            try:
                result = source.search(artist, song)
                if result and result.get('lyrics'):
                    print(f"  [OK] Found lyrics from {result['source']}!")
                    return result
            except Exception as e:
                print(f"  [X] {source.name} failed: {e}")
                continue
        
        print("\n[X] Could not find lyrics from any source.")
        return None


# Convenience function
def find_lyrics(artist: str, song: str) -> Optional[Dict]:
    """Find lyrics using multiple sources."""
    finder = MultiSourceLyricsFinder()
    return finder.find_lyrics(artist, song)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python lyrics_sources.py \"Artist\" \"Song\"")
        sys.exit(1)
    
    artist = sys.argv[1]
    song = sys.argv[2]
    
    result = find_lyrics(artist, song)
    
    if result:
        print(f"\n{'='*60}")
        print(f"Found lyrics from: {result['source']}")
        print(f"Title: {result['title']}")
        print(f"Artist: {result['artist']}")
        print(f"{'='*60}\n")
        print(result['lyrics'][:500] + "..." if len(result['lyrics']) > 500 else result['lyrics'])
    else:
        print("\nLyrics not found.")
