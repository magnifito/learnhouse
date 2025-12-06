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

### Admin Course Listings
#### [MODIFY] [client.tsx](file:///Users/kirov/dev/magnifito/maglearn/apps/web/app/orgs/[orgslug]/dash/courses/client.tsx)
- Import `useTranslations`.
- Translate "Courses", "Rights Guide", "No courses yet", "Create a course to add content", etc.

### Course Structure Editor
#### [MODIFY] [EditCourseStructure.tsx](file:///Users/kirov/dev/magnifito/maglearn/apps/web/components/Dashboard/Pages/Course/EditCourseStructure/EditCourseStructure.tsx)
- Import `useTranslations`.
- Translate "Create chapter", "Add a new chapter to the course", "Add Chapter".

### Translation Files
#### [MODIFY] [en.json](file:///Users/kirov/dev/magnifito/maglearn/apps/web/messages/en.json)
- Add `courseListings` and `courseStructure` namespaces.

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
