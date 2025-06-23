# Translation Guide

This guide explains how to use and extend the multi-language (i18n) support in the Angular application.

## Overview

The application uses `@ngx-translate/core` for internationalization with the following features:

- **Default Language**: Vietnamese (vi)
- **Supported Languages**: English (en), Vietnamese (vi)
- **Language Persistence**: User's language preference is stored in localStorage
- **Dynamic Language Switching**: Real-time language switching without page reload

## Current Implementation

### 1. Translation Files

Translation files are located in `src/assets/i18n/`:

- `en.json` - English translations
- `vi.json` - Vietnamese translations

### 2. Translation Service

The `TranslationService` (`src/app/core/services/translation.service.ts`) provides:

- Language switching functionality
- Current language management
- Language validation
- Translation utilities

### 3. Language Selector Component

The `LanguageSelectorComponent` (`src/app/shared/components/language-selector/`) provides:

- Dropdown menu for language selection
- Visual indication of current language
- Integration with the toolbar

## How to Use Translations

### 1. In Templates

Use the `translate` pipe:

```html
<!-- Simple translation -->
<h1>{{ 'COMMON.TITLE' | translate }}</h1>

<!-- Translation with parameters -->
<p>{{ 'AUTH.WELCOME' | translate: { name: userName } }}</p>

<!-- Translation with nested keys -->
<span>{{ 'COMMON.BUTTONS.SAVE' | translate }}</span>
```

### 2. In Components

Inject the `TranslationService`:

```typescript
import { TranslationService } from './core/services/translation.service';

export class MyComponent {
  constructor(private translationService: TranslationService) {}

  // Get translated text as observable
  getTranslatedText(): Observable<string> {
    return this.translationService.translate('COMMON.TITLE');
  }

  // Get translated text instantly
  getInstantText(): string {
    return this.translationService.instant('COMMON.TITLE');
  }

  // Switch language programmatically
  switchLanguage(langCode: string): void {
    this.translationService.setLanguage(langCode);
  }
}
```

### 3. Translation Keys Structure

Use a hierarchical structure for better organization:

```json
{
  "COMMON": {
    "TITLE": "AI Agent Platform",
    "BUTTONS": {
      "SAVE": "Save",
      "CANCEL": "Cancel",
      "DELETE": "Delete"
    }
  },
  "AUTH": {
    "LOGIN": "Login",
    "WELCOME": "Welcome, {{name}}"
  }
}
```

## How to Add New Languages

### Step 1: Add Language Configuration

1. **Update TranslationService** (`src/app/core/services/translation.service.ts`):

```typescript
public readonly availableLanguages: Language[] = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt' },
  { code: 'fr', name: 'French', nativeName: 'Français' }, // New language
  { code: 'de', name: 'German', nativeName: 'Deutsch' }   // New language
];
```

### Step 2: Create Translation File

Create a new JSON file in `src/assets/i18n/`:

**Example: `src/assets/i18n/fr.json`**
```json
{
  "COMMON": {
    "TITLE": "Plateforme d'Agent IA",
    "AGENTS": "Agents",
    "CHAT": "Chat",
    "LOGOUT": "Déconnexion",
    "WELCOME": "Bienvenue",
    "THEME": "Thème",
    "LIGHT_THEME": "Thème Clair",
    "DARK_THEME": "Thème Sombre",
    "AUTO_THEME": "Thème Auto",
    "SWITCH_TO_LIGHT": "Passer au Thème Clair",
    "SWITCH_TO_DARK": "Passer au Thème Sombre",
    "LANGUAGE": "Langue",
    "ENGLISH": "Anglais",
    "VIETNAMESE": "Vietnamien",
    "FRENCH": "Français"
  },
  "AUTH": {
    "LOGIN": "Connexion",
    "REGISTER": "S'inscrire",
    "EMAIL": "Email",
    "PASSWORD": "Mot de passe",
    "CONFIRM_PASSWORD": "Confirmer le mot de passe",
    "FORGOT_PASSWORD": "Mot de passe oublié ?",
    "LOGIN_BUTTON": "Se connecter",
    "REGISTER_BUTTON": "S'inscrire",
    "LOGIN_ERROR": "Email ou mot de passe invalide",
    "REGISTER_ERROR": "Échec de l'inscription"
  }
}
```

### Step 3: Update Existing Translation Files

Add the new language name to all existing translation files:

**Update `en.json`:**
```json
{
  "COMMON": {
    // ... existing translations ...
    "FRENCH": "French"
  }
}
```

**Update `vi.json`:**
```json
{
  "COMMON": {
    // ... existing translations ...
    "FRENCH": "Tiếng Pháp"
  }
}
```

### Step 4: Test the New Language

1. Start the development server: `npm start`
2. Navigate to the application
3. Click the language selector in the toolbar
4. Select the new language
5. Verify all translations are working correctly

## Best Practices

### 1. Translation Key Naming

- Use UPPERCASE for translation keys
- Use hierarchical structure (e.g., `COMMON.BUTTONS.SAVE`)
- Be descriptive and consistent
- Group related translations together

### 2. Translation File Organization

- Keep translation files organized by feature
- Use consistent structure across all language files
- Include comments for complex translations
- Validate JSON syntax

### 3. Component Integration

- Always use translation keys instead of hardcoded text
- Provide fallback text for missing translations
- Use translation parameters for dynamic content
- Test translations in all supported languages

### 4. Performance Considerations

- Lazy load translation files for large applications
- Use translation parameters instead of string concatenation
- Cache translations when appropriate
- Monitor translation file sizes

## Troubleshooting

### Common Issues

1. **Translation not showing**: Check if the translation key exists in all language files
2. **Language not switching**: Verify the language code is added to `availableLanguages`
3. **Missing translations**: Ensure all language files have the same structure
4. **JSON syntax errors**: Validate JSON files using a JSON validator

### Debugging

1. **Check browser console** for translation-related errors
2. **Verify translation files** are being loaded correctly
3. **Test with different languages** to ensure consistency
4. **Use browser dev tools** to inspect translation keys

## Example: Adding Spanish Support

Here's a complete example of adding Spanish support:

### 1. Update TranslationService

```typescript
public readonly availableLanguages: Language[] = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt' },
  { code: 'es', name: 'Spanish', nativeName: 'Español' }
];
```

### 2. Create `src/assets/i18n/es.json`

```json
{
  "COMMON": {
    "TITLE": "Plataforma de Agente IA",
    "AGENTS": "Agentes",
    "CHAT": "Chat",
    "LOGOUT": "Cerrar Sesión",
    "WELCOME": "Bienvenido",
    "THEME": "Tema",
    "LIGHT_THEME": "Tema Claro",
    "DARK_THEME": "Tema Oscuro",
    "AUTO_THEME": "Tema Automático",
    "SWITCH_TO_LIGHT": "Cambiar a Tema Claro",
    "SWITCH_TO_DARK": "Cambiar a Tema Oscuro",
    "LANGUAGE": "Idioma",
    "ENGLISH": "Inglés",
    "VIETNAMESE": "Vietnamita",
    "SPANISH": "Español"
  }
}
```

### 3. Update existing files

Add `"SPANISH": "Spanish"` to `en.json` and `"SPANISH": "Tiếng Tây Ban Nha"` to `vi.json`

### 4. Test

The Spanish language option will now appear in the language selector dropdown.

## Conclusion

This translation system provides a robust foundation for multi-language support. By following these guidelines, you can easily extend the application to support additional languages while maintaining consistency and performance. 