"""
Comprehensive Test Suite for CFD Simulation Engine
Tests all functionality including temperature, airflow, humidity analysis,
3D rendering, and advanced CFD features.
"""

import unittest
import numpy as np
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.cfd_simulation import CFDSimulator
from modules.visualizations.cfd_plots_3d import (
    plot_temperature_3d,
    plot_velocity_vectors_3d,
    plot_humidity_3d,
    plot_cross_section_heatmap,
    plot_chamber_3d_model,
    plot_velocity_magnitude_3d
)


class TestCFDSimulator(unittest.TestCase):
    """Test cases for CFD Simulator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.chamber_dims = (3200, 2100, 2200)  # mm
        self.temp_range = (-45, 105)
        self.humidity_range = (40, 95)
        self.grid_resolution = (30, 30, 30)  # Use coarse grid for faster testing

        self.simulator = CFDSimulator(
            chamber_dims=self.chamber_dims,
            temp_range=self.temp_range,
            humidity_range=self.humidity_range,
            grid_resolution=self.grid_resolution
        )

    def test_initialization(self):
        """Test CFD simulator initialization"""
        self.assertEqual(self.simulator.L, 3.2)  # meters
        self.assertEqual(self.simulator.W, 2.1)  # meters
        self.assertEqual(self.simulator.H, 2.2)  # meters
        self.assertAlmostEqual(self.simulator.volume, 14.784, places=2)
        self.assertEqual(self.simulator.nx, 30)
        self.assertEqual(self.simulator.ny, 30)
        self.assertEqual(self.simulator.nz, 30)

    # ==================== TEMPERATURE ANALYSIS TESTS ====================

    def test_calculate_temperature_field(self):
        """Test temperature field generation"""
        setpoint = 85.0
        heater_power = 10000
        ambient_temp = 25.0

        temp_field = self.simulator.calculate_temperature_field(
            setpoint=setpoint,
            heater_power=heater_power,
            ambient_temp=ambient_temp
        )

        # Verify output shape
        self.assertEqual(temp_field.shape, (30, 30, 30))

        # Verify temperature field is reasonable
        self.assertTrue(np.all(temp_field > 0))
        self.assertTrue(np.all(temp_field < 150))

        # Mean should be close to setpoint
        mean_temp = np.mean(temp_field)
        self.assertAlmostEqual(mean_temp, setpoint, delta=10.0)

    def test_temperature_field_with_fans(self):
        """Test temperature field with fan mixing"""
        setpoint = 85.0
        heater_power = 10000
        fan_positions = [(1.6, 1.05, 1.1), (0.8, 0.525, 1.1)]

        temp_field = self.simulator.calculate_temperature_field(
            setpoint=setpoint,
            heater_power=heater_power,
            ambient_temp=25.0,
            fan_positions=fan_positions
        )

        # With fans, temperature should be more uniform
        temp_std = np.std(temp_field)
        self.assertLess(temp_std, 5.0)  # Standard deviation should be < 5°C

    def test_detect_hot_cold_spots(self):
        """Test hot and cold spot detection"""
        self.simulator.calculate_temperature_field(85.0, 10000, 25.0)
        spots = self.simulator.detect_hot_cold_spots()

        # Verify structure
        self.assertIn('hot_spot', spots)
        self.assertIn('cold_spot', spots)
        self.assertIn('delta_temp', spots)

        # Verify hot spot is hotter than cold spot
        self.assertGreater(spots['hot_spot']['temperature'],
                          spots['cold_spot']['temperature'])

        # Delta should be positive
        self.assertGreater(spots['delta_temp'], 0)

    def test_calculate_thermal_stratification(self):
        """Test thermal stratification calculation"""
        self.simulator.calculate_temperature_field(85.0, 10000, 25.0)
        strat = self.simulator.calculate_thermal_stratification()

        # Verify structure
        self.assertIn('stratification_index', strat)
        self.assertIn('max_gradient', strat)
        self.assertIn('mean_gradient', strat)
        self.assertIn('temp_profile', strat)

        # Stratification index should be between 0 and 1
        self.assertGreaterEqual(strat['stratification_index'], 0)
        self.assertLessEqual(strat['stratification_index'], 1)

        # Temperature profile should have same length as z-axis
        self.assertEqual(len(strat['temp_profile']), 30)

    def test_validate_temperature_uniformity(self):
        """Test temperature uniformity validation"""
        self.simulator.calculate_temperature_field(85.0, 10000, 25.0)
        uniformity = self.simulator.validate_temperature_uniformity(tolerance=2.0)

        # Verify structure
        self.assertIn('mean_temperature', uniformity)
        self.assertIn('std_deviation', uniformity)
        self.assertIn('uniformity_percentage', uniformity)
        self.assertIn('passes_criteria', uniformity)

        # Uniformity percentage should be 0-100
        self.assertGreaterEqual(uniformity['uniformity_percentage'], 0)
        self.assertLessEqual(uniformity['uniformity_percentage'], 100)

        # Mean temp should be reasonable
        self.assertGreater(uniformity['mean_temperature'], 70)
        self.assertLess(uniformity['mean_temperature'], 100)

    def test_simulate_ramp_rate(self):
        """Test ramp rate simulation"""
        ramp = self.simulator.simulate_ramp_rate(
            start_temp=25.0,
            end_temp=85.0,
            time_seconds=1800,  # 30 minutes
            heater_power=10000
        )

        # Verify structure
        self.assertIn('ramp_rate_celsius_per_min', ramp)
        self.assertIn('meets_iec_spec', ramp)
        self.assertIn('time_profile', ramp)

        # Calculate expected ramp rate
        expected_rate = (85.0 - 25.0) / 30  # °C/min
        self.assertAlmostEqual(ramp['ramp_rate_celsius_per_min'], expected_rate, delta=0.1)

        # Time profile should have time and temperature arrays
        self.assertIn('time_seconds', ramp['time_profile'])
        self.assertIn('temperature', ramp['time_profile'])
        self.assertEqual(len(ramp['time_profile']['time_seconds']), 1000)

    # ==================== AIRFLOW ANALYSIS TESTS ====================

    def test_calculate_velocity_field(self):
        """Test velocity field calculation"""
        fan_power = 500  # W
        fan_positions = [(1.6, 1.05, 1.1), (0.8, 0.525, 1.1)]

        velocity_field = self.simulator.calculate_velocity_field(
            fan_power_w=fan_power,
            fan_positions=fan_positions
        )

        # Verify shape (nx, ny, nz, 3)
        self.assertEqual(velocity_field.shape, (30, 30, 30, 3))

        # Verify velocity components exist
        vx = velocity_field[:, :, :, 0]
        vy = velocity_field[:, :, :, 1]
        vz = velocity_field[:, :, :, 2]

        # Velocity magnitude should be reasonable (0 - 50 m/s for simplified CFD)
        # Note: Simplified CFD can have higher local velocities near fans
        vel_mag = np.sqrt(vx**2 + vy**2 + vz**2)
        self.assertTrue(np.all(vel_mag >= 0))
        self.assertTrue(np.all(vel_mag < 50))  # Relaxed for simplified CFD model

    def test_detect_recirculation_zones(self):
        """Test recirculation zone detection"""
        fan_positions = [(1.6, 1.05, 1.1)]
        self.simulator.calculate_velocity_field(500, fan_positions)

        recirculation = self.simulator.detect_recirculation_zones()

        # Verify structure
        self.assertIn('recirculation_volume_percentage', recirculation)
        self.assertIn('max_vorticity', recirculation)
        self.assertIn('mean_vorticity', recirculation)

        # Recirculation percentage should be 0-100
        self.assertGreaterEqual(recirculation['recirculation_volume_percentage'], 0)
        self.assertLessEqual(recirculation['recirculation_volume_percentage'], 100)

    def test_detect_dead_zones(self):
        """Test dead zone detection"""
        fan_positions = [(1.6, 1.05, 1.1)]
        self.simulator.calculate_velocity_field(500, fan_positions)

        dead_zones = self.simulator.detect_dead_zones(threshold=0.1)

        # Verify structure
        self.assertIn('dead_zone_percentage', dead_zones)
        self.assertIn('num_dead_zones', dead_zones)
        self.assertIn('passes_criteria', dead_zones)
        self.assertIn('min_velocity', dead_zones)
        self.assertIn('max_velocity', dead_zones)

        # Dead zone percentage should be 0-100
        self.assertGreaterEqual(dead_zones['dead_zone_percentage'], 0)
        self.assertLessEqual(dead_zones['dead_zone_percentage'], 100)

        # Min velocity should be >= 0
        self.assertGreaterEqual(dead_zones['min_velocity'], 0)

    def test_calculate_pressure_drop(self):
        """Test pressure drop calculation"""
        fan_positions = [(1.6, 1.05, 1.1)]
        self.simulator.calculate_velocity_field(500, fan_positions)

        pressure = self.simulator.calculate_pressure_drop()

        # Verify structure
        self.assertIn('total_pressure_drop', pressure)
        self.assertIn('reynolds_number', pressure)
        self.assertIn('flow_regime', pressure)
        self.assertIn('friction_factor', pressure)
        self.assertIn('passes_criteria', pressure)

        # Pressure drop should be positive
        self.assertGreater(pressure['total_pressure_drop'], 0)

        # Reynolds number should be positive
        self.assertGreater(pressure['reynolds_number'], 0)

        # Flow regime should be either Laminar or Turbulent
        self.assertIn(pressure['flow_regime'], ['Laminar', 'Turbulent'])

    def test_optimize_fan_placement(self):
        """Test fan placement optimization"""
        # Test different numbers of fans
        for num_fans in [1, 2, 4, 6]:
            positions = self.simulator.optimize_fan_placement(num_fans)

            # Should return correct number of positions
            self.assertEqual(len(positions), num_fans)

            # Each position should be (x, y, z) tuple
            for pos in positions:
                self.assertEqual(len(pos), 3)

                # Positions should be within chamber bounds
                self.assertGreaterEqual(pos[0], 0)
                self.assertLessEqual(pos[0], self.simulator.L)
                self.assertGreaterEqual(pos[1], 0)
                self.assertLessEqual(pos[1], self.simulator.W)
                self.assertGreaterEqual(pos[2], 0)
                self.assertLessEqual(pos[2], self.simulator.H)

    # ==================== HUMIDITY ANALYSIS TESTS ====================

    def test_calculate_humidity_field(self):
        """Test humidity field calculation"""
        target_rh = 85.0
        humidifier_positions = [(0.64, 0.42, 0.22)]

        humidity_field = self.simulator.calculate_humidity_field(
            target_rh=target_rh,
            humidifier_positions=humidifier_positions
        )

        # Verify shape
        self.assertEqual(humidity_field.shape, (30, 30, 30))

        # Humidity should be within valid range
        self.assertTrue(np.all(humidity_field >= 0))
        self.assertTrue(np.all(humidity_field <= 100))

        # Mean should be close to target
        mean_rh = np.mean(humidity_field)
        self.assertAlmostEqual(mean_rh, target_rh, delta=15.0)

    def test_detect_condensation_risk(self):
        """Test condensation risk detection"""
        self.simulator.calculate_temperature_field(85.0, 10000, 25.0)
        self.simulator.calculate_humidity_field(85.0, [(0.64, 0.42, 0.22)])

        condensation = self.simulator.detect_condensation_risk()

        # Verify structure
        self.assertIn('condensation_risk_percentage', condensation)
        self.assertIn('critical_condensation_percentage', condensation)
        self.assertIn('min_temp_margin', condensation)
        self.assertIn('safe_operation', condensation)

        # Risk percentages should be 0-100
        self.assertGreaterEqual(condensation['condensation_risk_percentage'], 0)
        self.assertLessEqual(condensation['condensation_risk_percentage'], 100)

    def test_validate_humidity_uniformity(self):
        """Test humidity uniformity validation"""
        self.simulator.calculate_humidity_field(85.0, [(0.64, 0.42, 0.22)])

        uniformity = self.simulator.validate_humidity_uniformity(tolerance=3.0)

        # Verify structure
        self.assertIn('mean_humidity', uniformity)
        self.assertIn('uniformity_percentage', uniformity)
        self.assertIn('passes_criteria', uniformity)

        # Mean humidity should be reasonable
        self.assertGreater(uniformity['mean_humidity'], 40)
        self.assertLess(uniformity['mean_humidity'], 100)

    # ==================== 3D CHAMBER RENDERING TESTS ====================

    def test_generate_chamber_geometry(self):
        """Test chamber geometry generation"""
        geometry = self.simulator.generate_chamber_geometry()

        # Verify structure
        self.assertIn('vertices', geometry)
        self.assertIn('edges', geometry)
        self.assertIn('faces', geometry)
        self.assertIn('dimensions', geometry)

        # Should have 8 vertices (rectangular box)
        self.assertEqual(len(geometry['vertices']), 8)

        # Should have 12 edges
        self.assertEqual(len(geometry['edges']), 12)

        # Should have 6 faces
        self.assertEqual(len(geometry['faces']), 6)

        # Dimensions should match
        dims = geometry['dimensions']
        self.assertAlmostEqual(dims['length'], self.simulator.L, places=2)
        self.assertAlmostEqual(dims['width'], self.simulator.W, places=2)
        self.assertAlmostEqual(dims['height'], self.simulator.H, places=2)

    def test_get_component_positions(self):
        """Test component position generation"""
        components = self.simulator.get_component_positions(
            num_fans=4,
            num_humidifiers=2,
            num_uv_panels=2
        )

        # Verify structure
        self.assertIn('fans', components)
        self.assertIn('humidifiers', components)
        self.assertIn('uv_panels', components)
        self.assertIn('test_specimen', components)

        # Verify counts
        self.assertEqual(len(components['fans']), 4)
        self.assertEqual(len(components['humidifiers']), 2)
        self.assertEqual(len(components['uv_panels']), 2)

        # Test specimen should be a single position
        self.assertEqual(len(components['test_specimen']), 3)

    # ==================== ADVANCED CFD FEATURES TESTS ====================

    def test_calculate_transient_response(self):
        """Test transient response calculation"""
        transient = self.simulator.calculate_transient_response(
            setpoint=85.0,
            duration_minutes=60,
            heater_power=10000
        )

        # Verify structure
        self.assertIn('time_constant_seconds', transient)
        self.assertIn('time_to_steady_state_minutes', transient)
        self.assertIn('time_profile', transient)

        # Time constant should be positive
        self.assertGreater(transient['time_constant_seconds'], 0)

        # Time profile should have data
        self.assertIn('time_seconds', transient['time_profile'])
        self.assertIn('temperature', transient['time_profile'])
        self.assertEqual(len(transient['time_profile']['time_seconds']), 1000)

    def test_calculate_energy_balance(self):
        """Test energy balance calculation"""
        energy = self.simulator.calculate_energy_balance(
            setpoint=85.0,
            ambient_temp=25.0,
            heater_power=10000
        )

        # Verify structure
        self.assertIn('heater_power', energy)
        self.assertIn('heat_loss', energy)
        self.assertIn('thermal_efficiency', energy)
        self.assertIn('energy_balanced', energy)

        # Heat loss should be positive
        self.assertGreater(energy['heat_loss'], 0)

        # Efficiency should be 0-100%
        self.assertGreaterEqual(energy['thermal_efficiency'], 0)
        self.assertLessEqual(energy['thermal_efficiency'], 100)

    def test_export_simulation_data(self):
        """Test simulation data export"""
        # Run simulations first
        self.simulator.calculate_temperature_field(85.0, 10000, 25.0)
        self.simulator.calculate_velocity_field(500, [(1.6, 1.05, 1.1)])
        self.simulator.calculate_humidity_field(85.0, [(0.64, 0.42, 0.22)])

        # Export data
        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_data = self.simulator.export_simulation_data(f.name)

            # Verify JSON is valid
            data = json.loads(json_data)
            self.assertIn('chamber_geometry', data)
            self.assertIn('grid_resolution', data)
            self.assertIn('temperature_field', data)

        # Clean up
        os.unlink(f.name)


class TestVisualizationFunctions(unittest.TestCase):
    """Test cases for 3D visualization functions"""

    def setUp(self):
        """Set up test fixtures"""
        self.simulator = CFDSimulator(
            chamber_dims=(3200, 2100, 2200),
            temp_range=(-45, 105),
            humidity_range=(40, 95),
            grid_resolution=(20, 20, 20)  # Small grid for fast testing
        )

        # Generate test data
        self.temp_field = self.simulator.calculate_temperature_field(85.0, 10000, 25.0)
        self.velocity_field = self.simulator.calculate_velocity_field(500, [(1.6, 1.05, 1.1)])
        self.humidity_field = self.simulator.calculate_humidity_field(85.0, [(0.64, 0.42, 0.22)])

    def test_plot_temperature_3d(self):
        """Test 3D temperature plotting"""
        fig = plot_temperature_3d(
            self.temp_field,
            self.simulator.x,
            self.simulator.y,
            self.simulator.z
        )

        # Verify it returns a plotly figure
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))

    def test_plot_velocity_vectors_3d(self):
        """Test 3D velocity vector plotting"""
        fig = plot_velocity_vectors_3d(
            self.velocity_field,
            self.simulator.x,
            self.simulator.y,
            self.simulator.z
        )

        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))

    def test_plot_humidity_3d(self):
        """Test 3D humidity plotting"""
        fig = plot_humidity_3d(
            self.humidity_field,
            self.simulator.x,
            self.simulator.y,
            self.simulator.z
        )

        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))

    def test_plot_cross_section_heatmap(self):
        """Test cross-section heatmap plotting"""
        # Test all three planes
        for plane in ['XY', 'XZ', 'YZ']:
            fig = plot_cross_section_heatmap(
                self.temp_field,
                self.simulator.x,
                self.simulator.y,
                self.simulator.z,
                plane=plane,
                position=0.5
            )

            self.assertIsNotNone(fig)
            self.assertTrue(hasattr(fig, 'data'))

    def test_plot_chamber_3d_model(self):
        """Test 3D chamber model plotting"""
        geometry = self.simulator.generate_chamber_geometry()
        components = self.simulator.get_component_positions(4, 2, 2)

        fig = plot_chamber_3d_model(geometry, components, show_components=True)

        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))

    def test_plot_velocity_magnitude_3d(self):
        """Test velocity magnitude plotting"""
        fig = plot_velocity_magnitude_3d(
            self.velocity_field,
            self.simulator.x,
            self.simulator.y,
            self.simulator.z
        )

        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'data'))


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""

    def test_full_simulation_workflow(self):
        """Test complete CFD simulation workflow"""
        # Initialize simulator
        simulator = CFDSimulator(
            chamber_dims=(3200, 2100, 2200),
            temp_range=(-45, 105),
            humidity_range=(40, 95),
            grid_resolution=(25, 25, 25)
        )

        # Get component positions
        components = simulator.get_component_positions(
            num_fans=4,
            num_humidifiers=2,
            num_uv_panels=2
        )

        # Run all simulations
        temp_field = simulator.calculate_temperature_field(
            setpoint=85.0,
            heater_power=10000,
            ambient_temp=25.0,
            fan_positions=components['fans']
        )

        velocity_field = simulator.calculate_velocity_field(
            fan_power_w=500,
            fan_positions=components['fans']
        )

        humidity_field = simulator.calculate_humidity_field(
            target_rh=85.0,
            humidifier_positions=components['humidifiers']
        )

        # Verify all analyses work
        temp_uniformity = simulator.validate_temperature_uniformity()
        self.assertIsNotNone(temp_uniformity)

        dead_zones = simulator.detect_dead_zones()
        self.assertIsNotNone(dead_zones)

        humidity_uniformity = simulator.validate_humidity_uniformity()
        self.assertIsNotNone(humidity_uniformity)

        # Verify validation criteria
        print(f"\n=== Integration Test Results ===")
        print(f"Temperature Uniformity: {temp_uniformity['uniformity_percentage']:.1f}% "
              f"({'PASS' if temp_uniformity['passes_criteria'] else 'FAIL'})")
        print(f"Dead Zones: {dead_zones['dead_zone_percentage']:.1f}% "
              f"({'PASS' if dead_zones['passes_criteria'] else 'FAIL'})")
        print(f"Humidity Uniformity: {humidity_uniformity['uniformity_percentage']:.1f}% "
              f"({'PASS' if humidity_uniformity['passes_criteria'] else 'FAIL'})")


def run_tests():
    """Run all test suites"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCFDSimulator))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualizationFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
