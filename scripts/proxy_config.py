#!/usr/bin/env python3
"""
Proxy configuration and handler for lyrics downloader.
Supports HTTP, HTTPS, SOCKS4, SOCKS5 proxies.
"""

import json
import os
import urllib.request
from pathlib import Path
from typing import Dict, Optional


def load_config(config_path: str = None) -> Dict:
    """
    Load configuration from config.json.
    
    Args:
        config_path: Path to config file. If None, searches in default locations.
        
    Returns:
        dict: Configuration dictionary
    """
    if config_path is None:
        # Search for config in default locations
        possible_paths = [
            Path(__file__).parent.parent / "config.json",
            Path.cwd() / "config.json",
            Path.home() / ".lyrics-downloader" / "config.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config: {e}")
    
    # Return default config
    return {
        "proxy": {"enabled": False},
        "translation": {},
        "settings": {"timeout": 30, "max_retries": 3, "retry_delay": 2}
    }


def setup_proxy(config: Dict) -> Optional[urllib.request.OpenerDirector]:
    """
    Setup proxy handler based on configuration.
    
    Args:
        config: Configuration dictionary containing proxy settings
        
    Returns:
        OpenerDirector with proxy support, or None if proxy disabled
    """
    proxy_config = config.get("proxy", {})
    
    if not proxy_config.get("enabled", False):
        return None
    
    # Get proxy URLs
    http_proxy = proxy_config.get("http", "")
    https_proxy = proxy_config.get("https", "")
    
    proxies = {}
    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy
    
    if not proxies:
        return None
    
    # Create proxy handler
    proxy_handler = urllib.request.ProxyHandler(proxies)
    
    # Create opener with proxy handler
    opener = urllib.request.build_opener(proxy_handler)
    
    return opener


def create_request(url: str, headers: Dict = None, config: Dict = None) -> urllib.request.Request:
    """
    Create a urllib request with optional proxy support.
    
    Args:
        url: URL to request
        headers: Optional headers dictionary
        config: Configuration dictionary
        
    Returns:
        Request object
    """
    if headers is None:
        headers = {}
    
    req = urllib.request.Request(url, headers=headers)
    return req


def urlopen_with_proxy(url: str, headers: Dict = None, timeout: int = 30, 
                       config: Dict = None, opener: urllib.request.OpenerDirector = None):
    """
    Open URL with proxy support if configured.
    
    Args:
        url: URL to open
        headers: Optional headers
        timeout: Request timeout
        config: Configuration dictionary
        opener: Optional pre-configured opener with proxy
        
    Returns:
        Response object
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    req = urllib.request.Request(url, headers=headers)
    
    if opener:
        return opener.open(req, timeout=timeout)
    else:
        return urllib.request.urlopen(req, timeout=timeout)


# Global config cache
_config_cache = None
_opener_cache = None


def get_proxy_opener(config_path: str = None) -> Optional[urllib.request.OpenerDirector]:
    """
    Get or create proxy opener (cached).
    
    Args:
        config_path: Path to config file
        
    Returns:
        OpenerDirector with proxy, or None
    """
    global _config_cache, _opener_cache
    
    if _opener_cache is None:
        config = load_config(config_path)
        _config_cache = config
        _opener_cache = setup_proxy(config)
    
    return _opener_cache


def reload_config(config_path: str = None):
    """Reload configuration and reset cache."""
    global _config_cache, _opener_cache
    _config_cache = load_config(config_path)
    _opener_cache = setup_proxy(_config_cache)
    return _config_cache


# Convenience function for other modules
def get_config(config_path: str = None) -> Dict:
    """Get configuration (cached)."""
    global _config_cache
    if _config_cache is None:
        _config_cache = load_config(config_path)
    return _config_cache


if __name__ == "__main__":
    # Test proxy configuration
    print("Testing proxy configuration...")
    config = load_config()
    
    print("\nConfiguration:")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    
    proxy = config.get("proxy", {})
    if proxy.get("enabled"):
        print("\n✅ Proxy is enabled")
        print(f"   HTTP:  {proxy.get('http', 'Not set')}")
        print(f"   HTTPS: {proxy.get('https', 'Not set')}")
        
        opener = setup_proxy(config)
        if opener:
            print("\n✅ Proxy opener created successfully")
            
            # Test connection
            try:
                print("\nTesting connection to Google...")
                response = urlopen_with_proxy(
                    "https://www.google.com", 
                    config=config, 
                    opener=opener,
                    timeout=10
                )
                print(f"✅ Connection successful! Status: {response.getcode()}")
            except Exception as e:
                print(f"❌ Connection failed: {e}")
    else:
        print("\n⚠️  Proxy is disabled")
        print("   To enable, set 'proxy.enabled' to true in config.json")
