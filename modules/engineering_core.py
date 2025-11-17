"""
Engineering Core Module for PV Test Chamber Configurator
Implements IEC 61215/61730 standards and thermal/environmental calculations
"""

import math
from typing import Dict, Tuple, List
from dataclasses import dataclass
import numpy as np


# Physical Constants
STEFAN_BOLTZMANN = 5.67e-8  # W/(m²·K⁴)
AIR_DENSITY_STP = 1.225  # kg/m³ at STP
AIR_SPECIFIC_HEAT = 1006  # J/(kg·K)
WATER_SPECIFIC_HEAT = 4186  # J/(kg·K)
WATER_LATENT_HEAT_VAPORIZATION = 2257e3  # J/kg at 100°C
R134A_COP_TYPICAL = 3.5  # Coefficient of Performance


@dataclass
class ChamberDimensions:
    """Chamber internal dimensions"""
    length: float  # meters
    width: float  # meters
    height: float  # meters

    @property
    def volume(self) -> float:
        """Calculate chamber volume in m³"""
        return self.length * self.width * self.height

    @property
    def surface_area(self) -> float:
        """Calculate total internal surface area in m²"""
        return 2 * (self.length * self.width +
                   self.length * self.height +
                   self.width * self.height)


@dataclass
class PVModuleSpec:
    """PV Module specifications"""
    length: float  # meters
    width: float  # meters
    thickness: float  # meters
    mass: float  # kg
    max_power: float  # watts
    quantity: int = 2

    @property
    def total_mass(self) -> float:
        """Total mass of all modules"""
        return self.mass * self.quantity

    @property
    def total_area(self) -> float:
        """Total front surface area"""
        return self.length * self.width * self.quantity


@dataclass
class TestConditions:
    """IEC Test Conditions"""
    min_temp: float = -45.0  # °C
    max_temp: float = 105.0  # °C
    temp_uniformity: float = 2.0  # ±°C
    min_humidity: float = 40.0  # %RH
    max_humidity: float = 95.0  # %RH
    humidity_uniformity: float = 3.0  # ±%RH
    uv_min_wavelength: float = 280.0  # nm
    uv_max_wavelength: float = 400.0  # nm
    uv_min_irradiance: float = 25.0  # W/m²
    uv_max_irradiance: float = 250.0  # W/m²
    uv_uniformity: float = 10.0  # ±%


