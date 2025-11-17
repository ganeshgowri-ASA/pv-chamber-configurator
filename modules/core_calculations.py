"""
Core Calculations Module for PV Chamber Configurator
Provides comprehensive calculations for chamber design, heat loads, airflow, power, and costs
"""

from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
import math


# Constants for calculations
SPECIFIC_HEAT_AIR = 1.005  # kJ/(kg·K) at constant pressure
AIR_DENSITY_STD = 1.184  # kg/m³ at 25°C, 1 atm
THERMAL_CONDUCTIVITY_SS = 16.3  # W/(m·K) for stainless steel 304
INSULATION_R_VALUE = 3.52  # m²·K/W for 100mm polyurethane foam
SAFETY_FACTOR = 1.25  # 25% safety margin for heat load calculations


@dataclass
class ChamberDimensions:
    """Chamber physical dimensions and constraints"""
    length_mm: float  # mm
    width_mm: float   # mm
    height_mm: float  # mm
    wall_thickness_mm: float = 100  # mm (insulation)

    def __post_init__(self):
        """Validate dimensions"""
        if self.length_mm <= 0 or self.width_mm <= 0 or self.height_mm <= 0:
            raise ValueError("All dimensions must be positive")
        if self.length_mm < 1000 or self.width_mm < 1000 or self.height_mm < 1000:
            raise ValueError("Minimum dimension is 1000mm for PV module testing")
        if self.length_mm > 10000 or self.width_mm > 10000 or self.height_mm > 10000:
            raise ValueError("Maximum dimension is 10000mm for practical chamber design")


@dataclass
class PerformanceSpec:
    """Chamber performance specifications"""
    temp_min_c: float = -45  # °C
    temp_max_c: float = 105  # °C
    humidity_min_rh: float = 40  # %RH
    humidity_max_rh: float = 95  # %RH
    uv_intensity_min: float = 25  # W/m²
    uv_intensity_max: float = 250  # W/m²

    def __post_init__(self):
        """Validate performance specifications"""
        if self.temp_min_c >= self.temp_max_c:
            raise ValueError("Min temperature must be less than max temperature")
        if self.humidity_min_rh >= self.humidity_max_rh:
            raise ValueError("Min humidity must be less than max humidity")
        if not (0 <= self.humidity_min_rh <= 100) or not (0 <= self.humidity_max_rh <= 100):
            raise ValueError("Humidity must be between 0-100 %RH")


@dataclass
class ComponentCosts:
    """Cost breakdown for chamber components (in Lakhs ₹)"""
    chamber_body: float = 35.0
    uv_led_arrays: float = 16.0
    refrigeration: float = 8.0
    controls_hmi: float = 7.0
    dc_power_supply: float = 6.0
    uniformity_robot: float = 12.0
    water_treatment: float = 6.3
    installation: float = 5.0
    calibration: float = 3.5

    def get_total_lakhs(self) -> float:
        """Calculate total cost in lakhs"""
        return (self.chamber_body + self.uv_led_arrays + self.refrigeration +
                self.controls_hmi + self.dc_power_supply + self.uniformity_robot +
                self.water_treatment + self.installation + self.calibration)

    def get_total_crores(self) -> float:
        """Calculate total cost in crores"""
        return self.get_total_lakhs() / 100

    def get_breakdown_dict(self) -> Dict[str, float]:
        """Return cost breakdown as dictionary"""
        return {
            "Chamber Body": self.chamber_body,
            "UV LED Arrays": self.uv_led_arrays,
            "Refrigeration System": self.refrigeration,
            "Controls & HMI": self.controls_hmi,
            "DC Power Supply": self.dc_power_supply,
            "Uniformity Robot": self.uniformity_robot,
            "Water Treatment": self.water_treatment,
            "Installation & Commissioning": self.installation,
            "Calibration & Certification": self.calibration
        }


