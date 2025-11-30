# i18n Implementation Plan for LearnHouse

This document outlines the comprehensive strategy for implementing internationalization (i18n) across both frontend and backend with minimal code disruption.

## 🎯 Goals

1. **Minimal Code Changes**: Leverage existing infrastructure and patterns
2. **Incremental Rollout**: Translate high-impact areas first
3. **Developer Experience**: Make it easy for developers to add translations
4. **User Experience**: Seamless language switching without page reloads where possible
5. **Maintainability**: Clear patterns that scale as the app grows

## 📊 Current State Assessment

### ✅ Already Done

- **Frontend Infrastructure**: next-intl configured and working
- **Translation Files**: Partial translations exist (en, fr, es)
- **Language Selector**: UI component built and functional
- **Cookie-based Persistence**: User language preference saved
- **Layout Integration**: Root layout handles locale detection

### ❌ Not Yet Done

- **Component Translation Coverage**: ~99% of components use hardcoded text
- **Backend i18n**: No translation infrastructure
- **API Response Translation**: API returns only English
- **Database Content**: Course content not translatable
- **Email Templates**: System emails only in English

## 🏗️ Architecture Overview

### Frontend Strategy: **Progressive Enhancement**

Use the existing next-intl setup without major refactoring:

```tsx
// BEFORE (hardcoded)
<Button>Save Changes</Button>

// AFTER (translated - one line change)
<Button>{t('common.save')}</Button>
```

### Backend Strategy: **Accept-Language Header + Response Translation**

Use standard HTTP headers without changing API structure:

```python
# Client sends:
Accept-Language: fr-FR,fr;q=0.9,en;q=0.8

# Backend responds with translated strings
# No API changes needed - just translate response values
```

## 📋 Implementation Roadmap

### Phase 1: Frontend Foundation (Week 1)

**Goal**: Establish patterns and translate critical user flows

#### 1.1 Update Translation Files

Expand existing translation files with comprehensive coverage:

```bash
apps/web/messages/
├── en.json  # Complete all keys
├── fr.json  # Translate all keys
└── es.json  # Translate all keys
```

**Action Items:**
- [ ] Audit all hardcoded strings in components
- [ ] Create comprehensive translation keys in `en.json`
- [ ] Organize by namespace (common, navigation, auth, etc.)
- [ ] Get professional translations for fr/es

#### 1.2 Create Translation Utilities

**File**: `apps/web/lib/i18n-utils.ts`

```typescript
// Helper to get translations without hooks (for non-components)
export async function getTranslations(locale: Locale, namespace: string) {
  const messages = await import(`@/messages/${locale}.json`);
  return messages[namespace];
}

// Helper for server components
export async function getServerTranslations(namespace: string) {
  const locale = getServerLocale(); // From cookies
  return getTranslations(locale, namespace);
}

// Type-safe translation keys
export type TranslationKey = keyof typeof import('@/messages/en.json');
```

**Action Items:**
- [ ] Create utility helpers
- [ ] Add TypeScript support for autocomplete
- [ ] Document usage patterns

#### 1.3 Translate Critical Components (Priority Order)

**High Priority** (User-facing, frequently used):
1. Authentication pages (`/auth/*`)
2. Navigation menus
3. Dashboard home
4. User settings
5. Course listings

**Medium Priority**:
6. Course editor
7. Assignment pages
8. Organization settings
9. User profiles

**Low Priority**:
10. Admin pages
11. Advanced settings
12. Error pages

**Action Items per Component:**
- [ ] Add `useTranslations` hook
- [ ] Replace hardcoded strings
- [ ] Update translation files
- [ ] Test in all languages
- [ ] Mark as ✅ complete

### Phase 2: Frontend Completion (Week 2-3)

#### 2.1 Component-by-Component Translation

Use a systematic approach:

**Template for each component:**

```tsx
// 1. Import hook
import { useTranslations } from 'next-intl';

// 2. Get translations
const t = useTranslations('ComponentName');
const c = useTranslations('common');

// 3. Replace strings
<Button>{c('save')}</Button>  // Instead of: Save Changes
<h1>{t('title')}</h1>        // Instead of: Component Title
```

**Action Items:**
- [ ] Create script to find hardcoded strings
- [ ] Prioritize components by usage analytics
- [ ] Create PR template for translation updates
- [ ] Review and test each component

#### 2.2 Dynamic Content Translation

For user-generated content (course titles, descriptions, etc.):

**Strategy**: Store translations in database

