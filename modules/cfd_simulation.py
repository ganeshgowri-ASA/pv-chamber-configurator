"""
CFD Simulation Engine for PV Chamber Environmental Testing
Implements comprehensive thermal, airflow, and humidity distribution analysis
with 3D chamber rendering capabilities.
"""

import numpy as np
from scipy import interpolate
from scipy.ndimage import gaussian_filter
import json
from typing import Dict, List, Tuple, Optional


class CFDSimulator:
    """
    Comprehensive CFD simulation engine for environmental test chamber analysis.

    Features:
    - 3D temperature field mapping with stratification analysis
    - Airflow velocity field calculation with recirculation detection
    - Humidity distribution with condensation risk assessment
    - 3D chamber model rendering with component placement
    - Transient thermal response simulation
    """

    def __init__(self, chamber_dims: Tuple[float, float, float],
                 temp_range: Tuple[float, float],
                 humidity_range: Tuple[float, float],
                 grid_resolution: Tuple[int, int, int] = (50, 50, 50)):
        """
        Initialize CFD simulator.

        Args:
            chamber_dims: (length, width, height) in mm
            temp_range: (min_temp, max_temp) in °C
            humidity_range: (min_rh, max_rh) in %
            grid_resolution: (nx, ny, nz) grid points
        """
        # Convert dimensions to meters
        self.L = chamber_dims[0] / 1000.0  # Length (m)
        self.W = chamber_dims[1] / 1000.0  # Width (m)
        self.H = chamber_dims[2] / 1000.0  # Height (m)
        self.volume = self.L * self.W * self.H  # m³

        self.temp_range = temp_range
        self.humidity_range = humidity_range

        # Grid resolution
        self.nx, self.ny, self.nz = grid_resolution

        # Create 3D mesh grid
        self.x = np.linspace(0, self.L, self.nx)
        self.y = np.linspace(0, self.W, self.ny)
        self.z = np.linspace(0, self.H, self.nz)
        self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing='ij')

        # Material properties
        self.wall_conductivity = 16.0  # W/m·K (Stainless steel 304)
        self.insulation_conductivity = 0.02  # W/m·K (Polyurethane)
        self.insulation_thickness = 0.1  # m

        # Air properties (at 25°C)
        self.air_density = 1.184  # kg/m³
        self.air_specific_heat = 1005  # J/kg·K
        self.air_thermal_conductivity = 0.026  # W/m·K
        self.air_dynamic_viscosity = 1.849e-5  # Pa·s
        self.air_kinematic_viscosity = 1.562e-5  # m²/s

        # Simulation results storage
        self.temp_field = None
        self.velocity_field = None
        self.humidity_field = None
        self.pressure_field = None

    # ==================== TEMPERATURE ANALYSIS ====================

    def calculate_temperature_field(self, setpoint: float, heater_power: float,
                                    ambient_temp: float = 25.0,
                                    fan_positions: Optional[List[Tuple[float, float, float]]] = None) -> np.ndarray:
        """
        Calculate 3D temperature distribution using simplified CFD model.

        Args:
            setpoint: Target temperature (°C)
            heater_power: Total heater power (W)
            ambient_temp: External ambient temperature (°C)
            fan_positions: List of (x, y, z) fan locations in meters

        Returns:
            3D temperature field array (nx, ny, nz)
        """
        # Initialize temperature field at setpoint
        temp_field = np.ones_like(self.X) * setpoint

        # Calculate heat loss through walls
        total_surface_area = 2 * (self.L * self.W + self.L * self.H + self.W * self.H)
        R_insulation = self.insulation_thickness / self.insulation_conductivity
        R_wall = 0.003 / self.wall_conductivity  # 3mm wall thickness
        R_total = R_insulation + R_wall
        heat_loss = (setpoint - ambient_temp) * total_surface_area / R_total

        # Effective temperature drop due to heat loss
        temp_drop = heat_loss / (heater_power + 1e-6) * abs(setpoint - ambient_temp) * 0.1

        # Add thermal stratification (natural convection)
        # Temperature increases with height for heating, decreases for cooling
        if setpoint > ambient_temp:
            # Heating mode - warmer at top
            stratification_gradient = np.linspace(-temp_drop, temp_drop, self.nz)
        else:
            # Cooling mode - cooler at top
            stratification_gradient = np.linspace(temp_drop, -temp_drop, self.nz)

        for k in range(self.nz):
            temp_field[:, :, k] += stratification_gradient[k]

        # Add heat source effects (heaters at bottom)
        heater_influence = np.exp(-self.Z / (self.H * 0.3))
        temp_field += heater_influence * temp_drop * 0.5

        # Add wall boundary effects (cooler near walls)
        wall_effect_x = np.minimum(self.X / self.L, (self.L - self.X) / self.L)
        wall_effect_y = np.minimum(self.Y / self.W, (self.W - self.Y) / self.W)
        wall_factor = np.minimum(wall_effect_x, wall_effect_y)
        temp_field -= (1 - wall_factor) * temp_drop * 0.3

        # Add fan mixing effects if fans are present
        if fan_positions:
            for fan_pos in fan_positions:
                fx, fy, fz = fan_pos
                # Calculate distance from each fan
                dist = np.sqrt((self.X - fx)**2 + (self.Y - fy)**2 + (self.Z - fz)**2)
                # Fan creates mixing zone - reduces temperature variation
                mixing_effect = np.exp(-dist / 0.5)  # 0.5m mixing radius
                temp_field = temp_field * (1 - mixing_effect * 0.3) + setpoint * mixing_effect * 0.3

        # Apply Gaussian smoothing for realistic distribution
        temp_field = gaussian_filter(temp_field, sigma=1.5)

        # Add small random variations for realism
        np.random.seed(42)  # Reproducible results
        temp_field += np.random.normal(0, 0.1, temp_field.shape)

        self.temp_field = temp_field
        return temp_field

    def detect_hot_cold_spots(self, temp_field: Optional[np.ndarray] = None) -> Dict:
        """
        Detect hot spots (max temp zones) and cold spots (min temp zones).

        Returns:
            Dictionary with hot/cold spot locations and temperatures
        """
        if temp_field is None:
            temp_field = self.temp_field

        if temp_field is None:
            raise ValueError("No temperature field available. Run calculate_temperature_field first.")

        # Find hot spot
        hot_idx = np.unravel_index(np.argmax(temp_field), temp_field.shape)
        hot_temp = temp_field[hot_idx]
        hot_location = (self.x[hot_idx[0]], self.y[hot_idx[1]], self.z[hot_idx[2]])

        # Find cold spot
        cold_idx = np.unravel_index(np.argmin(temp_field), temp_field.shape)
        cold_temp = temp_field[cold_idx]
        cold_location = (self.x[cold_idx[0]], self.y[cold_idx[1]], self.z[cold_idx[2]])

        return {
            'hot_spot': {
                'temperature': float(hot_temp),
                'location': hot_location,
                'location_mm': tuple(l * 1000 for l in hot_location)
            },
            'cold_spot': {
                'temperature': float(cold_temp),
                'location': cold_location,
                'location_mm': tuple(l * 1000 for l in cold_location)
            },
            'delta_temp': float(hot_temp - cold_temp)
        }

    def calculate_thermal_stratification(self, temp_field: Optional[np.ndarray] = None) -> Dict:
        """
        Calculate thermal stratification index and vertical temperature gradient.

        Returns:
            Dictionary with stratification metrics
        """
        if temp_field is None:
            temp_field = self.temp_field

        if temp_field is None:
            raise ValueError("No temperature field available.")

        # Calculate average temperature at each height
        temp_profile = np.mean(temp_field, axis=(0, 1))

        # Calculate vertical gradient (°C/m)
        dz = self.H / (self.nz - 1)
        gradient = np.gradient(temp_profile, dz)
        max_gradient = np.max(np.abs(gradient))
        mean_gradient = np.mean(np.abs(gradient))

        # Stratification index: ratio of vertical to total variation
        vertical_range = np.max(temp_profile) - np.min(temp_profile)
        total_range = np.max(temp_field) - np.min(temp_field)
        stratification_index = vertical_range / (total_range + 1e-6)

        return {
            'stratification_index': float(stratification_index),
            'max_gradient': float(max_gradient),  # °C/m
            'mean_gradient': float(mean_gradient),  # °C/m
            'vertical_temp_range': float(vertical_range),
            'temp_profile': temp_profile.tolist(),
            'heights': self.z.tolist()
        }

    def validate_temperature_uniformity(self, temp_field: Optional[np.ndarray] = None,
                                       tolerance: float = 2.0) -> Dict:
        """
        Validate temperature uniformity across chamber.

        Args:
            tolerance: Acceptable temperature deviation (°C)

        Returns:
            Dictionary with uniformity metrics
        """
        if temp_field is None:
            temp_field = self.temp_field

        if temp_field is None:
            raise ValueError("No temperature field available.")

        mean_temp = np.mean(temp_field)
        std_temp = np.std(temp_field)
        min_temp = np.min(temp_field)
        max_temp = np.max(temp_field)
        temp_range = max_temp - min_temp

        # Calculate percentage of volume within tolerance
        within_tolerance = np.abs(temp_field - mean_temp) <= tolerance
        uniformity_percentage = np.sum(within_tolerance) / temp_field.size * 100

        # Pass/fail criteria
        passes_uniformity = uniformity_percentage >= 90.0 and temp_range <= 2 * tolerance

        return {
            'mean_temperature': float(mean_temp),
            'std_deviation': float(std_temp),
            'min_temperature': float(min_temp),
            'max_temperature': float(max_temp),
            'temperature_range': float(temp_range),
            'uniformity_percentage': float(uniformity_percentage),
            'tolerance': tolerance,
            'passes_criteria': bool(passes_uniformity),
            'criteria': '±2°C across 90% of volume'
        }

    def simulate_ramp_rate(self, start_temp: float, end_temp: float,
                          time_seconds: float, heater_power: float = 10000) -> Dict:
        """
        Simulate temperature ramp rate and validate against specifications.

        Args:
            start_temp: Initial temperature (°C)
            end_temp: Target temperature (°C)
            time_seconds: Ramp duration (s)
            heater_power: Available heater power (W)

        Returns:
            Dictionary with ramp rate analysis
        """
        delta_T = end_temp - start_temp
        ramp_rate_celsius_per_min = (delta_T / time_seconds) * 60

        # Calculate required power using thermal mass
        thermal_mass = self.volume * self.air_density * self.air_specific_heat
        required_power = thermal_mass * abs(delta_T) / time_seconds

        # Calculate achievable ramp rate with available power
        achievable_delta_T_per_sec = heater_power / thermal_mass
        achievable_ramp_rate = achievable_delta_T_per_sec * 60

        # Time profile simulation
        num_points = 1000
        time_points = np.linspace(0, time_seconds, num_points)

        # Exponential approach to setpoint (first-order response)
        tau = thermal_mass / (heater_power / abs(delta_T) + 1e-6)  # Time constant
        if delta_T > 0:
            temp_profile = start_temp + delta_T * (1 - np.exp(-time_points / tau))
        else:
            temp_profile = start_temp + delta_T * (1 - np.exp(-time_points / tau))

        # Validate against IEC 61215 specs (1.6 - 3.5 °C/min typical)
        meets_spec = 1.6 <= abs(ramp_rate_celsius_per_min) <= 3.5

        return {
            'ramp_rate_celsius_per_min': float(ramp_rate_celsius_per_min),
            'achievable_ramp_rate': float(achievable_ramp_rate),
            'required_power': float(required_power),
            'available_power': float(heater_power),
            'power_sufficient': bool(heater_power >= required_power),
            'meets_iec_spec': bool(meets_spec),
            'spec_range': '1.6 - 3.5 °C/min',
            'time_profile': {
                'time_seconds': time_points.tolist(),
                'temperature': temp_profile.tolist()
            }
        }

    # ==================== AIRFLOW ANALYSIS ====================

    def calculate_velocity_field(self, fan_power_w: float,
                                 fan_positions: List[Tuple[float, float, float]]) -> np.ndarray:
        """
        Calculate 3D velocity vector field from fan configuration.

        Args:
            fan_power_w: Total fan power (W)
            fan_positions: List of (x, y, z) positions in meters

        Returns:
            Velocity field array (nx, ny, nz, 3) with [vx, vy, vz] components
        """
        # Initialize velocity field
        velocity_field = np.zeros((*self.X.shape, 3))

        # Calculate volumetric flow rate from fan power
        # Typical fan efficiency: 50%, pressure rise: 200 Pa
        fan_efficiency = 0.5
        pressure_rise = 200  # Pa
        volumetric_flow = (fan_power_w * fan_efficiency) / pressure_rise  # m³/s

        num_fans = len(fan_positions)
        flow_per_fan = volumetric_flow / max(num_fans, 1)

        for fan_pos in fan_positions:
            fx, fy, fz = fan_pos

            # Calculate distance from fan
            dx = self.X - fx
            dy = self.Y - fy
            dz = self.Z - fz
            dist = np.sqrt(dx**2 + dy**2 + dz**2) + 1e-6

            # Fan creates radial flow that decays with distance
            # Peak velocity at fan location
            peak_velocity = flow_per_fan / (0.1**2 * np.pi)  # Assume 0.1m radius fan

            # Velocity magnitude decays with distance
            velocity_magnitude = peak_velocity * np.exp(-dist / 1.0)  # 1m decay length

            # Velocity direction (radial from fan)
            vx = velocity_magnitude * dx / dist
            vy = velocity_magnitude * dy / dist
            vz = velocity_magnitude * dz / dist

            # Add to total velocity field
            velocity_field[:, :, :, 0] += vx
            velocity_field[:, :, :, 1] += vy
            velocity_field[:, :, :, 2] += vz

        # Add circulation pattern (vortex mixing)
        # Horizontal circulation in XY plane
        center_x, center_y = self.L / 2, self.W / 2

        # Create 2D circulation pattern in XY plane
        X_2d, Y_2d = np.meshgrid(self.x, self.y, indexing='ij')
        dx_center = X_2d - center_x
        dy_center = Y_2d - center_y
        r_center = np.sqrt(dx_center**2 + dy_center**2) + 1e-6

        # Tangential velocity component
        circulation_strength = 0.3  # m/s
        vx_circulation = -circulation_strength * dy_center / r_center * np.exp(-r_center / 1.0)
        vy_circulation = circulation_strength * dx_center / r_center * np.exp(-r_center / 1.0)

        # Broadcast circulation to all z-levels
        for k in range(self.nz):
            velocity_field[:, :, k, 0] += vx_circulation
            velocity_field[:, :, k, 1] += vy_circulation

        # Apply smoothing
        for i in range(3):
            velocity_field[:, :, :, i] = gaussian_filter(velocity_field[:, :, :, i], sigma=1.0)

        self.velocity_field = velocity_field
        return velocity_field

    def detect_recirculation_zones(self, velocity_field: Optional[np.ndarray] = None) -> Dict:
        """
        Identify recirculation zones using velocity curl analysis.

        Returns:
            Dictionary with recirculation zone information
        """
        if velocity_field is None:
            velocity_field = self.velocity_field

        if velocity_field is None:
            raise ValueError("No velocity field available.")

        vx = velocity_field[:, :, :, 0]
        vy = velocity_field[:, :, :, 1]
        vz = velocity_field[:, :, :, 2]

        # Calculate velocity magnitude
        velocity_magnitude = np.sqrt(vx**2 + vy**2 + vz**2)

        # Calculate vorticity (curl of velocity)
        dy = self.W / (self.ny - 1)
        dz = self.H / (self.nz - 1)

        # Vorticity in z-direction (main circulation)
        dvx_dy = np.gradient(vx, dy, axis=1)
        dvy_dx = np.gradient(vy, self.L / (self.nx - 1), axis=0)
        vorticity_z = dvy_dx - dvx_dy

        # High vorticity indicates recirculation
        vorticity_magnitude = np.abs(vorticity_z)
        recirculation_threshold = np.percentile(vorticity_magnitude, 90)

        recirculation_zones = vorticity_magnitude > recirculation_threshold
        recirculation_volume = np.sum(recirculation_zones) / recirculation_zones.size * 100

        return {
            'recirculation_volume_percentage': float(recirculation_volume),
            'max_vorticity': float(np.max(vorticity_magnitude)),
            'mean_vorticity': float(np.mean(vorticity_magnitude)),
            'num_recirculation_cells': int(np.sum(recirculation_zones > 0))
        }

    def detect_dead_zones(self, velocity_field: Optional[np.ndarray] = None,
                         threshold: float = 0.1) -> Dict:
        """
        Detect stagnant air zones (dead zones) where velocity < threshold.

        Args:
            threshold: Minimum velocity threshold (m/s)

        Returns:
            Dictionary with dead zone analysis
        """
        if velocity_field is None:
            velocity_field = self.velocity_field

        if velocity_field is None:
            raise ValueError("No velocity field available.")

        # Calculate velocity magnitude
        velocity_magnitude = np.sqrt(np.sum(velocity_field**2, axis=3))

        # Identify dead zones
        dead_zones = velocity_magnitude < threshold
        dead_zone_percentage = np.sum(dead_zones) / dead_zones.size * 100

        # Find largest dead zone cluster
        from scipy.ndimage import label
        labeled_zones, num_zones = label(dead_zones)

        zone_sizes = []
        if num_zones > 0:
            for i in range(1, num_zones + 1):
                zone_sizes.append(np.sum(labeled_zones == i))
            largest_zone_size = max(zone_sizes) if zone_sizes else 0
        else:
            largest_zone_size = 0

        passes_criteria = dead_zone_percentage < 10.0  # Target: <10% dead zones

        return {
            'dead_zone_percentage': float(dead_zone_percentage),
            'num_dead_zones': int(num_zones),
            'largest_dead_zone_cells': int(largest_zone_size),
            'velocity_threshold': threshold,
            'passes_criteria': bool(passes_criteria),
            'min_velocity': float(np.min(velocity_magnitude)),
            'max_velocity': float(np.max(velocity_magnitude)),
            'mean_velocity': float(np.mean(velocity_magnitude))
        }

    def calculate_pressure_drop(self, velocity_field: Optional[np.ndarray] = None) -> Dict:
        """
        Calculate pressure drop across chamber using Bernoulli equation.

        Returns:
            Dictionary with pressure drop analysis
        """
        if velocity_field is None:
            velocity_field = self.velocity_field

        if velocity_field is None:
            raise ValueError("No velocity field available.")

        # Calculate velocity magnitude
        velocity_magnitude = np.sqrt(np.sum(velocity_field**2, axis=3))

        # Dynamic pressure: 0.5 * rho * v^2
        dynamic_pressure = 0.5 * self.air_density * velocity_magnitude**2

        # Total pressure drop (max - min dynamic pressure)
        max_pressure = np.max(dynamic_pressure)
        min_pressure = np.min(dynamic_pressure)
        total_pressure_drop = max_pressure - min_pressure

        # Add frictional losses (Darcy-Weisbach)
        # Assuming hydraulic diameter Dh = 4*Volume/Surface_area
        surface_area = 2 * (self.L * self.W + self.L * self.H + self.W * self.H)
        hydraulic_diameter = 4 * self.volume / surface_area

        # Reynolds number
        mean_velocity = np.mean(velocity_magnitude)
        reynolds_number = self.air_density * mean_velocity * hydraulic_diameter / self.air_dynamic_viscosity

        # Friction factor (Blasius for turbulent flow)
        if reynolds_number > 2300:
            friction_factor = 0.316 / (reynolds_number ** 0.25)
            flow_regime = "Turbulent"
        else:
            friction_factor = 64 / (reynolds_number + 1e-6)
            flow_regime = "Laminar"

        # Frictional pressure drop
        friction_pressure_drop = friction_factor * (self.L / hydraulic_diameter) * \
                                0.5 * self.air_density * mean_velocity**2

        total_pressure_drop_with_friction = total_pressure_drop + friction_pressure_drop

        passes_criteria = total_pressure_drop_with_friction < 200  # Pa

        return {
            'total_pressure_drop': float(total_pressure_drop_with_friction),
            'dynamic_pressure_drop': float(total_pressure_drop),
            'friction_pressure_drop': float(friction_pressure_drop),
            'reynolds_number': float(reynolds_number),
            'flow_regime': flow_regime,
            'friction_factor': float(friction_factor),
            'passes_criteria': bool(passes_criteria),
            'criteria': '< 200 Pa'
        }

    def optimize_fan_placement(self, num_fans: int) -> List[Tuple[float, float, float]]:
        """
        Optimize fan placement for uniform airflow distribution.

        Args:
            num_fans: Number of fans to place

        Returns:
            List of optimal (x, y, z) fan positions in meters
        """
        fan_positions = []

        if num_fans == 1:
            # Single fan at center of chamber
            fan_positions.append((self.L / 2, self.W / 2, self.H / 2))

        elif num_fans == 2:
            # Two fans at opposite corners, mid-height
            fan_positions.append((self.L * 0.25, self.W * 0.25, self.H / 2))
            fan_positions.append((self.L * 0.75, self.W * 0.75, self.H / 2))

        elif num_fans == 4:
            # Four fans in corners, mid-height (optimal for rectangular chamber)
            positions = [
                (self.L * 0.25, self.W * 0.25, self.H / 2),
                (self.L * 0.75, self.W * 0.25, self.H / 2),
                (self.L * 0.25, self.W * 0.75, self.H / 2),
                (self.L * 0.75, self.W * 0.75, self.H / 2)
            ]
            fan_positions.extend(positions)

        else:
            # Distribute fans evenly in 3D grid
            fans_per_dim = int(np.ceil(num_fans ** (1/3)))
            count = 0
            for i in range(fans_per_dim):
                for j in range(fans_per_dim):
                    for k in range(fans_per_dim):
                        if count < num_fans:
                            x = self.L * (i + 1) / (fans_per_dim + 1)
                            y = self.W * (j + 1) / (fans_per_dim + 1)
                            z = self.H * (k + 1) / (fans_per_dim + 1)
                            fan_positions.append((x, y, z))
                            count += 1

        return fan_positions

    # ==================== HUMIDITY ANALYSIS ====================

    def calculate_humidity_field(self, target_rh: float,
                                 humidifier_positions: List[Tuple[float, float, float]]) -> np.ndarray:
        """
        Calculate 3D relative humidity distribution.

        Args:
            target_rh: Target relative humidity (%)
            humidifier_positions: List of (x, y, z) humidifier positions

        Returns:
            3D humidity field array (nx, ny, nz)
        """
        # Initialize humidity field
        humidity_field = np.ones_like(self.X) * target_rh

        # Add humidity sources
        for hum_pos in humidifier_positions:
            hx, hy, hz = hum_pos

            # Distance from humidifier
            dist = np.sqrt((self.X - hx)**2 + (self.Y - hy)**2 + (self.Z - hz)**2)

            # Humidity boost near humidifier
            humidity_boost = 5.0 * np.exp(-dist / 0.5)  # 5% RH boost, 0.5m decay
            humidity_field += humidity_boost

        # Add wall dehumidification effects (condensation on cold walls)
        if self.temp_field is not None:
            # Near walls, humidity may be lower due to condensation
            wall_effect_x = np.minimum(self.X / self.L, (self.L - self.X) / self.L)
            wall_effect_y = np.minimum(self.Y / self.W, (self.W - self.Y) / self.W)
            wall_factor = np.minimum(wall_effect_x, wall_effect_y)
            humidity_field -= (1 - wall_factor) * 2.0  # Up to 2% RH reduction near walls

        # Add vertical gradient (humidity settles down)
        humidity_gradient = np.linspace(1.0, -1.0, self.nz)  # +1% at top, -1% at bottom
        for k in range(self.nz):
            humidity_field[:, :, k] += humidity_gradient[k]

        # Apply smoothing
        humidity_field = gaussian_filter(humidity_field, sigma=1.5)

        # Clip to valid range
        humidity_field = np.clip(humidity_field, self.humidity_range[0], self.humidity_range[1])

        # Add small random variations
        np.random.seed(43)
        humidity_field += np.random.normal(0, 0.2, humidity_field.shape)
        humidity_field = np.clip(humidity_field, 0, 100)

        self.humidity_field = humidity_field
        return humidity_field

    def detect_condensation_risk(self, temp_field: Optional[np.ndarray] = None,
                                 humidity_field: Optional[np.ndarray] = None) -> Dict:
        """
        Detect zones at risk of condensation using dew point analysis.

        Returns:
            Dictionary with condensation risk assessment
        """
        if temp_field is None:
            temp_field = self.temp_field
        if humidity_field is None:
            humidity_field = self.humidity_field

        if temp_field is None or humidity_field is None:
            raise ValueError("Both temperature and humidity fields required.")

        # Calculate dew point using Magnus formula
        # Tdew = (b * α) / (a - α)
        # where α = (a * T) / (b + T) + ln(RH/100)
        a = 17.27
        b = 237.7  # °C

        alpha = (a * temp_field) / (b + temp_field) + np.log(humidity_field / 100.0)
        dew_point = (b * alpha) / (a - alpha)

        # Condensation risk where temperature approaches dew point
        temp_margin = temp_field - dew_point

        # Risk zones: within 2°C of dew point
        risk_zones = temp_margin < 2.0
        risk_percentage = np.sum(risk_zones) / risk_zones.size * 100

        # Critical zones: at or below dew point
        critical_zones = temp_margin <= 0
        critical_percentage = np.sum(critical_zones) / critical_zones.size * 100

        return {
            'condensation_risk_percentage': float(risk_percentage),
            'critical_condensation_percentage': float(critical_percentage),
            'min_temp_margin': float(np.min(temp_margin)),
            'mean_temp_margin': float(np.mean(temp_margin)),
            'min_dew_point': float(np.min(dew_point)),
            'max_dew_point': float(np.max(dew_point)),
            'safe_operation': bool(critical_percentage < 1.0)
        }

    def validate_humidity_uniformity(self, humidity_field: Optional[np.ndarray] = None,
                                    tolerance: float = 3.0) -> Dict:
        """
        Validate humidity uniformity across chamber.

        Args:
            tolerance: Acceptable RH deviation (%)

        Returns:
            Dictionary with humidity uniformity metrics
        """
        if humidity_field is None:
            humidity_field = self.humidity_field

        if humidity_field is None:
            raise ValueError("No humidity field available.")

        mean_rh = np.mean(humidity_field)
        std_rh = np.std(humidity_field)
        min_rh = np.min(humidity_field)
        max_rh = np.max(humidity_field)
        rh_range = max_rh - min_rh

        # Calculate percentage within tolerance
        within_tolerance = np.abs(humidity_field - mean_rh) <= tolerance
        uniformity_percentage = np.sum(within_tolerance) / humidity_field.size * 100

        passes_uniformity = uniformity_percentage >= 90.0 and rh_range <= 2 * tolerance

        return {
            'mean_humidity': float(mean_rh),
            'std_deviation': float(std_rh),
            'min_humidity': float(min_rh),
            'max_humidity': float(max_rh),
            'humidity_range': float(rh_range),
            'uniformity_percentage': float(uniformity_percentage),
            'tolerance': tolerance,
            'passes_criteria': bool(passes_uniformity),
            'criteria': '±3% RH across 90% of volume'
        }

    # ==================== 3D CHAMBER RENDERING ====================

    def generate_chamber_geometry(self) -> Dict:
        """
        Generate 3D chamber geometry data for rendering.

        Returns:
            Dictionary with vertices, faces, and component positions
        """
        # Chamber corners (8 vertices)
        vertices = [
            [0, 0, 0],
            [self.L, 0, 0],
            [self.L, self.W, 0],
            [0, self.W, 0],
            [0, 0, self.H],
            [self.L, 0, self.H],
            [self.L, self.W, self.H],
            [0, self.W, self.H]
        ]

        # Chamber edges (wireframe)
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom
            [4, 5], [5, 6], [6, 7], [7, 4],  # Top
            [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical
        ]

        # Chamber faces (for solid rendering)
        faces = [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Front
            [2, 3, 7, 6],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5]   # Right
        ]

        return {
            'vertices': vertices,
            'edges': edges,
            'faces': faces,
            'dimensions': {
                'length': self.L,
                'width': self.W,
                'height': self.H,
                'length_mm': self.L * 1000,
                'width_mm': self.W * 1000,
                'height_mm': self.H * 1000
            }
        }

    def get_component_positions(self, num_fans: int = 4, num_humidifiers: int = 2,
                               num_uv_panels: int = 2) -> Dict:
        """
        Generate optimal positions for chamber components.

        Returns:
            Dictionary with component positions
        """
        # Optimize fan placement
        fan_positions = self.optimize_fan_placement(num_fans)

        # Place humidifiers near bottom corners
        humidifier_positions = [
            (self.L * 0.2, self.W * 0.2, self.H * 0.1),
            (self.L * 0.8, self.W * 0.8, self.H * 0.1)
        ][:num_humidifiers]

        # Place UV panels on ceiling
        uv_panel_positions = [
            (self.L * 0.33, self.W / 2, self.H * 0.9),
            (self.L * 0.67, self.W / 2, self.H * 0.9)
        ][:num_uv_panels]

        # Test specimen location (center, lower portion)
        specimen_position = (self.L / 2, self.W / 2, self.H * 0.3)

        return {
            'fans': fan_positions,
            'humidifiers': humidifier_positions,
            'uv_panels': uv_panel_positions,
            'test_specimen': specimen_position
        }

    # ==================== ADVANCED CFD FEATURES ====================

    def calculate_transient_response(self, setpoint: float, duration_minutes: float,
                                    heater_power: float = 10000) -> Dict:
        """
        Simulate transient thermal response during temperature changes.

        Args:
            setpoint: Target temperature (°C)
            duration_minutes: Simulation duration (minutes)
            heater_power: Heater power (W)

        Returns:
            Dictionary with transient response data
        """
        # System time constant
        thermal_mass = self.volume * self.air_density * self.air_specific_heat

        # Heat loss coefficient
        total_surface_area = 2 * (self.L * self.W + self.L * self.H + self.W * self.H)
        R_total = self.insulation_thickness / self.insulation_conductivity
        UA = total_surface_area / R_total  # Overall heat transfer coefficient

        # Time constant: τ = thermal_mass / UA
        tau = thermal_mass / UA  # seconds

        # Generate time points
        time_seconds = duration_minutes * 60
        time_points = np.linspace(0, time_seconds, 1000)

        # First-order response: T(t) = Tss + (T0 - Tss) * exp(-t/τ)
        ambient_temp = 25.0
        steady_state_temp = ambient_temp + (heater_power * R_total) / total_surface_area

        # Assume starting from ambient
        temp_response = steady_state_temp + (ambient_temp - steady_state_temp) * np.exp(-time_points / tau)

        # Time to reach 95% of setpoint
        time_to_95_percent = -tau * np.log(0.05)
        time_to_steady = time_to_95_percent / 60  # minutes

        return {
            'time_constant_seconds': float(tau),
            'time_constant_minutes': float(tau / 60),
            'time_to_steady_state_minutes': float(time_to_steady),
            'steady_state_temperature': float(steady_state_temp),
            'time_profile': {
                'time_seconds': time_points.tolist(),
                'time_minutes': (time_points / 60).tolist(),
                'temperature': temp_response.tolist()
            }
        }

    def calculate_energy_balance(self, setpoint: float, ambient_temp: float = 25.0,
                                heater_power: float = 10000) -> Dict:
        """
        Calculate energy balance for the chamber system.

        Returns:
            Dictionary with energy balance analysis
        """
        # Heat loss through walls
        total_surface_area = 2 * (self.L * self.W + self.L * self.H + self.W * self.H)
        R_total = self.insulation_thickness / self.insulation_conductivity
        heat_loss = (setpoint - ambient_temp) * total_surface_area / R_total

        # Heat capacity
        thermal_mass = self.volume * self.air_density * self.air_specific_heat

        # Energy balance: heater_power = heat_loss + heat_accumulation
        heat_accumulation = heater_power - heat_loss

        # Efficiency
        thermal_efficiency = (heat_loss / heater_power * 100) if heater_power > 0 else 0

        # Power breakdown
        balance_check = abs(heater_power - heat_loss) / heater_power * 100 if heater_power > 0 else 0

        return {
            'heater_power': float(heater_power),
            'heat_loss': float(heat_loss),
            'heat_accumulation': float(heat_accumulation),
            'thermal_efficiency': float(thermal_efficiency),
            'thermal_mass': float(thermal_mass),
            'balance_error_percentage': float(balance_check),
            'energy_balanced': bool(balance_check < 5.0)
        }

    def export_simulation_data(self, filename: str = 'cfd_results.json') -> str:
        """
        Export all simulation results to JSON file.

        Returns:
            JSON string with all simulation data
        """
        export_data = {
            'chamber_geometry': {
                'length_m': float(self.L),
                'width_m': float(self.W),
                'height_m': float(self.H),
                'volume_m3': float(self.volume)
            },
            'grid_resolution': {
                'nx': self.nx,
                'ny': self.ny,
                'nz': self.nz
            },
            'temperature_field': self.temp_field.tolist() if self.temp_field is not None else None,
            'humidity_field': self.humidity_field.tolist() if self.humidity_field is not None else None,
            'velocity_field': self.velocity_field.tolist() if self.velocity_field is not None else None
        }

        json_data = json.dumps(export_data, indent=2)

        # Write to file
        with open(filename, 'w') as f:
            f.write(json_data)

        return json_data
