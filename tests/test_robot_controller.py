"""
Test Suite for Robot Controller Module
Tests movement commands, 9-point measurement, G-code parsing, and uniformity calculation
"""

import unittest
import os
import sys
import tempfile
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.robot_controller import UniformityRobot


class TestRobotController(unittest.TestCase):
    """Test cases for Uniformity Robot Controller"""

    def setUp(self):
        """Set up test fixtures"""
        self.robot = UniformityRobot()

    def test_initialization(self):
        """Test robot initialization"""
        self.assertIsNotNone(self.robot)
        self.assertEqual(self.robot.current_position['x'], 0)
        self.assertEqual(self.robot.current_position['y'], 0)
        self.assertEqual(self.robot.current_position['z'], 0)
        self.assertFalse(self.robot.is_homed)
        self.assertEqual(self.robot.status, "Idle")

    def test_workspace_dimensions(self):
        """Test workspace dimension settings"""
        custom_dims = {'x': 2000, 'y': 1500, 'z': 1000}
        robot = UniformityRobot(workspace_dims=custom_dims)

        self.assertEqual(robot.workspace_dims['x'], 2000)
        self.assertEqual(robot.workspace_dims['y'], 1500)
        self.assertEqual(robot.workspace_dims['z'], 1000)

    def test_homing(self):
        """Test robot homing"""
        # Move to some position first
        self.robot.current_position = {'x': 100, 'y': 200, 'z': 300}

        # Home the robot
        success = self.robot.home_axes()

        self.assertTrue(success)
        self.assertTrue(self.robot.is_homed)
        self.assertEqual(self.robot.current_position['x'], 0)
        self.assertEqual(self.robot.current_position['y'], 0)
        self.assertEqual(self.robot.current_position['z'], 0)
        self.assertEqual(self.robot.status, "Idle")

    def test_check_limits_valid(self):
        """Test limit checking with valid positions"""
        # Test valid positions
        is_valid, msg = self.robot.check_limits(1500, 1000, 750)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

        # Test boundary positions
        is_valid, msg = self.robot.check_limits(0, 0, 0)
        self.assertTrue(is_valid)

        is_valid, msg = self.robot.check_limits(3000, 2000, 1500)
        self.assertTrue(is_valid)

    def test_check_limits_invalid(self):
        """Test limit checking with invalid positions"""
        # Test out of bounds X
        is_valid, msg = self.robot.check_limits(-10, 1000, 750)
        self.assertFalse(is_valid)
        self.assertIn("X position", msg)

        is_valid, msg = self.robot.check_limits(3500, 1000, 750)
        self.assertFalse(is_valid)
        self.assertIn("X position", msg)

        # Test out of bounds Y
        is_valid, msg = self.robot.check_limits(1500, -10, 750)
        self.assertFalse(is_valid)
        self.assertIn("Y position", msg)

        # Test out of bounds Z
        is_valid, msg = self.robot.check_limits(1500, 1000, 2000)
        self.assertFalse(is_valid)
        self.assertIn("Z position", msg)

    def test_move_to_position_valid(self):
        """Test valid movement to position"""
        # Home first
        self.robot.home_axes()

        # Move to valid position
        success = self.robot.move_to_position(1500, 1000, 750)

        self.assertTrue(success)
        self.assertEqual(self.robot.current_position['x'], 1500)
        self.assertEqual(self.robot.current_position['y'], 1000)
        self.assertEqual(self.robot.current_position['z'], 750)

    def test_move_to_position_not_homed(self):
        """Test movement without homing"""
        # Don't home the robot
        success = self.robot.move_to_position(1500, 1000, 750)

        self.assertFalse(success)
        self.assertEqual(self.robot.status, "Error")

    def test_move_to_position_out_of_bounds(self):
        """Test movement to out of bounds position"""
        self.robot.home_axes()

        success = self.robot.move_to_position(5000, 1000, 750)

        self.assertFalse(success)
        self.assertEqual(self.robot.status, "Error")

    def test_jog_positive(self):
        """Test positive jog movements"""
        self.robot.home_axes()

        # Jog in positive X
        success = self.robot.jog('x', 100)
        self.assertTrue(success)
        self.assertEqual(self.robot.current_position['x'], 100)

        # Jog in positive Y
        success = self.robot.jog('y', 200)
        self.assertTrue(success)
        self.assertEqual(self.robot.current_position['y'], 200)

        # Jog in positive Z
        success = self.robot.jog('z', 300)
        self.assertTrue(success)
        self.assertEqual(self.robot.current_position['z'], 300)

    def test_jog_negative(self):
        """Test negative jog movements"""
        self.robot.home_axes()

        # Move to center first
        self.robot.move_to_position(1500, 1000, 750)

        # Jog in negative X
        success = self.robot.jog('x', -100)
        self.assertTrue(success)
        self.assertEqual(self.robot.current_position['x'], 1400)

        # Jog in negative Y
        success = self.robot.jog('y', -200)
        self.assertTrue(success)
        self.assertEqual(self.robot.current_position['y'], 800)

    def test_jog_invalid_axis(self):
        """Test jog with invalid axis"""
        self.robot.home_axes()

        success = self.robot.jog('invalid', 100)
        self.assertFalse(success)

    def test_get_current_position(self):
        """Test getting current position"""
        self.robot.home_axes()
        self.robot.move_to_position(1500, 1000, 750)

        position = self.robot.get_current_position()

        self.assertEqual(position['x'], 1500)
        self.assertEqual(position['y'], 1000)
        self.assertEqual(position['z'], 750)

        # Ensure it returns a copy, not reference
        position['x'] = 9999
        self.assertEqual(self.robot.current_position['x'], 1500)

    def test_measure_at_point(self):
        """Test measurement at a point"""
        self.robot.home_axes()

        measurement = self.robot.measure_at_point(1500, 1000, 750)

        self.assertIsNotNone(measurement)
        self.assertEqual(measurement['x'], 1500)
        self.assertEqual(measurement['y'], 1000)
        self.assertEqual(measurement['z'], 750)
        self.assertIn('temperature', measurement)
        self.assertIn('humidity', measurement)
        self.assertIn('uv_intensity', measurement)
        self.assertIn('timestamp', measurement)

    def test_generate_grid_path(self):
        """Test grid path generation"""
        waypoints = self.robot.generate_grid_path(grid_size=3, z_height=750)

        # Should generate 9 points for 3x3 grid
        self.assertEqual(len(waypoints), 9)

        # All points should have same Z
        for wp in waypoints:
            self.assertEqual(wp['z'], 750)

        # Check that points cover the workspace with margin
        x_coords = [wp['x'] for wp in waypoints]
        y_coords = [wp['y'] for wp in waypoints]

        self.assertGreater(min(x_coords), 0)  # Should have margin
        self.assertLess(max(x_coords), self.robot.workspace_dims['x'])

    def test_calculate_uniformity(self):
        """Test uniformity calculation"""
        # Create test measurements
        measurements = [
            {'temperature': 85.0, 'humidity': 85.0, 'uv_intensity': 60.0},
            {'temperature': 85.5, 'humidity': 84.0, 'uv_intensity': 61.0},
            {'temperature': 84.5, 'humidity': 86.0, 'uv_intensity': 59.0},
            {'temperature': 85.0, 'humidity': 85.0, 'uv_intensity': 60.0},
            {'temperature': 85.2, 'humidity': 85.5, 'uv_intensity': 60.5},
            {'temperature': 84.8, 'humidity': 84.5, 'uv_intensity': 59.5},
            {'temperature': 85.0, 'humidity': 85.0, 'uv_intensity': 60.0},
            {'temperature': 85.3, 'humidity': 85.2, 'uv_intensity': 60.2},
            {'temperature': 84.7, 'humidity': 84.8, 'uv_intensity': 59.8},
        ]

        uniformity = self.robot.calculate_uniformity(measurements)

        self.assertIn('temperature', uniformity)
        self.assertIn('humidity', uniformity)
        self.assertIn('uv_intensity', uniformity)

        # Check temperature uniformity structure
        self.assertIn('mean', uniformity['temperature'])
        self.assertIn('std', uniformity['temperature'])
        self.assertIn('min', uniformity['temperature'])
        self.assertIn('max', uniformity['temperature'])
        self.assertIn('uniformity_percent', uniformity['temperature'])

        # Mean should be approximately 85
        self.assertAlmostEqual(uniformity['temperature']['mean'], 85.0, delta=0.5)

        # Uniformity should be small (good uniformity)
        self.assertLess(uniformity['temperature']['uniformity_percent'], 2.0)

    def test_measure_9_point_grid(self):
        """Test 9-point grid measurement sequence"""
        self.robot.home_axes()

        result = self.robot.measure_9_point_grid(z_height=750)

        self.assertIn('timestamp', result)
        self.assertIn('duration', result)
        self.assertIn('measurements', result)
        self.assertIn('uniformity', result)
        self.assertIn('grid_size', result)

        # Should have 9 measurements
        self.assertEqual(len(result['measurements']), 9)
        self.assertEqual(result['grid_size'], 3)

        # Duration should be positive
        self.assertGreater(result['duration'], 0)

        # Check uniformity was calculated
        self.assertIn('temperature', result['uniformity'])
        self.assertIn('humidity', result['uniformity'])
        self.assertIn('uv_intensity', result['uniformity'])

    def test_parse_gcode_basic(self):
        """Test G-code parsing"""
        # Create temporary G-code file
        gcode_content = """
G28 ; Home all axes
G0 X1500 Y1000 Z750 F500 ; Move to position
M3 ; Start measurement
G1 X1600 Y1100 Z750 ; Move while measuring
M5 ; Stop measurement
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.gcode') as f:
            f.write(gcode_content)
            gcode_file = f.name

        try:
            commands = self.robot.parse_gcode(gcode_file)

            self.assertGreater(len(commands), 0)

            # Check first command is home
            self.assertEqual(commands[0]['type'], 'home')

            # Check move commands
            move_commands = [c for c in commands if c['type'] == 'move']
            self.assertGreater(len(move_commands), 0)

            # Check measure commands
            measure_start = [c for c in commands if c['type'] == 'measure_start']
            self.assertEqual(len(measure_start), 1)

        finally:
            os.remove(gcode_file)

    def test_parse_gcode_with_comments(self):
        """Test G-code parsing with comments"""
        gcode_content = """
