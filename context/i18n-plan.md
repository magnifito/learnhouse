# Frontend i18n Implementation Plan for LearnHouse

This document outlines the strategy for implementing internationalization (i18n) in the LearnHouse frontend.

## 🎯 Goals

1. **Minimal Code Changes**: Leverage existing next-intl infrastructure
2. **Incremental Rollout**: Translate high-impact areas first
3. **Developer Experience**: Simple, consistent translation patterns
4. **User Experience**: Instant language switching with persistence
5. **Maintainability**: Clear patterns that scale as the app grows

## ⚠️ Scope

**Frontend Only** - Backend translations are not needed as API responses return data (IDs, numbers, database values) rather than user-facing text. All user-visible strings are rendered and translated in the frontend.

## 📊 Current State

### ✅ Already Implemented

- **next-intl Integration**: Configured and working
- **5 Languages Supported**: 🇬🇧 en, 🇫🇷 fr, 🇪🇸 es, 🇩🇪 de, 🇧🇬 bg
- **Translation Files**: Base structure with common translations
- **Language Selector**: UI component in user settings
- **Cookie Persistence**: User preference saved across sessions
- **Layout Integration**: Auto-loads correct locale on mount

### ❌ To Be Done

- **Component Coverage**: ~99% of components still use hardcoded English
- **User-Generated Content**: Course titles/descriptions not translatable
- **Translation Completeness**: Need native speaker review

## 🏗️ Architecture

### Translation Pattern

```tsx
// BEFORE (hardcoded English)
<Button>Save Changes</Button>
<h1>Account Settings</h1>

// AFTER (translated)
const t = useTranslations('ComponentName');
const c = useTranslations('common');

<Button>{c('save')}</Button>
<h1>{t('title')}</h1>
```

**Key Principle**: Minimal one-line changes to components

## 📋 Implementation Plan

### Phase 1: High-Priority Components

**Critical User Flows** (translate first for maximum impact):

1. **Authentication** (`/auth/*`)
   - Login page
   - Signup page
   - Password reset
   - OAuth flows

2. **Navigation & Menus**
   - Header navigation
   - Sidebar menus
   - Mobile menu
   - Breadcrumbs

3. **Dashboard Home**
   - Welcome messages
   - Quick stats
   - Recent activity

4. **User Settings**
   - All settings tabs
   - Form labels
   - Help text
   - Success/error messages

5. **Course Discovery**
   - Course listings
   - Search interface
   - Filters
   - Enrollment flows

### Phase 2: User-Facing Features

**Medium Priority**:

6. Course Player
7. Assignment Submission
8. Certificates
9. User Profiles
10. Notifications

### Phase 3: Creator Tools

**Lower Priority** (used by fewer users):

11. Course Editor
12. Chapter/Activity Editor
13. Organization Settings
14. Analytics Dashboard
15. User Management

### Phase 4: System Pages

**Lowest Priority**:

16. Error pages (404, 500, etc.)
17. Admin tools
18. Advanced settings
19. Developer tools

## 🛠️ Development Workflow

### For Each Component

**Step 1**: Import translation hook

```tsx
import { useTranslations } from 'next-intl';
```

**Step 2**: Get translations

```tsx
// Component-specific translations
const t = useTranslations('UserEditGeneral');

// Common/shared translations
const c = useTranslations('common');
```

**Step 3**: Replace hardcoded strings

```tsx
// Labels
<Label>{t('labels.email')}</Label>

// Buttons (use common)
<Button>{c('save')}</Button>
<Button>{c('cancel')}</Button>

// Messages
{error && <p>{t('errors.emailInvalid')}</p>}

// Plurals
{t('messages.studentsEnrolled', { count: 5 })}
```

**Step 4**: Update translation files

Add keys to `apps/web/messages/[locale].json`:

```json
{
  "UserEditGeneral": {
    "title": "Account Settings",
    "labels": {
      "email": "Email",
      "username": "Username"
    },
    "errors": {
      "emailInvalid": "Invalid email address"
    }
  }
}
```

**Step 5**: Translate to all languages

Copy keys to fr.json, es.json, de.json, bg.json and translate

**Step 6**: Test

- Switch language in settings
- Verify all text translates
- Check pluralization works
- Ensure no console warnings

## 📁 Translation File Organization

```
apps/web/messages/
├── en.json  # English (source of truth)
├── fr.json  # French
├── es.json  # Spanish
├── de.json  # German
└── bg.json  # Bulgarian
```

### File Structure

```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit"
  },
  "navigation": {
    "home": "Home",
    "courses": "Courses",
    "dashboard": "Dashboard"
  },
  "ComponentName": {
    "title": "...",
    "subtitle": "...",
    "labels": { ... },
    "buttons": { ... },
    "messages": { ... },
    "errors": { ... }
  }
}
```

## 📝 Translation Checklist

For each component you translate:

- [ ] Import `useTranslations` hook
- [ ] Create component namespace in translation files
- [ ] Replace all hardcoded strings with translation keys
- [ ] Use `common` namespace for reusable strings
- [ ] Add translations for all 5 languages
- [ ] Test language switching
- [ ] Check for missing translation warnings in console
- [ ] Mark component as ✅ translated

