"""
Test cases for White Label Manager module
"""

import unittest
import sys
import json
from pathlib import Path
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.white_label_manager import WhiteLabelManager


class TestWhiteLabelManager(unittest.TestCase):
    """Test cases for WhiteLabelManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_config_path = 'tests/temp_wl_config.json'
        self.wl_manager = WhiteLabelManager(self.test_config_path)

    def tearDown(self):
        """Clean up test files"""
        Path(self.test_config_path).unlink(missing_ok=True)

    def test_initialization(self):
        """Test white label manager initialization"""
        self.assertIsNotNone(self.wl_manager)
        self.assertIn('company', self.wl_manager.config)
        self.assertIn('branding', self.wl_manager.config)

    def test_default_config_structure(self):
        """Test default configuration structure"""
        config = self.wl_manager.config

        # Check company section
        self.assertIn('name', config['company'])
        self.assertIn('address', config['company'])
        self.assertIn('email', config['company'])
        self.assertIn('phone', config['company'])
        self.assertIn('website', config['company'])

        # Check branding section
        self.assertIn('logo_path', config['branding'])
        self.assertIn('primary_color', config['branding'])
        self.assertIn('secondary_color', config['branding'])
        self.assertIn('font_family', config['branding'])

    def test_set_company_info(self):
        """Test setting company information"""
        company_data = {
            'name': 'Test Company',
            'address': 'Test Address',
            'email': 'test@test.com',
            'phone': '+91-123-456-7890',
            'website': 'https://test.com'
        }

        result = self.wl_manager.set_company_info(company_data)
        self.assertTrue(result)

        # Verify data was set
        self.assertEqual(self.wl_manager.config['company']['name'], 'Test Company')
        self.assertEqual(self.wl_manager.config['company']['email'], 'test@test.com')

    def test_set_brand_colors(self):
        """Test setting brand colors"""
        result = self.wl_manager.set_brand_colors('#FF0000', '#00FF00')
        self.assertTrue(result)

        self.assertEqual(self.wl_manager.config['branding']['primary_color'], '#FF0000')
        self.assertEqual(self.wl_manager.config['branding']['secondary_color'], '#00FF00')

    def test_invalid_hex_color(self):
        """Test invalid hex color validation"""
        result = self.wl_manager.set_brand_colors('invalid', '#00FF00')
        self.assertFalse(result)

        result = self.wl_manager.set_brand_colors('#FF0000', 'not-a-color')
        self.assertFalse(result)

    def test_valid_hex_color_formats(self):
        """Test valid hex color formats"""
        # Test 6-digit hex
        self.assertTrue(self.wl_manager._is_valid_hex_color('#FF0000'))
        self.assertTrue(self.wl_manager._is_valid_hex_color('#00ff00'))

        # Test 3-digit hex
        self.assertTrue(self.wl_manager._is_valid_hex_color('#F00'))
        self.assertTrue(self.wl_manager._is_valid_hex_color('#0f0'))

        # Test invalid formats
        self.assertFalse(self.wl_manager._is_valid_hex_color('FF0000'))
        self.assertFalse(self.wl_manager._is_valid_hex_color('#GG0000'))
        self.assertFalse(self.wl_manager._is_valid_hex_color('#FF00'))

    def test_set_font_family(self):
        """Test setting font family"""
        result = self.wl_manager.set_font_family('Arial')
        self.assertTrue(result)

        self.assertEqual(self.wl_manager.config['branding']['font_family'], 'Arial')

    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        # Modify config
        self.wl_manager.set_company_info({'name': 'Save Test Company'})

        # Save
        save_result = self.wl_manager.save_config()
        self.assertTrue(save_result)

        # Create new manager and load
        new_manager = WhiteLabelManager(self.test_config_path)
        load_result = new_manager.load_config()
        self.assertTrue(load_result)

        # Verify loaded data
        self.assertEqual(new_manager.config['company']['name'], 'Save Test Company')

    def test_reset_to_default(self):
        """Test resetting to default configuration"""
        # Modify config
        self.wl_manager.set_company_info({'name': 'Modified Company'})

        # Reset
        result = self.wl_manager.reset_to_default()
        self.assertTrue(result)

        # Verify reset
        self.assertEqual(
            self.wl_manager.config['company']['name'],
            'Your Company Name'
        )

    def test_apply_branding(self):
        """Test applying branding configuration"""
        branding = self.wl_manager.apply_branding()

        self.assertIn('company', branding)
        self.assertIn('branding', branding)
        self.assertIn('logo_base64', branding)

    def test_preview_branding(self):
        """Test branding preview"""
        preview = self.wl_manager.preview_branding()

        self.assertIn('company_name', preview)
        self.assertIn('logo_available', preview)
        self.assertIn('primary_color', preview)
        self.assertIn('secondary_color', preview)
        self.assertIn('font_family', preview)

    def test_get_css_variables(self):
        """Test CSS variables generation"""
        css = self.wl_manager.get_css_variables()

        self.assertIn(':root', css)
        self.assertIn('--primary-color', css)
        self.assertIn('--secondary-color', css)
        self.assertIn('--font-family', css)

    def test_export_branding_package(self):
        """Test exporting branding package"""
        export_path = 'tests/temp_branding_package.json'

        result = self.wl_manager.export_branding_package(export_path)
        self.assertTrue(result)

        # Verify file exists and contains data
        self.assertTrue(Path(export_path).exists())

        with open(export_path, 'r') as f:
            package = json.load(f)

        self.assertIn('config', package)
        self.assertIn('exported_at', package)

        # Cleanup
        Path(export_path).unlink(missing_ok=True)

    def test_font_families_list(self):
        """Test that font families list is valid"""
        self.assertIsInstance(self.wl_manager.FONT_FAMILIES, list)
        self.assertGreater(len(self.wl_manager.FONT_FAMILIES), 0)
        self.assertIn('Helvetica', self.wl_manager.FONT_FAMILIES)

    def test_supported_formats(self):
        """Test supported image formats"""
        self.assertIn('png', self.wl_manager.SUPPORTED_FORMATS)
        self.assertIn('jpg', self.wl_manager.SUPPORTED_FORMATS)
        self.assertIn('svg', self.wl_manager.SUPPORTED_FORMATS)


if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    Path('tests').mkdir(exist_ok=True)

    unittest.main()
