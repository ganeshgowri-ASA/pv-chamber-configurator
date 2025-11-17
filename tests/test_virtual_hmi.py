"""
Test Suite for Virtual HMI Module
Tests control functions, alarm management, data logging, and recipe execution
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.virtual_hmi import VirtualHMI


class TestVirtualHMI(unittest.TestCase):
    """Test cases for Virtual HMI Controller"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary database for testing
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()

        # Initialize HMI with test database
        self.hmi = VirtualHMI(db_path=self.test_db.name)

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary database
        if os.path.exists(self.test_db.name):
            os.remove(self.test_db.name)

    def test_initialization(self):
        """Test HMI initialization"""
        self.assertIsNotNone(self.hmi)
        self.assertEqual(self.hmi.chamber_state['status'], 'Idle')
        self.assertEqual(self.hmi.setpoints['temperature'], 25.0)
        self.assertEqual(self.hmi.setpoints['humidity'], 50.0)
        self.assertEqual(self.hmi.setpoints['uv_intensity'], 0.0)

    def test_set_temperature_setpoint(self):
        """Test temperature setpoint setting"""
        # Valid setpoint
        success, msg = self.hmi.set_temperature_setpoint(85.0)
        self.assertTrue(success)
        self.assertEqual(self.hmi.setpoints['temperature'], 85.0)

        # Invalid setpoint (too high)
        success, msg = self.hmi.set_temperature_setpoint(150.0)
        self.assertFalse(success)

        # Invalid setpoint (too low)
        success, msg = self.hmi.set_temperature_setpoint(-60.0)
        self.assertFalse(success)

    def test_set_humidity_setpoint(self):
        """Test humidity setpoint setting"""
        # Valid setpoint
        success, msg = self.hmi.set_humidity_setpoint(85.0)
        self.assertTrue(success)
        self.assertEqual(self.hmi.setpoints['humidity'], 85.0)

        # Invalid setpoint (too high)
        success, msg = self.hmi.set_humidity_setpoint(100.0)
        self.assertFalse(success)

        # Invalid setpoint (too low)
        success, msg = self.hmi.set_humidity_setpoint(30.0)
        self.assertFalse(success)

    def test_set_uv_intensity(self):
        """Test UV intensity setpoint setting"""
        # Valid setpoint
        success, msg = self.hmi.set_uv_intensity(60.0)
        self.assertTrue(success)
        self.assertEqual(self.hmi.setpoints['uv_intensity'], 60.0)

        # Invalid setpoint (too high)
        success, msg = self.hmi.set_uv_intensity(300.0)
        self.assertFalse(success)

        # Invalid setpoint (negative)
        success, msg = self.hmi.set_uv_intensity(-10.0)
        self.assertFalse(success)

    def test_set_ramp_rate(self):
        """Test ramp rate setting"""
        # Valid ramp rate
        success, msg = self.hmi.set_ramp_rate(3.0)
        self.assertTrue(success)
        self.assertEqual(self.hmi.setpoints['ramp_rate'], 3.0)

        # Invalid ramp rate (too high)
        success, msg = self.hmi.set_ramp_rate(10.0)
        self.assertFalse(success)

        # Invalid ramp rate (too low)
        success, msg = self.hmi.set_ramp_rate(0.1)
        self.assertFalse(success)

    def test_chamber_start_stop(self):
        """Test chamber start/stop operations"""
        # Start chamber
        success, msg = self.hmi.start_chamber()
        self.assertTrue(success)
        self.assertEqual(self.hmi.chamber_state['status'], 'Running')
        self.assertIsNotNone(self.hmi.chamber_state['start_time'])

        # Stop chamber
        success, msg = self.hmi.stop_chamber()
        self.assertTrue(success)
        self.assertEqual(self.hmi.chamber_state['status'], 'Idle')

        # Try to stop when already idle
        success, msg = self.hmi.stop_chamber()
        self.assertFalse(success)

    def test_chamber_pause(self):
        """Test chamber pause operation"""
        # Start chamber first
        self.hmi.start_chamber()

        # Pause chamber
        success, msg = self.hmi.pause_chamber()
        self.assertTrue(success)
        self.assertEqual(self.hmi.chamber_state['status'], 'Paused')

        # Try to pause when not running
        success, msg = self.hmi.pause_chamber()
        self.assertFalse(success)

    def test_emergency_stop(self):
        """Test emergency stop"""
        self.hmi.start_chamber()

        success, msg = self.hmi.emergency_stop()
        self.assertTrue(success)
        self.assertEqual(self.hmi.chamber_state['status'], 'Error')
        self.assertGreater(len(self.hmi.active_alarms), 0)

    def test_get_current_status(self):
        """Test getting current status"""
        status = self.hmi.get_current_status()

        self.assertIn('status', status)
        self.assertIn('mode', status)
        self.assertIn('temperature', status)
        self.assertIn('humidity', status)
        self.assertIn('uv_intensity', status)
        self.assertIn('power_consumption', status)

        self.assertEqual(status['status'], 'Idle')
        self.assertEqual(status['mode'], 'Manual')

    def test_get_live_data(self):
        """Test getting live data"""
        data = self.hmi.get_live_data()

        self.assertIn('timestamp', data)
        self.assertIn('temperature_grid', data)
        self.assertIn('humidity_grid', data)
        self.assertIn('uv_grid', data)
        self.assertIn('setpoints', data)

        # Check grid sizes
        self.assertEqual(len(data['temperature_grid']), 9)
        self.assertEqual(len(data['humidity_grid']), 9)
        self.assertEqual(len(data['uv_grid']), 9)

    def test_alarm_raising(self):
        """Test alarm raising"""
        initial_count = len(self.hmi.active_alarms)

        alarm_id = self.hmi.raise_alarm('WARNING', 'Test alarm')

        self.assertGreater(alarm_id, 0)
        self.assertEqual(len(self.hmi.active_alarms), initial_count + 1)

        # Check alarm properties
        alarm = self.hmi.active_alarms[-1]
        self.assertEqual(alarm['level'], 'WARNING')
        self.assertEqual(alarm['message'], 'Test alarm')
        self.assertFalse(alarm['acknowledged'])

    def test_alarm_acknowledgment(self):
        """Test alarm acknowledgment"""
        # Raise an alarm
        alarm_id = self.hmi.raise_alarm('INFO', 'Test alarm')

        # Acknowledge it
        success = self.hmi.acknowledge_alarm(alarm_id)
        self.assertTrue(success)

        # Check it's removed from active alarms
        self.assertEqual(len(self.hmi.active_alarms), 0)

        # Try to acknowledge non-existent alarm
        success = self.hmi.acknowledge_alarm(9999)
        self.assertFalse(success)

    def test_alarm_history(self):
        """Test alarm history"""
        # Raise multiple alarms
        self.hmi.raise_alarm('INFO', 'Alarm 1')
        self.hmi.raise_alarm('WARNING', 'Alarm 2')
        self.hmi.raise_alarm('CRITICAL', 'Alarm 3')

        history = self.hmi.get_alarm_history()

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['message'], 'Alarm 1')
        self.assertEqual(history[1]['message'], 'Alarm 2')
        self.assertEqual(history[2]['message'], 'Alarm 3')

    def test_data_logging(self):
        """Test data logging functionality"""
        # Log a data point
        self.hmi.log_data_point()

        # Verify it was logged to database
        stats = self.hmi.get_log_statistics(days=1)

        self.assertIsNotNone(stats)
        self.assertGreater(stats.get('total_records', 0), 0)

    def test_data_export_csv(self):
        """Test CSV data export"""
        # Log some data points
        for i in range(5):
            self.hmi.log_data_point()

        # Export data
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now()

        filepath = self.hmi.export_logs(start_date, end_date, format='csv')

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.csv'))

        # Clean up
        os.remove(filepath)

    def test_data_export_json(self):
        """Test JSON data export"""
        # Log some data points
        for i in range(5):
            self.hmi.log_data_point()

        # Export data
        start_date = datetime.now() - timedelta(hours=1)
        end_date = datetime.now()

        filepath = self.hmi.export_logs(start_date, end_date, format='json')

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.json'))

        # Clean up
        os.remove(filepath)

    def test_simulation_update(self):
        """Test simulation update"""
        # Set setpoints
        self.hmi.set_temperature_setpoint(85.0)
        self.hmi.set_humidity_setpoint(85.0)
        self.hmi.set_uv_intensity(60.0)

        # Start chamber
        self.hmi.start_chamber()

        # Run simulation
        for i in range(10):
            self.hmi.update_simulation(dt=1.0)

        # Check that values are approaching setpoints
        status = self.hmi.get_current_status()

        # Temperature should be moving towards setpoint
        self.assertNotEqual(status['temperature']['current'], 25.0)

    def test_uniformity_calculation(self):
        """Test uniformity calculation"""
        import numpy as np

        # Create test grid with known uniformity
        grid_values = np.array([100, 100, 100, 100, 100, 100, 100, 100, 110])

        uniformity = self.hmi._calculate_uniformity(grid_values)

        # Max deviation is 10 from mean ~101.1, so ~8.8%
        self.assertGreater(uniformity, 8.0)
        self.assertLess(uniformity, 10.0)

    def test_trend_chart_generation(self):
        """Test trend chart data generation"""
        # Generate trend data
        df = self.hmi.generate_trend_chart('temperature', hours=24)

        self.assertIsNotNone(df)
        self.assertFalse(df.empty)
        self.assertIn('temperature', df.columns)
        self.assertIn('timestamp', df.columns)

    def test_get_log_statistics(self):
        """Test log statistics retrieval"""
        # Log some data
        for i in range(10):
            self.hmi.log_data_point()

        stats = self.hmi.get_log_statistics(days=1)

        self.assertIsNotNone(stats)
        self.assertIn('total_records', stats)
        self.assertIn('avg_temperature', stats)
        self.assertEqual(stats['total_records'], 10)


