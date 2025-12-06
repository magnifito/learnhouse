'use client'
import '../styles/globals.css'
import StyledComponentsRegistry from '../components/Utils/libs/styled-registry'
import { motion } from 'framer-motion'
import { SessionProvider } from 'next-auth/react'
import LHSessionProvider from '@components/Contexts/LHSessionContext'
import { isDevEnv } from './auth/options'
import Script from 'next/script'
import { NextIntlClientProvider } from 'next-intl'
import { useEffect, useState } from 'react'
import { getLocaleFromCookie } from '@/i18n/utils'
import { defaultLocale, rtlLocales, type Locale } from '@/i18n/config'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [locale, setLocale] = useState<Locale>(defaultLocale)
  const [messages, setMessages] = useState<any>(null)

  useEffect(() => {
    // Detect locale from cookie on client side
    const detectedLocale = getLocaleFromCookie()
    setLocale(detectedLocale)

    // Load messages for the detected locale
    async function loadMessages() {
      const msgs = await import(`@/messages/${detectedLocale}.json`)
      setMessages(msgs.default)
    }
    loadMessages()

    // Safety cleanup: ensure body scroll is never permanently locked
    // This prevents issues where dialogs/modals don't clean up properly
    const cleanupInterval = setInterval(() => {
      const hasOpenDialog = document.querySelector('[role="dialog"][data-state="open"]')
      const isScrollLocked = document.body.hasAttribute('data-scroll-locked')

      if (isScrollLocked && !hasOpenDialog) {
        // Scroll is locked but no dialog is open - clean up
        document.body.removeAttribute('data-scroll-locked')
        document.body.style.pointerEvents = ''
        document.body.style.overflow = ''
      }
    }, 1000) // Check every second

    return () => clearInterval(cleanupInterval)
  }, [])

  const variants = {
    hidden: { opacity: 0, x: 0, y: 0 },
    enter: { opacity: 1, x: 0, y: 0 },
    exit: { opacity: 0, x: 0, y: 0 },
  }

  const isRtl = rtlLocales.includes(locale)

  return (
    <html className="" lang={locale} dir={isRtl ? 'rtl' : 'ltr'}>
      <head />
      <body>
        {/* Inject runtime configuration for client-side access */}
        <Script src="/runtime-config.js" strategy="beforeInteractive" />
        {isDevEnv ? '' : <Script data-website-id="a1af6d7a-9286-4a1f-8385-ddad2a29fcbb" src="/umami/script.js" />}
        {messages ? (
          <NextIntlClientProvider locale={locale} messages={messages}>
            <SessionProvider key="session-provider" refetchInterval={60000}>
              <LHSessionProvider>
                <StyledComponentsRegistry>
                  <motion.main
                    variants={variants} // Pass the variant object into Framer Motion
                    initial="hidden" // Set the initial state to variants.hidden
                    animate="enter" // Animated state to variants.enter
                    exit="exit" // Exit state (used later) to variants.exit
                    transition={{ type: 'tween' }} // Set the transition to tween
                  >
                    {children}
                  </motion.main>
                </StyledComponentsRegistry>
              </LHSessionProvider>
            </SessionProvider>
          </NextIntlClientProvider>
        ) : (
          <div>Loading...</div>
        )}
      </body>
    </html>
  )
}
