"""
UV Optical System Module for PV Chamber Configurator

This module provides comprehensive UV LED system design, analysis, and optimization
for photovoltaic module testing chambers. Includes uniformity calculations, spectrum
analysis, LED aging models, and robot path planning.

Author: PV Chamber Configurator System
Version: 2.0
Compliance: IEC 60904-9, IEC 61215, IEC 61730
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional, Any
from dataclasses import dataclass
from scipy.interpolate import griddata
from scipy.optimize import minimize
import math


@dataclass
class LEDSpecification:
    """UV LED technical specifications."""
    wavelength_peak: float = 365.0  # nm
    wavelength_range: Tuple[float, float] = (280.0, 400.0)  # nm
    power_per_led: float = 100.0  # W
    beam_angle: float = 120.0  # degrees
    efficiency: float = 0.45  # 45%
    lifespan_l80: float = 50000.0  # hours
    cost_per_led: float = 15000.0  # ₹


@dataclass
class ChamberDimensions:
    """Test chamber physical dimensions."""
    length: float  # mm
    width: float  # mm
    height: float  # mm
    led_mounting_height: float = 300.0  # mm above test plane


@dataclass
class UniformityGrid:
    """9-point uniformity measurement grid per IEC 60904-9."""
    rows: int = 3
    cols: int = 3

    @property
    def total_points(self) -> int:
        return self.rows * self.cols


class UVLEDLayoutCalculator:
    """
    Calculate optimal UV LED array layout for uniform irradiance.

    Uses inverse square law and beam pattern modeling to determine
    LED positions that achieve ±10% uniformity target across the test plane.
    """

    def __init__(
        self,
        chamber: ChamberDimensions,
        led_spec: LEDSpecification,
        target_irradiance: float = 60.0  # W/m²
    ):
        """
        Initialize LED layout calculator.

        Args:
            chamber: Chamber dimensions
            led_spec: LED technical specifications
            target_irradiance: Target average irradiance (W/m²)
        """
        self.chamber = chamber
        self.led_spec = led_spec
        self.target_irradiance = target_irradiance
        self.led_positions: Optional[List[Tuple[float, float, float]]] = None
        self.num_leds: Optional[int] = None

    def calculate_optimal_layout(self) -> Dict[str, Any]:
        """
        Calculate optimal LED array layout.

        Returns:
            Dictionary containing:
                - num_leds: Total number of LEDs
                - rows: Number of LED rows
                - cols: Number of LED columns
                - spacing_x: LED spacing in X direction (mm)
                - spacing_y: LED spacing in Y direction (mm)
                - positions: List of (x, y, z) LED coordinates
                - coverage_area: Effective coverage area (m²)
        """
        # Calculate test plane area
        area_m2 = (self.chamber.length * self.chamber.width) / 1e6

        # Calculate total UV power needed
        total_power_needed = self.target_irradiance * area_m2

        # Calculate number of LEDs (with efficiency factor)
        uv_power_per_led = self.led_spec.power_per_led * self.led_spec.efficiency
        self.num_leds = int(np.ceil(total_power_needed / uv_power_per_led))

        # Ensure minimum number for uniformity
        if self.num_leds < 16:
            self.num_leds = 16

        # Calculate rows and columns (prefer rectangular layout)
        aspect_ratio = self.chamber.length / self.chamber.width
        cols = int(np.ceil(np.sqrt(self.num_leds * aspect_ratio)))
        rows = int(np.ceil(self.num_leds / cols))

        # Adjust for actual number of LEDs
        self.num_leds = rows * cols

        # Calculate LED spacing
        spacing_x = self.chamber.length / (cols + 1)
        spacing_y = self.chamber.width / (rows + 1)

        # Generate LED positions
        self.led_positions = []
        z_height = self.chamber.led_mounting_height

        for row in range(rows):
            for col in range(cols):
                x = (col + 1) * spacing_x
                y = (row + 1) * spacing_y
                self.led_positions.append((x, y, z_height))

        return {
            'num_leds': self.num_leds,
            'rows': rows,
            'cols': cols,
            'spacing_x': spacing_x,
            'spacing_y': spacing_y,
            'positions': self.led_positions,
            'coverage_area': area_m2,
            'total_uv_power': self.num_leds * uv_power_per_led,
            'predicted_avg_irradiance': (self.num_leds * uv_power_per_led) / area_m2
        }

    def calculate_single_led_irradiance(
        self,
        led_pos: Tuple[float, float, float],
        point: Tuple[float, float, float]
    ) -> float:
        """
        Calculate irradiance at a point from a single LED.

        Uses inverse square law with cosine correction for incident angle.

        Args:
            led_pos: LED position (x, y, z) in mm
            point: Measurement point (x, y, z) in mm

        Returns:
            Irradiance at point (W/m²)
        """
        # Calculate distance vector
        dx = point[0] - led_pos[0]
        dy = point[1] - led_pos[1]
        dz = point[2] - led_pos[2]

        # Distance in meters
        distance = np.sqrt(dx**2 + dy**2 + dz**2) / 1000.0

        if distance < 0.01:  # Avoid division by zero
            distance = 0.01

        # Calculate incident angle (angle from normal)
        if dz == 0:
            cos_theta = 0
        else:
            cos_theta = abs(dz) / (distance * 1000.0)

        # Check if within beam angle
        angle_deg = np.arccos(cos_theta) * 180.0 / np.pi
        if angle_deg > self.led_spec.beam_angle / 2:
            return 0.0

        # UV power output per LED
        uv_power = self.led_spec.power_per_led * self.led_spec.efficiency

        # Lambertian distribution approximation
        # I = I0 * cos(θ) / d²
        irradiance = (uv_power * cos_theta) / (4 * np.pi * distance**2)

        # Apply beam angle factor (Gaussian-like falloff)
        beam_factor = np.cos(angle_deg * np.pi / 180.0) ** 2

        return irradiance * beam_factor

    def get_layout_summary(self) -> str:
        """
        Get human-readable summary of LED layout.

        Returns:
            Formatted string with layout details
        """
        if not self.led_positions:
            return "Layout not yet calculated. Call calculate_optimal_layout() first."

        layout = self.calculate_optimal_layout()

        summary = f"""