class ChamberVolumeCalculator:
    """Calculate chamber volumes and related metrics"""

    @staticmethod
    def calculate_internal_volume(dims: ChamberDimensions) -> float:
        """
        Calculate internal chamber volume in m³

        Args:
            dims: Chamber dimensions

        Returns:
            Volume in cubic meters
        """
        volume_m3 = (dims.length_mm * dims.width_mm * dims.height_mm) / 1e9
        return round(volume_m3, 3)

    @staticmethod
    def calculate_external_volume(dims: ChamberDimensions) -> float:
        """
        Calculate external chamber volume including wall thickness

        Args:
            dims: Chamber dimensions

        Returns:
            External volume in cubic meters
        """
        ext_length = dims.length_mm + (2 * dims.wall_thickness_mm)
        ext_width = dims.width_mm + (2 * dims.wall_thickness_mm)
        ext_height = dims.height_mm + (2 * dims.wall_thickness_mm)

        volume_m3 = (ext_length * ext_width * ext_height) / 1e9
        return round(volume_m3, 3)

    @staticmethod
    def calculate_working_volume(dims: ChamberDimensions,
                                 equipment_volume_m3: float = 0.5) -> float:
        """
        Calculate working volume (internal volume - equipment volume)

        Args:
            dims: Chamber dimensions
            equipment_volume_m3: Volume occupied by internal equipment (default 0.5 m³)

        Returns:
            Working volume in cubic meters
        """
        internal = ChamberVolumeCalculator.calculate_internal_volume(dims)
        working = internal - equipment_volume_m3
        return max(0, round(working, 3))

    @staticmethod
    def calculate_surface_area(dims: ChamberDimensions) -> Dict[str, float]:
        """
        Calculate internal surface areas

        Args:
            dims: Chamber dimensions

        Returns:
            Dictionary with wall, floor, ceiling, and total surface areas in m²
        """
        length_m = dims.length_mm / 1000
        width_m = dims.width_mm / 1000
        height_m = dims.height_mm / 1000

        wall_area = 2 * (length_m * height_m + width_m * height_m)
        floor_area = length_m * width_m
        ceiling_area = length_m * width_m
        total_area = wall_area + floor_area + ceiling_area

        return {
            "walls": round(wall_area, 2),
            "floor": round(floor_area, 2),
            "ceiling": round(ceiling_area, 2),
            "total": round(total_area, 2)
        }


