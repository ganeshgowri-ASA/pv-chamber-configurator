"""
Virtual HMI (Human-Machine Interface) Module
Real-time chamber monitoring, control, alarm management, and data logging
"""

import sqlite3
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
from pathlib import Path


class VirtualHMI:
    """
    Virtual HMI Controller for Environmental Chamber

    Features:
    - Real-time parameter monitoring
    - Setpoint control
    - Alarm management
    - Data logging and export
    - Recipe execution
    """

    def __init__(self, db_path: str = None, alarm_config_path: str = None):
        """
        Initialize Virtual HMI

        Args:
            db_path: Path to SQLite database for data logging
            alarm_config_path: Path to alarm configuration JSON
        """
        # Database setup
        if db_path is None:
            db_path = "logs/chamber_data.db"

        self.db_path = db_path
        self._init_database()

        # Load alarm configuration
        if alarm_config_path is None:
            alarm_config_path = "data/alarm_rules.json"

        self.alarm_config = self._load_alarm_config(alarm_config_path)

        # Chamber state
        self.chamber_state = {
            'status': 'Idle',  # Idle, Running, Paused, Alarm, Error
            'mode': 'Manual',  # Manual, Auto, Recipe
            'start_time': None,
            'uptime': 0,  # seconds
            'total_runtime': 0  # seconds
        }

        # Current setpoints
        self.setpoints = {
            'temperature': 25.0,  # °C
            'humidity': 50.0,  # %RH
            'uv_intensity': 0.0,  # W/m²
            'ramp_rate': 1.0  # °C/min
        }

        # Current process values (simulated)
        self.process_values = {
            'temperature': 25.0,
            'humidity': 50.0,
            'uv_intensity': 0.0,
            'temperature_grid': np.full(9, 25.0),  # 9-point grid
            'humidity_grid': np.full(9, 50.0),
            'uv_grid': np.full(9, 0.0),
            'power_consumption': 0.0,  # kW
            'ramp_rate_actual': 0.0  # °C/min
        }

        # Alarm system
        self.active_alarms = []
        self.alarm_history = []
        self.alarm_id_counter = 1

        # Data logging
        self.logging_interval = 60  # seconds
        self.last_log_time = datetime.now()

        # Recipe execution
        self.active_recipe = None
        self.recipe_start_time = None
        self.recipe_progress = 0  # 0-100%

    def _init_database(self):
        """Initialize SQLite database for data logging"""
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create data logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                uv_intensity REAL,
                temperature_setpoint REAL,
                humidity_setpoint REAL,
                uv_setpoint REAL,
                power_consumption REAL,
                ramp_rate REAL,
                status TEXT
            )
        ''')

        # Create alarm logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alarm_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alarm_id INTEGER,
                timestamp TEXT NOT NULL,
                level TEXT,
                message TEXT,
                acknowledged INTEGER DEFAULT 0,
                ack_timestamp TEXT
            )
        ''')

        # Create user actions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT,
                user TEXT,
                details TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def _load_alarm_config(self, config_path: str) -> Dict:
        """Load alarm configuration from JSON file"""
        default_config = {
            'CRITICAL': [
                {
                    'name': 'TEMP_DEVIATION_HIGH',
                    'condition': 'abs(pv - sp) > 5.0',
                    'message': 'Temperature deviation >5°C',
                    'parameter': 'temperature'
                },
                {
                    'name': 'OVER_TEMPERATURE',
                    'condition': 'pv > 110',
                    'message': 'Over-temperature alarm',
                    'parameter': 'temperature'
                },
                {
                    'name': 'EMERGENCY_STOP',
                    'condition': 'emergency_stop == True',
                    'message': 'Emergency stop activated'
                }
            ],
            'WARNING': [
                {
                    'name': 'UNIFORMITY_DEVIATION',
                    'condition': 'uniformity > 10.0',
                    'message': 'Uniformity deviation >10%',
                    'parameter': 'temperature'
                },
                {
                    'name': 'UV_OUT_OF_RANGE',
                    'condition': 'abs(pv - sp) > 10',
                    'message': 'UV intensity deviation >10 W/m²',
                    'parameter': 'uv_intensity'
                },
                {
                    'name': 'HUMIDITY_DEVIATION',
                    'condition': 'abs(pv - sp) > 5.0',
                    'message': 'Humidity deviation >5%',
                    'parameter': 'humidity'
                }
            ],
            'INFO': [
                {
                    'name': 'SETPOINT_REACHED',
                    'condition': 'at_setpoint == True',
                    'message': 'Setpoint reached'
                },
                {
                    'name': 'TEST_COMPLETE',
                    'condition': 'test_complete == True',
                    'message': 'Test sequence complete'
                }
            ]
        }

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass

        return default_config

    def get_current_status(self) -> Dict:
        """
        Get current chamber status

        Returns:
            Dictionary with comprehensive chamber status
        """
        # Calculate deviations
        temp_deviation = self.process_values['temperature'] - self.setpoints['temperature']
        humidity_deviation = self.process_values['humidity'] - self.setpoints['humidity']
        uv_deviation = self.process_values['uv_intensity'] - self.setpoints['uv_intensity']

        # Calculate uniformity
        temp_uniformity = self._calculate_uniformity(self.process_values['temperature_grid'])
        uv_uniformity = self._calculate_uniformity(self.process_values['uv_grid'])

        # Update uptime
        if self.chamber_state['start_time']:
            self.chamber_state['uptime'] = (datetime.now() - self.chamber_state['start_time']).total_seconds()

        return {
            'status': self.chamber_state['status'],
            'mode': self.chamber_state['mode'],
            'uptime': self.chamber_state['uptime'],
            'timestamp': datetime.now().isoformat(),
            'temperature': {
                'current': self.process_values['temperature'],
                'setpoint': self.setpoints['temperature'],
                'deviation': temp_deviation,
                'uniformity': temp_uniformity
            },
            'humidity': {
                'current': self.process_values['humidity'],
                'setpoint': self.setpoints['humidity'],
                'deviation': humidity_deviation
            },
            'uv_intensity': {
                'current': self.process_values['uv_intensity'],
                'setpoint': self.setpoints['uv_intensity'],
                'deviation': uv_deviation,
                'uniformity': uv_uniformity
            },
            'ramp_rate': self.process_values['ramp_rate_actual'],
            'power_consumption': self.process_values['power_consumption'],
            'active_alarms': len(self.active_alarms),
            'recipe_progress': self.recipe_progress
        }

    def get_live_data(self) -> Dict:
        """
        Get live process data including 9-point grids

        Returns:
            Dictionary with detailed process data
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'temperature_grid': self.process_values['temperature_grid'].tolist(),
            'humidity_grid': self.process_values['humidity_grid'].tolist(),
            'uv_grid': self.process_values['uv_grid'].tolist(),
            'setpoints': self.setpoints.copy(),
            'process_values': {
                'temperature': self.process_values['temperature'],
                'humidity': self.process_values['humidity'],
                'uv_intensity': self.process_values['uv_intensity'],
                'power_consumption': self.process_values['power_consumption'],
                'ramp_rate': self.process_values['ramp_rate_actual']
            }
        }

    def _calculate_uniformity(self, grid_values: np.ndarray) -> float:
        """
        Calculate uniformity percentage from grid values

        Args:
            grid_values: Array of measurements

        Returns:
            Uniformity as percentage deviation
        """
        mean_val = np.mean(grid_values)
        if mean_val == 0:
            return 0
        max_dev = np.max(np.abs(grid_values - mean_val))
        return (max_dev / mean_val) * 100

    def generate_trend_chart(self, parameter: str, hours: int = 24) -> pd.DataFrame:
        """
        Generate historical trend data for parameter

        Args:
            parameter: 'temperature', 'humidity', 'uv_intensity', or 'power_consumption'
            hours: Number of hours of historical data

        Returns:
            DataFrame with timestamp and parameter values
        """
        conn = sqlite3.connect(self.db_path)

        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        query = f'''
            SELECT timestamp, {parameter}, {parameter}_setpoint
            FROM data_logs
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        '''

        df = pd.read_sql_query(
            query,
            conn,
            params=(start_time.isoformat(), end_time.isoformat())
        )

        conn.close()

        if df.empty:
            # Generate simulated data for demo
            df = self._generate_simulated_trend(parameter, hours)

        return df

    def _generate_simulated_trend(self, parameter: str, hours: int) -> pd.DataFrame:
        """Generate simulated trend data for demonstration"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        # Generate timestamps (1 point per minute)
        timestamps = pd.date_range(start_time, end_time, freq='1min')

        # Generate simulated data with realistic patterns
        n_points = len(timestamps)
        t = np.linspace(0, hours, n_points)

        if parameter == 'temperature':
            # Simulate temperature ramp and stabilization
            setpoint = 85.0
            values = 25 + (setpoint - 25) * (1 - np.exp(-t / 2)) + np.random.normal(0, 0.5, n_points)
            setpoints = np.full(n_points, setpoint)

        elif parameter == 'humidity':
            setpoint = 85.0
            values = 50 + (setpoint - 50) * (1 - np.exp(-t / 3)) + np.random.normal(0, 2, n_points)
            setpoints = np.full(n_points, setpoint)

        elif parameter == 'uv_intensity':
            setpoint = 60.0
            values = setpoint * (1 - np.exp(-t / 1.5)) + np.random.normal(0, 3, n_points)
            setpoints = np.full(n_points, setpoint)

        elif parameter == 'power_consumption':
            # Power varies with load
            values = 15 + 10 * np.sin(t / 12 * 2 * np.pi) + np.random.normal(0, 2, n_points)
            setpoints = np.full(n_points, 0)

        else:
            values = np.zeros(n_points)
            setpoints = np.zeros(n_points)

        df = pd.DataFrame({
            'timestamp': timestamps,
            parameter: values,
            f'{parameter}_setpoint': setpoints
        })

        return df

    # Control Methods
    def set_temperature_setpoint(self, value: float) -> Tuple[bool, str]:
        """Set temperature setpoint"""
        if -45 <= value <= 105:
            self.setpoints['temperature'] = value
            self._log_user_action('set_temperature_setpoint', {'value': value})
            return True, f"Temperature setpoint set to {value}°C"
        return False, "Temperature must be between -45°C and 105°C"

    def set_humidity_setpoint(self, value: float) -> Tuple[bool, str]:
        """Set humidity setpoint"""
        if 40 <= value <= 95:
            self.setpoints['humidity'] = value
            self._log_user_action('set_humidity_setpoint', {'value': value})
            return True, f"Humidity setpoint set to {value}%RH"
        return False, "Humidity must be between 40% and 95%RH"

    def set_uv_intensity(self, value: float) -> Tuple[bool, str]:
        """Set UV intensity setpoint"""
        if 0 <= value <= 250:
            self.setpoints['uv_intensity'] = value
            self._log_user_action('set_uv_intensity', {'value': value})
            return True, f"UV intensity set to {value} W/m²"
        return False, "UV intensity must be between 0 and 250 W/m²"

    def set_ramp_rate(self, value: float) -> Tuple[bool, str]:
        """Set temperature ramp rate"""
        if 0.5 <= value <= 5.0:
            self.setpoints['ramp_rate'] = value
            self._log_user_action('set_ramp_rate', {'value': value})
            return True, f"Ramp rate set to {value}°C/min"
        return False, "Ramp rate must be between 0.5 and 5.0°C/min"

    def start_chamber(self) -> Tuple[bool, str]:
        """Start chamber operation"""
        if self.chamber_state['status'] in ['Idle', 'Paused']:
            self.chamber_state['status'] = 'Running'
            if self.chamber_state['start_time'] is None:
                self.chamber_state['start_time'] = datetime.now()
            self._log_user_action('start_chamber', {})
            return True, "Chamber started"
        return False, f"Cannot start from {self.chamber_state['status']} state"

    def stop_chamber(self) -> Tuple[bool, str]:
        """Stop chamber operation"""
        if self.chamber_state['status'] == 'Running':
            self.chamber_state['status'] = 'Idle'
            # Add runtime to total
            if self.chamber_state['start_time']:
                self.chamber_state['total_runtime'] += (datetime.now() - self.chamber_state['start_time']).total_seconds()
                self.chamber_state['start_time'] = None
            self._log_user_action('stop_chamber', {})
            return True, "Chamber stopped"
        return False, "Chamber is not running"

    def pause_chamber(self) -> Tuple[bool, str]:
        """Pause chamber operation"""
        if self.chamber_state['status'] == 'Running':
            self.chamber_state['status'] = 'Paused'
            self._log_user_action('pause_chamber', {})
            return True, "Chamber paused"
        return False, "Chamber is not running"

    def emergency_stop(self) -> Tuple[bool, str]:
        """Emergency stop"""
        self.chamber_state['status'] = 'Error'
        self.raise_alarm('CRITICAL', 'Emergency stop activated')
        self._log_user_action('emergency_stop', {})
        return True, "EMERGENCY STOP ACTIVATED"

    # Alarm Management
    def check_alarms(self):
        """Check alarm conditions and raise alarms if needed"""
        pv = self.process_values
        sp = self.setpoints

        # Check each alarm level
        for level in ['CRITICAL', 'WARNING', 'INFO']:
            if level not in self.alarm_config:
                continue

            for alarm_rule in self.alarm_config[level]:
                # Evaluate alarm condition
                should_alarm = self._evaluate_alarm_condition(alarm_rule, pv, sp)

                if should_alarm:
                    # Check if this alarm is already active
                    alarm_exists = any(
                        a['name'] == alarm_rule['name'] and not a['acknowledged']
                        for a in self.active_alarms
                    )

                    if not alarm_exists:
                        self.raise_alarm(level, alarm_rule['message'], alarm_rule['name'])

    def _evaluate_alarm_condition(self, alarm_rule: Dict, pv: Dict, sp: Dict) -> bool:
        """Evaluate if alarm condition is met"""
        try:
            # Get parameter if specified
            param = alarm_rule.get('parameter')
            if param:
                pv_val = pv.get(param, 0)
                sp_val = sp.get(param, 0)

                # Calculate uniformity if needed
                if 'uniformity' in alarm_rule['condition']:
                    grid_key = f'{param}_grid'
                    if grid_key in pv:
                        uniformity = self._calculate_uniformity(pv[grid_key])
                    else:
                        uniformity = 0
                else:
                    uniformity = 0

                # Evaluate condition
                condition = alarm_rule['condition']
                condition = condition.replace('pv', str(pv_val))
                condition = condition.replace('sp', str(sp_val))
                condition = condition.replace('uniformity', str(uniformity))

                return eval(condition)

        except Exception:
            return False

        return False

    def raise_alarm(self, level: str, message: str, name: str = None) -> int:
        """
        Raise a new alarm

        Args:
            level: 'CRITICAL', 'WARNING', or 'INFO'
            message: Alarm message
            name: Alarm identifier

        Returns:
            Alarm ID
        """
        alarm = {
            'id': self.alarm_id_counter,
            'level': level,
            'message': message,
            'name': name or f'ALARM_{self.alarm_id_counter}',
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False
        }

        self.active_alarms.append(alarm)
        self.alarm_history.append(alarm.copy())
        self.alarm_id_counter += 1

        # Log to database
        self._log_alarm(alarm)

        # Update chamber status if critical
        if level == 'CRITICAL' and self.chamber_state['status'] == 'Running':
            self.chamber_state['status'] = 'Alarm'

        return alarm['id']

    def acknowledge_alarm(self, alarm_id: int) -> bool:
        """Acknowledge an alarm"""
        for alarm in self.active_alarms:
            if alarm['id'] == alarm_id:
                alarm['acknowledged'] = True
                alarm['ack_timestamp'] = datetime.now().isoformat()

                # Update in database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE alarm_logs
                    SET acknowledged = 1, ack_timestamp = ?
                    WHERE alarm_id = ?
                ''', (alarm['ack_timestamp'], alarm_id))
                conn.commit()
                conn.close()

                # Remove from active alarms
                self.active_alarms.remove(alarm)

                # If no more critical alarms, return to running
                if self.chamber_state['status'] == 'Alarm':
                    has_critical = any(a['level'] == 'CRITICAL' for a in self.active_alarms)
                    if not has_critical:
                        self.chamber_state['status'] = 'Running'

                return True

        return False

    def get_alarm_history(self, limit: int = 100) -> List[Dict]:
        """Get alarm history"""
        return self.alarm_history[-limit:]

    # Data Logging
    def log_data_point(self, timestamp: datetime = None, data: Dict = None):
        """
        Log a data point to database

        Args:
            timestamp: Timestamp for log entry (default: now)
            data: Data dictionary (default: current process values)
        """
        if timestamp is None:
            timestamp = datetime.now()

        if data is None:
            data = self.process_values

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO data_logs (
                timestamp, temperature, humidity, uv_intensity,
                temperature_setpoint, humidity_setpoint, uv_setpoint,
                power_consumption, ramp_rate, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp.isoformat(),
            data.get('temperature', 0),
            data.get('humidity', 0),
            data.get('uv_intensity', 0),
            self.setpoints['temperature'],
            self.setpoints['humidity'],
            self.setpoints['uv_intensity'],
            data.get('power_consumption', 0),
            data.get('ramp_rate_actual', 0),
            self.chamber_state['status']
        ))

        conn.commit()
        conn.close()

        self.last_log_time = timestamp

    def _log_alarm(self, alarm: Dict):
        """Log alarm to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alarm_logs (
                alarm_id, timestamp, level, message, acknowledged
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            alarm['id'],
            alarm['timestamp'],
            alarm['level'],
            alarm['message'],
            0
        ))

        conn.commit()
        conn.close()

    def _log_user_action(self, action: str, details: Dict, user: str = 'Operator'):
        """Log user action to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_actions (timestamp, action, user, details)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            action,
            user,
            json.dumps(details)
        ))

        conn.commit()
        conn.close()

    def export_logs(self, start_date: datetime, end_date: datetime, format: str = 'csv') -> str:
        """
        Export data logs to file

        Args:
            start_date: Start date for export
            end_date: End date for export
            format: 'csv', 'excel', or 'json'

        Returns:
            Path to exported file
        """
        conn = sqlite3.connect(self.db_path)

        query = '''
            SELECT * FROM data_logs
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
        '''

        df = pd.read_sql_query(
            query,
            conn,
            params=(start_date.isoformat(), end_date.isoformat())
        )

        conn.close()

        # Generate filename
        filename = f"chamber_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"

        if format == 'csv':
            filepath = f"logs/{filename}.csv"
            df.to_csv(filepath, index=False)
        elif format == 'excel':
            filepath = f"logs/{filename}.xlsx"
            df.to_excel(filepath, index=False)
        elif format == 'json':
            filepath = f"logs/{filename}.json"
            df.to_json(filepath, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return filepath

    def get_log_statistics(self, days: int = 7) -> Dict:
        """Get statistics from logged data"""
        conn = sqlite3.connect(self.db_path)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = '''
            SELECT
                COUNT(*) as total_records,
                AVG(temperature) as avg_temp,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(humidity) as avg_humidity,
                AVG(power_consumption) as avg_power
            FROM data_logs
            WHERE timestamp >= ? AND timestamp <= ?
        '''

        result = conn.execute(query, (start_date.isoformat(), end_date.isoformat())).fetchone()
        conn.close()

        if result:
            return {
                'total_records': result[0],
                'avg_temperature': result[1],
                'min_temperature': result[2],
                'max_temperature': result[3],
                'avg_humidity': result[4],
                'avg_power_consumption': result[5]
            }

        return {}

    def update_simulation(self, dt: float = 1.0):
        """
        Update simulated process values (for demo mode)

        Args:
            dt: Time step in seconds
        """
        # Simulate temperature ramping towards setpoint
        temp_error = self.setpoints['temperature'] - self.process_values['temperature']
        ramp_rate_per_sec = self.setpoints['ramp_rate'] / 60.0  # Convert °C/min to °C/s

        if abs(temp_error) > 0.1:
            delta_temp = np.sign(temp_error) * min(ramp_rate_per_sec * dt, abs(temp_error))
            self.process_values['temperature'] += delta_temp + np.random.normal(0, 0.1)
            self.process_values['ramp_rate_actual'] = delta_temp / dt * 60  # °C/min
        else:
            self.process_values['temperature'] = self.setpoints['temperature'] + np.random.normal(0, 0.5)
            self.process_values['ramp_rate_actual'] = 0

        # Simulate humidity (slower response)
        humidity_error = self.setpoints['humidity'] - self.process_values['humidity']
        if abs(humidity_error) > 1.0:
            self.process_values['humidity'] += np.sign(humidity_error) * 0.5 + np.random.normal(0, 0.5)
        else:
            self.process_values['humidity'] = self.setpoints['humidity'] + np.random.normal(0, 2.0)

        # Simulate UV intensity (fast response)
        uv_error = self.setpoints['uv_intensity'] - self.process_values['uv_intensity']
        if abs(uv_error) > 2.0:
            self.process_values['uv_intensity'] += np.sign(uv_error) * 5.0 + np.random.normal(0, 2.0)
        else:
            self.process_values['uv_intensity'] = self.setpoints['uv_intensity'] + np.random.normal(0, 5.0)

        # Update grids with spatial variation
        self.process_values['temperature_grid'] = self.process_values['temperature'] + np.random.normal(0, 1.5, 9)
        self.process_values['humidity_grid'] = self.process_values['humidity'] + np.random.normal(0, 2.0, 9)
        self.process_values['uv_grid'] = self.process_values['uv_intensity'] + np.random.normal(0, 5.0, 9)

        # Simulate power consumption
        base_power = 5.0  # kW baseline
        temp_power = abs(temp_error) * 0.5
        uv_power = self.process_values['uv_intensity'] / 60 * 2.4  # UV LEDs
        self.process_values['power_consumption'] = base_power + temp_power + uv_power + np.random.normal(0, 0.5)

        # Check alarms
        self.check_alarms()

        # Auto-log if interval elapsed
        if (datetime.now() - self.last_log_time).total_seconds() >= self.logging_interval:
            self.log_data_point()


if __name__ == "__main__":
    # Test HMI controller
    hmi = VirtualHMI()

    print("Virtual HMI Test")
    print("=" * 50)

    # Set setpoints
    print("\n1. Setting setpoints...")
    hmi.set_temperature_setpoint(85.0)
    hmi.set_humidity_setpoint(85.0)
    hmi.set_uv_intensity(60.0)

    # Start chamber
    print("\n2. Starting chamber...")
    hmi.start_chamber()

    # Simulate for a few cycles
    print("\n3. Simulating chamber operation...")
    for i in range(10):
        hmi.update_simulation(dt=1.0)

    # Get status
    status = hmi.get_current_status()
    print(f"\n4. Current Status:")
    print(f"   Temperature: {status['temperature']['current']:.1f}°C (SP: {status['temperature']['setpoint']:.1f}°C)")
    print(f"   Humidity: {status['humidity']['current']:.1f}%RH (SP: {status['humidity']['setpoint']:.1f}%RH)")
    print(f"   UV Intensity: {status['uv_intensity']['current']:.1f} W/m²")
    print(f"   Active Alarms: {status['active_alarms']}")

    print("\n" + "=" * 50)
    print("Test complete!")
