# Internationalization (i18n) Guide

## Overview

The PV Chamber Configurator supports multiple languages through a comprehensive internationalization (i18n) system. This guide covers how to use, maintain, and extend multi-language support.

## Supported Languages

- **English (en_US)**: Default language
- **Hindi (hi_IN)**: Full Devanagari script support

## Getting Started

### User Language Selection

Users can change the language from the sidebar:

1. Navigate to sidebar
2. Select language from dropdown
3. Application updates immediately

### Programmatic Usage

```python
from modules import I18nManager

# Initialize with default locale
i18n = I18nManager(locale='en_US')

# Translate text
text = i18n.translate('app_title')
# Returns: "PV Chamber Configurator"

# Shorthand method
text = i18n.t('sidebar.language')
# Returns: "Language"
```

## Translation Files

### Location

`locales/[locale_code].json`

Examples:
- `locales/en_US.json` - English (US)
- `locales/hi_IN.json` - Hindi (India)

### File Structure

```json
{
  "_meta": {
    "language_name": "English",
    "language_code": "en_US",
    "direction": "ltr",
    "contributors": ["Team Name"]
  },
  "app_title": "PV Chamber Configurator",
  "sidebar": {
    "title": "Navigation",
    "language": "Language"
  },
  "buttons": {
    "save": "Save",
    "load": "Load"
  }
}
```

### Key Naming Conventions

Use dot notation for nested keys:

```python
# Good: Organized and clear
"sidebar.title": "Navigation"
"sidebar.language": "Language"
"buttons.save": "Save"

# Bad: Flat and unclear
"sidebar_title": "Navigation"
"save_button": "Save"
```

## API Reference

### Initialization

```python
from modules import I18nManager

# Default locale (English)
i18n = I18nManager()

# Specific locale
i18n = I18nManager(locale='hi_IN')

# Custom locales directory
i18n = I18nManager(locale='en_US', locales_dir='custom/locales')
```

### Translation Methods

#### Basic Translation

```python
# Translate simple key
text = i18n.translate('app_title')

# Translate nested key
text = i18n.translate('sidebar.language')

# Shorthand
text = i18n.t('buttons.save')
```

#### Translation with Parameters

```python
# In translation file:
"welcome_message": "Welcome, {name}!"

# In code:
message = i18n.t('welcome_message', name='John')
# Returns: "Welcome, John!"
```

### Locale Management

#### Set Locale

```python
# Change current locale
success = i18n.set_locale('hi_IN')

if success:
    print("Language changed to Hindi")
```

#### Get Current Locale

```python
current = i18n.get_current_locale()
# Returns: "en_US"
```

#### Get Available Locales

```python
locales = i18n.get_available_locales()
# Returns: [
#   {'code': 'en_US', 'name': 'English'},
#   {'code': 'hi_IN', 'name': 'हिंदी'}
# ]
```

### Locale Information

#### Check RTL Language

```python
is_rtl = i18n.is_rtl()  # Check current locale
is_rtl = i18n.is_rtl('ar_SA')  # Check specific locale

if is_rtl:
    apply_rtl_layout()
```

#### Get Locale Metadata

```python
metadata = i18n.get_locale_metadata()
# Returns: {
#   'language_name': 'English',
#   'language_code': 'en_US',
#   'direction': 'ltr'
# }
```

### Translation Management

#### Export Translations

```python
# Export for external editing
i18n.export_translations('en_US', 'exports/en_US.json')
```

#### Import Translations

```python
# Import edited translations
i18n.import_translations('hi_IN', 'translations/hi_IN.json')
```

#### Check Missing Keys

```python
# Find keys missing in translations compared to reference locale
missing = i18n.get_missing_keys('en_US')

# Returns: {
#   'hi_IN': ['messages.success.saved', 'tooltips.new_feature'],
#   'fr_FR': ['sidebar.title', ...]
# }
```

#### Get Translation Coverage

```python
coverage = i18n.get_translation_coverage()

# Returns: {
#   'en_US': 100.0,
#   'hi_IN': 95.5
# }
```

#### Create Locale Template

```python
# Create template for new language
i18n.create_locale_template('locales/template.json')
```

## Adding New Languages

### Step 1: Create Translation File

Create `locales/[locale_code].json`:

```json
{
  "_meta": {
    "language_name": "Français",
    "language_code": "fr_FR",
    "direction": "ltr",
    "contributors": ["Your Name"]
  },
  "app_title": "Configurateur de Chambre PV",
  ...
}
```

