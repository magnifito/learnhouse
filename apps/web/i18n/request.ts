import { getRequestConfig } from 'next-intl/server';
import { headers, cookies } from 'next/headers';
import { defaultLocale, locales } from './config';

export default getRequestConfig(async () => {
    // Basic locale detection for server components
    const cookieStore = await cookies(); // Next.js 15+ await cookies()
    const localeCookie = cookieStore.get('NEXT_LOCALE');
    let locale = localeCookie?.value || defaultLocale;

    if (!locales.includes(locale as any)) {
        locale = defaultLocale;
    }

    return {
        locale,
        messages: (await import(`../messages/${locale}.json`)).default
    };
});