UV LED Layout Summary
{'=' * 50}
Chamber Dimensions: {self.chamber.length} × {self.chamber.width} mm
Test Plane Area: {layout['coverage_area']:.2f} m²
Target Irradiance: {self.target_irradiance} W/m²

LED Configuration:
  Total LEDs: {layout['num_leds']} units
  Array Layout: {layout['rows']} rows × {layout['cols']} columns
  Spacing: {layout['spacing_x']:.1f} mm (X) × {layout['spacing_y']:.1f} mm (Y)
  Mounting Height: {self.chamber.led_mounting_height} mm

Power Requirements:
  Power per LED: {self.led_spec.power_per_led} W
  UV Output per LED: {self.led_spec.power_per_led * self.led_spec.efficiency:.1f} W
  Total UV Power: {layout['total_uv_power']:.1f} W
  Predicted Avg Irradiance: {layout['predicted_avg_irradiance']:.1f} W/m²
        """
        return summary.strip()


class UniformityGridMapper:
    """
    Calculate and analyze UV irradiance uniformity using 9-point grid.

    Implements IEC 60904-9 standard for solar simulator uniformity testing.
    """

    def __init__(
        self,
        chamber: ChamberDimensions,
        led_calculator: UVLEDLayoutCalculator,
        grid: UniformityGrid = UniformityGrid()
    ):
        """
        Initialize uniformity grid mapper.

        Args:
            chamber: Chamber dimensions
            led_calculator: LED layout calculator with positions
            grid: Uniformity measurement grid configuration
        """
        self.chamber = chamber
        self.led_calculator = led_calculator
        self.grid = grid
        self.grid_points: Optional[List[Tuple[float, float, float]]] = None
        self.irradiance_values: Optional[np.ndarray] = None

    def generate_grid_points(self) -> List[Tuple[float, float, float]]:
        """
        Generate 9-point uniformity measurement grid.

        Grid layout follows IEC 60904-9:
        - 3×3 grid with edge margins
        - Points at 1/6, 1/2, 5/6 positions

        Returns:
            List of (x, y, z) grid point coordinates in mm
        """
        self.grid_points = []

        # Grid point positions at 1/6, 1/2, 5/6 of dimensions
        x_positions = [
            self.chamber.length * 1/6,
            self.chamber.length * 1/2,
            self.chamber.length * 5/6
        ]

        y_positions = [
            self.chamber.width * 1/6,
            self.chamber.width * 1/2,
            self.chamber.width * 5/6
        ]

        # Test plane at z=0
        z = 0.0

        for y in y_positions:
            for x in x_positions:
                self.grid_points.append((x, y, z))

        return self.grid_points

    def calculate_irradiance_at_points(self) -> np.ndarray:
        """
        Calculate irradiance at all 9 grid points.

        Returns:
            Array of irradiance values (W/m²) at each grid point
        """
        if not self.grid_points:
            self.generate_grid_points()

        if not self.led_calculator.led_positions:
            self.led_calculator.calculate_optimal_layout()

        self.irradiance_values = np.zeros(len(self.grid_points))

        for i, point in enumerate(self.grid_points):
            total_irradiance = 0.0

            # Sum contributions from all LEDs
            for led_pos in self.led_calculator.led_positions:
                irradiance = self.led_calculator.calculate_single_led_irradiance(
                    led_pos, point
                )
                total_irradiance += irradiance

            self.irradiance_values[i] = total_irradiance

        return self.irradiance_values

    def analyze_uniformity(self) -> Dict[str, Any]:
        """
        Analyze uniformity metrics per IEC 60904-9.

        Returns:
            Dictionary containing:
                - avg_irradiance: Average irradiance (W/m²)
                - max_irradiance: Maximum irradiance (W/m²)
                - min_irradiance: Minimum irradiance (W/m²)
                - std_deviation: Standard deviation (W/m²)
                - non_uniformity_pct: Non-uniformity percentage
                - passes_10pct: Boolean, passes ±10% criterion
                - passes_5pct: Boolean, passes ±5% criterion (excellent)
                - grid_data: DataFrame with point-by-point data
        """
        if self.irradiance_values is None:
            self.calculate_irradiance_at_points()

        avg_irr = np.mean(self.irradiance_values)
        max_irr = np.max(self.irradiance_values)
        min_irr = np.min(self.irradiance_values)
        std_irr = np.std(self.irradiance_values)

        # Non-uniformity calculation: (Max - Min) / Avg × 100%
        non_uniformity = ((max_irr - min_irr) / avg_irr) * 100.0

        # Check compliance
        passes_10pct = non_uniformity <= 10.0
        passes_5pct = non_uniformity <= 5.0

        # Create detailed grid data
        grid_data = []
        for i, (point, irr) in enumerate(zip(self.grid_points, self.irradiance_values)):
            deviation_pct = ((irr - avg_irr) / avg_irr) * 100.0
            grid_data.append({
                'Point': i + 1,
                'X (mm)': point[0],
                'Y (mm)': point[1],
                'Irradiance (W/m²)': irr,
                'Deviation (%)': deviation_pct,
                'Status': self._get_status(abs(deviation_pct))
            })

        df_grid = pd.DataFrame(grid_data)

        return {
            'avg_irradiance': avg_irr,
            'max_irradiance': max_irr,
            'min_irradiance': min_irr,
            'std_deviation': std_irr,
            'non_uniformity_pct': non_uniformity,
            'passes_10pct': passes_10pct,
            'passes_5pct': passes_5pct,
            'grid_data': df_grid,
            'irradiance_array': self.irradiance_values.reshape(self.grid.rows, self.grid.cols)
        }

    def _get_status(self, deviation_pct: float) -> str:
        """Get status label based on deviation percentage."""
        if deviation_pct <= 5.0:
            return "Excellent"
        elif deviation_pct <= 10.0:
            return "Acceptable"
        else:
            return "Non-compliant"

    def get_recommendations(self) -> List[str]:
        """
        Get recommendations for improving uniformity.

        Returns:
            List of recommendation strings
        """
        analysis = self.analyze_uniformity()
        recommendations = []

        if not analysis['passes_10pct']:
            recommendations.append(
                "⚠️ CRITICAL: Uniformity does not meet ±10% IEC 60904-9 requirement"
            )
            recommendations.append(
                f"  → Increase number of LEDs from {self.led_calculator.num_leds} to " +
                f"{int(self.led_calculator.num_leds * 1.3)}"
            )
            recommendations.append(
                f"  → Reduce LED mounting height from {self.chamber.led_mounting_height}mm to " +
                f"{int(self.chamber.led_mounting_height * 0.85)}mm"
            )
        elif not analysis['passes_5pct']:
            recommendations.append(
                "✓ Uniformity meets ±10% requirement but could be improved to ±5%"
            )
            recommendations.append(
                f"  → Consider adding {int(self.led_calculator.num_leds * 0.15)} more LEDs for excellent uniformity"
            )
        else:
            recommendations.append(
                "✓ Excellent uniformity achieved (±5%)"
            )
            recommendations.append(
                "  → No changes recommended. System meets premium standards."
            )

        # Check for edge effects
        edge_points = [0, 2, 6, 8]  # Corner points
        center_point = 4

        edge_avg = np.mean([self.irradiance_values[i] for i in edge_points])
        center_val = self.irradiance_values[center_point]

        if abs(edge_avg - center_val) / center_val > 0.08:
            recommendations.append(
                "⚠️ Edge uniformity issue detected"
            )
            recommendations.append(
                "  → Add perimeter LEDs or adjust edge LED power +10%"
            )

        return recommendations


class SpectrumAnalyzer:
    """
    Analyze UV spectrum distribution and wavelength characteristics.

    Calculates UVA/UVB ratios and spectral power distribution for
    solar simulation accuracy.
    """

    def __init__(self, led_spec: LEDSpecification):
        """
        Initialize spectrum analyzer.

        Args:
            led_spec: LED technical specifications
        """
        self.led_spec = led_spec

    def generate_spectral_distribution(
        self,
        resolution: float = 1.0
    ) -> pd.DataFrame:
        """
        Generate spectral power distribution (SPD).

        Models UV LED spectrum as Gaussian distribution around peak wavelength.

        Args:
            resolution: Wavelength step size (nm)

        Returns:
            DataFrame with wavelength (nm) and relative intensity
        """
        wavelengths = np.arange(
            self.led_spec.wavelength_range[0],
            self.led_spec.wavelength_range[1],
            resolution
        )

        # Gaussian spectrum model
        # FWHM (Full Width Half Maximum) typically 10-15nm for UV LEDs
        fwhm = 12.0
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))

        # Gaussian distribution
        intensities = np.exp(
            -((wavelengths - self.led_spec.wavelength_peak) ** 2) / (2 * sigma ** 2)
        )

        # Normalize to 0-100%
        intensities = (intensities / np.max(intensities)) * 100.0

        df = pd.DataFrame({
            'Wavelength (nm)': wavelengths,
            'Relative Intensity (%)': intensities
        })

        return df

    def calculate_uva_uvb_ratio(self) -> Dict[str, float]:
        """
        Calculate UVA and UVB content percentages.

        UVA: 315-400 nm
        UVB: 280-315 nm

        Returns:
            Dictionary with UVA_pct, UVB_pct, and ratio
        """
        spd = self.generate_spectral_distribution(resolution=0.5)

        # Separate UVA and UVB regions
        uva_mask = (spd['Wavelength (nm)'] >= 315) & (spd['Wavelength (nm)'] <= 400)
        uvb_mask = (spd['Wavelength (nm)'] >= 280) & (spd['Wavelength (nm)'] < 315)

        uva_power = np.trapz(
            spd.loc[uva_mask, 'Relative Intensity (%)'],
            spd.loc[uva_mask, 'Wavelength (nm)']
        )

        uvb_power = np.trapz(
            spd.loc[uvb_mask, 'Relative Intensity (%)'],
            spd.loc[uvb_mask, 'Wavelength (nm)']
        )

        total_power = uva_power + uvb_power

        uva_pct = (uva_power / total_power) * 100.0
        uvb_pct = (uvb_power / total_power) * 100.0

        return {
            'UVA_pct': uva_pct,
            'UVB_pct': uvb_pct,
            'UVA_UVB_ratio': uva_pct / uvb_pct if uvb_pct > 0 else float('inf'),
            'weighted_avg_wavelength': self._calculate_weighted_avg(spd),
            'peak_wavelength': self.led_spec.wavelength_peak
        }

    def _calculate_weighted_avg(self, spd: pd.DataFrame) -> float:
        """Calculate weighted average wavelength."""
        weighted_sum = np.sum(
            spd['Wavelength (nm)'] * spd['Relative Intensity (%)']
        )
        total_intensity = np.sum(spd['Relative Intensity (%)'])
        return weighted_sum / total_intensity

    def get_spectrum_summary(self) -> str:
        """
        Get human-readable spectrum summary.

        Returns:
            Formatted summary string
        """
        ratios = self.calculate_uva_uvb_ratio()

        summary = f"""
