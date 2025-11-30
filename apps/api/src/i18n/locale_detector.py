"""
Locale detection utilities for API requests

Detects user's preferred locale from HTTP headers.
"""

from typing import Optional
from fastapi import Request

# Supported locales - must match frontend config
SUPPORTED_LOCALES = ['en', 'fr', 'es', 'ar']
DEFAULT_LOCALE = 'en'


def get_locale_from_header(request: Request) -> str:
    """
    Extract locale from X-Locale header.

    Args:
        request: FastAPI request object

    Returns:
        Locale code (e.g., 'en', 'fr') or default locale if not found/invalid
    """
    locale = request.headers.get('X-Locale', '').lower()

    # Validate locale is supported
    if locale and locale in SUPPORTED_LOCALES:
        return locale

    return DEFAULT_LOCALE


def detect_locale(
    request: Request,
    user_preferred_locale: Optional[str] = None
) -> str:
    """
    Detect locale with priority chain:
    1. User's database preference
    2. X-Locale header
    3. Fallback to default (en)

    Args:
        request: FastAPI request object
        user_preferred_locale: User's stored locale preference from database

    Returns:
        Locale code to use for this request
    """
    # 1. User preference from database (highest priority)
    if user_preferred_locale and user_preferred_locale in SUPPORTED_LOCALES:
        return user_preferred_locale

    # 2. X-Locale header
    header_locale = get_locale_from_header(request)
    if header_locale != DEFAULT_LOCALE:
        return header_locale

    # 3. Fallback
    return DEFAULT_LOCALE


def is_rtl_locale(locale: str) -> bool:
    """
    Check if locale uses right-to-left text direction.

    Args:
        locale: Locale code

    Returns:
        True if locale uses RTL, False otherwise
    """
    RTL_LOCALES = ['ar', 'he', 'fa', 'ur']
    return locale in RTL_LOCALES
