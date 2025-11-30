"""
i18n utilities for LearnHouse API

Provides internationalization support using GNU gettext.
"""

from .translator import get_translator, _
from .locale_detector import get_locale_from_header, detect_locale

__all__ = [
    'get_translator',
    '_',
    'get_locale_from_header',
    'detect_locale',
]
