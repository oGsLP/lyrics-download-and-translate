"""
Proxy handler module.
Manages HTTP/HTTPS proxy connections.
"""

import urllib.request
from typing import Optional, Dict
from .config import config


class ProxyHandler:
    """Handles proxy configuration and request execution."""
    
    def __init__(self):
        self._opener: Optional[urllib.request.OpenerDirector] = None
        self._setup_proxy()
    
    def _setup_proxy(self):
        """Setup proxy opener from configuration."""
        proxy_config = config.proxy
        
        if not proxy_config.get("enabled", False):
            return
        
        http_proxy = proxy_config.get("http", "")
        https_proxy = proxy_config.get("https", "")
        
        proxies = {}
        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        
        if proxies:
            proxy_handler = urllib.request.ProxyHandler(proxies)
            self._opener = urllib.request.build_opener(proxy_handler)
            
            # Display proxy info
            print("  [Proxy] Enabled")
            if http_proxy:
                print(f"  [Proxy] HTTP: {http_proxy}")
            if https_proxy:
                print(f"  [Proxy] HTTPS: {https_proxy}")
    
    def open(self, url: str, headers: Optional[Dict] = None, timeout: int = 30):
        """Make HTTP request with proxy support."""
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        
        req = urllib.request.Request(url, headers=headers)
        
        if self._opener:
            return self._opener.open(req, timeout=timeout)
        else:
            return urllib.request.urlopen(req, timeout=timeout)
    
    @property
    def is_enabled(self) -> bool:
        return self._opener is not None


# Global proxy handler instance
proxy_handler = ProxyHandler()