```typescript
// Course model (example)
interface Course {
  id: string;
  title: string;              // Default language
  title_translations?: {      // Optional translations
    fr?: string;
    es?: string;
  };
  description: string;
  description_translations?: {
    fr?: string;
    es?: string;
  };
}

// Helper to get translated field
function getTranslatedField(
  object: any,
  field: string,
  locale: Locale
): string {
  const translationField = `${field}_translations`;
  return object[translationField]?.[locale] || object[field];
}

// Usage
const courseTitle = getTranslatedField(course, 'title', currentLocale);
```

**Action Items:**
- [ ] Design translation schema for database
- [ ] Create migration for translation fields
- [ ] Build translation UI for content creators
- [ ] Implement fallback logic

### Phase 3: Backend i18n (Week 3-4)

#### 3.1 Backend Translation Infrastructure

**Recommended Library**: `Babel` (already in Python ecosystem)

**Setup:**

```bash
# Install
cd apps/api
uv add babel

# Initialize
pybabel init -i messages.pot -d locales -l fr
pybabel init -i messages.pot -d locales -l es
```

**File Structure:**
```
apps/api/
├── locales/
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       └── messages.po
│   ├── fr/
│   │   └── LC_MESSAGES/
│   │       └── messages.po
│   └── es/
│       └── LC_MESSAGES/
│           └── messages.po
├── babel.cfg
└── src/
    └── i18n/
        └── translator.py
```

**Action Items:**
- [ ] Install and configure Babel
- [ ] Create locale directories
- [ ] Set up extraction workflow

#### 3.2 Translation Middleware

**File**: `apps/api/src/middleware/i18n.py`

```python
from fastapi import Request
from babel import Locale, negotiate_locale
from typing import Optional

SUPPORTED_LOCALES = ['en', 'fr', 'es']
DEFAULT_LOCALE = 'en'

def get_locale_from_request(request: Request) -> str:
    """Extract locale from Accept-Language header"""
    accept_language = request.headers.get('Accept-Language', '')

    # Parse Accept-Language header
    # Example: "fr-FR,fr;q=0.9,en;q=0.8,es;q=0.7"
    locale = negotiate_locale(
        accept_language.split(','),
        SUPPORTED_LOCALES
    )

    return locale or DEFAULT_LOCALE

# Dependency for routes
async def get_translator(request: Request):
    locale = get_locale_from_request(request)
    return Translator(locale)
```

**Action Items:**
- [ ] Create middleware
- [ ] Add to FastAPI app
- [ ] Test with different Accept-Language headers

#### 3.3 Translation Helper

**File**: `apps/api/src/i18n/translator.py`

```python
from babel.support import Translations
import os

class Translator:
    def __init__(self, locale: str = 'en'):
        self.locale = locale
        locale_path = os.path.join(
            os.path.dirname(__file__),
            '../../locales'
        )
        try:
            self.translations = Translations.load(
                locale_path,
                [locale]
            )
        except:
            # Fallback to English
            self.translations = Translations.load(
                locale_path,
                ['en']
            )

    def gettext(self, message: str) -> str:
        """Translate a message"""
        return self.translations.gettext(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Translate with pluralization"""
        return self.translations.ngettext(singular, plural, n)

    # Shorthand
    def t(self, message: str) -> str:
        return self.gettext(message)

# Global translator instance
_translator = None

def get_translator(locale: str = 'en') -> Translator:
    return Translator(locale)
```

**Action Items:**
- [ ] Implement translator class
- [ ] Add caching for loaded translations
- [ ] Create helper functions

#### 3.4 Update API Responses

**Before:**
```python
@router.post("/courses")
async def create_course(course: CourseCreate):
    return {
        "message": "Course created successfully",
        "course": course
    }
```

**After:**
```python
@router.post("/courses")
async def create_course(
    course: CourseCreate,
    t: Translator = Depends(get_translator)
):
    return {
        "message": t.t("Course created successfully"),
        "course": course
    }
```

**Action Items:**
- [ ] Update all API responses
- [ ] Extract strings to .po files
- [ ] Translate messages
- [ ] Test API with different locales

#### 3.5 Email Template Translation

**Structure:**
```
apps/api/
├── templates/
│   └── emails/
│       ├── en/
│       │   ├── welcome.html
│       │   └── password-reset.html
│       ├── fr/
│       │   ├── welcome.html
│       │   └── password-reset.html
│       └── es/
│           ├── welcome.html
│           └── password-reset.html
```

**Email Service:**
```python
class EmailService:
    def __init__(self, locale: str = 'en'):
        self.locale = locale

    def send_welcome_email(self, user: User):
        template_path = f"templates/emails/{self.locale}/welcome.html"
        template = self.load_template(template_path)
        # Render and send...
```

**Action Items:**
- [ ] Create template directory structure
- [ ] Translate all email templates
- [ ] Update email service to use locale
- [ ] Test email sending in all languages

### Phase 4: Database Content Translation (Week 4-5)

