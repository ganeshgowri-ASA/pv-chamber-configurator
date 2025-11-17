"""
Test cases for I18n Manager module
"""

import unittest
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.i18n_manager import I18nManager


class TestI18nManager(unittest.TestCase):
    """Test cases for I18nManager class"""

    @classmethod
    def setUpClass(cls):
        """Set up test translation files"""
        cls.test_locales_dir = Path('tests/test_locales')
        cls.test_locales_dir.mkdir(exist_ok=True)

        # Create test translation files
        en_translations = {
            '_meta': {
                'language_name': 'English',
                'language_code': 'en_US'
            },
            'app_title': 'Test App',
            'sidebar': {
                'title': 'Navigation',
                'language': 'Language'
            },
            'messages': {
                'success': {
                    'saved': 'Saved successfully'
                }
            }
        }

        hi_translations = {
            '_meta': {
                'language_name': 'हिंदी',
                'language_code': 'hi_IN'
            },
            'app_title': 'परीक्षण एप्लिकेशन',
            'sidebar': {
                'title': 'नेविगेशन',
                'language': 'भाषा'
            }
        }

        with open(cls.test_locales_dir / 'en_US.json', 'w', encoding='utf-8') as f:
            json.dump(en_translations, f, ensure_ascii=False, indent=2)

        with open(cls.test_locales_dir / 'hi_IN.json', 'w', encoding='utf-8') as f:
            json.dump(hi_translations, f, ensure_ascii=False, indent=2)

    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        for file in cls.test_locales_dir.glob('*.json'):
            file.unlink()
        cls.test_locales_dir.rmdir()

    def setUp(self):
        """Set up test fixtures"""
        self.i18n = I18nManager(locale='en_US', locales_dir=str(self.test_locales_dir))

    def test_initialization(self):
        """Test i18n manager initialization"""
        self.assertIsNotNone(self.i18n)
        self.assertEqual(self.i18n.current_locale, 'en_US')
        self.assertIsInstance(self.i18n.translations, dict)

    def test_translate_simple_key(self):
        """Test translating a simple key"""
        result = self.i18n.translate('app_title')
        self.assertEqual(result, 'Test App')

    def test_translate_nested_key(self):
        """Test translating a nested key"""
        result = self.i18n.translate('sidebar.title')
        self.assertEqual(result, 'Navigation')

        result = self.i18n.translate('messages.success.saved')
        self.assertEqual(result, 'Saved successfully')

    def test_translate_missing_key(self):
        """Test translating a missing key"""
        result = self.i18n.translate('nonexistent.key')
        self.assertEqual(result, 'nonexistent.key')

    def test_translate_shorthand(self):
        """Test shorthand t() method"""
        result = self.i18n.t('app_title')
        self.assertEqual(result, 'Test App')

    def test_set_locale(self):
        """Test changing locale"""
        result = self.i18n.set_locale('hi_IN')
        self.assertTrue(result)
        self.assertEqual(self.i18n.current_locale, 'hi_IN')

        # Test Hindi translation
        title = self.i18n.translate('app_title')
        self.assertEqual(title, 'परीक्षण एप्लिकेशन')

    def test_get_available_locales(self):
        """Test getting available locales"""
        locales = self.i18n.get_available_locales()

        self.assertIsInstance(locales, list)
        self.assertGreater(len(locales), 0)

        locale_codes = [loc['code'] for loc in locales]
        self.assertIn('en_US', locale_codes)
        self.assertIn('hi_IN', locale_codes)

    def test_is_rtl(self):
        """Test RTL detection"""
        # English is LTR
        self.assertFalse(self.i18n.is_rtl('en_US'))

        # Arabic is RTL
        self.assertTrue(self.i18n.is_rtl('ar_SA'))

        # Hebrew is RTL
        self.assertTrue(self.i18n.is_rtl('he_IL'))

    def test_get_current_locale(self):
        """Test getting current locale"""
        locale = self.i18n.get_current_locale()
        self.assertEqual(locale, 'en_US')

    def test_get_locale_metadata(self):
        """Test getting locale metadata"""
        metadata = self.i18n.get_locale_metadata()

        self.assertIn('language_name', metadata)
        self.assertEqual(metadata['language_name'], 'English')

    def test_flatten_dict(self):
        """Test dictionary flattening"""
        nested = {
            'a': 1,
            'b': {
                'c': 2,
                'd': {
                    'e': 3
                }
            }
        }

        flattened = self.i18n._flatten_dict(nested)

        self.assertEqual(flattened['a'], 1)
        self.assertEqual(flattened['b.c'], 2)
        self.assertEqual(flattened['b.d.e'], 3)

    def test_export_translations(self):
        """Test exporting translations"""
        export_path = 'tests/temp_export_translations.json'

        result = self.i18n.export_translations('en_US', export_path)
        self.assertTrue(result)

        # Verify file exists
        self.assertTrue(Path(export_path).exists())

        # Cleanup
        Path(export_path).unlink(missing_ok=True)

    def test_import_translations(self):
        """Test importing translations"""
        # Create a translation file
        import_data = {
            '_meta': {'language_name': 'Test Language'},
            'test_key': 'test_value'
        }

        import_path = self.test_locales_dir / 'test_import.json'
        with open(import_path, 'w', encoding='utf-8') as f:
            json.dump(import_data, f, ensure_ascii=False)

        # Import
        result = self.i18n.import_translations('test_locale', str(import_path))
        self.assertTrue(result)

        # Verify imported file exists
        imported_file = self.test_locales_dir / 'test_locale.json'
        self.assertTrue(imported_file.exists())

        # Cleanup
        import_path.unlink(missing_ok=True)
        imported_file.unlink(missing_ok=True)

    def test_get_missing_keys(self):
        """Test finding missing translation keys"""
        missing = self.i18n.get_missing_keys('en_US')

        self.assertIsInstance(missing, dict)

        # hi_IN should be missing some keys that en_US has
        if 'hi_IN' in missing:
            self.assertIn('messages.success.saved', missing['hi_IN'])

    def test_create_locale_template(self):
        """Test creating locale template"""
        template_path = 'tests/temp_locale_template.json'

        result = self.i18n.create_locale_template(template_path)
        self.assertTrue(result)

        # Verify file exists and has correct structure
        self.assertTrue(Path(template_path).exists())

        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)

        self.assertIn('_meta', template)

        # Cleanup
        Path(template_path).unlink(missing_ok=True)

    def test_get_translation_coverage(self):
        """Test getting translation coverage"""
        coverage = self.i18n.get_translation_coverage()

        self.assertIsInstance(coverage, dict)
        self.assertIn('en_US', coverage)
        self.assertEqual(coverage['en_US'], 100.0)


if __name__ == '__main__':
    unittest.main()