UV Spectrum Analysis
{'=' * 50}
Peak Wavelength: {ratios['peak_wavelength']} nm
Weighted Avg Wavelength: {ratios['weighted_avg_wavelength']:.1f} nm

UVA Content (315-400nm): {ratios['UVA_pct']:.1f}%
UVB Content (280-315nm): {ratios['UVB_pct']:.1f}%
UVA/UVB Ratio: {ratios['UVA_UVB_ratio']:.1f}

Compliance Status:
  UVA Target (90-97%): {'✓ PASS' if 90 <= ratios['UVA_pct'] <= 97 else '✗ FAIL'}
  UVB Target (3-10%): {'✓ PASS' if 3 <= ratios['UVB_pct'] <= 10 else '✗ FAIL'}
        """
        return summary.strip()


class LEDAgingModel:
    """
    Model LED degradation and predict maintenance requirements.

    Uses exponential decay model: L(t) = L0 × exp(-t/τ)
    where τ is the time constant derived from L80 @ 50,000 hours
    """

    def __init__(
        self,
        led_spec: LEDSpecification,
        num_leds: int,
        operating_hours: float = 0.0
    ):
        """
        Initialize LED aging model.

        Args:
            led_spec: LED specifications
            num_leds: Total number of LEDs in system
            operating_hours: Current operating hours
        """
        self.led_spec = led_spec
        self.num_leds = num_leds
        self.operating_hours = operating_hours

        # Calculate time constant from L80 specification
        # L80 means 80% output at specified lifetime
        # 0.80 = exp(-t_L80 / τ)
        # τ = -t_L80 / ln(0.80)
        self.time_constant = -self.led_spec.lifespan_l80 / np.log(0.80)

    def calculate_current_output(self) -> float:
        """
        Calculate current LED output percentage.

        Returns:
            Current output as percentage of original (0-100%)
        """
        output_fraction = np.exp(-self.operating_hours / self.time_constant)
        return output_fraction * 100.0

    def calculate_remaining_lifetime(self, threshold: float = 80.0) -> float:
        """
        Calculate remaining operating hours until threshold.

        Args:
            threshold: Output threshold percentage (default 80% for L80)

        Returns:
            Remaining hours until threshold reached
        """
        # Solve: threshold/100 = exp(-t_remaining / τ)
        # t_remaining = -τ × ln(threshold/100) - current_hours

        target_hours = -self.time_constant * np.log(threshold / 100.0)
        remaining = target_hours - self.operating_hours

        return max(0, remaining)

    def predict_degradation_curve(
        self,
        time_points: int = 100
    ) -> pd.DataFrame:
        """
        Generate LED degradation curve data.

        Args:
            time_points: Number of time points to calculate

        Returns:
            DataFrame with hours and output percentage
        """
        max_hours = self.led_spec.lifespan_l80 * 1.5
        hours = np.linspace(0, max_hours, time_points)

        outputs = np.exp(-hours / self.time_constant) * 100.0

        df = pd.DataFrame({
            'Operating Hours': hours,
            'Output (%)': outputs
        })

        return df

    def calculate_maintenance_cost(
        self,
        years: int = 10,
        annual_usage_hours: float = 2000.0,
        labor_cost_per_led: float = 500.0
    ) -> Dict[str, Any]:
        """
        Calculate maintenance cost projection.

        Args:
            years: Projection period (years)
            annual_usage_hours: Operating hours per year
            labor_cost_per_led: Labor cost for LED replacement (₹)

        Returns:
            Dictionary with cost breakdown
        """
        total_hours = years * annual_usage_hours

        # Calculate number of replacement cycles
        replacement_cycles = int(total_hours / self.led_spec.lifespan_l80)

        # Costs
        led_material_cost = self.num_leds * self.led_spec.cost_per_led
        led_labor_cost = self.num_leds * labor_cost_per_led
        total_replacement_cost = led_material_cost + led_labor_cost

        total_maintenance_cost = replacement_cycles * total_replacement_cost

        return {
            'projection_years': years,
            'total_operating_hours': total_hours,
            'replacement_cycles': replacement_cycles,
            'cost_per_replacement': total_replacement_cost,
            'total_maintenance_cost': total_maintenance_cost,
            'annual_avg_cost': total_maintenance_cost / years,
            'next_replacement_hours': self.led_spec.lifespan_l80 - (
                self.operating_hours % self.led_spec.lifespan_l80
            )
        }

    def get_aging_summary(self) -> str:
        """
        Get human-readable aging status summary.

        Returns:
            Formatted summary string
        """
        current_output = self.calculate_current_output()
        remaining_hours = self.calculate_remaining_lifetime()
        remaining_years = remaining_hours / 2000.0  # Assume 2000 hrs/year

        summary = f"""
