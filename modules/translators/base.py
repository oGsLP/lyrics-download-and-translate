"""
Base translator class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranslationResult:
    """Result container for translation operation."""
    success: bool
    text: str
    source: str = "auto"
    target: str = "zh"
    error: Optional[str] = None


class BaseTranslator(ABC):
    """Abstract base class for translators."""

    @abstractmethod
    def translate(self, text: str, source: str = 'auto', target: str = 'zh') -> str:
        """Translate text and return result."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return translator name."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if translator is properly configured."""
        pass
