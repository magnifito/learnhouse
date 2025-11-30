"""
Translation utilities using GNU gettext

Provides functions for translating strings in the API.
"""

import gettext
import os
from pathlib import Path
from typing import Optional
from functools import lru_cache

# Path to locale directory (will be created in setup step)
LOCALE_DIR = Path(__file__).parent.parent.parent / 'locales'

# Supported locales
SUPPORTED_LOCALES = ['en', 'fr', 'es', 'ar']
DEFAULT_LOCALE = 'en'


@lru_cache(maxsize=32)
def get_translator(locale: str = DEFAULT_LOCALE) -> gettext.GNUTranslations:
    """
    Get a translator instance for the specified locale.

    Uses LRU cache to avoid re-loading translation files.

    Args:
        locale: Locale code (e.g., 'en', 'fr', 'es', 'ar')

    Returns:
        GNUTranslations instance for the locale
    """
    # Validate locale
    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE

    try:
        # Load translation file for locale
        translation = gettext.translation(
            domain='messages',  # Translation domain (messages.po)
            localedir=str(LOCALE_DIR),
            languages=[locale],
            fallback=True  # Fall back to default if locale not found
        )
        return translation
    except Exception as e:
        # If loading fails, return NullTranslations (no-op translator)
        print(f"Warning: Failed to load translations for locale '{locale}': {e}")
        return gettext.NullTranslations()


def _(message: str, locale: str = DEFAULT_LOCALE) -> str:
    """
    Translate a message to the specified locale.

    This is the main translation function used throughout the API.

    Args:
        message: String to translate (English source text)
        locale: Target locale code

    Returns:
        Translated string, or original message if translation not found

    Example:
        >>> _("Welcome back!", locale="fr")
        "Bon retour!"
    """
    translator = get_translator(locale)
    return translator.gettext(message)


def ngettext(singular: str, plural: str, n: int, locale: str = DEFAULT_LOCALE) -> str:
    """
    Translate a message with plural forms.

    Args:
        singular: Singular form (e.g., "1 student")
        plural: Plural form (e.g., "5 students")
        n: Count to determine which form to use
        locale: Target locale code

    Returns:
        Translated string in correct plural form

    Example:
        >>> ngettext("1 student", "{n} students", 5, locale="fr")
        "5 étudiants"
    """
    translator = get_translator(locale)
    return translator.ngettext(singular, plural, n)


def clear_translation_cache():
    """
    Clear the translation cache.

    Useful when reloading translations after updates.
    """
    get_translator.cache_clear()