LED Aging Analysis
{'=' * 50}
Current Operating Hours: {self.operating_hours:,.0f} hrs
Current Output Level: {current_output:.1f}%
Degradation: {100 - current_output:.1f}%

Remaining Lifetime (L80):
  Hours: {remaining_hours:,.0f} hrs
  Years (@ 2000 hrs/yr): {remaining_years:.1f} years

Status: {'🟢 GOOD' if current_output > 90 else '🟡 FAIR' if current_output > 80 else '🔴 REPLACE'}
        """
        return summary.strip()


class PowerRequirementCalculator:
    """
    Calculate electrical power requirements and energy costs.

    Includes LED power, driver losses, and operational costs.
    """

    def __init__(
        self,
        num_leds: int,
        led_spec: LEDSpecification,
        driver_efficiency: float = 0.92,
        power_factor: float = 0.95
    ):
        """
        Initialize power calculator.

        Args:
            num_leds: Total number of LEDs
            led_spec: LED specifications
            driver_efficiency: LED driver efficiency (default 92%)
            power_factor: System power factor (default 0.95)
        """
        self.num_leds = num_leds
        self.led_spec = led_spec
        self.driver_efficiency = driver_efficiency
        self.power_factor = power_factor

    def calculate_power_requirements(self) -> Dict[str, float]:
        """
        Calculate comprehensive power requirements.

        Returns:
            Dictionary with power calculations in kW
        """
        # LED power consumption
        led_power = (self.num_leds * self.led_spec.power_per_led) / 1000.0  # kW

        # Account for driver losses
        input_power = led_power / self.driver_efficiency  # kW

        # Apparent power (considering power factor)
        apparent_power = input_power / self.power_factor  # kVA

        return {
            'led_power_kw': led_power,
            'driver_losses_kw': input_power - led_power,
            'total_input_power_kw': input_power,
            'apparent_power_kva': apparent_power,
            'power_factor': self.power_factor,
            'driver_efficiency': self.driver_efficiency
        }

    def calculate_energy_cost(
        self,
        annual_usage_hours: float = 2000.0,
        electricity_rate: float = 8.0  # ₹/kWh
    ) -> Dict[str, float]:
        """
        Calculate annual energy consumption and costs.

        Args:
            annual_usage_hours: Operating hours per year
            electricity_rate: Electricity cost (₹/kWh)

        Returns:
            Dictionary with energy and cost data
        """
        power_req = self.calculate_power_requirements()

        # Annual energy consumption
        annual_energy_kwh = power_req['total_input_power_kw'] * annual_usage_hours

        # Annual cost
        annual_cost = annual_energy_kwh * electricity_rate

        # Daily metrics
        daily_hours = annual_usage_hours / 365.0
        daily_energy_kwh = annual_energy_kwh / 365.0
        daily_cost = annual_cost / 365.0

        return {
            'annual_usage_hours': annual_usage_hours,
            'annual_energy_kwh': annual_energy_kwh,
            'annual_cost_inr': annual_cost,
            'daily_hours': daily_hours,
            'daily_energy_kwh': daily_energy_kwh,
            'daily_cost_inr': daily_cost,
            'electricity_rate': electricity_rate,
            'cost_per_hour': annual_cost / annual_usage_hours
        }

    def get_power_summary(self, annual_hours: float = 2000.0) -> str:
        """
        Get human-readable power summary.

        Returns:
            Formatted summary string
        """
        power = self.calculate_power_requirements()
        energy = self.calculate_energy_cost(annual_hours)

        summary = f"""
