"""
Uncertainty Budget Calculator Module

This module implements measurement uncertainty calculations per:
- GUM (Guide to the Expression of Uncertainty in Measurement)
- ISO/IEC 17025:2017
- JCGM 100:2008

Supports Type A (statistical) and Type B (non-statistical) uncertainty evaluation.

Author: PV Chamber Configurator
Version: 1.0.0
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class DistributionType(Enum):
    """Probability distribution types for Type B uncertainty"""
    NORMAL = "normal"
    RECTANGULAR = "rectangular"
    TRIANGULAR = "triangular"
    U_SHAPED = "u-shaped"


class UncertaintyType(Enum):
    """Type of uncertainty evaluation"""
    TYPE_A = "A"  # Statistical evaluation
    TYPE_B = "B"  # Non-statistical evaluation


@dataclass
class UncertaintySource:
    """Individual source of uncertainty"""
    name: str
    value: float  # Uncertainty value (standard deviation or half-width)
    uncertainty_type: UncertaintyType
    distribution: DistributionType = DistributionType.NORMAL
    degrees_of_freedom: Optional[float] = None
    sensitivity_coefficient: float = 1.0  # ci in GUM
    description: str = ""


@dataclass
class UncertaintyBudget:
    """Complete uncertainty budget with all sources"""
    parameter_name: str
    measured_value: float
    unit: str
    sources: List[UncertaintySource]
    coverage_factor: float = 2.0  # k value (typically 2 for 95% confidence)
    combined_standard_uncertainty: float = 0.0
    expanded_uncertainty: float = 0.0
    effective_degrees_of_freedom: float = 0.0
    relative_uncertainty_percent: float = 0.0


class UncertaintyCalculator:
    """
    Calculator for measurement uncertainty budgets
    """

    @staticmethod
    def calculate_type_a_uncertainty(measurements: List[float]) -> Tuple[float, float]:
        """
        Calculate Type A (statistical) standard uncertainty from repeated measurements

        Args:
            measurements: List of repeated measurement values

        Returns:
            Tuple of (standard_uncertainty, degrees_of_freedom)
        """
        n = len(measurements)
        if n < 2:
            raise ValueError("At least 2 measurements required for Type A evaluation")

        # Calculate mean
        mean = sum(measurements) / n

        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in measurements) / (n - 1)
        std_dev = math.sqrt(variance)

        # Standard uncertainty of the mean
        standard_uncertainty = std_dev / math.sqrt(n)

        # Degrees of freedom
        degrees_of_freedom = n - 1

        return standard_uncertainty, degrees_of_freedom

    @staticmethod
    def calculate_repeatability_uncertainty(measurements: List[float]) -> float:
        """
        Calculate repeatability (standard deviation of repeated measurements)

        Args:
            measurements: List of repeated measurements

        Returns:
            Standard uncertainty from repeatability
        """
        n = len(measurements)
        if n < 2:
            return 0.0

        mean = sum(measurements) / n
        variance = sum((x - mean) ** 2 for x in measurements) / (n - 1)
        return math.sqrt(variance)

    @staticmethod
    def calculate_type_b_uncertainty(
        value: float,
        distribution: DistributionType
    ) -> float:
        """
        Calculate Type B (non-statistical) standard uncertainty

        Args:
            value: Half-width of the distribution (e.g., tolerance, certificate uncertainty)
            distribution: Probability distribution type

        Returns:
            Standard uncertainty
        """
        divisors = {
            DistributionType.NORMAL: 2.0,  # For k=2 expanded uncertainty
            DistributionType.RECTANGULAR: math.sqrt(3),
            DistributionType.TRIANGULAR: math.sqrt(6),
            DistributionType.U_SHAPED: math.sqrt(2)
        }

        divisor = divisors.get(distribution, 1.0)
        return value / divisor

    @staticmethod
    def calculate_resolution_uncertainty(resolution: float) -> float:
        """
        Calculate uncertainty from instrument resolution (rectangular distribution)

        Args:
            resolution: Instrument resolution (smallest division)

        Returns:
            Standard uncertainty from resolution
        """
        # Resolution uncertainty = resolution / (2 * sqrt(3))
        return resolution / (2 * math.sqrt(3))

    @staticmethod
    def calculate_combined_uncertainty(sources: List[UncertaintySource]) -> float:
        """
        Calculate combined standard uncertainty from multiple sources

        Formula: uc = sqrt(sum(ci^2 * ui^2))
        where ci = sensitivity coefficient, ui = standard uncertainty

        Args:
            sources: List of UncertaintySource objects

        Returns:
            Combined standard uncertainty
        """
        variance_sum = 0.0

        for source in sources:
            # Calculate standard uncertainty for this source
            if source.uncertainty_type == UncertaintyType.TYPE_A:
                u_i = source.value
            else:  # Type B
                u_i = UncertaintyCalculator.calculate_type_b_uncertainty(
                    source.value,
                    source.distribution
                )

            # Apply sensitivity coefficient and square
            variance_sum += (source.sensitivity_coefficient * u_i) ** 2

        return math.sqrt(variance_sum)

    @staticmethod
    def calculate_expanded_uncertainty(
        combined_uncertainty: float,
        coverage_factor: float = 2.0
    ) -> float:
        """
        Calculate expanded uncertainty

        Formula: U = k * uc
        where k = coverage factor (typically 2 for ~95% confidence)

        Args:
            combined_uncertainty: Combined standard uncertainty
            coverage_factor: Coverage factor k (default: 2)

        Returns:
            Expanded uncertainty
        """
        return coverage_factor * combined_uncertainty

    @staticmethod
    def calculate_effective_degrees_of_freedom(
        sources: List[UncertaintySource],
        combined_uncertainty: float
    ) -> float:
        """
        Calculate effective degrees of freedom using Welch-Satterthwaite formula

        Formula: νeff = uc^4 / sum(ui^4 / νi)

        Args:
            sources: List of UncertaintySource objects
            combined_uncertainty: Combined standard uncertainty

        Returns:
            Effective degrees of freedom
        """
        if combined_uncertainty == 0:
            return float('inf')

        denominator = 0.0

        for source in sources:
            # Calculate standard uncertainty for this source
            if source.uncertainty_type == UncertaintyType.TYPE_A:
                u_i = source.value
                # Use provided DoF or assume large value for Type A
                nu_i = source.degrees_of_freedom if source.degrees_of_freedom else 50
            else:  # Type B
                u_i = UncertaintyCalculator.calculate_type_b_uncertainty(
                    source.value,
                    source.distribution
                )
                # Type B typically has infinite DoF, use large value
                nu_i = source.degrees_of_freedom if source.degrees_of_freedom else 10000

            # Apply sensitivity coefficient
            u_i = source.sensitivity_coefficient * u_i

            # Add to denominator (avoid division by zero)
            if nu_i > 0 and u_i > 0:
                denominator += (u_i ** 4) / nu_i

        if denominator == 0:
            return float('inf')

        return (combined_uncertainty ** 4) / denominator

    @staticmethod
    def calculate_coverage_factor(
        degrees_of_freedom: float,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate coverage factor k based on degrees of freedom and confidence level

        For simplicity, uses approximations:
        - νeff >= 30: k ≈ 2.0 for 95% confidence
        - νeff < 30: k from Student's t-distribution (approximated)

        Args:
            degrees_of_freedom: Effective degrees of freedom
            confidence_level: Confidence level (default: 0.95 for 95%)

        Returns:
            Coverage factor k
        """
        if degrees_of_freedom >= 100:
            # Use normal distribution approximation
            if confidence_level == 0.95:
                return 2.0
            elif confidence_level == 0.99:
                return 2.576
            else:
                return 2.0

        # Simplified t-distribution approximation for 95% confidence
        # This is a rough approximation; for precise values, use scipy.stats.t
        t_values = {
            1: 12.71,
            2: 4.30,
            3: 3.18,
            4: 2.78,
            5: 2.57,
            10: 2.23,
            20: 2.09,
            30: 2.04,
            50: 2.01,
            100: 1.98
        }

        # Find closest DoF in table
        dof_keys = sorted(t_values.keys())
        for i, dof in enumerate(dof_keys):
            if degrees_of_freedom <= dof:
                return t_values[dof]

        return 2.0  # Default for large DoF

    @staticmethod
    def create_uncertainty_budget(
        parameter_name: str,
        measured_value: float,
        unit: str,
        sources: List[UncertaintySource],
        coverage_factor: float = 2.0
    ) -> UncertaintyBudget:
        """
        Create complete uncertainty budget

        Args:
            parameter_name: Name of measured parameter
            measured_value: Measured value
            unit: Unit of measurement
            sources: List of uncertainty sources
            coverage_factor: Coverage factor k (default: 2)

        Returns:
            Complete UncertaintyBudget object
        """
        # Calculate combined standard uncertainty
        uc = UncertaintyCalculator.calculate_combined_uncertainty(sources)

        # Calculate expanded uncertainty
        U = UncertaintyCalculator.calculate_expanded_uncertainty(uc, coverage_factor)

        # Calculate effective degrees of freedom
        veff = UncertaintyCalculator.calculate_effective_degrees_of_freedom(sources, uc)

        # Calculate relative uncertainty
        rel_uncertainty = (U / abs(measured_value) * 100) if measured_value != 0 else 0

        budget = UncertaintyBudget(
            parameter_name=parameter_name,
            measured_value=measured_value,
            unit=unit,
            sources=sources,
            coverage_factor=coverage_factor,
            combined_standard_uncertainty=uc,
            expanded_uncertainty=U,
            effective_degrees_of_freedom=veff,
            relative_uncertainty_percent=rel_uncertainty
        )

        return budget

    @staticmethod
    def generate_budget_table(budget: UncertaintyBudget) -> str:
        """
        Generate formatted uncertainty budget table

        Args:
            budget: UncertaintyBudget object

        Returns:
            Formatted table string
        """
        lines = []
        lines.append("=" * 100)
        lines.append(f"UNCERTAINTY BUDGET: {budget.parameter_name}")
        lines.append("=" * 100)
        lines.append(f"Measured Value: {budget.measured_value} {budget.unit}")
        lines.append(f"Coverage Factor: k = {budget.coverage_factor}")
        lines.append("")

        # Table header
        lines.append("-" * 100)
        lines.append(f"{'Source':<30} {'Type':<6} {'Value':<12} {'Distribution':<15} {'u(xi)':<12} {'ci':<8} {'ui':<12}")
        lines.append("-" * 100)

        # Table rows
        for source in budget.sources:
            if source.uncertainty_type == UncertaintyType.TYPE_A:
                u_xi = source.value
            else:
                u_xi = UncertaintyCalculator.calculate_type_b_uncertainty(
                    source.value,
                    source.distribution
                )

            ui = source.sensitivity_coefficient * u_xi

            lines.append(
                f"{source.name:<30} "
                f"{source.uncertainty_type.value:<6} "
                f"{source.value:<12.4f} "
                f"{source.distribution.value:<15} "
                f"{u_xi:<12.4f} "
                f"{source.sensitivity_coefficient:<8.2f} "
                f"{ui:<12.4f}"
            )

        lines.append("-" * 100)
        lines.append("")

        # Summary
        lines.append(f"Combined Standard Uncertainty (uc):     {budget.combined_standard_uncertainty:.4f} {budget.unit}")
        lines.append(f"Effective Degrees of Freedom (νeff):    {budget.effective_degrees_of_freedom:.1f}")
        lines.append(f"Coverage Factor (k):                    {budget.coverage_factor}")
        lines.append(f"Expanded Uncertainty (U = k·uc):        {budget.expanded_uncertainty:.4f} {budget.unit}")
        lines.append(f"Relative Expanded Uncertainty:          {budget.relative_uncertainty_percent:.2f}%")
        lines.append("")
        lines.append(f"RESULT: {budget.measured_value} ± {budget.expanded_uncertainty} {budget.unit} (k={budget.coverage_factor})")
        lines.append("=" * 100)

        return "\n".join(lines)

    @staticmethod
    def create_temperature_sensor_budget(
        measured_temp: float,
        reference_uncertainty: float = 0.05,
        resolution: float = 0.1,
        repeatability_stdev: float = 0.08,
        drift: float = 0.03,
        num_readings: int = 10
    ) -> UncertaintyBudget:
        """
        Create typical uncertainty budget for temperature sensor calibration

        Args:
            measured_temp: Measured temperature value (°C)
            reference_uncertainty: Reference standard uncertainty (°C)
            resolution: Instrument resolution (°C)
            repeatability_stdev: Standard deviation of repeatability (°C)
            drift: Estimated drift (°C)
            num_readings: Number of repeated readings

        Returns:
            UncertaintyBudget object
        """
        sources = [
            UncertaintySource(
                name="Reference Standard",
                value=reference_uncertainty,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.NORMAL,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Uncertainty from calibrated reference RTD"
            ),
            UncertaintySource(
                name="Resolution",
                value=resolution / 2,  # Half-width
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.RECTANGULAR,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Digital display resolution"
            ),
            UncertaintySource(
                name="Repeatability",
                value=repeatability_stdev / math.sqrt(num_readings),
                uncertainty_type=UncertaintyType.TYPE_A,
                distribution=DistributionType.NORMAL,
                degrees_of_freedom=num_readings - 1,
                sensitivity_coefficient=1.0,
                description="Standard deviation of repeated readings"
            ),
            UncertaintySource(
                name="Drift",
                value=drift / 2,  # Half-width
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.RECTANGULAR,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Estimated drift since last calibration"
            )
        ]

        return UncertaintyCalculator.create_uncertainty_budget(
            parameter_name="Temperature",
            measured_value=measured_temp,
            unit="°C",
            sources=sources,
            coverage_factor=2.0
        )

    @staticmethod
    def create_humidity_sensor_budget(
        measured_rh: float,
        reference_uncertainty: float = 1.0,
        resolution: float = 0.1,
        repeatability_stdev: float = 0.5,
        num_readings: int = 10
    ) -> UncertaintyBudget:
        """
        Create typical uncertainty budget for humidity sensor calibration

        Args:
            measured_rh: Measured relative humidity (%RH)
            reference_uncertainty: Reference standard uncertainty (%RH)
            resolution: Instrument resolution (%RH)
            repeatability_stdev: Standard deviation of repeatability (%RH)
            num_readings: Number of repeated readings

        Returns:
            UncertaintyBudget object
        """
        sources = [
            UncertaintySource(
                name="Reference Standard",
                value=reference_uncertainty,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.NORMAL,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Uncertainty from calibrated reference hygrometer"
            ),
            UncertaintySource(
                name="Resolution",
                value=resolution / 2,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.RECTANGULAR,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Digital display resolution"
            ),
            UncertaintySource(
                name="Repeatability",
                value=repeatability_stdev / math.sqrt(num_readings),
                uncertainty_type=UncertaintyType.TYPE_A,
                distribution=DistributionType.NORMAL,
                degrees_of_freedom=num_readings - 1,
                sensitivity_coefficient=1.0,
                description="Standard deviation of repeated readings"
            )
        ]

        return UncertaintyCalculator.create_uncertainty_budget(
            parameter_name="Relative Humidity",
            measured_value=measured_rh,
            unit="%RH",
            sources=sources,
            coverage_factor=2.0
        )

    @staticmethod
    def create_uv_intensity_budget(
        measured_intensity: float,
        reference_uncertainty: float = 2.0,
        resolution: float = 1.0,
        repeatability_stdev: float = 1.5,
        uniformity: float = 5.0,
        num_readings: int = 10
    ) -> UncertaintyBudget:
        """
        Create typical uncertainty budget for UV intensity measurement

        Args:
            measured_intensity: Measured UV intensity (W/m²)
            reference_uncertainty: Reference standard uncertainty (W/m²)
            resolution: Instrument resolution (W/m²)
            repeatability_stdev: Standard deviation of repeatability (W/m²)
            uniformity: Spatial uniformity variation (W/m²)
            num_readings: Number of repeated readings

        Returns:
            UncertaintyBudget object
        """
        sources = [
            UncertaintySource(
                name="Reference Standard",
                value=reference_uncertainty,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.NORMAL,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Uncertainty from calibrated reference radiometer"
            ),
            UncertaintySource(
                name="Resolution",
                value=resolution / 2,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.RECTANGULAR,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Display resolution"
            ),
            UncertaintySource(
                name="Repeatability",
                value=repeatability_stdev / math.sqrt(num_readings),
                uncertainty_type=UncertaintyType.TYPE_A,
                distribution=DistributionType.NORMAL,
                degrees_of_freedom=num_readings - 1,
                sensitivity_coefficient=1.0,
                description="Measurement repeatability"
            ),
            UncertaintySource(
                name="Spatial Uniformity",
                value=uniformity / 2,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.RECTANGULAR,
                degrees_of_freedom=10000,
                sensitivity_coefficient=1.0,
                description="Variation across measurement plane"
            )
        ]

        return UncertaintyCalculator.create_uncertainty_budget(
            parameter_name="UV Irradiance",
            measured_value=measured_intensity,
            unit="W/m²",
            sources=sources,
            coverage_factor=2.0
        )