class ThermalCalculations:
    """Thermal load and heat transfer calculations"""

    @staticmethod
    def chamber_heat_load(
        chamber: ChamberDimensions,
        ambient_temp: float,
        chamber_temp: float,
        wall_thickness: float = 0.15,  # meters
        insulation_k: float = 0.024  # W/(m·K) for polyurethane foam
    ) -> Dict[str, float]:
        """
        Calculate heat transfer through chamber walls

        Args:
            chamber: Chamber dimensions
            ambient_temp: Outside temperature (°C)
            chamber_temp: Inside temperature (°C)
            wall_thickness: Insulation thickness (m)
            insulation_k: Thermal conductivity W/(m·K)

        Returns:
            Dictionary with heat transfer components
        """
        temp_diff = abs(chamber_temp - ambient_temp)

        # Conductive heat transfer: Q = k * A * ΔT / L
        q_conduction = (insulation_k * chamber.surface_area * temp_diff) / wall_thickness

        # Add thermal bridging (15% extra)
        q_thermal_bridge = q_conduction * 0.15

        # Add infiltration losses (assume 0.5 air changes per hour)
        air_mass = chamber.volume * AIR_DENSITY_STP
        q_infiltration = (0.5 * air_mass * AIR_SPECIFIC_HEAT * temp_diff) / 3600

        total_load = q_conduction + q_thermal_bridge + q_infiltration

        return {
            'conduction_W': q_conduction,
            'thermal_bridge_W': q_thermal_bridge,
            'infiltration_W': q_infiltration,
            'total_W': total_load,
            'total_kW': total_load / 1000
        }

    @staticmethod
    def product_heat_load(
        module: PVModuleSpec,
        irradiance: float = 1000.0,  # W/m² (1 sun)
        absorption_coeff: float = 0.90  # 90% absorption
    ) -> Dict[str, float]:
        """
        Calculate heat load from PV modules under illumination

        Args:
            module: PV module specifications
            irradiance: Solar/UV irradiance (W/m²)
            absorption_coeff: Fraction of light converted to heat

        Returns:
            Dictionary with product heat loads
        """
        # Heat generated = absorbed irradiance - electrical output
        absorbed_power = module.total_area * irradiance * absorption_coeff
        electrical_power = module.max_power * module.quantity / 1000  # kW

        heat_load = absorbed_power - (electrical_power * 1000)  # watts

        return {
            'absorbed_W': absorbed_power,
            'electrical_W': electrical_power * 1000,
            'heat_load_W': heat_load,
            'heat_load_kW': heat_load / 1000
        }

    @staticmethod
    def lighting_heat_load(
        uv_power: float,  # Total UV LED power (W)
        led_efficiency: float = 0.30  # 30% electrical to optical
    ) -> Dict[str, float]:
        """
        Calculate heat from UV LED systems

        Args:
            uv_power: Optical output power (W)
            led_efficiency: LED wall-plug efficiency

        Returns:
            Heat load from LEDs
        """
        # Electrical power = optical power / efficiency
        electrical_power = uv_power / led_efficiency

        # Heat = electrical - optical
        heat_load = electrical_power - uv_power

        return {
            'electrical_W': electrical_power,
            'optical_W': uv_power,
            'heat_load_W': heat_load,
            'heat_load_kW': heat_load / 1000
        }

    @staticmethod
    def total_refrigeration_load(
        chamber_load_kW: float,
        product_load_kW: float,
        lighting_load_kW: float,
        safety_factor: float = 1.2
    ) -> Dict[str, float]:
        """
        Calculate total refrigeration requirement

        Args:
            chamber_load_kW: Chamber heat transfer (kW)
            product_load_kW: Product heat load (kW)
            lighting_load_kW: Lighting heat load (kW)
            safety_factor: Safety margin (typically 1.15-1.25)

        Returns:
            Total refrigeration requirements
        """
        base_load = chamber_load_kW + product_load_kW + lighting_load_kW
        design_load = base_load * safety_factor

        # Convert to tons of refrigeration (1 TR = 3.517 kW)
        tons_refrigeration = design_load / 3.517

        return {
            'chamber_kW': chamber_load_kW,
            'product_kW': product_load_kW,
            'lighting_kW': lighting_load_kW,
            'base_total_kW': base_load,
            'safety_factor': safety_factor,
            'design_load_kW': design_load,
            'tons_refrigeration': tons_refrigeration
        }


class HumidityCalculations:
    """Humidity and psychrometric calculations"""

    @staticmethod
    def saturation_vapor_pressure(temp_celsius: float) -> float:
        """
        Calculate saturation vapor pressure using Magnus formula

        Args:
            temp_celsius: Temperature in °C

        Returns:
            Saturation vapor pressure in Pa
        """
        # Magnus formula
        return 610.7 * math.exp((17.27 * temp_celsius) / (temp_celsius + 237.3))

    @staticmethod
    def absolute_humidity(temp_celsius: float, relative_humidity: float) -> float:
        """
        Calculate absolute humidity (g/m³)

        Args:
            temp_celsius: Temperature in °C
            relative_humidity: Relative humidity (0-100%)

        Returns:
            Absolute humidity in g/m³
        """
        p_sat = HumidityCalculations.saturation_vapor_pressure(temp_celsius)
        p_vapor = p_sat * (relative_humidity / 100.0)

        # Absolute humidity = (p_vapor * M_water) / (R * T)
        # Simplified: AH ≈ (2.16679 * p_vapor) / T_kelvin
        temp_kelvin = temp_celsius + 273.15
        abs_humidity = (2.16679 * p_vapor) / temp_kelvin

        return abs_humidity

    @staticmethod
    def humidity_load(
        chamber: ChamberDimensions,
        current_rh: float,
        target_rh: float,
        temp_celsius: float
    ) -> Dict[str, float]:
        """
        Calculate energy required for humidification/dehumidification

        Args:
            chamber: Chamber dimensions
            current_rh: Current relative humidity (%)
            target_rh: Target relative humidity (%)
            temp_celsius: Chamber temperature (°C)

        Returns:
            Humidity control energy requirements
        """
        ah_current = HumidityCalculations.absolute_humidity(temp_celsius, current_rh)
        ah_target = HumidityCalculations.absolute_humidity(temp_celsius, target_rh)

        mass_water = abs(ah_target - ah_current) * chamber.volume / 1000  # kg

        if target_rh > current_rh:
            # Humidification
            energy = mass_water * WATER_LATENT_HEAT_VAPORIZATION / 1000  # kJ
            operation = "humidification"
        else:
            # Dehumidification (condensation + cooling)
            energy = mass_water * WATER_LATENT_HEAT_VAPORIZATION / 1000  # kJ
            operation = "dehumidification"

        return {
            'operation': operation,
            'water_mass_kg': mass_water,
            'energy_kJ': energy,
            'energy_kWh': energy / 3600
        }


