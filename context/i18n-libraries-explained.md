# i18n Libraries Deep Dive: How They Work

This document explains in detail how the chosen internationalization libraries work for LearnHouse, including their internal mechanisms, usage patterns, and best practices.

---

## Table of Contents

1. [Frontend: next-intl](#frontend-next-intl)
2. [Backend: Babel (GNU gettext)](#backend-babel-gnu-gettext)
3. [How They Work Together](#how-they-work-together)
4. [Common Patterns & Best Practices](#common-patterns--best-practices)

---

## Frontend: next-intl

### What is next-intl?

**next-intl** is a React internationalization library specifically built for Next.js 13+ App Router. It provides type-safe translations with full support for both server and client components.

**Repository:** https://github.com/amannn/next-intl
**Documentation:** https://next-intl-docs.vercel.app/

### Core Concepts

#### 1. Translation Messages (JSON Format)

Messages are stored in JSON files organized by locale:

```
apps/web/messages/
├── en.json         # English (default)
├── fr.json         # French
├── es.json         # Spanish
└── ar.json         # Arabic
```

**Structure Example (`messages/en.json`):**
```json
{
  "navigation": {
    "home": "Home",
    "courses": "Courses",
    "dashboard": "Dashboard"
  },
  "courses": {
    "title": "All Courses",
    "createNew": "Create New Course",
    "empty": "No courses available yet",
    "enrolledCount": "{count, plural, =0 {No students} =1 {1 student} other {# students}}"
  },
  "auth": {
    "signIn": "Sign in",
    "signUp": "Sign up",
    "welcome": "Welcome back, {name}!",
    "emailPlaceholder": "Enter your email"
  }
}
```

**Key Features:**
- **Nested namespaces**: Group related translations (`navigation`, `courses`, `auth`)
- **Variables**: Use `{name}` for dynamic content
- **Pluralization**: ICU message format for plural rules
- **Type safety**: TypeScript autocomplete for message keys

#### 2. How next-intl Works (Session-Based Mode)

**Architecture Flow:**

```
1. User Request
   ↓
2. Root Layout (apps/web/app/layout.tsx)
   - Detects locale from session/cookie/browser
   ↓
3. Load Translation Messages
   - import(`../messages/${locale}.json`)
   ↓
4. NextIntlClientProvider
   - Wraps app with locale context
   - Makes messages available to all components
   ↓
5. Components
   - Use useTranslations() hook
   - Access translated strings
```

**Detailed Mechanism:**

```typescript
// Step 1: Layout detects locale
import { NextIntlClientProvider } from 'next-intl';

export default function RootLayout({ children }) {
  const session = useLHSession();
  const [locale, setLocale] = useState('en');
  const [messages, setMessages] = useState(null);

  useEffect(() => {
    // Detect locale (priority order)
    const detectedLocale =
      session?.user?.preferred_locale ||  // 1. Database
      getCookie('NEXT_LOCALE') ||         // 2. Cookie
      navigator.language.split('-')[0] || // 3. Browser
      'en';                               // 4. Fallback

    setLocale(detectedLocale);

    // Dynamically import translation file
    import(`../messages/${detectedLocale}.json`)
      .then(module => setMessages(module.default));
  }, [session]);

  if (!messages) return null; // Wait for messages to load

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider
          locale={locale}
          messages={messages}
        >
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

#### 3. Using Translations in Components

**Client Component Example:**

```typescript
'use client';
import { useTranslations } from 'next-intl';

export default function CourseCard({ course }) {
  const t = useTranslations('courses');

  return (
    <div>
      <h2>{t('title')}</h2>
      {/* Output: "All Courses" (en) or "Tous les cours" (fr) */}

      <button>{t('createNew')}</button>
      {/* Output: "Create New Course" (en) or "Créer un nouveau cours" (fr) */}

      <p>{t('enrolledCount', { count: course.studentCount })}</p>
      {/* Output: "5 students" (en) or "5 étudiants" (fr) */}
    </div>
  );
}
```

**How `useTranslations()` Works Internally:**

1. **Hook calls React Context**: `useTranslations('courses')` accesses the context created by `NextIntlClientProvider`
2. **Namespace lookup**: Finds the `courses` key in the loaded messages object
3. **Key resolution**: When you call `t('title')`, it looks up `messages.courses.title`
4. **Variable interpolation**: Replaces `{name}`, `{count}` with provided values
5. **Pluralization**: Applies ICU plural rules based on locale
6. **Returns translated string**

**Server Component Example:**

```typescript
import { useTranslations } from 'next-intl/server';

export default async function CoursePage() {
  const t = await useTranslations('courses');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('empty')}</p>
    </div>
  );
}
```

**Note:** Server components use `next-intl/server` which works with async/await.

#### 4. Advanced Features

**A. Variable Interpolation**

```json
{
  "greeting": "Hello, {username}! You have {count} notifications."
}
```

```typescript
const t = useTranslations('messages');
t('greeting', { username: 'Alice', count: 5 });
// Output: "Hello, Alice! You have 5 notifications."
```

**B. Pluralization (ICU Message Format)**

```json
{
  "items": "{count, plural, =0 {No items} =1 {One item} other {# items}}"
}
```

```typescript
t('items', { count: 0 });  // "No items"
t('items', { count: 1 });  // "One item"
t('items', { count: 5 });  // "5 items"
```

**ICU Plural Rules by Locale:**
- English: `one`, `other`
- French: `one`, `other` (but 0 is "other", not "zero")
- Arabic: `zero`, `one`, `two`, `few`, `many`, `other` (complex rules)
- Russian: `one`, `few`, `many`, `other`

**C. Rich Text Formatting**

```json
{
  "terms": "By signing up, you agree to our <link>Terms of Service</link>."
}
```

```typescript
const t = useTranslations('auth');
t.rich('terms', {
  link: (chunks) => <a href="/terms">{chunks}</a>
});
// Output: "By signing up, you agree to our <a href="/terms">Terms of Service</a>."
```

**D. Date & Number Formatting**

```typescript
import { useFormatter } from 'next-intl';

function PriceDisplay({ amount, date }) {
  const format = useFormatter();

  return (
    <div>
      <p>{format.number(amount, { style: 'currency', currency: 'USD' })}</p>
      {/* US: $1,234.56 | FR: 1 234,56 $ */}

      <p>{format.dateTime(date, { dateStyle: 'long' })}</p>
      {/* US: November 28, 2025 | FR: 28 novembre 2025 */}
    </div>
  );
}
```

#### 5. Type Safety

**Enable TypeScript autocomplete:**

```typescript
// global.d.ts
type Messages = typeof import('./messages/en.json');

declare interface IntlMessages extends Messages {}
```

Now TypeScript will autocomplete:

```typescript
const t = useTranslations('courses');
t('title');      // ✅ Autocomplete works!
t('invalid');    // ❌ TypeScript error: Key doesn't exist
```

#### 6. How Session-Based Locale Detection Works

**Cookie-Based Detection (for guests):**

```typescript
// Set cookie when user changes language
function setLocaleCookie(locale: string) {
  document.cookie = `NEXT_LOCALE=${locale}; path=/; max-age=31536000`;
  // max-age=31536000 = 1 year
}

// Read cookie on page load
function getLocaleFromCookie(): string {
  const cookie = document.cookie
    .split('; ')
    .find(row => row.startsWith('NEXT_LOCALE='));

  return cookie ? cookie.split('=')[1] : 'en';
}
```

**Database-Based Detection (for authenticated users):**

```typescript
// User model has preferred_locale field
interface User {
  id: number;
  email: string;
  preferred_locale: string; // 'en', 'fr', 'es', 'ar'
}

// Load from session
const session = await getSession();
const locale = session?.user?.preferred_locale || 'en';
```

**Priority Chain:**

```typescript
function detectLocale(session: any): string {
  // 1. Authenticated user's DB preference (highest priority)
  if (session?.user?.preferred_locale) {
    return session.user.preferred_locale;
  }

  // 2. Guest user's cookie
  const cookieLocale = getLocaleFromCookie();
  if (cookieLocale && ['en', 'fr', 'es', 'ar'].includes(cookieLocale)) {
    return cookieLocale;
  }

  // 3. Browser's Accept-Language
  if (typeof navigator !== 'undefined') {
    const browserLang = navigator.language.split('-')[0];
    if (['en', 'fr', 'es', 'ar'].includes(browserLang)) {
      return browserLang;
    }
  }

  // 4. Fallback
  return 'en';
}
```

#### 7. Performance Optimization

**A. Code Splitting (Bundle Size)**

Translation files are loaded dynamically:

```typescript
// Instead of importing all locales upfront
import enMessages from './messages/en.json';
import frMessages from './messages/fr.json';

// Use dynamic import (loads only needed locale)
const messages = await import(`./messages/${locale}.json`);
```

**Result:** Only the current locale's JSON is sent to the browser.

**B. Caching**

```typescript
// Cache loaded messages
const messagesCache = new Map<string, any>();

async function loadMessages(locale: string) {
  if (messagesCache.has(locale)) {
    return messagesCache.get(locale);
  }

  const messages = await import(`./messages/${locale}.json`);
  messagesCache.set(locale, messages);
  return messages;
}
```

**C. Server-Side Rendering**

next-intl works with SSR out of the box:
- Messages loaded on server
- Rendered HTML includes translated content
- No client-side flash of untranslated text

---

## Backend: Babel (GNU gettext)

### What is GNU gettext?

**GNU gettext** is the industry-standard internationalization system for software, created in 1995. It's used by thousands of projects across multiple programming languages.

**Babel** is the Python implementation/toolchain for gettext.

**Documentation:** http://babel.pocoo.org/

### Core Concepts

#### 1. Translation Files (PO/MO Format)

**File Structure:**

```
apps/api/locales/
├── messages.pot         # Template (POT = Portable Object Template)
├── en/
│   └── LC_MESSAGES/
│       ├── messages.po  # Human-readable (PO = Portable Object)
│       └── messages.mo  # Compiled binary (MO = Machine Object)
├── fr/
│   └── LC_MESSAGES/
│       ├── messages.po
│       └── messages.mo
└── es/
    └── LC_MESSAGES/
        ├── messages.po
        └── messages.mo
```

**PO File Format (`locales/fr/LC_MESSAGES/messages.po`):**

```po
# French translations for LearnHouse
# Copyright (C) 2025
msgid ""
msgstr ""
"Project-Id-Version: 1.0\n"
"Language: fr\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"

# Simple string
msgid "Course created successfully"
msgstr "Cours créé avec succès"

# String with context
msgctxt "error message"
msgid "Invalid data"
msgstr "Données invalides"

# Plural forms
msgid "{count} student enrolled"
msgid_plural "{count} students enrolled"
msgstr[0] "{count} étudiant inscrit"
msgstr[1] "{count} étudiants inscrits"

# String with variable
msgid "Welcome, {username}!"
msgstr "Bienvenue, {username} !"
```

**Key Components:**
- `msgid`: Original string (source language, usually English)
- `msgstr`: Translated string (target language)
- `msgctxt`: Context (disambiguates identical strings with different meanings)
- `msgid_plural`: Plural form of the source string
- `msgstr[0]`, `msgstr[1]`: Plural translations

#### 2. How gettext Works

**Workflow:**

```
1. Developer writes code with translatable strings
   _("Course created successfully")
   ↓
2. Extract strings from code → messages.pot
   pybabel extract -o locales/messages.pot .
   ↓
3. Initialize/Update PO files for each locale
   pybabel init -i locales/messages.pot -d locales -l fr
   pybabel update -i locales/messages.pot -d locales
   ↓
4. Translators edit PO files
   (manually or using tools like Crowdin, POEditor)
   ↓
5. Compile PO → MO (binary)
   pybabel compile -d locales
   ↓
6. Runtime: Load MO file and translate
   translator = gettext.translation('messages', localedir='locales', languages=['fr'])
   translator.gettext("Course created successfully")
   → "Cours créé avec succès"
```

#### 3. Implementation in FastAPI

**A. Translation Utility (`apps/api/src/i18n/translator.py`)**

```python
import gettext
from functools import lru_cache
from pathlib import Path

# Directory containing locale files
LOCALE_DIR = Path(__file__).parent.parent.parent / 'locales'

@lru_cache(maxsize=None)
def get_translator(locale: str = 'en'):
    """
    Get cached translator instance for given locale.

    Uses @lru_cache to avoid reloading translation files on every request.
    Translations are loaded once and cached in memory.
    """
    try:
        return gettext.translation(
            'messages',              # Domain name (matches messages.po)
            localedir=LOCALE_DIR,    # Directory containing locale folders
            languages=[locale],      # Try this locale
            fallback=True            # Fall back to English if locale not found
        )
    except FileNotFoundError:
        # If locale files don't exist, return fallback translator
        return gettext.translation(
            'messages',
            localedir=LOCALE_DIR,
            languages=['en'],
            fallback=True
        )

def _(message: str, locale: str = 'en') -> str:
    """
    Translate a message.

    Args:
        message: String to translate (msgid)
        locale: Target locale code (e.g., 'fr', 'es')

    Returns:
        Translated string (msgstr) or original if not found
    """
    translator = get_translator(locale)
    return translator.gettext(message)

def ngettext(singular: str, plural: str, count: int, locale: str = 'en') -> str:
    """
    Translate with plural forms.

    Args:
        singular: Singular form (e.g., "1 student")
        plural: Plural form (e.g., "{count} students")
        count: Number to determine which form to use
        locale: Target locale

    Returns:
        Appropriate plural form translated
    """
    translator = get_translator(locale)
    return translator.ngettext(singular, plural, count)
```

**How `@lru_cache` Works:**
- First call: Loads translation file from disk, caches in memory
- Subsequent calls: Returns cached translator instantly
- Cache key: locale string ('fr', 'es', etc.)
- Memory efficient: Only loaded locales are cached

**B. Using in API Endpoints**

```python
from fastapi import APIRouter, HTTPException, Request, Depends
from src.i18n.translator import _, ngettext
from src.i18n.locale_detector import detect_locale

router = APIRouter()

@router.post("/courses/")
async def create_course(
    course: CourseCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Detect user's locale
    locale = detect_locale(request, current_user)

    try:
        # Create course logic
        new_course = Course(**course.dict())
        db.add(new_course)
        db.commit()

        # Return translated success message
        return {
            "message": _("Course created successfully", locale),
            "course": new_course
        }

    except ValidationError as e:
        # Return translated error message
        raise HTTPException(
            status_code=400,
            detail=_("Invalid course data", locale)
        )

    except IntegrityError as e:
        # Return translated error with context
        raise HTTPException(
            status_code=409,
            detail=_("A course with this name already exists", locale)
        )

@router.get("/courses/{course_id}/students")
async def get_course_students(
    course_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    locale = detect_locale(request, current_user)

    course = db.get(Course, course_id)
    student_count = len(course.students)

    # Use plural translation
    message = ngettext(
        "{count} student enrolled",
        "{count} students enrolled",
        student_count,
        locale
    ).format(count=student_count)

    return {
        "message": message,
        "students": course.students
    }
```

**C. Locale Detection from Request**

```python
# apps/api/src/i18n/locale_detector.py
from fastapi import Request
from typing import Optional

def detect_locale(request: Request, user: Optional[dict] = None) -> str:
    """
    Detect user locale with priority chain.

    Priority:
    1. User's database preference (if authenticated)
    2. X-Locale header (from frontend cookie)
    3. Accept-Language header (browser default)
    4. Fallback to 'en'
    """

    # 1. User preference from database (highest priority)
    if user and user.get('preferred_locale'):
        return user['preferred_locale']

    # 2. X-Locale header (sent from frontend)
    locale_header = request.headers.get('X-Locale')
    if locale_header:
        # Validate it's a supported locale
        if locale_header in ['en', 'fr', 'es', 'ar', 'de', 'pt', 'zh', 'ja']:
            return locale_header

    # 3. Accept-Language header (browser)
    accept_language = request.headers.get('Accept-Language', '')
    if accept_language:
        # Parse "en-US,en;q=0.9,fr;q=0.8" → "en"
        locale = accept_language.split(',')[0].split('-')[0]
        if locale in ['en', 'fr', 'es', 'ar', 'de', 'pt', 'zh', 'ja']:
            return locale

    # 4. Fallback
    return 'en'
```

#### 4. String Extraction Workflow

**A. Mark Strings for Translation in Code**

```python
# Translatable strings
from src.i18n.translator import _

# Simple string
message = _("Course created successfully")

# String with variable (use Python .format())
message = _("Welcome, {username}!").format(username=user.username)

# Plural
from src.i18n.translator import ngettext
message = ngettext(
    "{count} course found",
    "{count} courses found",
    count
).format(count=count)
```

**B. Configure Extraction (`apps/api/babel.cfg`)**

```ini
# Extraction rules for Python files
[python: **.py]
encoding = utf-8

# Extract from _() and ngettext() calls
keywords = _:1,2, ngettext:1,2
```

**C. Extract Strings to POT Template**

```bash
cd apps/api

# Extract all translatable strings from Python code
pybabel extract -F babel.cfg -o locales/messages.pot .

# This scans all .py files and creates messages.pot
```

**Result (`locales/messages.pot`):**

```pot
# SOME DESCRIPTIVE TITLE.
# Copyright (C) 2025
#: src/routers/courses.py:45
msgid "Course created successfully"
msgstr ""

#: src/routers/courses.py:67
msgid "Invalid course data"
msgstr ""

#: src/routers/courses.py:89
msgid "{count} student enrolled"
msgid_plural "{count} students enrolled"
msgstr[0] ""
msgstr[1] ""
```

**D. Initialize New Locale**

```bash
# Create French translation file
pybabel init -i locales/messages.pot -d locales -l fr

# Creates: locales/fr/LC_MESSAGES/messages.po
```

**E. Update Existing Locales (After Adding New Strings)**

```bash
# Update all existing PO files with new strings from POT
pybabel update -i locales/messages.pot -d locales

# This merges new msgid entries into existing PO files
```

**F. Translate PO Files**

Translators edit `locales/fr/LC_MESSAGES/messages.po`:

```po
msgid "Course created successfully"
msgstr "Cours créé avec succès"

msgid "Invalid course data"
msgstr "Données invalides"
```

**G. Compile to Binary MO**

```bash
# Compile all PO files to MO (machine-readable binary)
pybabel compile -d locales

# Creates: locales/fr/LC_MESSAGES/messages.mo
```

**Why MO files?**
- **Performance**: Binary format is 10-50x faster to load than text PO
- **Size**: Smaller file size (removes comments, metadata)
- **Runtime**: gettext loads MO files at runtime, not PO

#### 5. Advanced Features

**A. Context for Disambiguation**

Sometimes the same English word has different translations based on context:

```python
from src.i18n.translator import pgettext

# "Course" as a noun (a class)
course_noun = pgettext("noun", "Course")
# French: "Cours"

# "Course" as a verb (to flow)
course_verb = pgettext("verb", "Course")
# French: "Couler"
```

In PO file:

```po
msgctxt "noun"
msgid "Course"
msgstr "Cours"

msgctxt "verb"
msgid "Course"
msgstr "Couler"
```

**B. Plural Forms with Complex Rules**

Different languages have different plural rules:

**English (2 forms):**
- `one`: n == 1
- `other`: everything else

**French (2 forms):**
- `one`: n == 0 or n == 1
- `other`: n > 1

**Arabic (6 forms):**
- `zero`: n == 0
- `one`: n == 1
- `two`: n == 2
- `few`: n % 100 in 3..10
- `many`: n % 100 in 11..99
- `other`: everything else

**PO file header specifies plural rules:**

```po
"Plural-Forms: nplurals=2; plural=(n > 1);\n"
```

**C. Variable Interpolation**

```python
# Python code
message = _("Welcome, {username}! You have {count} notifications.").format(
    username=user.username,
    count=notification_count
)
```

**PO file:**

```po
msgid "Welcome, {username}! You have {count} notifications."
msgstr "Bienvenue, {username} ! Vous avez {count} notifications."
```

#### 6. Content Translation (User-Generated Content)

For translating user-created content (courses, descriptions), we use JSON fields:

```python
# apps/api/src/i18n/content_translator.py

def get_translated_field(
    obj: Any,
    field: str,
    locale: str,
    fallback_locale: str = 'en'
) -> str:
    """
    Get translated value from object's translations JSON field.

    Course.translations structure:
    {
        "fr": {
            "name": "Introduction à Python",
            "description": "Apprenez les bases de Python"
        },
        "es": {
            "name": "Introducción a Python",
            "description": "Aprenda los conceptos básicos de Python"
        }
    }
    """
    # Return original if requesting default locale
    if locale == fallback_locale:
        return getattr(obj, field, '')

    # Check if translations exist for this locale
    if not hasattr(obj, 'translations') or not obj.translations:
        return getattr(obj, field, '')

    # Get translation for field
    locale_data = obj.translations.get(locale, {})
    if field in locale_data and locale_data[field]:
        return locale_data[field]

    # Fallback to original language
    return getattr(obj, field, '')

# Usage in endpoint
@router.get("/courses/{course_id}")
async def get_course(
    course_id: int,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    locale = detect_locale(request, current_user)
    course = db.get(Course, course_id)

    return {
        "id": course.id,
        "name": get_translated_field(course, "name", locale),
        "description": get_translated_field(course, "description", locale),
        "created_at": course.created_at
    }
```

---

## How They Work Together

### Complete Request Flow (Frontend → Backend)

```
┌─────────────────────────────────────────────────────────────┐
│                  User Action: Load Course Page              │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
         ┌───────────────────────────────────────┐
         │  Frontend (Next.js + next-intl)       │
         │                                       │
         │  1. Layout detects locale             │
         │     → session.user.preferred_locale   │
         │     → 'fr'                            │
         │                                       │
         │  2. Loads messages/fr.json            │
         │     → { "courses": { ... } }          │
         │                                       │
         │  3. Component renders                 │
         │     → t('courses.title')              │
         │     → "Tous les cours"                │
         │                                       │
         │  4. User clicks "View Course"         │
         │     → Triggers API call               │
         └───────────────┬───────────────────────┘
                         │
                         │ HTTP Request
                         │ GET /api/v1/courses/123
                         │ Headers:
                         │   X-Locale: fr
                         │   Authorization: Bearer ...
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │  Backend (FastAPI + gettext)          │
         │                                       │
         │  1. detect_locale(request, user)      │
         │     → Checks X-Locale header          │
         │     → Returns 'fr'                    │
         │                                       │
         │  2. get_translator('fr')              │
         │     → Loads locales/fr/.../messages.mo│
         │     → Cached for performance          │
         │                                       │
         │  3. Database query                    │
         │     → course = db.get(Course, 123)    │
         │                                       │
         │  4. Translate content                 │
         │     → get_translated_field(           │
         │         course, "name", "fr"          │
         │       )                               │
         │     → Returns "Cours de Python"       │
         │                                       │
         │  5. Translate system message          │
         │     → _("Course found", "fr")         │
         │     → Returns "Cours trouvé"          │
         │                                       │
         │  6. Return JSON response              │
         │     {                                 │
         │       "message": "Cours trouvé",      │
         │       "course": {                     │
         │         "name": "Cours de Python",    │
         │         "description": "..."          │
         │       }                               │
         │     }                                 │
         └───────────────┬───────────────────────┘
                         │
                         │ HTTP Response
                         │ Status: 200
                         │ Body: JSON (in French)
                         │
                         ▼
         ┌───────────────────────────────────────┐
         │  Frontend Receives Response           │
         │                                       │
         │  1. Parse JSON                        │
         │  2. Display course in French          │
         │     → Title: "Cours de Python"        │
         │     → Button: t('courses.enroll')     │
         │                → "S'inscrire"         │
         └───────────────────────────────────────┘
```

### Locale Switching Flow

```
User clicks locale switcher: "Español"
              ↓
┌─────────────────────────────────┐
│  LocaleSwitcher Component       │
│                                 │
│  if (authenticated) {           │
│    // Save to database          │
│    updateUserPreference({       │
│      preferred_locale: 'es'     │
│    });                          │
│  } else {                       │
│    // Save to cookie            │
│    setCookie('NEXT_LOCALE', 'es'│
│      { maxAge: 31536000 });     │
│  }                              │
│                                 │
│  router.refresh();              │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Page Reloads                   │
│                                 │
│  1. Layout detects new locale   │
│     → 'es' (from DB or cookie)  │
│                                 │
│  2. Loads messages/es.json      │
│                                 │
│  3. All components re-render    │
│     in Spanish                  │
│                                 │
│  4. Future API calls include    │
│     X-Locale: es header         │
└─────────────────────────────────┘
```

---

## Common Patterns & Best Practices

### Frontend (next-intl)

#### 1. Organize Messages by Domain

```json
{
  "auth": { /* authentication strings */ },
  "courses": { /* course-related strings */ },
  "dashboard": { /* dashboard strings */ },
  "common": { /* shared strings like "Save", "Cancel" */ }
}
```

#### 2. Use Namespaced Translations

```typescript
// Good: Scoped to feature
const t = useTranslations('courses');
const title = t('createForm.title');

// Avoid: Global namespace pollution
const t = useTranslations();
const title = t('coursesCreateFormTitle'); // Too verbose
```

#### 3. Extract Reusable Strings

```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "confirm": "Confirm"
  }
}
```

```typescript
const tCommon = useTranslations('common');
<button>{tCommon('save')}</button>
```

#### 4. Handle Missing Translations

```typescript
// next-intl will show the key if translation is missing
t('nonexistent.key')  // Shows: "nonexistent.key"

// Provide fallback in dev mode
const message = t('courses.title', {
  defaultValue: 'Courses'
});
```

#### 5. Preload Translations for Better UX

```typescript
// Preload next likely locale
import { useEffect } from 'react';

function preloadLocale(locale: string) {
  import(`../messages/${locale}.json`);
}

// In locale switcher
<select onChange={(e) => {
  preloadLocale(e.target.value); // Load before switching
  changeLocale(e.target.value);
}}>
```

### Backend (gettext)

#### 1. Mark All User-Facing Strings

```python
# Good: All messages translatable
raise HTTPException(
    status_code=404,
    detail=_("Course not found", locale)
)

# Bad: Hardcoded English
raise HTTPException(
    status_code=404,
    detail="Course not found"  # Won't be translated!
)
```

#### 2. Use Lazy Translation for Constants

```python
# For module-level constants that need translation
from src.i18n.translator import lazy_gettext as _

ERROR_MESSAGES = {
    'not_found': _("Resource not found"),
    'unauthorized': _("Unauthorized access"),
}

# At runtime, when locale is known:
message = str(ERROR_MESSAGES['not_found'])  # Translates based on current locale
```

#### 3. Provide Context for Ambiguous Strings

```python
from src.i18n.translator import pgettext

# "Order" as in sequence
sequence_label = pgettext("sequence", "Order")

# "Order" as in purchase
purchase_label = pgettext("purchase", "Order")
```

#### 4. Extract Regularly

```bash
# Add to development workflow
pybabel extract -F babel.cfg -o locales/messages.pot .
pybabel update -i locales/messages.pot -d locales
pybabel compile -d locales
```

#### 5. Validate Translations in Tests

```python
# apps/api/src/tests/test_i18n.py
from src.i18n.translator import _

def test_french_translations():
    assert _("Course created successfully", "fr") == "Cours créé avec succès"
    assert _("Invalid data", "fr") == "Données invalides"

def test_fallback_to_english():
    # Unknown locale should fallback
    assert _("Some message", "unknown") == "Some message"
```

### Performance Best Practices

#### 1. Frontend: Code Splitting

```typescript
// Dynamic import per locale (already done in layout)
const messages = await import(`../messages/${locale}.json`);

// Result: Only 1 locale file loaded per user
// en.json: 50KB → User only downloads 50KB, not 200KB for all locales
```

#### 2. Backend: Caching

```python
# Use @lru_cache for translator instances
@lru_cache(maxsize=None)
def get_translator(locale: str):
    return gettext.translation(...)

# Result: Translation files loaded once, cached in memory
```

#### 3. Database Queries

```python
# Fetch user preference once, reuse
user_locale = current_user.get('preferred_locale', 'en')

# Don't query DB for locale on every translation
# Bad:
for item in items:
    translate(item.name, db.get_user_locale())  # N+1 queries!

# Good:
locale = db.get_user_locale()  # 1 query
for item in items:
    translate(item.name, locale)
```

### Testing Strategies

#### 1. Frontend: Test Multiple Locales

```typescript
import { render } from '@testing-library/react';
import { NextIntlClientProvider } from 'next-intl';

describe('CourseCard', () => {
  it('renders in English', () => {
    const { getByText } = render(
      <NextIntlClientProvider locale="en" messages={enMessages}>
        <CourseCard />
      </NextIntlClientProvider>
    );
    expect(getByText('Create Course')).toBeInTheDocument();
  });

  it('renders in French', () => {
    const { getByText } = render(
      <NextIntlClientProvider locale="fr" messages={frMessages}>
        <CourseCard />
      </NextIntlClientProvider>
    );
    expect(getByText('Créer un cours')).toBeInTheDocument();
  });
});
```

#### 2. Backend: Test Locale Detection

```python
from fastapi.testclient import TestClient
from src.i18n.locale_detector import detect_locale

def test_locale_from_header(client: TestClient):
    response = client.get(
        "/api/v1/courses",
        headers={"X-Locale": "fr"}
    )
    # Verify French response
    assert response.json()["message"] == "Cours trouvés"

def test_locale_fallback(client: TestClient):
    response = client.get("/api/v1/courses")
    # Should fallback to English
    assert response.json()["message"] == "Courses found"
```

---

## Troubleshooting Common Issues

### Frontend (next-intl)

**Issue 1: "Translation key not found"**

```typescript
// Error: t('courses.nonexistent')
```

**Solution:**
- Check messages/en.json for the key
- Ensure nested path is correct: `courses.createForm.title`
- Check for typos

**Issue 2: Locale not switching**

**Solution:**
- Verify cookie is set: Check browser DevTools → Application → Cookies
- Ensure `router.refresh()` is called after locale change
- Check if session is loading user's `preferred_locale`

**Issue 3: Variables not interpolating**

```typescript
// Shows: "Hello, {name}!" instead of "Hello, Alice!"
```

**Solution:**
```typescript
// Correct usage
t('greeting', { name: 'Alice' })

// Not this
t('greeting')  // Missing variable!
```

### Backend (gettext)

**Issue 1: Translations not loading**

**Solution:**
- Ensure MO files are compiled: `pybabel compile -d locales`
- Check file paths: `locales/fr/LC_MESSAGES/messages.mo` exists
- Verify locale code matches directory name

**Issue 2: Updated translations not showing**

**Solution:**
```bash
# After editing PO files, must recompile
pybabel compile -d locales

# Restart FastAPI server (to reload cached translations)
uvicorn app:app --reload
```

**Issue 3: Plural forms not working correctly**

**Solution:**
- Check PO file header has correct `Plural-Forms` rule
- Verify `ngettext()` usage:

```python
# Correct
ngettext("{count} item", "{count} items", count)

# Wrong
_("{count} items")  # Won't pluralize!
```

---

## Summary

### Frontend (next-intl)
- **Format:** JSON files (`messages/en.json`)
- **Loading:** Dynamic import based on locale
- **Usage:** `useTranslations()` hook
- **Locale source:** Session → Cookie → Browser → Fallback
- **Performance:** Code splitting, SSR support

### Backend (gettext + Babel)
- **Format:** PO files (human) → MO files (machine)
- **Loading:** Cached via `@lru_cache`
- **Usage:** `_()` function for translation
- **Locale source:** X-Locale header → Accept-Language → Fallback
- **Performance:** Binary MO files, memory caching

### Together
- Frontend sends `X-Locale` header with every request
- Backend translates system messages + content
- Both share same locale codes ('en', 'fr', 'es', 'ar')
- Consistent user experience across UI and API

**Result:** Seamless multilingual experience with no URL changes! 🌍
