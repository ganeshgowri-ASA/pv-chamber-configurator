"""
Uniformity Robot Controller Module
Handles 3-axis gantry robot for environmental chamber uniformity measurements
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Tuple, List, Dict, Optional
import json
import time


class UniformityRobot:
    """
    3-Axis Gantry Robot Controller for Chamber Uniformity Measurements

    Specifications:
    - Travel: X=3000mm, Y=2000mm, Z=1500mm
    - Speed: 100-500 mm/s
    - Acceleration: 1000 mm/s²
    - Positioning accuracy: ±1mm
    - Measurement points: 9-point grid (3x3)
    """

    def __init__(self, workspace_dims: Dict[str, float] = None):
        """
        Initialize robot controller

        Args:
            workspace_dims: Dictionary with 'x', 'y', 'z' maximum dimensions in mm
        """
        self.workspace_dims = workspace_dims or {
            'x': 3000,  # mm
            'y': 2000,  # mm
            'z': 1500   # mm
        }

        # Robot parameters
        self.max_speed = 500  # mm/s
        self.min_speed = 100  # mm/s
        self.acceleration = 1000  # mm/s²
        self.positioning_accuracy = 1  # mm

        # Current state
        self.current_position = {'x': 0, 'y': 0, 'z': 0}
        self.is_homed = False
        self.status = "Idle"  # Idle, Moving, Measuring, Error, Homing
        self.emergency_stop_active = False

        # Measurement configuration
        self.grid_size = 3  # 3x3 grid
        self.measurement_delay = 2.0  # seconds to stabilize sensor

        # Measurement history
        self.measurement_history = []

    def home_axes(self) -> bool:
        """
        Home all axes to establish coordinate system

        Returns:
            True if homing successful, False otherwise
        """
        if self.emergency_stop_active:
            return False

        self.status = "Homing"

        # Simulate homing sequence (in real system, move to limit switches)
        time.sleep(0.1)  # Simulate movement time

        self.current_position = {'x': 0, 'y': 0, 'z': 0}
        self.is_homed = True
        self.status = "Idle"

        return True

    def check_limits(self, x: float, y: float, z: float) -> Tuple[bool, str]:
        """
        Check if position is within workspace limits

        Args:
            x, y, z: Target position in mm

        Returns:
            (is_valid, error_message)
        """
        if x < 0 or x > self.workspace_dims['x']:
            return False, f"X position {x}mm out of range [0, {self.workspace_dims['x']}]"
        if y < 0 or y > self.workspace_dims['y']:
            return False, f"Y position {y}mm out of range [0, {self.workspace_dims['y']}]"
        if z < 0 or z > self.workspace_dims['z']:
            return False, f"Z position {z}mm out of range [0, {self.workspace_dims['z']}]"

        return True, ""

    def move_to_position(self, x: float, y: float, z: float, speed: float = None) -> bool:
        """
        Move to specified XYZ position

        Args:
            x, y, z: Target position in mm
            speed: Movement speed in mm/s (default: max_speed)

        Returns:
            True if movement successful, False otherwise
        """
        if not self.is_homed:
            self.status = "Error"
            return False

        if self.emergency_stop_active:
            self.status = "Error"
            return False

        # Check limits
        is_valid, error_msg = self.check_limits(x, y, z)
        if not is_valid:
            self.status = "Error"
            return False

        # Use specified speed or default to max speed
        if speed is None:
            speed = self.max_speed
        else:
            speed = np.clip(speed, self.min_speed, self.max_speed)

        # Calculate movement distance and time
        dx = x - self.current_position['x']
        dy = y - self.current_position['y']
        dz = z - self.current_position['z']
        distance = np.sqrt(dx**2 + dy**2 + dz**2)

        # Simple motion profile (acceleration, constant speed, deceleration)
        move_time = distance / speed

        # Simulate movement
        self.status = "Moving"
        time.sleep(min(0.1, move_time / 10))  # Simulated delay

        # Update position
        self.current_position = {'x': x, 'y': y, 'z': z}
        self.status = "Idle"

        return True

    def jog(self, axis: str, distance: float) -> bool:
        """
        Jog (incremental move) along specified axis

        Args:
            axis: 'x', 'y', or 'z'
            distance: Distance to move in mm (positive or negative)

        Returns:
            True if jog successful, False otherwise
        """
        if axis.lower() not in ['x', 'y', 'z']:
            return False

        new_pos = self.current_position.copy()
        new_pos[axis.lower()] += distance

        return self.move_to_position(new_pos['x'], new_pos['y'], new_pos['z'])

    def get_current_position(self) -> Dict[str, float]:
        """
        Get current robot position

        Returns:
            Dictionary with x, y, z coordinates in mm
        """
        return self.current_position.copy()

    def measure_at_point(self, x: float, y: float, z: float) -> Dict[str, float]:
        """
        Move to position and take measurement

        Args:
            x, y, z: Measurement position in mm

        Returns:
            Dictionary with temperature, humidity, uv_intensity measurements
        """
        # Move to position
        if not self.move_to_position(x, y, z):
            return None

        # Wait for sensor stabilization
        self.status = "Measuring"
        time.sleep(min(0.05, self.measurement_delay / 20))  # Simulated delay

        # Simulate sensor readings with realistic noise
        # In real system, read from actual sensors
        base_temp = 85.0  # °C
        base_humidity = 85.0  # %RH
        base_uv = 60.0  # W/m²

        # Add spatial variation (edges typically different from center)
        center_x = self.workspace_dims['x'] / 2
        center_y = self.workspace_dims['y'] / 2
        dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_dist = np.sqrt(center_x**2 + center_y**2)
        spatial_factor = dist_from_center / max_dist  # 0 at center, 1 at corners

        measurement = {
            'x': x,
            'y': y,
            'z': z,
            'temperature': base_temp + spatial_factor * 3.0 + np.random.normal(0, 0.5),
            'humidity': base_humidity + spatial_factor * 2.5 + np.random.normal(0, 2.0),
            'uv_intensity': base_uv - spatial_factor * 5.0 + np.random.normal(0, 5.0),
            'timestamp': datetime.now().isoformat()
        }

        self.status = "Idle"

        return measurement

    def generate_grid_path(self, grid_size: int = 3, z_height: float = 750) -> List[Dict[str, float]]:
        """
        Generate 9-point grid measurement path

        Args:
            grid_size: Number of points per axis (default: 3 for 3x3 grid)
            z_height: Z height for measurements in mm

        Returns:
            List of waypoints with x, y, z coordinates
        """
        # Create grid points with 10% margin from edges
        margin_x = self.workspace_dims['x'] * 0.1
        margin_y = self.workspace_dims['y'] * 0.1

        x_points = np.linspace(margin_x, self.workspace_dims['x'] - margin_x, grid_size)
        y_points = np.linspace(margin_y, self.workspace_dims['y'] - margin_y, grid_size)

        waypoints = []
        for i, x in enumerate(x_points):
            # Snake pattern to minimize travel
            y_list = y_points if i % 2 == 0 else reversed(y_points)
            for y in y_list:
                waypoints.append({'x': x, 'y': y, 'z': z_height})

        return waypoints

    def measure_9_point_grid(self, z_height: float = 750) -> Dict:
        """
        Execute 9-point grid measurement sequence

        Args:
            z_height: Z height for measurements in mm

        Returns:
            Dictionary with measurement results and uniformity analysis
        """
        if not self.is_homed:
            return {"error": "Robot not homed"}

        # Generate measurement path
        waypoints = self.generate_grid_path(grid_size=3, z_height=z_height)

        # Execute measurements
        measurements = []
        start_time = datetime.now()

        for waypoint in waypoints:
            measurement = self.measure_at_point(waypoint['x'], waypoint['y'], waypoint['z'])
            if measurement:
                measurements.append(measurement)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Calculate uniformity
        uniformity = self.calculate_uniformity(measurements)

        # Store in history
        result = {
            'timestamp': start_time.isoformat(),
            'duration': duration,
            'measurements': measurements,
            'uniformity': uniformity,
            'grid_size': 3
        }

        self.measurement_history.append(result)

        return result

    def calculate_uniformity(self, measurements: List[Dict]) -> Dict:
        """
        Calculate uniformity statistics from measurements

        Args:
            measurements: List of measurement dictionaries

        Returns:
            Dictionary with uniformity statistics
        """
        if not measurements:
            return {}

        # Extract values
        temps = [m['temperature'] for m in measurements]
        humidities = [m['humidity'] for m in measurements]
        uv_values = [m['uv_intensity'] for m in measurements]

        # Calculate uniformity (deviation from mean)
        def calc_uniformity_percent(values):
            mean_val = np.mean(values)
            max_dev = np.max(np.abs(values - mean_val))
            if mean_val == 0:
                return 0
            return (max_dev / mean_val) * 100

        uniformity = {
            'temperature': {
                'mean': np.mean(temps),
                'std': np.std(temps),
                'min': np.min(temps),
                'max': np.max(temps),
                'uniformity_percent': calc_uniformity_percent(np.array(temps))
            },
            'humidity': {
                'mean': np.mean(humidities),
                'std': np.std(humidities),
                'min': np.min(humidities),
                'max': np.max(humidities),
                'uniformity_percent': calc_uniformity_percent(np.array(humidities))
            },
            'uv_intensity': {
                'mean': np.mean(uv_values),
                'std': np.std(uv_values),
                'min': np.min(uv_values),
                'max': np.max(uv_values),
                'uniformity_percent': calc_uniformity_percent(np.array(uv_values))
            }
        }

        return uniformity

    def parse_gcode(self, gcode_file: str) -> List[Dict]:
        """
        Parse G-code file for custom measurement paths

        Supported G-code commands:
        - G0/G1: Linear move (G0 X100 Y200 Z50 F500)
        - G28: Home axes
        - M3: Start measurement
        - M5: Stop measurement

        Args:
            gcode_file: Path to G-code file

        Returns:
            List of parsed commands
        """
        commands = []

        try:
            with open(gcode_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    # Remove comments and whitespace
                    line = line.split(';')[0].strip()
                    if not line:
                        continue

                    # Parse command
                    parts = line.split()
                    cmd = parts[0].upper()

                    if cmd in ['G0', 'G1']:  # Linear move
                        move_cmd = {'type': 'move', 'line': line_num}
                        for part in parts[1:]:
                            if part[0] == 'X':
                                move_cmd['x'] = float(part[1:])
                            elif part[0] == 'Y':
                                move_cmd['y'] = float(part[1:])
                            elif part[0] == 'Z':
                                move_cmd['z'] = float(part[1:])
                            elif part[0] == 'F':
                                move_cmd['feed_rate'] = float(part[1:])
                        commands.append(move_cmd)

                    elif cmd == 'G28':  # Home
                        commands.append({'type': 'home', 'line': line_num})

                    elif cmd == 'M3':  # Start measurement
                        commands.append({'type': 'measure_start', 'line': line_num})

                    elif cmd == 'M5':  # Stop measurement
                        commands.append({'type': 'measure_stop', 'line': line_num})

        except FileNotFoundError:
            return []

        return commands

    def execute_gcode(self, gcode_commands: List[Dict]) -> bool:
        """
        Execute parsed G-code commands

        Args:
            gcode_commands: List of parsed G-code commands

        Returns:
            True if execution successful, False otherwise
        """
        measuring = False
        measurements = []

        for cmd in gcode_commands:
            if self.emergency_stop_active:
                return False

            cmd_type = cmd.get('type')

            if cmd_type == 'home':
                if not self.home_axes():
                    return False

            elif cmd_type == 'move':
                x = cmd.get('x', self.current_position['x'])
                y = cmd.get('y', self.current_position['y'])
                z = cmd.get('z', self.current_position['z'])
                speed = cmd.get('feed_rate', self.max_speed)

                if not self.move_to_position(x, y, z, speed):
                    return False

                # If measuring, take reading at this position
                if measuring:
                    measurement = self.measure_at_point(x, y, z)
                    if measurement:
                        measurements.append(measurement)

            elif cmd_type == 'measure_start':
                measuring = True

            elif cmd_type == 'measure_stop':
                measuring = False

        return True

    def get_robot_status(self) -> Dict:
        """
        Get comprehensive robot status

        Returns:
            Dictionary with robot state information
        """
        return {
            'position': self.current_position.copy(),
            'status': self.status,
            'is_homed': self.is_homed,
            'emergency_stop': self.emergency_stop_active,
            'workspace': self.workspace_dims.copy(),
            'total_measurements': len(self.measurement_history)
        }

    def estimate_completion_time(self, path: List[Dict]) -> float:
        """
        Estimate time to complete a measurement path

        Args:
            path: List of waypoints

        Returns:
            Estimated time in seconds
        """
        total_time = 0
        current_pos = self.current_position.copy()

        for waypoint in path:
            # Calculate distance
            dx = waypoint['x'] - current_pos['x']
            dy = waypoint['y'] - current_pos['y']
            dz = waypoint['z'] - current_pos['z']
            distance = np.sqrt(dx**2 + dy**2 + dz**2)

            # Add movement time
            total_time += distance / self.max_speed

            # Add measurement time
            total_time += self.measurement_delay

            current_pos = waypoint.copy()

        return total_time

    def emergency_stop(self):
        """Activate emergency stop"""
        self.emergency_stop_active = True
        self.status = "Error"

    def reset_emergency_stop(self):
        """Reset emergency stop"""
        self.emergency_stop_active = False
        self.status = "Idle"

    def export_measurements(self, filename: str, format: str = 'csv'):
        """
        Export measurement history to file

        Args:
            filename: Output filename
            format: 'csv' or 'json'
        """
        if not self.measurement_history:
            return

        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(self.measurement_history, f, indent=2)

        elif format == 'csv':
            # Flatten measurements for CSV
            rows = []
            for session in self.measurement_history:
                for measurement in session['measurements']:
                    row = {
                        'session_timestamp': session['timestamp'],
                        **measurement
                    }
                    rows.append(row)

            df = pd.DataFrame(rows)
            df.to_csv(filename, index=False)


if __name__ == "__main__":
    # Test robot controller
    robot = UniformityRobot()

    print("Robot Controller Test")
    print("=" * 50)

    # Home robot
    print("\n1. Homing robot...")
    robot.home_axes()
    print(f"   Status: {robot.get_robot_status()}")

    # Move to position
    print("\n2. Moving to position (1500, 1000, 750)...")
    robot.move_to_position(1500, 1000, 750)
    print(f"   Current position: {robot.get_current_position()}")

    # Jog test
    print("\n3. Jogging +100mm in X...")
    robot.jog('x', 100)
    print(f"   Current position: {robot.get_current_position()}")

    # 9-point measurement
    print("\n4. Executing 9-point grid measurement...")
    result = robot.measure_9_point_grid()
    print(f"   Duration: {result['duration']:.2f}s")
    print(f"   Temperature uniformity: ±{result['uniformity']['temperature']['uniformity_percent']:.2f}%")
    print(f"   UV uniformity: ±{result['uniformity']['uv_intensity']['uniformity_percent']:.2f}%")

    print("\n" + "=" * 50)
    print("Test complete!")