class HeatLoadCalculator:
    """Calculate heating and cooling loads for chamber"""

    @staticmethod
    def calculate_transmission_load(dims: ChamberDimensions,
                                    temp_inside_c: float,
                                    temp_ambient_c: float = 25.0) -> float:
        """
        Calculate heat transmission through walls (steady-state)

        Args:
            dims: Chamber dimensions
            temp_inside_c: Internal temperature (°C)
            temp_ambient_c: Ambient temperature (°C)

        Returns:
            Heat load in Watts
        """
        surface_area = ChamberVolumeCalculator.calculate_surface_area(dims)["total"]
        temp_diff = abs(temp_inside_c - temp_ambient_c)

        # Q = U × A × ΔT, where U = 1/R (overall heat transfer coefficient)
        u_value = 1 / INSULATION_R_VALUE  # W/(m²·K)
        transmission_load_w = u_value * surface_area * temp_diff

        return round(transmission_load_w, 2)

    @staticmethod
    def calculate_air_change_load(dims: ChamberDimensions,
                                  temp_inside_c: float,
                                  temp_ambient_c: float = 25.0,
                                  air_changes_per_hour: float = 3.0) -> float:
        """
        Calculate heat load from air infiltration/ventilation

        Args:
            dims: Chamber dimensions
            temp_inside_c: Internal temperature (°C)
            temp_ambient_c: Ambient temperature (°C)
            air_changes_per_hour: Number of air changes per hour

        Returns:
            Heat load in Watts
        """
        volume_m3 = ChamberVolumeCalculator.calculate_internal_volume(dims)
        temp_diff = abs(temp_inside_c - temp_ambient_c)

        # Q = (V × ACH × ρ × Cp × ΔT) / 3600
        heat_load_w = (volume_m3 * air_changes_per_hour * AIR_DENSITY_STD *
                       SPECIFIC_HEAT_AIR * temp_diff * 1000) / 3600

        return round(heat_load_w, 2)

    @staticmethod
    def calculate_equipment_load(uv_power_w: float = 2400,
                                 circulation_fan_w: float = 750,
                                 other_equipment_w: float = 500) -> float:
        """
        Calculate internal heat generation from equipment

        Args:
            uv_power_w: UV LED system power (Watts)
            circulation_fan_w: Circulation fan power (Watts)
            other_equipment_w: Other internal equipment (Watts)

        Returns:
            Total equipment heat load in Watts
        """
        return uv_power_w + circulation_fan_w + other_equipment_w

    @staticmethod
    def calculate_product_load(num_modules: int = 2,
                              module_mass_kg: float = 25,
                              temp_change_c: float = 50,
                              ramp_time_minutes: float = 30,
                              specific_heat_module: float = 0.84) -> float:
        """
        Calculate heat load for heating/cooling test modules

        Args:
            num_modules: Number of PV modules
            module_mass_kg: Mass per module (kg)
            temp_change_c: Temperature change magnitude (°C)
            ramp_time_minutes: Time for temperature ramp (minutes)
            specific_heat_module: Specific heat of PV module (kJ/kg·K)

        Returns:
            Product heat load in Watts
        """
        total_mass = num_modules * module_mass_kg
        energy_kj = total_mass * specific_heat_module * temp_change_c
        time_seconds = ramp_time_minutes * 60

        power_w = (energy_kj * 1000) / time_seconds
        return round(power_w, 2)

    @staticmethod
    def calculate_total_cooling_load(dims: ChamberDimensions,
                                     temp_inside_c: float,
                                     num_modules: int = 2,
                                     uv_power_w: float = 2400) -> Dict[str, float]:
        """
        Calculate total cooling load at maximum temperature

        Args:
            dims: Chamber dimensions
            temp_inside_c: Internal temperature (°C)
            num_modules: Number of PV modules
            uv_power_w: UV system power (Watts)

        Returns:
            Dictionary with breakdown of cooling loads and total
        """
        transmission = HeatLoadCalculator.calculate_transmission_load(dims, temp_inside_c)
        air_change = HeatLoadCalculator.calculate_air_change_load(dims, temp_inside_c)
        equipment = HeatLoadCalculator.calculate_equipment_load(uv_power_w)
        product = HeatLoadCalculator.calculate_product_load(num_modules)

        subtotal = transmission + air_change + equipment + product
        total_with_safety = subtotal * SAFETY_FACTOR

        return {
            "transmission_w": transmission,
            "air_infiltration_w": air_change,
            "equipment_w": equipment,
            "product_w": product,
            "subtotal_w": round(subtotal, 2),
            "safety_factor": SAFETY_FACTOR,
            "total_w": round(total_with_safety, 2),
            "total_kw": round(total_with_safety / 1000, 2),
            "total_tons": round(total_with_safety / 3517, 2)  # 1 ton = 3517 W
        }

    @staticmethod
    def calculate_total_heating_load(dims: ChamberDimensions,
                                     temp_inside_c: float = -45,
                                     num_modules: int = 2) -> Dict[str, float]:
        """
        Calculate total heating load at minimum temperature

        Args:
            dims: Chamber dimensions
            temp_inside_c: Internal temperature (°C)
            num_modules: Number of PV modules

        Returns:
            Dictionary with breakdown of heating loads and total
        """
        transmission = HeatLoadCalculator.calculate_transmission_load(dims, temp_inside_c)
        air_change = HeatLoadCalculator.calculate_air_change_load(dims, temp_inside_c)
        product = HeatLoadCalculator.calculate_product_load(num_modules, temp_change_c=70)

        subtotal = transmission + air_change + product
        total_with_safety = subtotal * SAFETY_FACTOR

        return {
            "transmission_w": transmission,
            "air_infiltration_w": air_change,
            "product_w": product,
            "subtotal_w": round(subtotal, 2),
            "safety_factor": SAFETY_FACTOR,
            "total_w": round(total_with_safety, 2),
            "total_kw": round(total_with_safety / 1000, 2)
        }


