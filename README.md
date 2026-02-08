# Lyrics Download and Translate

一款支持多源歌词下载和翻译的 Claude Code Skill。

## ✨ 特性

- 🔍 **多源歌词搜索**: 自动在 Genius、AZLyrics、Musixmatch、Letras、YouTube 中搜索
- 🌐 **智能回退**: 当一个源失败时自动切换到其他源
- 🔄 **翻译支持**: 支持 Google、百度、有道翻译 API
- 🚀 **代理支持**: 内置代理配置，支持 Clash 等工具
- 📝 **格式保留**: 保留 [Verse]、[Chorus] 等段落标记

## 🚀 快速开始

### 安装依赖

```bash
pip install deep_translator
```

### 下载歌词

```bash
python scripts/download_lyrics.py "Taylor Swift" "Anti-Hero" ./lyrics/
```

### 翻译歌词

```bash
python scripts/translate_lyrics.py ./lyrics/Taylor\ Swift\ -\ Anti-Hero.txt ./translated/
```

## ⚙️ 配置

### 配置文件

创建 `config.json` 文件：

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
    "max_retries": 3,
    "retry_delay": 2
  }
}
```

### 代理配置（Clash）

如果使用 Clash，修改 `config.json`：

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  }
}
```

验证 Clash 端口：

```bash
netstat -an | findstr 7890
```

支持其他代理工具：v2rayN、Shadowsocks 等。

## 📚 支持的歌词源

| 源 | 特点 | 状态 |
|---|------|------|
| **Genius** | 最全的歌词数据库 | ✅ 支持 |
| **AZLyrics** | 简洁快速 | ✅ 支持 |
| **Musixmatch** | 社区贡献 | ✅ 支持 |
| **Letras.com** | 西班牙语/葡萄牙语 | ✅ 支持 |
| **YouTube** | 视频描述中的歌词 | ✅ 支持 |

## 🔧 翻译 API 配置

### 百度翻译

1. 访问 https://fanyi-api.baidu.com/
2. 注册并创建应用
3. 获取 `appid` 和 `secret_key`
4. 填入 `config.json`

### 有道翻译

1. 访问 https://ai.youdao.com/
2. 注册并创建应用
3. 获取 `appkey` 和 `secret_key`
4. 填入 `config.json`

## 📖 使用示例

### 完整工作流

```bash
# 1. 下载歌词
python scripts/download_lyrics.py "Beyond Awareness" "Crime" ./lyrics/

# 2. 翻译歌词
python scripts/translate_lyrics.py ./lyrics/Beyond\ Awareness\ -\ Crime.txt ./output/

# 3. 查看结果
cat ./output/Beyond\ Awareness\ -\ Crime\ \(translated\ chinese\).txt
```

## 📝 输出格式

歌词文件格式示例：

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

## ❓ 常见问题

**Q: Genius 无法访问怎么办？**  
A: 配置代理或等待自动切换到其他源（AZLyrics、Musixmatch、Letras、YouTube）。

**Q: 翻译失败怎么办？**  
A: 检查网络连接，或配置百度/有道 API 作为备用。

**Q: 如何禁用代理？**  
A: 修改 `config.json`，设置 `"enabled": false`。

## 📄 相关文档

- [SKILL.md](./SKILL.md) - 详细使用说明
- [CHANGELOG.md](./CHANGELOG.md) - 更新日志

## 🏷️ 版本

当前版本: v2.0

## 📜 License

MIT License