Power Requirements & Energy Cost Analysis
{'=' * 50}
LED Configuration:
  Number of LEDs: {self.num_leds}
  Power per LED: {self.led_spec.power_per_led} W
  Total LED Power: {power['led_power_kw']:.2f} kW

System Power:
  Driver Efficiency: {self.driver_efficiency * 100:.0f}%
  Driver Losses: {power['driver_losses_kw']:.2f} kW
  Total Input Power: {power['total_input_power_kw']:.2f} kW
  Apparent Power: {power['apparent_power_kva']:.2f} kVA
  Power Factor: {self.power_factor}

Annual Energy (@ {annual_hours:,.0f} hrs/year):
  Energy Consumption: {energy['annual_energy_kwh']:,.0f} kWh
  Energy Cost (@ ₹{energy['electricity_rate']}/kWh): ₹{energy['annual_cost_inr']:,.0f}
  Daily Cost: ₹{energy['daily_cost_inr']:.2f}
  Hourly Cost: ₹{energy['cost_per_hour']:.2f}
        """
        return summary.strip()


class UniformityRobotPathPlanner:
    """
    Plan robot measurement path for uniformity verification.

    Generates optimized 3-axis gantry robot path for 9-point
    uniformity measurements with G-code export capability.
    """

    def __init__(
        self,
        grid_points: List[Tuple[float, float, float]],
        dwell_time: float = 5.0,  # seconds
        travel_speed: float = 100.0,  # mm/s
        measurement_height: float = 0.0  # mm (test plane)
    ):
        """
        Initialize robot path planner.

        Args:
            grid_points: List of measurement points (x, y, z)
            dwell_time: Measurement dwell time per point (seconds)
            travel_speed: Robot travel speed (mm/s)
            measurement_height: Z-height for measurements (mm)
        """
        self.grid_points = grid_points
        self.dwell_time = dwell_time
        self.travel_speed = travel_speed
        self.measurement_height = measurement_height
        self.optimized_path: Optional[List[Tuple[float, float, float]]] = None

    def optimize_path(self, start_point: Tuple[float, float, float] = None) -> List[Tuple[float, float, float]]:
        """
        Optimize measurement path using nearest neighbor algorithm.

        Args:
            start_point: Starting position (default: first grid point)

        Returns:
            Optimized list of points
        """
        if start_point is None:
            start_point = self.grid_points[0]

        unvisited = self.grid_points.copy()
        path = [start_point]

        if start_point in unvisited:
            unvisited.remove(start_point)

        current = start_point

        while unvisited:
            # Find nearest unvisited point
            distances = [
                self._calculate_distance(current, point)
                for point in unvisited
            ]

            nearest_idx = np.argmin(distances)
            nearest_point = unvisited[nearest_idx]

            path.append(nearest_point)
            current = nearest_point
            unvisited.pop(nearest_idx)

        self.optimized_path = path
        return path

    def _calculate_distance(
        self,
        point1: Tuple[float, float, float],
        point2: Tuple[float, float, float]
    ) -> float:
        """Calculate Euclidean distance between two points."""
        return np.sqrt(
            (point2[0] - point1[0])**2 +
            (point2[1] - point1[1])**2 +
            (point2[2] - point1[2])**2
        )

    def calculate_cycle_time(self) -> Dict[str, float]:
        """
        Calculate total measurement cycle time.

        Returns:
            Dictionary with timing breakdown
        """
        if not self.optimized_path:
            self.optimize_path()

        # Calculate travel distances
        total_travel_distance = 0.0
        for i in range(len(self.optimized_path) - 1):
            distance = self._calculate_distance(
                self.optimized_path[i],
                self.optimized_path[i + 1]
            )
            total_travel_distance += distance

        # Calculate times
        travel_time = total_travel_distance / self.travel_speed
        measurement_time = len(self.grid_points) * self.dwell_time
        total_time = travel_time + measurement_time

        return {
            'total_travel_distance_mm': total_travel_distance,
            'travel_time_sec': travel_time,
            'measurement_time_sec': measurement_time,
            'total_cycle_time_sec': total_time,
            'total_cycle_time_min': total_time / 60.0,
            'num_points': len(self.grid_points)
        }

    def generate_gcode(self, feedrate: float = 6000.0) -> str:
        """
        Generate G-code for robot controller.

        Args:
            feedrate: Feed rate in mm/min (default 6000 mm/min = 100 mm/s)

        Returns:
            G-code string
        """
        if not self.optimized_path:
            self.optimize_path()

        gcode_lines = [
            "; UV Uniformity Measurement Path",
            "; Generated by PV Chamber Configurator",
            f"; Total Points: {len(self.optimized_path)}",
            f"; Dwell Time: {self.dwell_time} seconds",
            "",
            "G21 ; Set units to millimeters",
            "G90 ; Absolute positioning",
            "G28 ; Home all axes",
            f"F{feedrate} ; Set feed rate",
            ""
        ]

        for i, (x, y, z) in enumerate(self.optimized_path, start=1):
            gcode_lines.append(f"; Point {i}")
            gcode_lines.append(f"G0 X{x:.2f} Y{y:.2f} Z{z + 50:.2f} ; Move above point")
            gcode_lines.append(f"G1 Z{z:.2f} ; Lower to measurement height")
            gcode_lines.append(f"G4 P{self.dwell_time * 1000:.0f} ; Dwell (ms)")
            gcode_lines.append(f"G0 Z{z + 50:.2f} ; Retract")
            gcode_lines.append("")

        gcode_lines.extend([
            "G28 ; Return home",
            "M84 ; Disable motors",
            "; End of program"
        ])

        return "\n".join(gcode_lines)

    def get_path_dataframe(self) -> pd.DataFrame:
        """
        Get path as DataFrame for visualization.

        Returns:
            DataFrame with point sequence and coordinates
        """
        if not self.optimized_path:
            self.optimize_path()

        data = []
        for i, (x, y, z) in enumerate(self.optimized_path):
            data.append({
                'Sequence': i + 1,
                'X (mm)': x,
                'Y (mm)': y,
                'Z (mm)': z,
                'Action': 'Measure'
            })

        return pd.DataFrame(data)

    def get_path_summary(self) -> str:
        """
        Get human-readable path summary.

        Returns:
            Formatted summary string
        """
        timing = self.calculate_cycle_time()

        summary = f"""
