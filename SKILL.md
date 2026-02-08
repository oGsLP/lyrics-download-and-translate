---
name: lyrics-download-and-translate
description: Search and download lyrics from multiple sources (Genius, AZLyrics, Musixmatch, Letras, YouTube) and translate them to Chinese. Supports proxy configuration for accessing blocked sites. Use when users need to (1) Find and download song lyrics, (2) Translate English or other language lyrics to Chinese, or (3) Process lyrics files with automatic multi-source fallback.
---

# Lyrics Download and Translate

## Overview

This skill helps you download song lyrics from multiple sources and translate them to Chinese.

**Version**: 2.0.0  
**New in v2.0**: Multi-source search, proxy support, YouTube lyrics extraction

### Features

- 🔍 **Multi-source lyrics search**: Genius, AZLyrics, Musixmatch, Letras, YouTube
- 🌐 **Smart fallback**: Automatically switches sources when one fails
- 🔄 **Multi-source translation**: Google, Baidu, Youdao APIs
- 🚀 **Proxy support**: Works with Clash, v2rayN, Shadowsocks
- 📝 **Format preservation**: Keeps [Verse], [Chorus] markers

## Quick Start

### Prerequisites

```bash
pip install deep_translator
```

### Download Lyrics

```bash
python scripts/download_lyrics.py "Artist Name" "Song Title" [output_path]
```

**Example**:
```bash
python scripts/download_lyrics.py "Taylor Swift" "Anti-Hero" ./lyrics/
```

**Output**: `lyrics/Taylor Swift - Anti-Hero.txt`

### Translate Lyrics

```bash
python scripts/translate_lyrics.py <lyrics_file> [output_path]
```

**Example**:
```bash
python scripts/translate_lyrics.py "lyrics/Taylor Swift - Anti-Hero.txt" ./translated/
```

**Output**: `translated/Taylor Swift - Anti-Hero (translated chinese).txt`

## Configuration

### Config File

Create `config.json` in the skill directory:

```json
{
  "proxy": {
    "enabled": false,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  },
  "translation": {
    "baidu": {
      "appid": "your_appid",
      "secret_key": "your_secret_key"
    },
    "youdao": {
      "appkey": "your_appkey",
      "secret_key": "your_secret_key"
    }
  },
  "settings": {
    "timeout": 30,
    "max_retries": 3
  }
}
```

### Proxy Setup (Clash)

If using Clash:

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  }
}
```

Verify Clash is running:
```bash
netstat -an | findstr 7890
```

## Supported Sources

### Lyrics Sources (Auto Fallback)

1. **Genius** - Primary source with comprehensive database
2. **AZLyrics** - Simple and reliable
3. **Musixmatch** - Large community-contributed database
4. **Letras.com** - Best for Spanish/Portuguese songs
5. **YouTube** - Extracts from video descriptions

### Translation Sources

1. **Google Translate** - Free, no API key (default)
2. **Baidu Translate** - Requires API key
3. **Youdao Translate** - Requires API key

## Usage Examples

### Complete Workflow

```bash
# 1. Download
python scripts/download_lyrics.py "Beyond Awareness" "Crime" ./lyrics/

# 2. Translate
python scripts/translate_lyrics.py ./lyrics/Beyond\ Awareness\ -\ Crime.txt ./output/

# 3. Result
cat ./output/Beyond\ Awareness\ -\ Crime\ \(translated\ chinese\).txt
```

### With Proxy

When proxy is enabled in config.json:

```bash
python scripts/download_lyrics.py "Artist" "Song" ./lyrics/
# Output: [Proxy] Enabled
#         [Proxy] HTTP: http://127.0.0.1:7890
#         Trying Genius...
#         [OK] Found lyrics on Genius!
```

### Batch Processing

Create `songs.txt`:
```
Taylor Swift - Anti-Hero
The Weeknd - Blinding Lights
```

**Windows**:
```batch
for /f "tokens=1* delims=-" %%a in (songs.txt) do (
    python scripts/download_lyrics.py "%%a" "%%b" "./lyrics/"
)
```

**Linux/Mac**:
```bash
while IFS=' - ' read -r artist song; do
    python scripts/download_lyrics.py "$artist" "$song" "./lyrics/"
done < songs.txt
```

## Output Format

### Lyrics File

```
[Verse 1]
Every time I look in your eyes its a memory
Takes me back to the moment that started it
I was coming undone
Got my demons to run

[Chorus]
I was running out of breath then you gave me life
You're the cure
You're my remedy
```

### Translated File

```
Artist Name - Song Title
==================================================
Original Lyrics | 中文翻译
==================================================

【原文】
[Verse 1]
Every time I look in your eyes its a memory

【翻译】
每当我看着你的眼睛，那是一段回忆

------------------------------
```

## Troubleshooting

### "Could not find lyrics"

- Check spelling of artist and song
- Try without special characters
- Enable proxy if Genius/YouTube is blocked
- Script will auto-fallback to other sources

### "Translation failed"

- Check internet connection
- For rate limiting, wait a few minutes
- Configure Baidu/Youdao API as backup

### "Proxy connection failed"

- Verify Clash is running: `netstat -an | findstr 7890`
- Check config.json proxy settings
- Ensure firewall allows local connections

## API Keys

### Baidu Translate

1. Visit https://fanyi-api.baidu.com/
2. Register and create application
3. Get `appid` and `secret_key`
4. Add to config.json

### Youdao Translate

1. Visit https://ai.youdao.com/
2. Register and create application
3. Get `appkey` and `secret_key`
4. Add to config.json

## File Structure

```
lyrics-download-and-translate/
├── CHANGELOG.md              # Version history
├── README.md                 # Quick start
├── SKILL.md                  # This file
├── config.json               # User configuration
└── scripts/
    ├── download_lyrics.py    # Main downloader
    ├── translate_lyrics.py   # Translator
    └── proxy_config.py       # Proxy management
```

## Version History

- **v2.0** (2026-02-09): Multi-source support, proxy configuration, YouTube source
- **v1.1** (2026-02-08): Bug fixes, retry mechanism, encoding fixes
- **v1.0** (2026-02-07): Initial release

## License

MIT License