### Step 2: Translate All Keys

Use English file as reference:

```bash
# Copy English file as template
cp locales/en_US.json locales/fr_FR.json

# Edit and translate all values
```

### Step 3: Test Translations

```python
# Load and test new locale
i18n = I18nManager(locale='fr_FR')
print(i18n.t('app_title'))

# Check for missing keys
missing = i18n.get_missing_keys('en_US')
if 'fr_FR' in missing:
    print("Missing keys:", missing['fr_FR'])
```

### Step 4: Verify Coverage

```python
coverage = i18n.get_translation_coverage()
print(f"French coverage: {coverage['fr_FR']}%")
```

## Translation Best Practices

### 1. Use Placeholders for Dynamic Content

```json
// Good
"error_message": "Failed to save {item_name}"

// Bad
"error_message": "Failed to save"  // Can't specify what failed
```

### 2. Provide Context in Key Names

```json
// Good
"buttons.save_configuration": "Save Configuration"
"buttons.save_results": "Save Results"

// Bad
"save1": "Save Configuration"
"save2": "Save Results"
```

### 3. Keep Translations Concise

```json
// Good
"tooltips.temp_uniformity": "Temperature uniformity across chamber. Target: ±2°C"

// Bad (too verbose)
"tooltips.temp_uniformity": "This tooltip explains that temperature uniformity is a measurement of how evenly the temperature is distributed across the entire chamber volume and the target specification for this parameter is plus or minus two degrees Celsius"
```

### 4. Maintain Consistency

Use consistent terminology across all translations:

```json
"buttons.save": "Save",
"messages.success.saved": "Saved successfully",  // Not "Stored successfully"
"tooltips.save_info": "Save configuration for later use"  // Not "Store configuration"
```

### 5. Consider Cultural Differences

```json
// Date formats
"en_US": "MM/DD/YYYY"
"en_GB": "DD/MM/YYYY"
"hi_IN": "DD/MM/YYYY"

// Number formats
"en_US": "1,234.56"
"hi_IN": "1,234.56" or "1234.56"
```

## Integration with Streamlit

### Basic Integration

```python
import streamlit as st
from modules import I18nManager

# Initialize in session state
if 'i18n' not in st.session_state:
    st.session_state.i18n = I18nManager()

# Helper function
def t(key, **kwargs):
    return st.session_state.i18n.translate(key, **kwargs)

# Use in UI
st.title(t('app_title'))
st.button(t('buttons.save'))
```

### Language Switcher

```python
# Language selector in sidebar
available_locales = st.session_state.i18n.get_available_locales()
locale_options = {loc['code']: loc['name'] for loc in available_locales}

selected_locale = st.selectbox(
    t('sidebar.language'),
    options=list(locale_options.keys()),
    format_func=lambda x: locale_options[x]
)

if selected_locale != st.session_state.i18n.get_current_locale():
    st.session_state.i18n.set_locale(selected_locale)
    st.rerun()
```

### Dynamic Content Translation

```python
# Translate dataframe columns
df = pd.DataFrame({
    t('labels.component'): ['Item 1', 'Item 2'],
    t('labels.cost'): [100, 200]
})

st.dataframe(df)
```

## Translation Workflow

### For Translators

1. **Get Template**
   ```python
   i18n.create_locale_template('translations/template.json')
   ```

2. **Translate**
   - Edit template file
   - Translate all values (keep keys unchanged)
   - Maintain JSON structure
   - Use UTF-8 encoding

3. **Submit**
   - Save as `[locale_code].json`
   - Submit for review

4. **Review**
   ```python
   # Check for errors
   i18n.import_translations('new_locale', 'file.json')
   missing = i18n.get_missing_keys()
   ```

### For Developers

1. **Add New Keys**
   - Add to `en_US.json` (reference language)
   - Use descriptive key names
   - Organize in logical groups

2. **Update All Translations**
   ```python
   missing = i18n.get_missing_keys('en_US')
   for locale, keys in missing.items():
       print(f"{locale} missing: {keys}")
   ```

3. **Test**
   ```python
   for locale in ['en_US', 'hi_IN']:
       i18n.set_locale(locale)
       assert i18n.t('new_key') != 'new_key'  # Translated
   ```

## Special Characters and Encoding

### Unicode Support

All translation files use UTF-8 encoding:

