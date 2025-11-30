# Translation Best Practices for LearnHouse

This document outlines the best practices for implementing i18n (internationalization) in the LearnHouse codebase.

## 🎯 Recommended Approach: Descriptive Dot Notation

Use clear, self-documenting keys that are readable in English while maintaining proper translation structure.

```tsx
// ✅ GOOD - Readable and maintainable
const t = useTranslations('settings');

<Label>{t('emailLabel')}</Label>
<Button>{t('saveButton')}</Button>
<p>{t('emailDescription')}</p>
```

**Translation file:**
```json
{
  "settings": {
    "emailLabel": "Email Address",
    "saveButton": "Save Changes",
    "emailDescription": "We'll never share your email"
  }
}
```

## 📋 Best Practices

### 1. Namespace by Component/Feature

Each component should have its own namespace for translations. This prevents conflicts and makes it easy to find translations.

```tsx
// Use component-scoped namespace
const t = useTranslations('UserEditGeneral');

return (
  <>
    <h1>{t('title')}</h1>              // "Account Settings"
    <Label>{t('firstNameLabel')}</Label> // "First Name"
    <Button>{t('submitButton')}</Button> // "Save Changes"
  </>
);
```

### 2. Use Descriptive, Self-Documenting Keys

Keys should clearly describe what they represent. Avoid abbreviations or generic names.

```tsx
// ❌ BAD - Not clear what these mean
t('label1')
t('text2')
t('btn')

// ✅ GOOD - Clear and readable
t('emailLabel')
t('welcomeMessage')
t('saveButton')
t('deleteConfirmation')
```

### 3. Group Related Translations

Organize translations into logical groups within each namespace.

```json
{
  "UserEditGeneral": {
    "title": "Account Settings",
    "subtitle": "Manage your personal information",

    "labels": {
      "email": "Email",
      "username": "Username",
      "firstName": "First Name",
      "lastName": "Last Name"
    },

    "buttons": {
      "save": "Save Changes",
      "cancel": "Cancel",
      "delete": "Delete Account"
    },

    "messages": {
      "saveSuccess": "Profile updated successfully",
      "saveError": "Failed to update profile"
    }
  }
}
```

**Usage:**
```tsx
const t = useTranslations('UserEditGeneral');

<Label>{t('labels.email')}</Label>
<Button>{t('buttons.save')}</Button>
toast.success(t('messages.saveSuccess'));
```

### 4. Common Translations in Shared Namespace

Frequently used translations should be in the `common` namespace for reuse across the app.

```tsx
// Reusable across app
const c = useTranslations('common');

<Button>{c('save')}</Button>      // Used everywhere
<Button>{c('cancel')}</Button>
<Button>{c('delete')}</Button>
<Button>{c('edit')}</Button>
<Button>{c('create')}</Button>
```

## 🏗️ File Structure

Our translation files follow this structure:

```
apps/web/messages/
├── en.json
├── fr.json
└── es.json
```

Each file contains:

```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "create": "Create"
  },
  "navigation": {
    "home": "Home",
    "courses": "Courses",
    "dashboard": "Dashboard"
  },
  "UserEditGeneral": {
    "title": "Account Settings",
    "labels": {
      "email": "Email",
      "username": "Username"
    }
  },
  "CourseDashboard": {
    // Component-specific translations
  }
}
```

## 💡 Advanced Features

### Variables in Translations

Use variables for dynamic content:

```json
{
  "welcome": "Welcome, {name}!",
  "courseCount": "You have {count} courses",
  "lastLogin": "Last login: {date}"
}
```

```tsx
t('welcome', { name: user.name })
t('courseCount', { count: 5 })
t('lastLogin', { date: new Date().toLocaleDateString() })
```

### Pluralization

Handle singular/plural forms automatically:

```json
{
  "studentsEnrolled": "{count, plural, =0 {No students} =1 {1 student} other {# students}}",
  "coursesCompleted": "{count, plural, =0 {No courses completed} =1 {1 course completed} other {# courses completed}}"
}
```

```tsx
t('studentsEnrolled', { count: 0 })  // "No students"
t('studentsEnrolled', { count: 1 })  // "1 student"
t('studentsEnrolled', { count: 42 }) // "42 students"
```

### Rich Text Formatting

For text with HTML elements:

```json
{
  "terms": "I agree to the <link>terms and conditions</link>",
  "emailWarning": "You will be logged out after changing your <strong>email address</strong>"
}
```

```tsx
t.rich('terms', {
  link: (chunks) => <Link href="/terms">{chunks}</Link>
})

t.rich('emailWarning', {
  strong: (chunks) => <strong>{chunks}</strong>
})
```

## 🎨 Recommended Pattern for LearnHouse Components

Here's the recommended pattern for implementing translations in components:

