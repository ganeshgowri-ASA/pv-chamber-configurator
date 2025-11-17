"""
Test cases for Integration Layer module
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.integration_layer import IntegrationLayer


class TestIntegrationLayer(unittest.TestCase):
    """Test cases for IntegrationLayer class"""

    def setUp(self):
        """Set up test fixtures"""
        self.integration = IntegrationLayer()

    def test_initialization(self):
        """Test integration layer initialization"""
        self.assertIsNotNone(self.integration)
        self.assertEqual(len(self.integration.modules), 9)
        self.assertIn('phase1_core', self.integration.modules)

    def test_initialize_all_modules(self):
        """Test module initialization"""
        result = self.integration.initialize_all_modules()
        self.assertTrue(result)

        for module_id, module_info in self.integration.modules.items():
            self.assertTrue(module_info['initialized'])

    def test_set_and_get_module_data(self):
        """Test setting and getting module data"""
        test_data = {
            'length': 3200,
            'width': 2100,
            'height': 2200
        }

        # Set data
        result = self.integration.set_module_data('phase1_core', test_data)
        self.assertTrue(result)

        # Get data
        retrieved_data = self.integration.get_module_data('phase1_core')
        self.assertEqual(retrieved_data['length'], 3200)
        self.assertEqual(retrieved_data['width'], 2100)

    def test_invalid_module_name(self):
        """Test handling of invalid module names"""
        result = self.integration.set_module_data('invalid_module', {})
        self.assertFalse(result)

        data = self.integration.get_module_data('invalid_module')
        self.assertEqual(data, {})

    def test_collect_all_data(self):
        """Test collecting data from all modules"""
        # Set some data
        self.integration.set_module_data('phase1_core', {'test': 'data1'})
        self.integration.set_module_data('phase2_uv', {'test': 'data2'})

        all_data = self.integration.collect_all_data()

        self.assertIn('timestamp', all_data)
        self.assertIn('modules', all_data)
        self.assertEqual(len(all_data['modules']), 9)

    def test_validate_data_consistency(self):
        """Test data consistency validation"""
        validation_result = self.integration.validate_data_consistency()

        self.assertIn('valid', validation_result)
        self.assertIn('errors', validation_result)
        self.assertIn('warnings', validation_result)

    def test_resolve_dependencies(self):
        """Test dependency resolution"""
        execution_order = self.integration.resolve_dependencies()

        self.assertIsInstance(execution_order, list)
        self.assertGreater(len(execution_order), 0)

        # Check that phase1_core comes before phase2_uv (which depends on it)
        if 'phase2_uv' in self.integration.dependencies:
            phase1_index = execution_order.index('phase1_core')
            phase2_index = execution_order.index('phase2_uv')
            self.assertLess(phase1_index, phase2_index)

    def test_propagate_changes(self):
        """Test change propagation"""
        # Set data for a module
        self.integration.set_module_data('phase1_core', {'test': 'data'})

        # Check that dependent modules are marked for update
        dependent = self.integration._get_dependent_modules('phase1_core')

        for module in dependent:
            if module in self.integration.modules:
                self.assertTrue(
                    self.integration.modules[module].get('needs_update', False)
                )

    def test_session_state_save_load(self):
        """Test saving and loading session state"""
        # Set some data
        test_data = {'test_key': 'test_value'}
        self.integration.set_module_data('phase1_core', test_data)

        # Save state
        temp_file = 'tests/temp_session_state.json'
        result = self.integration.save_session_state(temp_file)
        self.assertTrue(result)

        # Create new integration layer and load state
        new_integration = IntegrationLayer()
        load_result = new_integration.load_session_state(temp_file)
        self.assertTrue(load_result)

        # Verify data
        loaded_data = new_integration.get_module_data('phase1_core')
        self.assertEqual(loaded_data.get('test_key'), 'test_value')

        # Cleanup
        Path(temp_file).unlink(missing_ok=True)

    def test_reset_to_defaults(self):
        """Test resetting to default state"""
        # Set some data
        self.integration.set_module_data('phase1_core', {'test': 'data'})

        # Reset
        self.integration.reset_to_defaults()

        # Verify reset
        for module_id, module_info in self.integration.modules.items():
            self.assertEqual(module_info['data'], {})
            self.assertFalse(module_info['initialized'])

    def test_get_module_status(self):
        """Test getting module status"""
        status = self.integration.get_module_status()

        self.assertIn('total_modules', status)
        self.assertIn('initialized_modules', status)
        self.assertIn('modules_needing_update', status)
        self.assertIn('module_details', status)

        self.assertEqual(status['total_modules'], 9)

    def test_export_module_data(self):
        """Test exporting module data"""
        # Set data
        test_data = {'test_key': 'test_value'}
        self.integration.set_module_data('phase1_core', test_data)

        # Export
        temp_file = 'tests/temp_export.json'
        result = self.integration.export_module_data('phase1_core', temp_file)
        self.assertTrue(result)

        # Verify file exists
        self.assertTrue(Path(temp_file).exists())

        # Cleanup
        Path(temp_file).unlink(missing_ok=True)


if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    Path('tests').mkdir(exist_ok=True)

    unittest.main()