class AirflowCalculations:
    """Airflow and uniformity calculations"""

    @staticmethod
    def required_airflow(
        chamber: ChamberDimensions,
        heat_load_kW: float,
        temp_rise: float = 5.0  # °C temperature rise across load
    ) -> Dict[str, float]:
        """
        Calculate required airflow for temperature uniformity

        Args:
            chamber: Chamber dimensions
            heat_load_kW: Total heat load (kW)
            temp_rise: Allowable temperature rise (°C)

        Returns:
            Required airflow rates
        """
        # Q = m_dot * c_p * ΔT
        # m_dot = Q / (c_p * ΔT)

        heat_load_W = heat_load_kW * 1000
        mass_flow = heat_load_W / (AIR_SPECIFIC_HEAT * temp_rise)  # kg/s

        # Volume flow = mass flow / density
        volume_flow_m3s = mass_flow / AIR_DENSITY_STP
        volume_flow_m3h = volume_flow_m3s * 3600

        # Air velocity (assume flow through chamber cross-section)
        cross_section = chamber.width * chamber.height
        velocity = volume_flow_m3s / cross_section

        # Air changes per hour
        air_changes = volume_flow_m3h / chamber.volume

        return {
            'mass_flow_kg_s': mass_flow,
            'volume_flow_m3_s': volume_flow_m3s,
            'volume_flow_m3_h': volume_flow_m3h,
            'velocity_m_s': velocity,
            'air_changes_per_hour': air_changes
        }

    @staticmethod
    def fan_power(
        volume_flow_m3h: float,
        static_pressure_Pa: float = 250,  # Typical for HVAC
        fan_efficiency: float = 0.65
    ) -> Dict[str, float]:
        """
        Calculate fan power requirements

        Args:
            volume_flow_m3h: Volumetric flow rate (m³/h)
            static_pressure_Pa: Static pressure (Pa)
            fan_efficiency: Fan total efficiency

        Returns:
            Fan power requirements
        """
        volume_flow_m3s = volume_flow_m3h / 3600

        # Hydraulic power = Q * ΔP
        hydraulic_power = volume_flow_m3s * static_pressure_Pa  # watts

        # Shaft power = hydraulic power / efficiency
        shaft_power = hydraulic_power / fan_efficiency

        return {
            'hydraulic_power_W': hydraulic_power,
            'shaft_power_W': shaft_power,
            'shaft_power_kW': shaft_power / 1000
        }


