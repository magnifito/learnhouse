// Locale detection utilities for session-based i18n

import { defaultLocale, locales, type Locale } from './config';

/**
 * Get locale from cookie (client-side)
 */
export function getLocaleFromCookie(): Locale {
  if (typeof document === 'undefined') return defaultLocale;

  const cookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('NEXT_LOCALE='));

  const cookieValue = cookie ? cookie.split('=')[1] : null;

  // Validate locale is supported
  if (cookieValue && locales.includes(cookieValue as Locale)) {
    return cookieValue as Locale;
  }

  return defaultLocale;
}

/**
 * Set locale cookie
 */
export function setLocaleCookie(locale: Locale): void {
  // Set cookie for 1 year
  document.cookie = `NEXT_LOCALE=${locale}; path=/; max-age=31536000; SameSite=Lax`;
}

/**
 * Get locale from browser's language preference
 */
export function getBrowserLocale(): Locale {
  if (typeof navigator === 'undefined') return defaultLocale;

  const browserLang = navigator.language.split('-')[0];

  // Check if browser language is supported
  if (locales.includes(browserLang as Locale)) {
    return browserLang as Locale;
  }

  return defaultLocale;
}

/**
 * Detect locale with priority chain:
 * 1. User's database preference (from session)
 * 2. Cookie (NEXT_LOCALE)
 * 3. Browser language
 * 4. Fallback to default (en)
 */
export function detectLocale(userPreferredLocale?: string | null): Locale {
  // 1. User preference from database (highest priority)
  if (userPreferredLocale && locales.includes(userPreferredLocale as Locale)) {
    return userPreferredLocale as Locale;
  }

  // 2. Cookie
  const cookieLocale = getLocaleFromCookie();
  if (cookieLocale !== defaultLocale) {
    return cookieLocale;
  }

  // 3. Browser language
  const browserLocale = getBrowserLocale();
  if (browserLocale !== defaultLocale) {
    return browserLocale;
  }

  // 4. Fallback
  return defaultLocale;
}