#### 4.1 Schema Design

**Option A: JSON Column (Recommended)**

```python
from sqlmodel import SQLModel, Field
from typing import Optional

class Course(SQLModel, table=True):
    id: int
    title: str  # Default language (English)
    translations: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    # translations structure:
    # {
    #   "fr": {"title": "...", "description": "..."},
    #   "es": {"title": "...", "description": "..."}
    # }
```

**Option B: Separate Translation Table**

```python
class Course(SQLModel, table=True):
    id: int
    title: str  # Default language

class CourseTranslation(SQLModel, table=True):
    id: int
    course_id: int
    locale: str  # 'fr', 'es', etc.
    title: str
    description: str
```

**Recommendation**: Use Option A (JSON) for simplicity and fewer joins.

**Action Items:**
- [ ] Design schema
- [ ] Create migration
- [ ] Update models
- [ ] Create helper methods

#### 4.2 Translation UI for Content Creators

**Component**: `ContentTranslationEditor.tsx`

```tsx
interface TranslationEditorProps {
  content: any;
  field: string;
  onSave: (translations: Record<Locale, string>) => void;
}

function ContentTranslationEditor({ content, field }: TranslationEditorProps) {
  return (
    <div>
      <h3>Translate: {field}</h3>

      {/* Default language (read-only) */}
      <div>
        <Label>English (Default)</Label>
        <Input value={content[field]} disabled />
      </div>

      {/* Translation inputs */}
      {['fr', 'es'].map(locale => (
        <div key={locale}>
          <Label>{localeNames[locale]}</Label>
          <Input
            value={content.translations?.[locale]?.[field] || ''}
            onChange={(e) => handleTranslationChange(locale, field, e.target.value)}
          />
        </div>
      ))}
    </div>
  );
}
```

**Action Items:**
- [ ] Build translation UI
- [ ] Add to course editor
- [ ] Add to organization settings
- [ ] Add to chapter/activity editors

## 🛠️ Development Workflow

### For Frontend Developers

**Adding translations to a component:**

1. **Import the hook:**
   ```tsx
   import { useTranslations } from 'next-intl';
   ```

2. **Get translations:**
   ```tsx
   const t = useTranslations('ComponentName');
   const c = useTranslations('common');
   ```

3. **Replace hardcoded strings:**
   ```tsx
   // Before
   <Button>Save Changes</Button>

   // After
   <Button>{c('save')}</Button>
   ```

4. **Update translation files:**
   ```json
   {
     "ComponentName": {
       "title": "Component Title"
     },
     "common": {
       "save": "Save"
     }
   }
   ```

5. **Test all languages:**
   - Switch language in settings
   - Verify translations appear correctly

### For Backend Developers

**Adding translations to API endpoints:**

1. **Add translator dependency:**
   ```python
   from src.i18n.translator import get_translator, Translator

   @router.post("/endpoint")
   async def endpoint(t: Translator = Depends(get_translator)):
   ```

2. **Wrap user-facing strings:**
   ```python
   return {"message": t.t("Operation successful")}
   ```

3. **Extract strings:**
   ```bash
   pybabel extract -F babel.cfg -o messages.pot .
   ```

4. **Update translations:**
   ```bash
   pybabel update -i messages.pot -d locales
   ```

5. **Compile:**
   ```bash
   pybabel compile -d locales
   ```

## 📊 Progress Tracking

### Frontend Components

**Critical Path (Must Do First):**
- [ ] Authentication pages (login, signup, forgot password)
- [ ] Navigation (header, sidebar, mobile menu)
- [ ] Dashboard home page
- [ ] User settings (all tabs)
- [ ] Course listing page

**User-Facing (High Priority):**
- [ ] Course detail page
- [ ] Course player/activity viewer
- [ ] Assignment submission
- [ ] Certificate pages
- [ ] Profile pages

**Admin/Creator Tools (Medium Priority):**
- [ ] Course editor
- [ ] Chapter editor
- [ ] Activity editor
- [ ] Organization settings
- [ ] User management

**System/Admin (Lower Priority):**
- [ ] Admin dashboard
- [ ] Payments/billing
- [ ] Advanced settings
- [ ] Error pages
- [ ] Developer tools

### Backend Endpoints

**User-Facing APIs:**
- [ ] Auth endpoints
- [ ] Course endpoints
- [ ] Assignment endpoints
- [ ] Profile endpoints
- [ ] Enrollment endpoints

**Content Management:**
- [ ] Course creation/update
- [ ] Chapter management
- [ ] Activity management
- [ ] Media upload responses

**System:**
- [ ] Error messages
- [ ] Validation messages
- [ ] Email content
- [ ] Notifications

## 🧪 Testing Strategy

### Automated Testing