class AirflowCalculator:
    """Calculate airflow requirements and velocities"""

    @staticmethod
    def calculate_required_airflow_for_uniformity(dims: ChamberDimensions,
                                                  target_velocity_ms: float = 0.78) -> Dict[str, float]:
        """
        Calculate airflow rate for temperature uniformity

        Args:
            dims: Chamber dimensions
            target_velocity_ms: Target air velocity (m/s) for uniformity

        Returns:
            Dictionary with CFM, m³/h, and velocity
        """
        # Cross-sectional area for airflow
        length_m = dims.length_mm / 1000
        width_m = dims.width_mm / 1000
        cross_section_m2 = length_m * width_m

        # Q = V × A
        flow_rate_m3s = target_velocity_ms * cross_section_m2
        flow_rate_m3h = flow_rate_m3s * 3600
        flow_rate_cfm = flow_rate_m3h * 0.588578  # Convert m³/h to CFM

        return {
            "velocity_ms": target_velocity_ms,
            "flow_rate_m3s": round(flow_rate_m3s, 3),
            "flow_rate_m3h": round(flow_rate_m3h, 1),
            "flow_rate_cfm": round(flow_rate_cfm, 1)
        }

    @staticmethod
    def calculate_required_airflow_for_cooling(cooling_load_w: float,
                                               temp_supply_c: float,
                                               temp_return_c: float) -> Dict[str, float]:
        """
        Calculate airflow rate required to handle cooling load

        Args:
            cooling_load_w: Cooling load in Watts
            temp_supply_c: Supply air temperature (°C)
            temp_return_c: Return air temperature (°C)

        Returns:
            Dictionary with required airflow rates
        """
        temp_diff = abs(temp_return_c - temp_supply_c)
        if temp_diff < 1:
            temp_diff = 5  # Assume minimum 5°C differential

        # Q = (Heat Load) / (ρ × Cp × ΔT)
        flow_rate_m3s = cooling_load_w / (AIR_DENSITY_STD * SPECIFIC_HEAT_AIR * 1000 * temp_diff)
        flow_rate_m3h = flow_rate_m3s * 3600
        flow_rate_cfm = flow_rate_m3h * 0.588578

        return {
            "temp_differential_c": temp_diff,
            "flow_rate_m3s": round(flow_rate_m3s, 3),
            "flow_rate_m3h": round(flow_rate_m3h, 1),
            "flow_rate_cfm": round(flow_rate_cfm, 1)
        }

    @staticmethod
    def calculate_fan_power(flow_rate_m3h: float,
                           static_pressure_pa: float = 500,
                           fan_efficiency: float = 0.65) -> Dict[str, float]:
        """
        Calculate fan motor power requirements

        Args:
            flow_rate_m3h: Volumetric flow rate (m³/h)
            static_pressure_pa: Static pressure (Pascals)
            fan_efficiency: Fan efficiency (0-1)

        Returns:
            Dictionary with fan power and current draw
        """
        flow_rate_m3s = flow_rate_m3h / 3600

        # Power = (Q × ΔP) / η
        power_w = (flow_rate_m3s * static_pressure_pa) / fan_efficiency

        # Assume 3-phase 415V motor
        current_a = power_w / (415 * 0.85 * math.sqrt(3))  # Power factor 0.85

        return {
            "power_w": round(power_w, 1),
            "power_kw": round(power_w / 1000, 2),
            "current_a": round(current_a, 1),
            "voltage_v": 415
        }

    @staticmethod
    def calculate_air_changes_per_hour(dims: ChamberDimensions,
                                      flow_rate_m3h: float) -> float:
        """
        Calculate air changes per hour

        Args:
            dims: Chamber dimensions
            flow_rate_m3h: Volumetric flow rate (m³/h)

        Returns:
            Air changes per hour
        """
        volume_m3 = ChamberVolumeCalculator.calculate_internal_volume(dims)
        ach = flow_rate_m3h / volume_m3 if volume_m3 > 0 else 0
        return round(ach, 1)