class UVCalculations:
    """UV irradiance and optical calculations"""

    @staticmethod
    def led_array_design(
        target_area: float,  # m²
        target_irradiance: float,  # W/m²
        led_power: float = 10,  # watts per LED
        led_efficiency: float = 0.30,
        uniformity_target: float = 0.10  # ±10%
    ) -> Dict[str, float]:
        """
        Design UV LED array for target irradiance

        Args:
            target_area: Illumination area (m²)
            target_irradiance: Target UV irradiance (W/m²)
            led_power: Electrical power per LED (W)
            led_efficiency: LED wall-plug efficiency
            uniformity_target: Required uniformity (fraction)

        Returns:
            LED array specifications
        """
        # Total optical power needed
        total_optical = target_area * target_irradiance

        # Add margin for uniformity (need higher average for ±10% uniformity)
        margin_factor = 1 + uniformity_target
        total_optical_design = total_optical * margin_factor

        # Optical power per LED
        optical_per_led = led_power * led_efficiency

        # Number of LEDs
        num_leds = math.ceil(total_optical_design / optical_per_led)

        # Total electrical power
        total_electrical = num_leds * led_power

        return {
            'target_optical_W': total_optical,
            'design_optical_W': total_optical_design,
            'optical_per_led_W': optical_per_led,
            'num_leds': num_leds,
            'total_electrical_W': total_electrical,
            'total_electrical_kW': total_electrical / 1000
        }

    @staticmethod
    def inverse_square_law(
        source_power: float,  # watts
        distance: float,  # meters
        cosine_correction: float = 1.0
    ) -> float:
        """
        Calculate irradiance using inverse square law

        Args:
            source_power: Source power (W)
            distance: Distance from source (m)
            cosine_correction: Cosine of incident angle

        Returns:
            Irradiance in W/m²
        """
        # E = P / (4π * r²) * cos(θ)
        # For LED with Lambertian distribution
        irradiance = (source_power * cosine_correction) / (4 * math.pi * distance**2)
        return irradiance


class IECValidation:
    """IEC 61215/61730 standards validation"""

    @staticmethod
    def validate_temperature_range(min_temp: float, max_temp: float) -> Dict[str, any]:
        """Validate against IEC 61215-2 temperature cycling requirements"""
        iec_min = -40.0
        iec_max = 85.0
        extended_max = 105.0  # Extended range

        valid_min = min_temp <= iec_min
        valid_max = max_temp >= iec_max
        extended = max_temp >= extended_max

        return {
            'valid': valid_min and valid_max,
            'extended_range': extended,
            'min_compliant': valid_min,
            'max_compliant': valid_max,
            'iec_min_required': iec_min,
            'iec_max_required': iec_max,
            'chamber_min': min_temp,
            'chamber_max': max_temp
        }

    @staticmethod
    def validate_humidity_range(min_rh: float, max_rh: float) -> Dict[str, any]:
        """Validate against IEC 61215-2 damp heat requirements"""
        iec_min = 85.0  # For damp heat test

        valid = max_rh >= iec_min

        return {
            'valid': valid,
            'iec_required': iec_min,
            'chamber_min': min_rh,
            'chamber_max': max_rh
        }

    @staticmethod
    def validate_uv_spectrum(min_wavelength: float, max_wavelength: float) -> Dict[str, any]:
        """Validate against IEC 61215-2 UV preconditioning"""
        iec_min = 280.0  # nm
        iec_max = 400.0  # nm (UV-A + UV-B)

        valid = min_wavelength <= iec_min and max_wavelength >= iec_max

        return {
            'valid': valid,
            'iec_min_wavelength': iec_min,
            'iec_max_wavelength': iec_max,
            'chamber_min': min_wavelength,
            'chamber_max': max_wavelength,
            'spectrum': 'UV-A + UV-B' if valid else 'Incomplete'
        }


# Unit Conversion Utilities
class UnitConverter:
    """Unit conversion helpers"""

    @staticmethod
    def celsius_to_kelvin(celsius: float) -> float:
        return celsius + 273.15

    @staticmethod
    def kelvin_to_celsius(kelvin: float) -> float:
        return kelvin - 273.15

    @staticmethod
    def kw_to_tons_refrigeration(kw: float) -> float:
        """Convert kW to tons of refrigeration (1 TR = 3.517 kW)"""
        return kw / 3.517

    @staticmethod
    def watts_to_kw(watts: float) -> float:
        return watts / 1000

    @staticmethod
    def m3s_to_m3h(m3s: float) -> float:
        """Convert m³/s to m³/h"""
        return m3s * 3600

    @staticmethod
    def m3h_to_cfm(m3h: float) -> float:
        """Convert m³/h to CFM (cubic feet per minute)"""
        return m3h * 0.5886
