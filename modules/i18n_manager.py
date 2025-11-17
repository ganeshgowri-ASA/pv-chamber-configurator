"""
Internationalization Manager for PV Chamber Configurator
Handles multi-language support and translations
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List


class I18nManager:
    """
    Manages internationalization (i18n) for the PV Chamber Configurator.
    Supports multiple languages with dynamic translation loading.
    """

    # Right-to-left languages
    RTL_LANGUAGES = ['ar', 'he', 'fa', 'ur']

    def __init__(self, locale: str = 'en_US', locales_dir: str = 'locales'):
        """
        Initialize the i18n manager.

        Args:
            locale: Default locale (e.g., 'en_US', 'hi_IN')
            locales_dir: Directory containing translation files
        """
        self.locales_dir = Path(locales_dir)
        self.current_locale = locale
        self.translations = {}
        self.fallback_locale = 'en_US'
        self.logger = self._setup_logger()

        # Create locales directory if it doesn't exist
        self.locales_dir.mkdir(parents=True, exist_ok=True)

        # Load translations
        self.load_translations(locale)

        self.logger.info(f"I18n Manager initialized with locale: {locale}")

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the i18n manager."""
        logger = logging.getLogger('I18nManager')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def load_translations(self, locale: str) -> bool:
        """
        Load translations for a specific locale.

        Args:
            locale: Locale to load (e.g., 'en_US')

        Returns:
            bool: True if successful
        """
        translation_file = self.locales_dir / f"{locale}.json"

        try:
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)

                self.current_locale = locale
                self.logger.info(f"Translations loaded for locale: {locale}")
                return True
            else:
                self.logger.warning(f"Translation file not found: {translation_file}")

                # Try to load fallback
                if locale != self.fallback_locale:
                    self.logger.info(f"Attempting to load fallback locale: {self.fallback_locale}")
                    return self.load_translations(self.fallback_locale)

                return False

        except Exception as e:
            self.logger.error(f"Failed to load translations: {str(e)}")
            return False

    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key to the current locale.

        Args:
            key: Translation key (e.g., 'app_title' or 'sidebar.core_calculations')
            **kwargs: Optional format parameters

        Returns:
            str: Translated text or key if not found
        """
        # Navigate nested keys (e.g., 'sidebar.core_calculations')
        keys = key.split('.')
        value = self.translations

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                self.logger.warning(f"Translation key not found: {key}")
                return key

        # Format string if kwargs provided
        if kwargs and isinstance(value, str):
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                self.logger.error(f"Missing format parameter for key {key}: {e}")

        return value

    def t(self, key: str, **kwargs) -> str:
        """
        Shorthand for translate().

        Args:
            key: Translation key
            **kwargs: Optional format parameters

        Returns:
            str: Translated text
        """
        return self.translate(key, **kwargs)

    def set_locale(self, locale: str) -> bool:
        """
        Change the current locale.

        Args:
            locale: New locale to set

        Returns:
            bool: True if successful
        """
        if locale == self.current_locale:
            return True

        success = self.load_translations(locale)

        if success:
            self.logger.info(f"Locale changed to: {locale}")

        return success

    def get_available_locales(self) -> List[Dict[str, str]]:
        """
        Get list of available locales.

        Returns:
            List of dicts with locale info
        """
        available_locales = []

        # Scan locales directory for JSON files
        for locale_file in self.locales_dir.glob('*.json'):
            locale_code = locale_file.stem

            # Try to get locale name from the file
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    locale_name = data.get('_meta', {}).get('language_name', locale_code)

                available_locales.append({
                    'code': locale_code,
                    'name': locale_name
                })
            except Exception as e:
                self.logger.error(f"Error reading locale file {locale_file}: {e}")
                available_locales.append({
                    'code': locale_code,
                    'name': locale_code
                })

        return available_locales

    def is_rtl(self, locale: Optional[str] = None) -> bool:
        """
        Check if a locale uses right-to-left text direction.

        Args:
            locale: Locale to check (defaults to current locale)

        Returns:
            bool: True if RTL
        """
        check_locale = locale or self.current_locale
        language_code = check_locale.split('_')[0].lower()

        return language_code in self.RTL_LANGUAGES

    def get_current_locale(self) -> str:
        """
        Get the current locale.

        Returns:
            str: Current locale code
        """
        return self.current_locale

    def get_locale_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the current locale.

        Returns:
            Dict with locale metadata
        """
        return self.translations.get('_meta', {
            'language_name': self.current_locale,
            'language_code': self.current_locale,
            'direction': 'rtl' if self.is_rtl() else 'ltr'
        })

    def export_translations(self, locale: str, output_path: str) -> bool:
        """
        Export translations for a locale to a file.

        Args:
            locale: Locale to export
            output_path: Output file path

        Returns:
            bool: True if successful
        """
        translation_file = self.locales_dir / f"{locale}.json"

        try:
            if not translation_file.exists():
                self.logger.error(f"Locale file not found: {locale}")
                return False

            with open(translation_file, 'r', encoding='utf-8') as f:
                translations = json.load(f)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Translations exported to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export translations: {str(e)}")
            return False

    def import_translations(self, locale: str, input_path: str) -> bool:
        """
        Import translations from a file.

        Args:
            locale: Locale code for the translations
            input_path: Path to the translation file

        Returns:
            bool: True if successful
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                translations = json.load(f)

            # Validate translation structure
            if not isinstance(translations, dict):
                raise ValueError("Translations must be a dictionary")

            # Save to locales directory
            output_file = self.locales_dir / f"{locale}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Translations imported for locale: {locale}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to import translations: {str(e)}")
            return False

    def get_missing_keys(self, reference_locale: str = 'en_US') -> Dict[str, List[str]]:
        """
        Find missing translation keys compared to reference locale.

        Args:
            reference_locale: Reference locale to compare against

        Returns:
            Dict with missing keys per locale
        """
        reference_file = self.locales_dir / f"{reference_locale}.json"

        if not reference_file.exists():
            self.logger.error(f"Reference locale not found: {reference_locale}")
            return {}

        try:
            with open(reference_file, 'r', encoding='utf-8') as f:
                reference_keys = self._flatten_dict(json.load(f))

            missing_keys = {}

            # Check all other locales
            for locale_file in self.locales_dir.glob('*.json'):
                locale_code = locale_file.stem

                if locale_code == reference_locale:
                    continue

                with open(locale_file, 'r', encoding='utf-8') as f:
                    locale_keys = self._flatten_dict(json.load(f))

                # Find missing keys
                missing = set(reference_keys.keys()) - set(locale_keys.keys())

                if missing:
                    missing_keys[locale_code] = sorted(list(missing))

            return missing_keys

        except Exception as e:
            self.logger.error(f"Failed to check missing keys: {str(e)}")
            return {}

    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
        """Flatten nested dictionary with dot notation keys."""
        items = []

        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict) and not k.startswith('_'):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))

        return dict(items)

    def create_locale_template(self, output_path: str) -> bool:
        """
        Create a template for a new locale based on current translations.

        Args:
            output_path: Path to save the template

        Returns:
            bool: True if successful
        """
        try:
            template = {
                '_meta': {
                    'language_name': 'Language Name',
                    'language_code': 'xx_XX',
                    'direction': 'ltr',
                    'contributors': []
                }
            }

            # Copy structure from current translations
            template.update(self.translations)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Locale template created: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create locale template: {str(e)}")
            return False

    def get_translation_coverage(self) -> Dict[str, float]:
        """
        Get translation coverage percentage for all locales.

        Returns:
            Dict with locale codes and coverage percentages
        """
        reference_file = self.locales_dir / f"{self.fallback_locale}.json"

        if not reference_file.exists():
            return {}

        try:
            with open(reference_file, 'r', encoding='utf-8') as f:
                reference_keys = set(self._flatten_dict(json.load(f)).keys())

            total_keys = len(reference_keys)
            coverage = {}

            for locale_file in self.locales_dir.glob('*.json'):
                locale_code = locale_file.stem

                with open(locale_file, 'r', encoding='utf-8') as f:
                    locale_keys = set(self._flatten_dict(json.load(f)).keys())

                translated_keys = len(reference_keys & locale_keys)
                coverage[locale_code] = (translated_keys / total_keys * 100) if total_keys > 0 else 0

            return coverage

        except Exception as e:
            self.logger.error(f"Failed to calculate coverage: {str(e)}")
            return {}