class PowerConsumptionCalculator:
    """Calculate total power consumption and operating costs"""

    @staticmethod
    def calculate_refrigeration_power(cooling_load_w: float,
                                     cop: float = 2.5) -> Dict[str, float]:
        """
        Calculate refrigeration system power consumption

        Args:
            cooling_load_w: Cooling load in Watts
            cop: Coefficient of Performance

        Returns:
            Dictionary with compressor power and current
        """
        compressor_power_w = cooling_load_w / cop

        # 3-phase 415V motor
        current_a = compressor_power_w / (415 * 0.85 * math.sqrt(3))

        return {
            "cooling_capacity_w": cooling_load_w,
            "cooling_capacity_kw": round(cooling_load_w / 1000, 2),
            "cop": cop,
            "compressor_power_w": round(compressor_power_w, 1),
            "compressor_power_kw": round(compressor_power_w / 1000, 2),
            "current_a": round(current_a, 1)
        }

    @staticmethod
    def calculate_heating_power(heating_load_w: float,
                               efficiency: float = 0.95) -> Dict[str, float]:
        """
        Calculate electric heater power consumption

        Args:
            heating_load_w: Heating load in Watts
            efficiency: Heater efficiency

        Returns:
            Dictionary with heater power and current
        """
        heater_power_w = heating_load_w / efficiency

        # 3-phase 415V heaters
        current_a = heater_power_w / (415 * math.sqrt(3))

        return {
            "heating_capacity_w": heating_load_w,
            "heating_capacity_kw": round(heating_load_w / 1000, 2),
            "efficiency": efficiency,
            "heater_power_w": round(heater_power_w, 1),
            "heater_power_kw": round(heater_power_w / 1000, 2),
            "current_a": round(current_a, 1)
        }

    @staticmethod
    def calculate_total_power_consumption(
        cooling_power_kw: float,
        heating_power_kw: float,
        uv_power_kw: float = 2.4,
        fan_power_kw: float = 0.75,
        control_power_kw: float = 0.5,
        humidifier_power_kw: float = 3.0
    ) -> Dict[str, float]:
        """
        Calculate total connected load and power consumption

        Args:
            cooling_power_kw: Refrigeration system power (kW)
            heating_power_kw: Heating system power (kW)
            uv_power_kw: UV LED system power (kW)
            fan_power_kw: Circulation fan power (kW)
            control_power_kw: Control system power (kW)
            humidifier_power_kw: Humidifier power (kW)

        Returns:
            Dictionary with total power consumption breakdown
        """
        # Cooling and heating don't run simultaneously
        max_thermal_power = max(cooling_power_kw, heating_power_kw)

        # Maximum demand (all systems running)
        max_demand_kw = (max_thermal_power + uv_power_kw + fan_power_kw +
                        control_power_kw + humidifier_power_kw)

        # Connected load (sum of all installed capacity)
        connected_load_kw = (cooling_power_kw + heating_power_kw + uv_power_kw +
                            fan_power_kw + control_power_kw + humidifier_power_kw)

        # 3-phase current at 415V
        max_current_a = (max_demand_kw * 1000) / (415 * 0.85 * math.sqrt(3))

        return {
            "cooling_power_kw": cooling_power_kw,
            "heating_power_kw": heating_power_kw,
            "uv_power_kw": uv_power_kw,
            "fan_power_kw": fan_power_kw,
            "humidifier_power_kw": humidifier_power_kw,
            "control_power_kw": control_power_kw,
            "max_demand_kw": round(max_demand_kw, 2),
            "connected_load_kw": round(connected_load_kw, 2),
            "max_current_a": round(max_current_a, 1),
            "recommended_breaker_a": round(max_current_a * 1.25, 0)  # 125% of max current
        }

    @staticmethod
    def calculate_energy_cost(
        avg_power_kw: float,
        operating_hours_per_day: float = 16,
        operating_days_per_year: float = 250,
        electricity_rate_per_kwh: float = 8.0
    ) -> Dict[str, float]:
        """
        Calculate annual energy consumption and cost

        Args:
            avg_power_kw: Average power consumption (kW)
            operating_hours_per_day: Operating hours per day
            operating_days_per_year: Operating days per year
            electricity_rate_per_kwh: Electricity rate (₹/kWh)

        Returns:
            Dictionary with energy consumption and costs
        """
        daily_kwh = avg_power_kw * operating_hours_per_day
        annual_kwh = daily_kwh * operating_days_per_year

        daily_cost = daily_kwh * electricity_rate_per_kwh
        monthly_cost = daily_cost * (operating_days_per_year / 12)
        annual_cost = annual_kwh * electricity_rate_per_kwh

        return {
            "avg_power_kw": avg_power_kw,
            "daily_kwh": round(daily_kwh, 1),
            "monthly_kwh": round(annual_kwh / 12, 1),
            "annual_kwh": round(annual_kwh, 0),
            "daily_cost_inr": round(daily_cost, 0),
            "monthly_cost_inr": round(monthly_cost, 0),
            "annual_cost_inr": round(annual_cost, 0),
            "annual_cost_lakhs": round(annual_cost / 100000, 2),
            "electricity_rate_per_kwh": electricity_rate_per_kwh
        }


