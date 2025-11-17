"""
Test cases for Config Manager module
"""

import unittest
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_templates_dir = 'tests/test_templates'
        self.config_manager = ConfigManager(self.test_templates_dir)

    def tearDown(self):
        """Clean up test files"""
        templates_path = Path(self.test_templates_dir)
        if templates_path.exists():
            for file in templates_path.glob('*.json'):
                file.unlink()
            templates_path.rmdir()

    def test_initialization(self):
        """Test config manager initialization"""
        self.assertIsNotNone(self.config_manager)
        self.assertTrue(Path(self.test_templates_dir).exists())

    def test_save_configuration(self):
        """Test saving configuration"""
        config_data = {
            'chamber_specs': {
                'length': 3200,
                'width': 2100,
                'height': 2200
            },
            'uv_system': {
                'uv_intensity': 60
            }
        }

        output_path = 'tests/temp_config.json'

        result = self.config_manager.save_configuration(config_data, output_path)
        self.assertTrue(result)

        # Verify file exists and has correct structure
        self.assertTrue(Path(output_path).exists())

        with open(output_path, 'r') as f:
            saved_config = json.load(f)

        self.assertIn('config_version', saved_config)
        self.assertIn('saved_date', saved_config)
        self.assertIn('chamber_specs', saved_config)

        # Cleanup
        Path(output_path).unlink(missing_ok=True)

    def test_load_configuration(self):
        """Test loading configuration"""
        # Create a test config file
        test_config = {
            'config_version': '1.0',
            'saved_date': '2025-01-20T10:00:00Z',
            'chamber_specs': {
                'length': 3200
            },
            'uv_system': {},
            'user_preferences': {}
        }

        config_path = 'tests/temp_load_config.json'
        with open(config_path, 'w') as f:
            json.dump(test_config, f)

        # Load it
        loaded_config = self.config_manager.load_configuration(config_path)

        self.assertIsNotNone(loaded_config)
        self.assertEqual(loaded_config['chamber_specs']['length'], 3200)

        # Cleanup
        Path(config_path).unlink(missing_ok=True)

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent configuration file"""
        result = self.config_manager.load_configuration('nonexistent.json')
        self.assertIsNone(result)

    def test_validate_config(self):
        """Test configuration validation"""
        valid_config = {
            'config_version': '1.0',
            'chamber_specs': {
                'length': 3200,
                'width': 2100,
                'height': 2200
            },
            'uv_system': {
                'uv_intensity': 60
            },
            'user_preferences': {}
        }

        is_valid, message = self.config_manager.validate_config(valid_config)
        self.assertTrue(is_valid)

    def test_validate_invalid_config(self):
        """Test validation of invalid configuration"""
        # Missing required sections
        invalid_config = {
            'config_version': '1.0'
        }

        is_valid, message = self.config_manager.validate_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertIn('Missing required section', message)

    def test_validate_invalid_chamber_specs(self):
        """Test validation of invalid chamber specifications"""
        invalid_config = {
            'config_version': '1.0',
            'chamber_specs': {
                'length': -100,  # Invalid negative value
                'width': 2100,
                'height': 2200
            },
            'uv_system': {},
            'user_preferences': {}
        }

        is_valid, message = self.config_manager.validate_config(invalid_config)
        self.assertFalse(is_valid)

    def test_validate_uv_intensity_range(self):
        """Test validation of UV intensity range"""
        invalid_config = {
            'config_version': '1.0',
            'chamber_specs': {
                'length': 3200,
                'width': 2100,
                'height': 2200
            },
            'uv_system': {
                'uv_intensity': 2000  # Out of range
            },
            'user_preferences': {}
        }

        is_valid, message = self.config_manager.validate_config(invalid_config)
        self.assertFalse(is_valid)
        self.assertIn('UV intensity out of range', message)

    def test_create_template(self):
        """Test creating a configuration template"""
        config_data = {
            'chamber_specs': {'length': 3200},
            'uv_system': {'uv_intensity': 60},
            'user_preferences': {}
        }

        result = self.config_manager.create_template(
            'test_template',
            config_data,
            'Test template description'
        )

        self.assertTrue(result)

        # Verify template file exists
        template_path = Path(self.test_templates_dir) / 'test_template.json'
        self.assertTrue(template_path.exists())

    def test_get_config_templates(self):
        """Test getting list of templates"""
        # Create a test template
        self.config_manager.create_template(
            'test_template',
            {'chamber_specs': {}, 'uv_system': {}, 'user_preferences': {}},
            'Test'
        )

        templates = self.config_manager.get_config_templates()

        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)

        template_names = [t['name'] for t in templates]
        self.assertIn('test_template', template_names)

    def test_load_template(self):
        """Test loading a template"""
        # Create a template
        template_data = {
            'chamber_specs': {'length': 3200},
            'uv_system': {},
            'user_preferences': {}
        }

        self.config_manager.create_template('load_test', template_data)

        # Load it
        loaded = self.config_manager.load_template('load_test')

        self.assertIsNotNone(loaded)
        self.assertIn('chamber_specs', loaded)

    def test_delete_template(self):
        """Test deleting a template"""
        # Create a template
        self.config_manager.create_template(
            'delete_test',
            {'chamber_specs': {}, 'uv_system': {}, 'user_preferences': {}}
        )

        # Delete it
        result = self.config_manager.delete_template('delete_test')
        self.assertTrue(result)

        # Verify it's gone
        template_path = Path(self.test_templates_dir) / 'delete_test.json'
        self.assertFalse(template_path.exists())

    def test_merge_configurations(self):
        """Test merging configurations"""
        base = {
            'chamber_specs': {'length': 3200, 'width': 2100},
            'uv_system': {'uv_intensity': 60}
        }

        overlay = {
            'chamber_specs': {'length': 3500},
            'new_section': {'data': 'value'}
        }

        merged = self.config_manager.merge_configurations(base, overlay)

        # Check merged values
        self.assertEqual(merged['chamber_specs']['length'], 3500)  # Overridden
        self.assertEqual(merged['chamber_specs']['width'], 2100)   # Preserved
        self.assertIn('new_section', merged)  # Added

    def test_export_partial_config(self):
        """Test exporting partial configuration"""
        full_config = {
            'chamber_specs': {'length': 3200},
            'uv_system': {'uv_intensity': 60},
            'other_section': {'data': 'value'}
        }

        output_path = 'tests/temp_partial.json'

        result = self.config_manager.export_partial_config(
            full_config,
            ['chamber_specs', 'uv_system'],
            output_path
        )

        self.assertTrue(result)

        # Verify exported file
        with open(output_path, 'r') as f:
            partial = json.load(f)

        self.assertIn('chamber_specs', partial)
        self.assertIn('uv_system', partial)
        self.assertNotIn('other_section', partial)
        self.assertTrue(partial.get('partial_export', False))

        # Cleanup
        Path(output_path).unlink(missing_ok=True)

    def test_compare_configurations(self):
        """Test comparing configurations"""
        config1 = {
            'chamber_specs': {'length': 3200, 'width': 2100},
            'uv_system': {'uv_intensity': 60}
        }

        config2 = {
            'chamber_specs': {'length': 3500, 'width': 2100},
            'new_section': {'data': 'value'}
        }

        differences = self.config_manager.compare_configurations(config1, config2)

        self.assertIn('only_in_config1', differences)
        self.assertIn('only_in_config2', differences)
        self.assertIn('different_values', differences)

        # Check that length difference is detected
        self.assertIn('chamber_specs.length', differences['different_values'])

    def test_get_config_summary(self):
        """Test getting configuration summary"""
        config = {
            'config_version': '1.0',
            'saved_date': '2025-01-20T10:00:00Z',
            'chamber_specs': {
                'length': 3200,
                'width': 2100,
                'height': 2200
            },
            'uv_system': {
                'uv_intensity': 60
            }
        }

        summary = self.config_manager.get_config_summary(config)

        self.assertIn('version', summary)
        self.assertIn('saved_date', summary)
        self.assertIn('sections', summary)
        self.assertIn('section_count', summary)
        self.assertIn('chamber_volume', summary)
        self.assertIn('uv_intensity', summary)


if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    Path('tests').mkdir(exist_ok=True)

    unittest.main()
