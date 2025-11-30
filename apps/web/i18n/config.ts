// i18n configuration for next-intl (session-based, no URL routing)

export const locales = ['en', 'fr', 'es', 'de', 'bg'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'en';

// RTL (Right-to-Left) languages
export const rtlLocales: Locale[] = [];

export function isRTL(locale: Locale): boolean {
  return rtlLocales.includes(locale);
}

// Locale display names
export const localeNames: Record<Locale, string> = {
  en: 'English',
  fr: 'Français',
  es: 'Español',
  de: 'Deutsch',
  bg: 'Български',
};

// Locale configuration
export const localeConfig = {
  defaultLocale,
  locales,
  rtlLocales,
  localeNames,
};
