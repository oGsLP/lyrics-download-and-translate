# Changelog - Lyrics Download and Translate

## Version 2.0.0 (2026-02-08) - MAJOR UPDATE: Multi-Source Support

### 🎉 New Features

#### 1. Multi-Source Lyrics Search
**Problem**: Genius.com is often blocked or rate-limited  
**Solution**: Automatically try multiple lyrics sources

**New Sources Supported**:
- ✅ **Genius.com** (primary)
- ✅ **AZLyrics.com** 
- ✅ **Musixmatch.com**
- ✅ **Letras.com** (Portuguese/Spanish songs)

**Usage**:
```bash
python scripts/download_lyrics_v2.py "Artist" "Song" ./lyrics/
```

The script will automatically try all sources in order until lyrics are found.

#### 2. Multi-Source Translation
**Problem**: Google Translate may be rate-limited or unavailable in some regions  
**Solution**: Support multiple translation APIs with automatic fallback

**Translation Sources**:
1. **Google Translate** (free, no API key needed)
2. **Baidu Translate** (requires API key, good for China)
3. **Youdao Translate** (requires API key, good for China)

**Usage**:
```bash
# Using Google Translate only (default)
python scripts/translate_lyrics_v2.py "lyrics/Song.txt" ./output/

# Using multiple sources with config
python scripts/translate_lyrics_v2.py "lyrics/Song.txt" ./output/ --config config.json
```

**Config File Format** (`config.json`):
```json
{
  "baidu": {
    "appid": "your_appid",
    "secret_key": "your_secret_key"
  },
  "youdao": {
    "appkey": "your_appkey",
    "secret_key": "your_secret_key"
  }
}
```

### 🔧 Technical Improvements

#### New Files Added:
- `scripts/download_lyrics_v2.py` - Multi-source lyrics downloader
- `scripts/translate_lyrics_v2.py` - Multi-source translation
- `scripts/lyrics_sources.py` - Modular lyrics source classes
- `scripts/translate_sources.py` - Modular translation source classes
- `scripts/config.example.json` - Example API configuration

#### Architecture Changes:
- **Modular Design**: Each source is now a separate class
- **Plugin System**: Easy to add new lyrics or translation sources
- **Automatic Fallback**: Seamlessly switches between sources
- **Better Error Handling**: Each source failure is logged but doesn't stop the process

### 📊 Source Reliability

| Source | Free | Speed | Coverage | Notes |
|--------|------|-------|----------|-------|
| Genius | ✅ | Fast | High | May be blocked in some regions |
| AZLyrics | ✅ | Medium | Medium | Simple, reliable |
| Musixmatch | ✅ | Medium | High | Sometimes requires login |
| Letras | ✅ | Medium | Medium | Best for Spanish/Portuguese |

| Translation | Free | Speed | Accuracy | Setup |
|-------------|------|-------|----------|-------|
| Google | ✅ | Fast | High | No setup needed |
| Baidu | ✅* | Fast | High | Requires API key |
| Youdao | ✅* | Fast | High | Requires API key |

*Free tier available with API key

---

## Version 1.1.0 (2026-02-08)

### Improvements

#### 1. Fixed Windows Console Encoding Issues
- **Problem**: Unicode characters (❌, ✅) caused `UnicodeEncodeError` on Windows
- **Solution**: Added UTF-8 encoding wrapper for stdout/stderr on Windows
- **Files Modified**: 
  - `scripts/download_lyrics.py`
  - `scripts/translate_lyrics.py`

#### 2. Fixed Language Code Bug
- **Problem**: Using `zh-cn` instead of `zh-CN` caused `LanguageNotSupportedException`
- **Solution**: Changed default target language to `zh-CN` (correct case)
- **File Modified**: `scripts/translate_lyrics.py`

#### 3. Added Retry Mechanism
- **Problem**: Network timeouts caused immediate failure
- **Solution**: 
  - Added exponential backoff retry (up to 3 attempts)
  - Increased timeout from 10s to 30s
  - Better handling of socket timeouts and URL errors
- **Files Modified**:
  - `scripts/download_lyrics.py` - `search_genius()` and `extract_lyrics_from_page()`

#### 4. Improved Error Messages
- **Problem**: Vague error messages like "❌ Song not found"
- **Solution**: 
  - Replaced Unicode symbols with ASCII-friendly markers ([X], [OK])
  - Added helpful tips for common errors
  - More descriptive error messages with troubleshooting suggestions
- **Files Modified**:
  - `scripts/download_lyrics.py`
  - `scripts/translate_lyrics.py`

#### 5. Enhanced Lyrics Extraction
- **Problem**: Genius page structure changes broke extraction
- **Solution**: 
  - Added new extraction method for `Lyrics__Container` class
  - Maintained backward compatibility with old methods
  - Better HTML parsing with regex improvements
- **File Modified**: `scripts/download_lyrics.py`

#### 6. Updated User-Agent Headers
- **Problem**: Old User-Agent strings might be blocked
- **Solution**: Updated to modern Chrome 120 User-Agent
- **Files Modified**: 
  - `scripts/download_lyrics.py`

### Testing

Tested with:
- Windows 10/11
- Python 3.11
- deep_translator 1.11.4

### Known Issues

1. **Network Restrictions**: Some networks may block access to Genius.com
   - Workaround: Use VPN or manual download
   
2. **Rate Limiting**: Google Translate may rate-limit heavy usage
   - Workaround: Wait a few minutes between large batch translations

### Usage Examples

```bash
# Download lyrics
python scripts/download_lyrics.py "FabvL" "Your King" "./lyrics/"

# Translate lyrics
python scripts/translate_lyrics.py "lyrics/FabvL - Your King.txt" "./output/"
```

---

## Version 1.0.0 (Initial Release)

- Basic lyrics download from Genius.com
- Translation to Chinese using Google Translate
- Support for deep_translator and googletrans libraries
- Batch processing support
- Side-by-side original and translated output
