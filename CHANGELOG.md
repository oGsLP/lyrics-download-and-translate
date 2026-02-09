# Changelog - Lyrics Download and Translate

All notable changes to this project will be documented in this file.

## [2.0.1] - 2026-02-09

### 🐛 Bug Fixes

#### Lyrics Format
- **Fixed line breaks**: Properly preserve `<br>` and `<p>` tags from HTML
- **Paragraph separation**: Empty lines now correctly separate lyric sections
- **Metadata cleanup**: Better removal of UI elements without breaking structure

#### Translation
- **Proxy support**: Google Translator now correctly uses proxy from config
- **Empty lines**: Translation output preserves paragraph breaks

### 🔧 Improvements

- Better HTML parsing for Letras.com source
- Preserved double newlines as paragraph separators
- Cleaner lyrics extraction logic

---

## [2.0.0] - 2026-02-09

### 🎉 Release Highlights

**Major version update with multi-source support and proxy configuration!**

---

### ✨ New Features

#### Multi-Source Lyrics Search
- **5 lyrics sources**: Genius, AZLyrics, Musixmatch, Letras, YouTube
- **Automatic fallback**: When one source fails, automatically tries others
- **YouTube support**: Extracts lyrics from video descriptions

#### Multi-Source Translation
- **Google Translate**: Free, no API key required (default)
- **Baidu Translate**: Chinese translation API support
- **Youdao Translate**: Alternative Chinese translation API
- **Automatic fallback**: Seamlessly switches between translation services

#### Proxy Support
- **HTTP/HTTPS proxy**: Support for Clash, v2rayN, Shadowsocks, etc.
- **Easy configuration**: Via `config.json`
- **Clash optimized**: Default config for Clash `http://127.0.0.1:7890`

---

### 🔧 Improvements

#### Code Quality
- **Windows encoding fix**: Resolved Unicode display issues
- **Language code fix**: Changed `zh-cn` to `zh-CN`
- **Retry mechanism**: Exponential backoff for failed requests
- **Error messages**: Clearer, ASCII-friendly error markers

#### Architecture
- **Single script**: Merged v1 and v2 into unified `download_lyrics.py`
- **Proxy module**: New `proxy_config.py` for proxy management
- **Clean config**: JSON-compliant configuration file

---

### 📁 New Files

```
scripts/
├── proxy_config.py          # Proxy configuration management
├── download_lyrics.py       # Unified multi-source downloader
└── translate_lyrics.py      # Multi-source translator

config.json                  # User configuration (proxy, API keys)
README.md                    # Quick start guide
```

---

### 📊 Supported Sources

#### Lyrics Sources

| Source | Free | Speed | Coverage | Best For |
|--------|------|-------|----------|----------|
| Genius | ✅ | Fast | High | Comprehensive database |
| AZLyrics | ✅ | Medium | Medium | Simple, reliable |
| Musixmatch | ✅ | Medium | High | Community contributions |
| Letras.com | ✅ | Medium | Medium | Spanish/Portuguese songs |
| YouTube | ✅ | Fast | Medium | Video description lyrics |

#### Translation Sources

| Service | Free Tier | Speed | Setup |
|---------|-----------|-------|-------|
| Google Translate | ✅ Unlimited | Fast | None required |
| Baidu Translate | ✅ 2M chars/month | Fast | API key required |
| Youdao Translate | ✅ 1M chars/month | Fast | API key required |

---

### 🚀 Usage

#### Download Lyrics
```bash
python scripts/download_lyrics.py "Artist Name" "Song Title" ./lyrics/
```

#### Translate Lyrics
```bash
python scripts/translate_lyrics.py ./lyrics/Song.txt ./translated/
```

#### With Proxy (Clash)
```json
// config.json
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  }
}
```

---

### ⚠️ Breaking Changes

- **Config format changed**: Old `_comment` fields removed for JSON compliance
- **Script merge**: `download_lyrics_v2.py` removed, use `download_lyrics.py`
- **Proxy required**: For accessing blocked sites (Genius, YouTube, etc.)

---

### 🐛 Known Issues

1. **Network restrictions**: Some regions require proxy for Genius/YouTube
   - **Solution**: Configure proxy in `config.json`

2. **Translation rate limits**: Google Translate may limit heavy usage
   - **Solution**: Configure Baidu/Youdao API as backup

---

### 🔮 Future Plans

- [ ] GUI interface
- [ ] Batch album processing
- [ ] LRC synchronized lyrics
- [ ] More translation services (DeepL, Azure)
- [ ] Local lyrics cache

---

## [1.1.0] - 2026-02-08

### Bug Fixes

- **Windows encoding**: Fixed `UnicodeEncodeError` for special characters
- **Language code**: Fixed `zh-cn` → `zh-CN` for Chinese translation
- **Timeouts**: Increased timeout from 10s to 30s with retry logic
- **Error messages**: Improved clarity with ASCII markers

### Technical

- Added retry mechanism with exponential backoff
- Updated User-Agent to Chrome 120
- Enhanced lyrics extraction for Genius HTML changes

---

## [1.0.0] - 2026-02-07

### Initial Release

- Basic lyrics download from Genius.com
- Translation to Chinese using Google Translate
- Support for deep_translator library
- Batch processing capability
- Side-by-side translation output

---

## Version Format

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

---

**Full Changelog**: Compare versions on GitHub