def validate_chamber_configuration(dims: ChamberDimensions,
                                   spec: PerformanceSpec,
                                   num_modules: int = 2) -> Dict[str, any]:
    """
    Validate complete chamber configuration and return warnings/errors

    Args:
        dims: Chamber dimensions
        spec: Performance specifications
        num_modules: Number of PV modules

    Returns:
        Dictionary with validation results, warnings, and recommendations
    """
    warnings = []
    errors = []
    recommendations = []

    # Check volume vs number of modules
    volume = ChamberVolumeCalculator.calculate_internal_volume(dims)
    min_volume_per_module = 2.0  # m³
    if volume < num_modules * min_volume_per_module:
        warnings.append(f"Chamber volume ({volume:.2f} m³) is tight for {num_modules} modules")

    # Check temperature ramp capability
    heating_load = HeatLoadCalculator.calculate_total_heating_load(dims, spec.temp_min_c, num_modules)
    if heating_load["total_kw"] > 50:
        warnings.append(f"High heating load ({heating_load['total_kw']} kW) may increase cost")

    # Check cooling capacity
    cooling_load = HeatLoadCalculator.calculate_total_cooling_load(dims, spec.temp_max_c, num_modules)
    if cooling_load["total_tons"] > 10:
        recommendations.append("Consider split refrigeration system for better reliability")

    # Check UV intensity feasibility
    floor_area = ChamberVolumeCalculator.calculate_surface_area(dims)["floor"]
    total_uv_power = spec.uv_intensity_max * floor_area
    if total_uv_power > 5000:
        warnings.append(f"High UV power requirement ({total_uv_power:.0f} W) - verify LED availability")

    # Check aspect ratio
    length_m = dims.length_mm / 1000
    width_m = dims.width_mm / 1000
    height_m = dims.height_mm / 1000
    aspect_ratio = max(length_m, width_m) / min(length_m, width_m)
    if aspect_ratio > 3:
        recommendations.append("Aspect ratio >3:1 may affect temperature uniformity")

    is_valid = len(errors) == 0

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "recommendations": recommendations,
        "volume_m3": volume,
        "floor_area_m2": floor_area,
        "cooling_load_kw": cooling_load["total_kw"],
        "heating_load_kw": heating_load["total_kw"]
    }


# Example usage and testing
if __name__ == "__main__":
    # Example chamber configuration
    dims = ChamberDimensions(length_mm=3200, width_mm=2100, height_mm=2200)
    spec = PerformanceSpec(temp_min_c=-45, temp_max_c=105, uv_intensity_max=250)
    costs = ComponentCosts()

    print("=== PV Chamber Configurator - Core Calculations ===\n")

    # Volume calculations
    print("1. VOLUME CALCULATIONS")
    volume = ChamberVolumeCalculator.calculate_internal_volume(dims)
    print(f"   Internal Volume: {volume} m³")

    surface = ChamberVolumeCalculator.calculate_surface_area(dims)
    print(f"   Total Surface Area: {surface['total']} m²\n")

    # Heat load calculations
    print("2. HEAT LOAD CALCULATIONS")
    cooling = HeatLoadCalculator.calculate_total_cooling_load(dims, 105, num_modules=2)
    print(f"   Cooling Load: {cooling['total_kw']} kW ({cooling['total_tons']:.1f} tons)")

    heating = HeatLoadCalculator.calculate_total_heating_load(dims, -45, num_modules=2)
    print(f"   Heating Load: {heating['total_kw']} kW\n")

    # Airflow calculations
    print("3. AIRFLOW CALCULATIONS")
    airflow = AirflowCalculator.calculate_required_airflow_for_uniformity(dims)
    print(f"   Required Airflow: {airflow['flow_rate_cfm']:.0f} CFM ({airflow['flow_rate_m3h']:.0f} m³/h)")
    print(f"   Air Velocity: {airflow['velocity_ms']} m/s\n")

    # Power consumption
    print("4. POWER CONSUMPTION")
    refrig_power = PowerConsumptionCalculator.calculate_refrigeration_power(cooling['total_w'])
    total_power = PowerConsumptionCalculator.calculate_total_power_consumption(
        refrig_power['compressor_power_kw'],
        heating['total_kw']
    )
    print(f"   Connected Load: {total_power['connected_load_kw']} kW")
    print(f"   Max Demand: {total_power['max_demand_kw']} kW")
    print(f"   Recommended Breaker: {total_power['recommended_breaker_a']} A\n")

    # Energy cost
    energy = PowerConsumptionCalculator.calculate_energy_cost(total_power['max_demand_kw'] * 0.6)
    print(f"   Annual Energy Cost: ₹{energy['annual_cost_lakhs']} Lakhs\n")

    # Cost breakdown
    print("5. COST BREAKDOWN")
    print(f"   Total Project Cost: ₹{costs.get_total_lakhs():.1f} Lakhs (₹{costs.get_total_crores():.2f} Crores)")
    for component, cost in costs.get_breakdown_dict().items():
        print(f"   - {component}: ₹{cost} Lakhs")

    # Validation
    print("\n6. CONFIGURATION VALIDATION")
    validation = validate_chamber_configuration(dims, spec, num_modules=2)
    print(f"   Valid: {validation['is_valid']}")
    if validation['warnings']:
        print("   Warnings:")
        for warning in validation['warnings']:
            print(f"   - {warning}")
    if validation['recommendations']:
        print("   Recommendations:")
        for rec in validation['recommendations']:
            print(f"   - {rec}")