**Frontend:**
```tsx
// Test component in all languages
describe('UserSettings', () => {
  ['en', 'fr', 'es'].forEach(locale => {
    it(`renders correctly in ${locale}`, () => {
      const { getByText } = render(
        <NextIntlProvider locale={locale} messages={messages[locale]}>
          <UserSettings />
        </NextIntlProvider>
      );
      // Assertions...
    });
  });
});
```

**Backend:**
```python
def test_endpoint_with_locale():
    headers = {"Accept-Language": "fr"}
    response = client.post("/api/v1/courses", headers=headers)
    assert response.json()["message"] == "Cours créé avec succès"
```

### Manual Testing Checklist

For each translated page/feature:
- [ ] Switch to French - verify all text translated
- [ ] Switch to Spanish - verify all text translated
- [ ] Check pluralization (0, 1, many items)
- [ ] Verify variables are correctly interpolated
- [ ] Test RTL layout (if supported)
- [ ] Verify language persistence after reload
- [ ] Check console for missing translation warnings

## 🔧 Tools & Scripts

### Translation Coverage Script

**File**: `scripts/check-translation-coverage.js`

```javascript
// Find hardcoded English strings in components
const fs = require('fs');
const path = require('path');

function findHardcodedStrings(dir) {
  // Regex to find potential hardcoded strings
  const stringRegex = /['"]([A-Z][a-z\s]{3,})['"]/g;

  // Scan files for strings not using t() or c()
  // Report files needing translation
}

findHardcodedStrings('apps/web/components');
```

### Auto-generate Translation Keys

**File**: `scripts/generate-translation-keys.js`

```javascript
// Extract strings and suggest translation keys
// Update translation files with missing keys
```

### Translation Status Dashboard

Create a simple HTML page showing:
- % of components translated
- Missing translations per language
- Recently added strings needing translation

## 🚀 Deployment Strategy

### Progressive Rollout

**Phase 1: Beta Testing**
- Enable for internal users only
- Collect feedback
- Fix issues

**Phase 2: Opt-in**
- Language selector visible to all
- Default to English
- Let users opt-in

**Phase 3: Full Release**
- Auto-detect browser language
- Set as default for new users
- Announce feature

### Feature Flags

```typescript
// Control rollout via config
const I18N_CONFIG = {
  enabled: true,
  availableLanguages: ['en', 'fr', 'es'],
  autoDetect: true,  // Auto-detect browser language
  fallback: 'en'
};
```

## 📚 Resources & References

### Documentation
- [next-intl docs](https://next-intl-docs.vercel.app/)
- [Babel (Python) docs](http://babel.pocoo.org/)
- [Translation best practices](./translations.md)

### Translation Files
- `apps/web/messages/*.json` - Frontend translations
- `apps/api/locales/*/LC_MESSAGES/*.po` - Backend translations

### Key Components
- `LanguageSelector.tsx` - Language switcher UI
- `apps/web/i18n/` - i18n configuration
- `apps/api/src/i18n/` - Backend i18n utilities

## 🎯 Success Metrics

**Coverage:**
- [ ] 100% of user-facing components translated
- [ ] 100% of API responses translated
- [ ] All email templates translated

**Quality:**
- [ ] Professional translations reviewed by native speakers
- [ ] No hardcoded strings in critical paths
- [ ] Consistent terminology across languages

**Performance:**
- [ ] No performance degradation from i18n
- [ ] Translation files lazy-loaded
- [ ] Translations cached appropriately

**User Experience:**
- [ ] Language persists across sessions
- [ ] Language switch is instant (no reload where possible)
- [ ] Fallback to English graceful

## 💡 Best Practices Summary

### Frontend
1. ✅ Use `useTranslations('namespace')` in components
2. ✅ Group common strings in `common` namespace
3. ✅ Use descriptive, readable translation keys
4. ✅ Always provide fallback to English
5. ✅ Test in all supported languages

### Backend
1. ✅ Use Accept-Language header for locale detection
2. ✅ Translate all user-facing strings
3. ✅ Extract and compile translations regularly
4. ✅ Cache translations in production
5. ✅ Log missing translations for monitoring

### Content
1. ✅ Store translations in database for user-generated content
2. ✅ Provide easy UI for content creators to add translations
3. ✅ Always have English as fallback
4. ✅ Show which languages are complete/incomplete
5. ✅ Allow partial translations (fallback to default)

## 🤝 Getting Help

**Questions?**
- Check `/context/translations.md` for implementation guide
- Review existing translated components for examples
- Ask in development chat

**Found an issue?**
- Report missing translations
- Suggest better translations
- Report bugs in language switching

---

**Last Updated**: 2025-01-29
**Status**: Planning Phase
**Next Review**: After Phase 1 completion