```json
{
  "app_title": "पीवी चैम्बर कॉन्फ़िगरेटर",  // Hindi (Devanagari)
  "company": "شركة",  // Arabic
  "test": "测试"  // Chinese
}
```

### Escape Sequences

```json
{
  "message": "Line 1\nLine 2",  // Newline
  "path": "C:\\Program Files\\App",  // Windows path
  "quote": "He said \"Hello\""  // Quoted text
}
```

## Right-to-Left (RTL) Languages

### Detection

```python
if i18n.is_rtl():
    st.markdown('<div dir="rtl">Content</div>', unsafe_allow_html=True)
```

### RTL Languages Supported

- Arabic (ar)
- Hebrew (he)
- Persian (fa)
- Urdu (ur)

## Troubleshooting

### Key Not Found

```python
# Returns key itself if translation not found
text = i18n.t('nonexistent.key')
# Returns: "nonexistent.key"

# Check logs
import logging
logging.getLogger('I18nManager').setLevel(logging.DEBUG)
```

### Encoding Issues

Ensure files are UTF-8:

```bash
# Check encoding
file -i locales/hi_IN.json

# Convert if needed
iconv -f ISO-8859-1 -t UTF-8 input.json > output.json
```

### Missing Translations

```python
# Find all missing keys
missing = i18n.get_missing_keys('en_US')

for locale, keys in missing.items():
    print(f"\n{locale} missing {len(keys)} keys:")
    for key in keys:
        print(f"  - {key}")
```

### Locale Not Loading

```python
# Debug locale loading
i18n = I18nManager(locale='hi_IN')

if not i18n.translations:
    print("Failed to load translations")
    print(f"Looking for: locales/hi_IN.json")
    print(f"File exists: {Path('locales/hi_IN.json').exists()}")
```

## Performance Optimization

### Caching Translations

```python
# Translations are cached after first load
i18n = I18nManager(locale='en_US')  # Loads from file
text1 = i18n.t('app_title')  # Uses cache
text2 = i18n.t('app_title')  # Uses cache
```

### Lazy Loading

Only load locale when needed:

```python
# Don't load all locales at startup
# Load on demand when user changes language
if new_locale != current_locale:
    i18n.set_locale(new_locale)  # Loads only this locale
```

## Testing Translations

### Unit Tests

```python
import unittest
from modules import I18nManager

class TestTranslations(unittest.TestCase):
    def test_english_translations(self):
        i18n = I18nManager(locale='en_US')
        self.assertEqual(i18n.t('app_title'), 'PV Chamber Configurator')

    def test_hindi_translations(self):
        i18n = I18nManager(locale='hi_IN')
        self.assertEqual(i18n.t('app_title'), 'पीवी चैम्बर कॉन्फ़िगरेटर')

    def test_all_keys_translated(self):
        i18n = I18nManager()
        missing = i18n.get_missing_keys('en_US')
        self.assertEqual(len(missing), 0, f"Missing translations: {missing}")
```

### Manual Testing Checklist

- [ ] All UI text displays correctly
- [ ] No translation keys visible (e.g., "sidebar.title")
- [ ] Special characters render properly
- [ ] RTL languages display right-to-left
- [ ] Numbers and dates format correctly
- [ ] Tooltips translate properly
- [ ] Error messages translate
- [ ] Email templates use correct language

## Contributing Translations

### Guidelines for Contributors

1. **Native Speaker**: Be a native speaker of the target language
2. **Context**: Understand the PV testing domain
3. **Consistency**: Use consistent terminology
4. **Testing**: Test translations in the actual application
5. **Formatting**: Preserve formatting and placeholders

### Submission Process

1. Fork repository
2. Create translation file
3. Test thoroughly
4. Submit pull request
5. Include translation coverage report

## Resources

### Language Codes

- en_US: English (United States)
- en_GB: English (United Kingdom)
- hi_IN: Hindi (India)
- es_ES: Spanish (Spain)
- fr_FR: French (France)
- de_DE: German (Germany)
- zh_CN: Chinese (Simplified)
- ja_JP: Japanese (Japan)

### Tools

- **JSON Validators**: https://jsonlint.com/
- **UTF-8 Checkers**: https://www.charset.org/utf-8
- **Translation Memory**: Use CAT tools for consistency

### Further Reading

- [Unicode Standard](https://unicode.org/)
- [CLDR Locale Data](https://cldr.unicode.org/)
- [ISO 639 Language Codes](https://www.iso.org/iso-639-language-codes.html)