class TestAlarmSystem(unittest.TestCase):
    """Test cases for Alarm System"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.hmi = VirtualHMI(db_path=self.test_db.name)

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_db.name):
            os.remove(self.test_db.name)

    def test_critical_alarm_changes_status(self):
        """Test that critical alarms change chamber status"""
        self.hmi.start_chamber()
        self.assertEqual(self.hmi.chamber_state['status'], 'Running')

        # Raise critical alarm
        self.hmi.raise_alarm('CRITICAL', 'Critical issue')

        self.assertEqual(self.hmi.chamber_state['status'], 'Alarm')

    def test_alarm_priority_levels(self):
        """Test different alarm priority levels"""
        # Raise alarms of different levels
        id1 = self.hmi.raise_alarm('INFO', 'Info alarm')
        id2 = self.hmi.raise_alarm('WARNING', 'Warning alarm')
        id3 = self.hmi.raise_alarm('CRITICAL', 'Critical alarm')

        self.assertEqual(len(self.hmi.active_alarms), 3)

        # Check alarm levels
        levels = [a['level'] for a in self.hmi.active_alarms]
        self.assertIn('INFO', levels)
        self.assertIn('WARNING', levels)
        self.assertIn('CRITICAL', levels)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestVirtualHMI))
    suite.addTests(loader.loadTestsFromTestCase(TestAlarmSystem))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