## 🎨 Best Practices

### ✅ DO

- Use descriptive, readable keys: `emailLabel`, `saveButton`, `welcomeMessage`
- Group related translations: `labels.email`, `errors.emailInvalid`
- Reuse common translations: `common.save`, `common.cancel`
- Keep translations in sync across languages
- Use variables for dynamic content: `Welcome, {name}!`

### ❌ DON'T

- Use generic keys: `label1`, `text2`, `btn`
- Hardcode strings: `<Button>Save</Button>`
- Duplicate translations across namespaces
- Concatenate translated strings
- Skip languages (must translate all 5)

## 🗄️ User-Generated Content

### Problem

Course titles, descriptions, chapter names are in the database - single language only.

### Solution Options

**Option A: JSON Column** (Recommended)

```typescript
interface Course {
  id: string;
  title: string;  // English (default)
  translations?: {
    fr?: { title: string; description: string; };
    es?: { title: string; description: string; };
    de?: { title: string; description: string; };
    bg?: { title: string; description: string; };
  };
}
```

**Option B: Separate Table**

```typescript
interface CourseTranslation {
  id: string;
  course_id: string;
  locale: string;
  title: string;
  description: string;
}
```

**Recommendation**: Option A (simpler, fewer joins)

### Implementation Later

This requires:
- Database schema changes
- API updates
- Translation UI for course creators
- Not critical for Phase 1-3

## 🧪 Testing

### Manual Testing

For each translated page:

1. Switch to French → verify translations
2. Switch to Spanish → verify translations
3. Switch to German → verify translations
4. Switch to Bulgarian → verify translations
5. Check pluralization (0, 1, many items)
6. Verify variables interpolate correctly
7. Test language persistence after reload
8. Check console for missing translation warnings

### Automated Testing

```tsx
import { NextIntlProvider } from 'next-intl';
import messages from '@/messages/en.json';

describe('UserSettings', () => {
  it('renders in French', () => {
    const frMessages = require('@/messages/fr.json');

    render(
      <NextIntlProvider locale="fr" messages={frMessages}>
        <UserSettings />
      </NextIntlProvider>
    );

    expect(screen.getByText('Paramètres')).toBeInTheDocument();
  });
});
```

## 📊 Progress Tracking

### By Priority

**Phase 1 - Critical (Must Do):**
- [ ] Authentication pages
- [ ] Navigation/menus
- [ ] Dashboard home
- [ ] User settings
- [ ] Course listings

**Phase 2 - User-Facing:**
- [ ] Course player
- [ ] Assignments
- [ ] Certificates
- [ ] Profiles
- [ ] Notifications

**Phase 3 - Creator Tools:**
- [ ] Course editor
- [ ] Chapter/activity editor
- [ ] Org settings
- [ ] Analytics
- [ ] User management

**Phase 4 - System:**
- [ ] Error pages
- [ ] Admin tools
- [ ] Advanced settings

### Coverage Metrics

Target: **100% of user-facing components**

- Current: ~1% (LanguageSelector only)
- Phase 1 Goal: 20%
- Phase 2 Goal: 60%
- Phase 3 Goal: 90%
- Phase 4 Goal: 100%

## 🚀 Rollout Strategy

### Stage 1: Internal Testing
- Enable for team members
- Collect feedback
- Fix issues
- Refine translations

### Stage 2: Beta
- Enable for early adopters
- Monitor for missing translations
- Get native speaker feedback
- Iterate

### Stage 3: General Availability
- Auto-detect browser language
- Announce feature
- Full rollout

## 🔧 Tools

### Find Hardcoded Strings

```bash
# Grep for potential hardcoded strings in components
grep -r ">[A-Z][a-z]\+<" apps/web/components
```

### Check Translation Coverage

```typescript
// Script to check which components are translated
// List files with useTranslations vs total files
```

### Validate Translation Files

```bash
# Check all translation files have same keys
node scripts/validate-translations.js
```

## 📚 Documentation

- **Translation Best Practices**: `/context/translations.md`
- **Complete i18n Plan**: This file
- **next-intl docs**: https://next-intl-docs.vercel.app

## 🎯 Success Criteria

- ✅ All user-facing text translated to 5 languages
- ✅ No hardcoded strings in critical paths
- ✅ Language selection persists across sessions
- ✅ Instant language switching
- ✅ Native speaker approval of translations
- ✅ No console warnings for missing translations
- ✅ Consistent terminology across app

## 💡 Quick Reference

```tsx
// Import
import { useTranslations } from 'next-intl';

// Use
const t = useTranslations('ComponentName');
const c = useTranslations('common');

// Basic
{t('title')}
{c('save')}

// With variables
{t('welcome', { name: user.name })}

// Pluralization
{t('studentsCount', { count: n })}

// Rich text
{t.rich('terms', {
  link: (chunks) => <Link>{chunks}</Link>
})}
```

---

**Status**: Phase 1 in progress
**Last Updated**: 2025-01-29
**Next Review**: After Phase 1 completion