Robot Path Planning Summary
{'=' * 50}
Measurement Configuration:
  Total Points: {timing['num_points']}
  Dwell Time: {self.dwell_time} seconds/point
  Travel Speed: {self.travel_speed} mm/s

Path Optimization:
  Total Travel Distance: {timing['total_travel_distance_mm']:.1f} mm
  Travel Time: {timing['travel_time_sec']:.1f} seconds
  Measurement Time: {timing['measurement_time_sec']:.1f} seconds

Total Cycle Time: {timing['total_cycle_time_min']:.2f} minutes ({timing['total_cycle_time_sec']:.1f} seconds)
        """
        return summary.strip()


# Utility functions

def create_default_uv_system(
    chamber_length: float = 3200.0,
    chamber_width: float = 2100.0,
    chamber_height: float = 2200.0,
    target_irradiance: float = 60.0
) -> Dict[str, Any]:
    """
    Create complete UV system with default configuration.

    Convenience function to initialize all components.

    Args:
        chamber_length: Chamber length (mm)
        chamber_width: Chamber width (mm)
        chamber_height: Chamber height (mm)
        target_irradiance: Target irradiance (W/m²)

    Returns:
        Dictionary with all system components
    """
    # Initialize components
    chamber = ChamberDimensions(
        length=chamber_length,
        width=chamber_width,
        height=chamber_height
    )

    led_spec = LEDSpecification()

    led_calculator = UVLEDLayoutCalculator(
        chamber=chamber,
        led_spec=led_spec,
        target_irradiance=target_irradiance
    )

    layout = led_calculator.calculate_optimal_layout()

    uniformity_mapper = UniformityGridMapper(
        chamber=chamber,
        led_calculator=led_calculator
    )

    uniformity_analysis = uniformity_mapper.analyze_uniformity()

    spectrum_analyzer = SpectrumAnalyzer(led_spec)

    aging_model = LEDAgingModel(
        led_spec=led_spec,
        num_leds=layout['num_leds']
    )

    power_calculator = PowerRequirementCalculator(
        num_leds=layout['num_leds'],
        led_spec=led_spec
    )

    robot_planner = UniformityRobotPathPlanner(
        grid_points=uniformity_mapper.grid_points
    )

    return {
        'chamber': chamber,
        'led_spec': led_spec,
        'led_calculator': led_calculator,
        'layout': layout,
        'uniformity_mapper': uniformity_mapper,
        'uniformity_analysis': uniformity_analysis,
        'spectrum_analyzer': spectrum_analyzer,
        'aging_model': aging_model,
        'power_calculator': power_calculator,
        'robot_planner': robot_planner
    }
