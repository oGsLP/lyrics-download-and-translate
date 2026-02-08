"""
Configuration management module.
Handles loading and accessing config.json settings.
"""

import json
from pathlib import Path
from typing import Dict


class Config:
    """Configuration manager for lyrics downloader."""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config = cls._load_config()
        return cls._instance

    @staticmethod
    def _load_config() -> Dict:
        """Load configuration from config.json."""
        possible_paths = [
            Path(__file__).parent.parent / "config.json",
            Path.cwd() / "config.json",
            Path.home() / ".lyrics-downloader" / "config.json",
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception:
                    pass

        return {
            "proxy": {"enabled": False},
            "translation": {},
            "settings": {"timeout": 30, "max_retries": 3, "retry_delay": 2}
        }

    def reload(self):
        """Reload configuration from file."""
        self._config = self._load_config()

    @property
    def proxy(self) -> Dict:
        return self._config.get("proxy", {"enabled": False})

    @property
    def translation(self) -> Dict:
        return self._config.get("translation", {})

    @property
    def settings(self) -> Dict:
        return self._config.get("settings", {"timeout": 30, "max_retries": 3})

    def get(self, key: str, default=None):
        return self._config.get(key, default)


config = Config()
