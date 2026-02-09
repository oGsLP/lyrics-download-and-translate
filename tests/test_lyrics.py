#!/usr/bin/env python3
"""Unit tests for lyrics download and translation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.sources import (
    GeniusFetcher, AZLyricsFetcher, MusixmatchFetcher,
    LetrasFetcher, YouTubeFetcher, LyricsSourceManager
)
from modules.translators import GoogleTranslator, TranslationManager

TEST_ARTIST = "Linkin Park"
TEST_SONG = "Numb"


def test_sources():
    """Test all lyrics sources."""
    print("\n============================================================")
    print(" Testing Lyrics Sources")
    print("============================================================")
    
    sources = [
        ("Genius", GeniusFetcher()),
        ("AZLyrics", AZLyricsFetcher()),
        ("Musixmatch", MusixmatchFetcher()),
        ("Letras", LetrasFetcher()),
        ("YouTube", YouTubeFetcher()),
    ]
    
    results = {}
    
    for name, fetcher in sources:
        print(f"\n  Testing {name}...")
        try:
            result = fetcher.fetch(TEST_ARTIST, TEST_SONG)
            
            if result.success and result.lyrics:
                # Check format
                issues = []
                if len(result.lyrics) < 100:
                    issues.append("too short")
                if "Add to favorites" in result.lyrics or "Contributor" in result.lyrics:
                    issues.append("has UI elements")
                
                if issues:
                    print(f"    WARN: {len(result.lyrics)} chars, issues: {', '.join(issues)}")
                else:
                    print(f"    OK: {len(result.lyrics)} chars, format OK")
                results[name] = {"success": True, "issues": issues}
            else:
                print(f"    FAIL: {result.error or 'no lyrics'}")
                results[name] = {"success": False, "error": result.error}
        except Exception as e:
            print(f"    ERROR: {str(e)[:50]}")
            results[name] = {"success": False, "error": str(e)}
    
    return results


def test_manager():
    """Test source manager."""
    print("\n============================================================")
    print(" Testing LyricsSourceManager")
    print("============================================================")
    
    manager = LyricsSourceManager()
    print(f"  Available sources: {', '.join(manager.sources)}")
    
    try:
        result = manager.fetch_lyrics(TEST_ARTIST, TEST_SONG)
        
        if result.success:
            print(f"  OK: Got lyrics from {result.source}")
            print(f"  Length: {len(result.lyrics)} chars")
            return result.lyrics
        else:
            print(f"  FAIL: {result.error}")
            return None
    except Exception as e:
        print(f"  ERROR: {str(e)[:50]}")
        return None


def test_translation():
    """Test translation."""
    print("\n============================================================")
    print(" Testing Translation")
    print("============================================================")
    
    # Test Google Translator
    try:
        google = GoogleTranslator()
        if google.is_available:
            result = google.translate("Hello world", target='zh')
            print(f"  Google: '{result}'")
        else:
            print(f"  Google: not available")
    except Exception as e:
        print(f"  Google ERROR: {str(e)[:50]}")
    
    # Test TranslationManager
    try:
        manager = TranslationManager({})
        print(f"  Available translators: {', '.join(manager.available_translators)}")
        
        texts = ["Hello", "World", "Test"]
        results = manager.translate_batch(texts, delay=0.1)
        print(f"  Batch translation: {len(results)} texts")
    except Exception as e:
        print(f"  Batch ERROR: {str(e)[:50]}")


def run_tests():
    """Run all tests."""
    print("\nStarting Unit Tests...")
    print(f"Test song: {TEST_ARTIST} - {TEST_SONG}")
    
    source_results = test_sources()
    manager_lyrics = test_manager()
    test_translation()
    
    # Summary
    print("\n============================================================")
    print(" Test Summary")
    print("============================================================")
    
    success_count = sum(1 for r in source_results.values() if r.get("success"))
    total_count = len(source_results)
    
    print(f"  Sources working: {success_count}/{total_count}")
    
    # Show issues
    for name, result in source_results.items():
        if result.get("success") and result.get("issues"):
            print(f"    {name}: has issues - {', '.join(result['issues'])}")
    
    print(f"  Manager: {'OK' if manager_lyrics else 'FAIL'}")
    
    return success_count > 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