```tsx
'use client';

import { useTranslations } from 'next-intl';
import { Button } from '@components/ui/button';
import { Label } from '@components/ui/label';
import { Input } from '@components/ui/input';

export default function UserEditGeneral() {
  // Component-specific translations
  const t = useTranslations('UserEditGeneral');
  // Common/shared translations
  const c = useTranslations('common');

  return (
    <Form>
      <h1>{t('title')}</h1>                    // "Account Settings"
      <p>{t('subtitle')}</p>                   // "Manage your personal information"

      <div>
        <Label>{t('labels.email')}</Label>     // "Email"
        <Input
          placeholder={t('placeholders.email')}
          type="email"
        />
        {error && <p className="text-red-500">{t('errors.emailInvalid')}</p>}
      </div>

      <div>
        <Label>{t('labels.username')}</Label>  // "Username"
        <Input placeholder={t('placeholders.username')} />
      </div>

      <div className="flex gap-2">
        <Button type="submit">{c('save')}</Button>    // Shared "Save"
        <Button type="button">{c('cancel')}</Button>  // Shared "Cancel"
      </div>

      {success && toast.success(t('messages.saveSuccess'))}
    </Form>
  );
}
```

### Corresponding Translation File (en.json):

```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit"
  },
  "UserEditGeneral": {
    "title": "Account Settings",
    "subtitle": "Manage your personal information and preferences",

    "labels": {
      "email": "Email",
      "username": "Username",
      "firstName": "First Name",
      "lastName": "Last Name",
      "bio": "Bio"
    },

    "placeholders": {
      "email": "Enter your email address",
      "username": "Choose a username",
      "firstName": "Your first name",
      "lastName": "Your last name",
      "bio": "Tell us about yourself"
    },

    "errors": {
      "emailInvalid": "Invalid email address",
      "emailRequired": "Email is required",
      "usernameRequired": "Username is required",
      "usernameTaken": "This username is already taken"
    },

    "messages": {
      "saveSuccess": "Profile updated successfully",
      "saveError": "Failed to update profile",
      "emailChanged": "You will be logged out to verify your new email"
    },

    "buttons": {
      "save": "Save Changes",
      "uploadAvatar": "Change Avatar",
      "removeAvatar": "Remove Avatar"
    }
  }
}
```

## 🌍 Supported Languages

Currently, LearnHouse supports:

- 🇬🇧 **English** (en) - Default
- 🇫🇷 **Français** (fr) - French
- 🇪🇸 **Español** (es) - Spanish

### Adding a New Language

1. Create new translation file: `apps/web/messages/[locale].json`
2. Add locale to `apps/web/i18n/config.ts`:
   ```ts
   export const locales = ['en', 'fr', 'es', 'de'] as const; // Added German

   export const localeNames: Record<Locale, string> = {
     en: 'English',
     fr: 'Français',
     es: 'Español',
     de: 'Deutsch', // Added
   };
   ```
3. Update `LanguageSelector` component with flag emoji
4. Translate all keys from `en.json` to the new language

## 🔧 Implementation Checklist

When adding translations to a component:

- [ ] Import `useTranslations` from `next-intl`
- [ ] Create component namespace in translation files
- [ ] Use `useTranslations('ComponentName')` for component-specific text
- [ ] Use `useTranslations('common')` for shared/reusable text
- [ ] Replace all hardcoded strings with `t('key')` calls
- [ ] Group translations logically (labels, buttons, messages, etc.)
- [ ] Add translations for all supported languages (en, fr, es)
- [ ] Test language switching to verify translations work

## 🚫 Common Pitfalls to Avoid

### ❌ Don't use generic key names
```tsx
// BAD
t('text1')
t('label')
t('button')

// GOOD
t('welcomeMessage')
t('emailLabel')
t('submitButton')
```

### ❌ Don't hardcode strings in components
```tsx
// BAD
<Button>Save Changes</Button>

// GOOD
<Button>{c('save')}</Button>
```

### ❌ Don't duplicate translations
```tsx
// BAD - Define "Save" in every component
{
  "UserEditGeneral": { "save": "Save" },
  "CourseEdit": { "save": "Save" },
  "OrgSettings": { "save": "Save" }
}

// GOOD - Use common namespace
{
  "common": { "save": "Save" }
}
```

### ❌ Don't concatenate translated strings
```tsx
// BAD
const message = t('hello') + ' ' + t('world');

// GOOD - Use single key with variable
t('greeting', { name: 'World' })
```

## 📚 Resources

- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [ICU Message Format](https://formatjs.io/docs/core-concepts/icu-syntax/)
- [Language Selector Component](../apps/web/components/Objects/LanguageSelector/LanguageSelector.tsx)
- [i18n Config](../apps/web/i18n/config.ts)
- [Translation Request Helpers](../apps/web/i18n/request.ts)

## 🎯 Quick Reference

```tsx
// Import
import { useTranslations } from 'next-intl';

// Component-specific
const t = useTranslations('ComponentName');

// Common/shared
const c = useTranslations('common');

// Basic usage
{t('key')}

// With variables
{t('key', { variable: value })}

// With pluralization
{t('key', { count: number })}

// Rich text
{t.rich('key', {
  bold: (chunks) => <strong>{chunks}</strong>
})}
```

## 💬 Need Help?

If you're unsure about how to structure translations for a component:

1. Check existing translated components (e.g., `LanguageSelector`)
2. Look at the translation files in `apps/web/messages/`
3. Follow the patterns in this guide
4. When in doubt, prioritize readability and consistency
