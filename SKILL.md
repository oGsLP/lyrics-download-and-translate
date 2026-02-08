---
name: lyrics-download-and-translate
description: Search and download lyrics from Genius.com and translate them to Chinese. Use when users need to (1) Find and download song lyrics from Genius, (2) Translate English or other language lyrics to Chinese, or (3) Process lyrics files for translation. Supports both automated workflows and step-by-step manual processing.
---

# Lyrics Download and Translate

## Overview

This skill helps you download song lyrics from Genius.com and translate them to Chinese. It consists of two main scripts:

1. **download_lyrics.py** - Searches Genius.com and downloads lyrics
2. **translate_lyrics.py** - Translates lyrics files to Chinese

## Quick Start

### Prerequisites

Python 3.6+ is required. For translation functionality, install one of these packages:

```bash
# Recommended (more reliable)
pip install deep_translator

# Alternative
pip install googletrans==4.0.0-rc1
```

### Download Lyrics

```bash
python scripts/download_lyrics.py "Artist Name" "Song Title" [output_path]
```

Example:
```bash
python scripts/download_lyrics.py "Beyond Awareness" "Crime" "D:/Tools/BesLyric-for-X/lyrics/"
```

Output: `D:/Tools/BesLyric-for-X/lyrics/Beyond Awareness - Crime.txt`

### Translate Lyrics

```bash
python scripts/translate_lyrics.py <lyrics_file> [output_path]
```

Example:
```bash
python scripts/translate_lyrics.py "lyrics/Beyond Awareness - Crime.txt" "D:/Tools/BesLyric-for-X/output/"
```

Output: `D:/Tools/BesLyric-for-X/output/Beyond Awareness - Crime (translated chinese).txt`

## Complete Workflow

### Step 1: Download Lyrics

Search for and download lyrics from Genius.com:

```bash
python scripts/download_lyrics.py "Taylor Swift" "Anti-Hero" "./lyrics/"
```

The script will:
1. Search Genius.com for the song
2. Extract lyrics from the song page
3. Save to: `./lyrics/Taylor Swift - Anti-Hero.txt`

### Step 2: Translate to Chinese

Translate the downloaded lyrics:

```bash
python scripts/translate_lyrics.py "lyrics/Taylor Swift - Anti-Hero.txt" "./output/"
```

The script will:
1. Read the lyrics file
2. Translate to Chinese using Google Translate
3. Save both original and translation: `./output/Taylor Swift - Anti-Hero (translated chinese).txt`

## Output Format

### Downloaded Lyrics Format

```
Artist Name - Song Title
==================================================

[Verse 1]
Lyrics line 1
Lyrics line 2
...
```

### Translated Lyrics Format

```
Artist Name - Song Title
==================================================
Original Lyrics | 中文翻译
==================================================

【原文】
Original lyrics paragraph

【翻译】
Translated Chinese text

------------------------------
```

## Advanced Usage

### Batch Processing Multiple Songs

Create a text file `songs.txt` with one song per line:
```
Beyond Awareness - Crime
Taylor Swift - Anti-Hero
The Weeknd - Blinding Lights
```

Then use a batch script:

**Windows (batch_process.bat):**
```batch
@echo off
set LYRICS_DIR=D:\Tools\BesLyric-for-X\lyrics
set OUTPUT_DIR=D:\Tools\BesLyric-for-X\output

for /f "tokens=1* delims=-" %%a in (songs.txt) do (
    python scripts/download_lyrics.py "%%a" "%%b" "%LYRICS_DIR%"
    python scripts/translate_lyrics.py "%LYRICS_DIR%\%%a - %%b.txt" "%OUTPUT_DIR%"
)
```

**Linux/Mac (batch_process.sh):**
```bash
#!/bin/bash
LYRICS_DIR="./lyrics"
OUTPUT_DIR="./output"

while IFS=' - ' read -r artist song; do
    python scripts/download_lyrics.py "$artist" "$song" "$LYRICS_DIR"
    python scripts/translate_lyrics.py "$LYRICS_DIR/$artist - $song.txt" "$OUTPUT_DIR"
done < songs.txt
```

### Handling Translation Errors

If translation fails:
1. Check your internet connection
2. Try installing the alternative translation library
3. For very long songs, the script automatically chunks the text

### Custom Translation Services

To use other translation services (Youdao, Baidu, etc.), modify `translate_lyrics.py`:

1. Add your API credentials
2. Implement the translation function
3. Replace `translate_with_google()` with your implementation

## Troubleshooting

### "Song not found on Genius"
- Try alternative spellings or the original artist name
- Some songs may not be available on Genius
- Try searching without special characters

### "Could not extract lyrics"
- Genius may have changed their page structure
- The song page might have anti-scraping measures
- Try accessing the song page manually to verify it exists

### "Translation library not found"
```bash
pip install deep_translator
```

### "Translation error"
- Check internet connection
- Google Translate may rate-limit requests for very long texts
- The script handles chunking automatically, but wait a moment and retry

## Resources

### scripts/

- **download_lyrics.py** - Downloads lyrics from Genius.com
  - Handles search and web scraping
  - Multiple extraction methods for reliability
  - Saves formatted lyrics files

- **translate_lyrics.py** - Translates lyrics to Chinese
  - Uses Google Translate via deep_translator or googletrans
  - Preserves formatting with side-by-side display
  - Handles large texts with automatic chunking

### references/

Additional documentation and examples (if needed for complex use cases).

### assets/

Template files or resources (if needed).

## Notes

- Lyrics extraction relies on Genius.com page structure and may need updates if Genius changes their HTML
- Translation uses free Google Translate which has usage limits
- For commercial or heavy use, consider obtaining official API keys
- Respect copyright laws and Genius.com's terms of service
