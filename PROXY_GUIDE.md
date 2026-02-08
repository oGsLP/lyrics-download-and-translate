# Proxy Configuration Guide - 代理配置指南

## 🌐 概述

Lyrics Download and Translate Skill 现在支持通过代理服务器访问被屏蔽的歌词网站。

**支持的代理类型**:
- HTTP 代理
- HTTPS 代理  
- SOCKS4/SOCKS5 代理

**测试通过的代理工具**:
- ✅ Clash (推荐)
- ✅ Clash Verge
- ✅ v2rayN
- ✅ Shadowsocks
- ✅ 任何标准 HTTP/HTTPS 代理

---

## 📍 Clash 配置（推荐）

### 1. 确认 Clash 运行正常

**默认端口**:
```
HTTP 代理:  http://127.0.0.1:7890
SOCKS5:     socks5://127.0.0.1:7891
```

**验证端口**:
```bash
# Windows
netstat -an | findstr 7890

# 应该看到 127.0.0.1:7890 正在监听
```

### 2. 配置 Skill

编辑 `config.json` 文件:

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  }
}
```

### 3. 使用 Skill

```bash
python scripts/download_lyrics.py "Artist" "Song" ./lyrics/
```

如果代理配置正确，你会看到:
```
Searching for: Artist - Song
  [Proxy] Enabled
  [Proxy] HTTP: http://127.0.0.1:7890
  [Proxy] HTTPS: http://127.0.0.1:7890
Will try multiple sources...

  Trying Genius...
  [OK] Found lyrics on Genius!
```

---

## 🔧 其他代理工具配置

### v2rayN

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809"
  }
}
```

### Shadowsocks

如果使用 Shadowsocks 客户端，需要转换为 HTTP 代理:

**Windows**:
1. 安装 Privoxy 或其他 HTTP→SOCKS 转换工具
2. 或使用 Clash 作为前端

**macOS/Linux**:
```json
{
  "proxy": {
    "enabled": true,
    "http": "socks5://127.0.0.1:1080",
    "https": "socks5://127.0.0.1:1080"
  }
}
```

### 带认证的代理

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://username:password@proxy.example.com:8080",
    "https": "http://username:password@proxy.example.com:8080"
  }
}
```

---

## 📁 配置文件说明

### 文件位置

Config 文件会自动在以下位置搜索:
1. `lyrics-download-and-translate/config.json` (推荐)
2. `./config.json` (当前目录)
3. `~/.lyrics-downloader/config.json` (用户目录)

### 完整配置示例

```json
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  },
  
  "translation": {
    "baidu": {
      "appid": "your_baidu_appid",
      "secret_key": "your_baidu_secret_key"
    },
    "youdao": {
      "appkey": "your_youdao_appkey",
      "secret_key": "your_youdao_secret_key"
    }
  },
  
  "settings": {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 2
  }
}
```

---

## 🧪 测试代理连接

### 方法1: 使用内置测试

```bash
# 在 Python 中测试
python scripts/proxy_config.py
```

输出示例:
```
Testing proxy configuration...

Configuration:
{
  "proxy": {
    "enabled": true,
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
  }
}

✅ Proxy is enabled
   HTTP:  http://127.0.0.1:7890
   HTTPS: http://127.0.0.1:7890

✅ Proxy opener created successfully

Testing connection to Google...
✅ Connection successful! Status: 200
```

### 方法2: 直接测试歌词下载

```bash
python scripts/download_lyrics.py "Taylor Swift" "Anti-Hero" ./test/
```

如果能成功从 Genius 下载，说明代理工作正常。

---

## ❌ 常见问题

### 问题1: 连接超时

**症状**:
```
Genius error: <urlopen error [WinError 10060] 连接超时>
```

**解决**:
1. 确认 Clash 正在运行
2. 检查端口是否正确
3. 尝试增加超时时间:
   ```json
   {
     "settings": {
       "timeout": 60
     }
   }
   ```

### 问题2: 代理被拒绝

**症状**:
```
Error: Proxy connection refused
```

**解决**:
1. 检查 Clash 是否允许局域网连接（如果适用）
2. 确认防火墙未拦截
3. 尝试使用 127.0.0.1 而不是 localhost

### 问题3: 部分网站仍无法访问

**症状**:
某些网站通过代理也无法访问

**解决**:
1. 检查 Clash 规则是否包含这些域名
2. 尝试切换 Clash 节点
3. 使用全局代理模式测试

---

## 🔒 安全提示

1. **不要提交 config.json 到 Git**
   ```bash
   # 已添加到 .gitignore
   echo "config.json" >> .gitignore
   ```

2. **使用本地代理**
   - 推荐使用 127.0.0.1 (本地回环)
   - 避免使用公共代理服务器

3. **代理认证信息**
   - 如果代理需要认证，确保 config.json 文件权限安全
   - Windows: 设置为只读
   - Linux/Mac: `chmod 600 config.json`

---

## 📊 性能对比

| 网络环境 | Genius | YouTube | 翻译服务 |
|---------|--------|---------|----------|
| 无代理 | ❌ 超时 | ❌ 超时 | ⚠️ 慢 |
| Clash 代理 | ✅ 正常 | ✅ 正常 | ✅ 正常 |

---

## 🎯 最佳实践

1. **始终开启代理**: 如果你有稳定的代理，建议始终开启
2. **自动切换**: Skill 会自动在多个源之间切换，即使某个源失败也能继续
3. **本地缓存**: 下载过的歌词会保存在本地，避免重复请求

---

## 💡 高级用法

### 环境变量方式（备用）

如果不想使用 config.json，可以设置环境变量:

**Windows PowerShell**:
```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
python scripts/download_lyrics.py "Artist" "Song" ./lyrics/
```

**Linux/macOS**:
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
python scripts/download_lyrics.py "Artist" "Song" ./lyrics/
```

### 禁用代理

临时禁用代理:
```json
{
  "proxy": {
    "enabled": false
  }
}
```

---

**现在你可以通过 Clash 代理顺利访问所有歌词网站了！** 🎉