; This is a comment
G28 ; Home all axes
; Another comment
G0 X1500 Y1000 Z750 ; Move to center
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.gcode') as f:
            f.write(gcode_content)
            gcode_file = f.name

        try:
            commands = self.robot.parse_gcode(gcode_file)

            # Should only have 2 commands (comments ignored)
            self.assertEqual(len(commands), 2)

        finally:
            os.remove(gcode_file)

    def test_execute_gcode(self):
        """Test G-code execution"""
        commands = [
            {'type': 'home', 'line': 1},
            {'type': 'move', 'x': 1500, 'y': 1000, 'z': 750, 'line': 2}
        ]

        success = self.robot.execute_gcode(commands)

        self.assertTrue(success)
        self.assertEqual(self.robot.current_position['x'], 1500)
        self.assertEqual(self.robot.current_position['y'], 1000)
        self.assertEqual(self.robot.current_position['z'], 750)

    def test_get_robot_status(self):
        """Test getting robot status"""
        self.robot.home_axes()

        status = self.robot.get_robot_status()

        self.assertIn('position', status)
        self.assertIn('status', status)
        self.assertIn('is_homed', status)
        self.assertIn('emergency_stop', status)
        self.assertIn('workspace', status)
        self.assertIn('total_measurements', status)

        self.assertTrue(status['is_homed'])
        self.assertFalse(status['emergency_stop'])
        self.assertEqual(status['status'], 'Idle')

    def test_estimate_completion_time(self):
        """Test completion time estimation"""
        path = self.robot.generate_grid_path(grid_size=3, z_height=750)

        estimated_time = self.robot.estimate_completion_time(path)

        # Should be positive
        self.assertGreater(estimated_time, 0)

        # Should be reasonable (not too large)
        self.assertLess(estimated_time, 1000)

    def test_emergency_stop(self):
        """Test emergency stop"""
        self.robot.home_axes()
        self.robot.emergency_stop()

        self.assertTrue(self.robot.emergency_stop_active)
        self.assertEqual(self.robot.status, "Error")

        # Should not be able to move after e-stop
        success = self.robot.move_to_position(1500, 1000, 750)
        self.assertFalse(success)

    def test_reset_emergency_stop(self):
        """Test emergency stop reset"""
        self.robot.home_axes()
        self.robot.emergency_stop()

        # Reset e-stop
        self.robot.reset_emergency_stop()

        self.assertFalse(self.robot.emergency_stop_active)
        self.assertEqual(self.robot.status, "Idle")

        # Should be able to move after reset
        success = self.robot.move_to_position(1500, 1000, 750)
        self.assertTrue(success)

    def test_export_measurements_csv(self):
        """Test measurement export to CSV"""
        self.robot.home_axes()

        # Perform a measurement
        self.robot.measure_9_point_grid()

        # Export to CSV
        csv_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        csv_file.close()

        try:
            self.robot.export_measurements(csv_file.name, format='csv')

            self.assertTrue(os.path.exists(csv_file.name))
            self.assertGreater(os.path.getsize(csv_file.name), 0)

        finally:
            os.remove(csv_file.name)

    def test_export_measurements_json(self):
        """Test measurement export to JSON"""
        self.robot.home_axes()

        # Perform a measurement
        self.robot.measure_9_point_grid()

        # Export to JSON
        json_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        json_file.close()

        try:
            self.robot.export_measurements(json_file.name, format='json')

            self.assertTrue(os.path.exists(json_file.name))
            self.assertGreater(os.path.getsize(json_file.name), 0)

        finally:
            os.remove(json_file.name)

    def test_measurement_history(self):
        """Test measurement history tracking"""
        self.robot.home_axes()

        initial_count = len(self.robot.measurement_history)

        # Perform multiple measurements
        self.robot.measure_9_point_grid()
        self.robot.measure_9_point_grid()

        # Should have 2 more measurements in history
        self.assertEqual(len(self.robot.measurement_history), initial_count + 2)


class TestGridGeneration(unittest.TestCase):
    """Test cases for grid path generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.robot = UniformityRobot()

    def test_grid_3x3(self):
        """Test 3x3 grid generation"""
        waypoints = self.robot.generate_grid_path(grid_size=3)
        self.assertEqual(len(waypoints), 9)

    def test_grid_5x5(self):
        """Test 5x5 grid generation"""
        waypoints = self.robot.generate_grid_path(grid_size=5)
        self.assertEqual(len(waypoints), 25)

    def test_grid_margin(self):
        """Test that grid has margin from edges"""
        waypoints = self.robot.generate_grid_path(grid_size=3)

        x_coords = [wp['x'] for wp in waypoints]
        y_coords = [wp['y'] for wp in waypoints]

        # Check minimum values have margin
        margin_x = self.robot.workspace_dims['x'] * 0.1
        margin_y = self.robot.workspace_dims['y'] * 0.1

        self.assertGreaterEqual(min(x_coords), margin_x - 1)  # Allow small tolerance
        self.assertGreaterEqual(min(y_coords), margin_y - 1)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestRobotController))
    suite.addTests(loader.loadTestsFromTestCase(TestGridGeneration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
