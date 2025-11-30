'use client';

import React, { useState } from 'react';
import { Globe } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@components/ui/select";
import { Label } from "@components/ui/label";
import { locales, localeNames, type Locale, defaultLocale } from '@/i18n/config';
import { getLocaleFromCookie, setLocaleCookie } from '@/i18n/request';
import { toast } from 'react-hot-toast';
import { useTranslations } from 'next-intl';

interface LanguageSelectorProps {
  className?: string;
  showLabel?: boolean;
}

export default function LanguageSelector({
  className = '',
  showLabel = true
}: LanguageSelectorProps) {
  const t = useTranslations('settings');
  const [currentLocale, setCurrentLocale] = useState<Locale>(() => getLocaleFromCookie());

  const handleLanguageChange = (newLocale: string) => {
    const locale = newLocale as Locale;

    // Set the cookie
    setLocaleCookie(locale);

    // Update local state
    setCurrentLocale(locale);

    // Show success message
    toast.success(`Language changed to ${localeNames[locale]}`, {
      duration: 2000,
    });

    // Reload page to apply new language
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  return (
    <div className={className}>
      {showLabel && (
        <Label htmlFor="language" className="flex items-center gap-2 mb-2">
          <Globe className="w-4 h-4" />
          {t('language')}
        </Label>
      )}
      <Select value={currentLocale} onValueChange={handleLanguageChange}>
        <SelectTrigger id="language" className="w-full">
          <SelectValue>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4" />
              <span>{localeNames[currentLocale]}</span>
            </div>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {locales.map((locale) => (
            <SelectItem key={locale} value={locale}>
              <div className="flex items-center gap-2">
                <span className="text-lg">{getLanguageFlag(locale)}</span>
                <span>{localeNames[locale]}</span>
                {locale === currentLocale && (
                  <span className="ml-auto text-green-600 text-xs">✓ Active</span>
                )}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <p className="text-xs text-gray-500 mt-1">
        {t('selectLanguage')}
      </p>
    </div>
  );
}

// Helper function to get flag emoji for language
function getLanguageFlag(locale: Locale): string {
  const flags: Record<Locale, string> = {
    en: '🇬🇧',
    fr: '🇫🇷',
    es: '🇪🇸',
    de: '🇩🇪',
    bg: '🇧🇬',
  };
  return flags[locale] || '🌐';
}
