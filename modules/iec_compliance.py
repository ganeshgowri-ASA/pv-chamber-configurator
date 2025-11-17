"""
IEC Compliance Checker Module

This module validates environmental test chamber compliance with:
- IEC 61215: PV module design qualification and type approval
- IEC 61730: PV module safety qualification
- IEC 60068-3-5 & 60068-3-6: Environmental testing guidance

Author: PV Chamber Configurator
Version: 1.0.0
"""

import json
import os
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ChamberSpecifications:
    """Chamber specifications for compliance validation"""
    temp_min: float  # °C
    temp_max: float  # °C
    humidity_min: float  # %RH
    humidity_max: float  # %RH
    temp_uniformity: float  # °C (±)
    air_velocity: float  # m/s
    ramp_rate: float  # °C/min
    recovery_time: float  # minutes
    volume: float  # m³
    has_uv_system: bool = False
    uv_intensity_max: float = 0.0  # W/m²
    uv_wavelength_range: Tuple[float, float] = (280, 400)  # nm
    uv_uniformity: float = 0.0  # ±%


@dataclass
class ComplianceResult:
    """Result of a compliance check"""
    test_id: str
    test_name: str
    is_compliant: bool
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    chamber_capabilities: Dict[str, Any] = field(default_factory=dict)


class IECComplianceChecker:
    """
    IEC Compliance validation engine for environmental test chambers
    """

    def __init__(self, chamber_specs: ChamberSpecifications):
        """
        Initialize compliance checker with chamber specifications

        Args:
            chamber_specs: ChamberSpecifications object with chamber capabilities
        """
        self.chamber_specs = chamber_specs
        self.compliance_results: List[ComplianceResult] = []
        self.standards_data = self._load_standards_data()

    def _load_standards_data(self) -> Dict:
        """Load IEC standards data from JSON file"""
        try:
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'iec_standards.json'
            )
            with open(data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default standards if file not found
            return self._get_default_standards()

    def _get_default_standards(self) -> Dict:
        """Return default IEC standards requirements"""
        return {
            "IEC_61215": {
                "MST_11_UV": {
                    "name": "UV Preconditioning Test",
                    "uv_dose": 15.0,  # kWh/m²
                    "wavelength_min": 280,  # nm
                    "wavelength_max": 400,  # nm
                    "intensity": 60,  # W/m²
                    "temperature": 60,  # °C
                    "temp_tolerance": 5,  # °C
                    "duration_hours": 250
                },
                "MST_12_Thermal_Cycling": {
                    "name": "Thermal Cycling Test",
                    "cycles": 200,
                    "temp_low": -40,  # °C
                    "temp_high": 85,  # °C
                    "dwell_time_minutes": 30,
                    "ramp_rate_min": 1.0,  # °C/min
                    "ramp_rate_max": 3.0  # °C/min
                },
                "MST_13_Humidity_Freeze": {
                    "name": "Humidity-Freeze Test",
                    "cycles": 10,
                    "temp_high": 85,  # °C
                    "humidity_high": 85,  # %RH
                    "temp_low": -40,  # °C
                    "dwell_high_hours": 20,
                    "dwell_low_hours": 4
                },
                "MST_14_Damp_Heat": {
                    "name": "Damp Heat Test",
                    "temperature": 85,  # °C
                    "temp_tolerance": 2,  # °C
                    "humidity": 85,  # %RH
                    "humidity_tolerance": 5,  # %RH
                    "duration_hours": 1000
                }
            },
            "IEC_61730": {
                "MST_23_Hot_Spot": {
                    "name": "Hot Spot Endurance",
                    "temperature": 75,  # °C (ambient)
                    "temp_tolerance": 5,
                    "duration_hours": 5
                },
                "MST_34_UV_Conditioning": {
                    "name": "UV Conditioning",
                    "uv_dose": 60.0,  # kWh/m²
                    "intensity": 60,  # W/m²
                    "temperature": 60,  # °C
                    "temp_tolerance": 5
                },
                "MST_44_Thermal_Cycling": {
                    "name": "Thermal Cycling (Safety)",
                    "cycles": 50,
                    "temp_low": -40,
                    "temp_high": 85,
                    "dwell_time_minutes": 30
                },
                "MST_50_Damp_Heat": {
                    "name": "Damp Heat (Safety)",
                    "temperature": 85,
                    "humidity": 85,
                    "duration_hours": 1000
                }
            },
            "IEC_60068": {
                "temp_uniformity": {
                    "name": "Temperature Uniformity",
                    "max_deviation": 2.0  # °C
                },
                "air_velocity": {
                    "name": "Air Velocity at Specimen",
                    "max_velocity": 2.0  # m/s
                },
                "recovery_time": {
                    "name": "Temperature Recovery Time",
                    "max_time_minutes": 30  # minutes
                }
            }
        }

    # ========== IEC 61215 Compliance Validation ==========

    def validate_iec_61215_capability(self) -> List[ComplianceResult]:
        """
        Validate chamber capability for all IEC 61215 tests

        Returns:
            List of ComplianceResult objects
        """
        results = []

        # Check each MST test
        results.append(self.check_uv_preconditioning_compliance())
        results.append(self.check_thermal_cycling_compliance())
        results.append(self.check_humidity_freeze_compliance())
        results.append(self.check_damp_heat_compliance())

        self.compliance_results.extend(results)
        return results

    def check_uv_preconditioning_compliance(self) -> ComplianceResult:
        """Check IEC 61215 MST 11 UV Preconditioning compliance"""
        std = self.standards_data["IEC_61215"]["MST_11_UV"]
        result = ComplianceResult(
            test_id="IEC_61215_MST_11",
            test_name=std["name"],
            is_compliant=True,
            requirements={
                "UV Dose": f"{std['uv_dose']} kWh/m²",
                "Wavelength Range": f"{std['wavelength_min']}-{std['wavelength_max']} nm",
                "Intensity": f"{std['intensity']} W/m²",
                "Temperature": f"{std['temperature']}±{std['temp_tolerance']}°C",
                "Duration": f"{std['duration_hours']} hours"
            },
            chamber_capabilities={
                "UV System": self.chamber_specs.has_uv_system,
                "Max UV Intensity": f"{self.chamber_specs.uv_intensity_max} W/m²",
                "UV Wavelength": f"{self.chamber_specs.uv_wavelength_range[0]}-{self.chamber_specs.uv_wavelength_range[1]} nm",
                "Temp Range": f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C"
            }
        )

        # Check UV system availability
        if not self.chamber_specs.has_uv_system:
            result.is_compliant = False
            result.issues.append("UV system not available in chamber")
            result.recommendations.append("Install UV LED array system (280-400nm)")

        # Check UV intensity capability
        if self.chamber_specs.uv_intensity_max < std['intensity']:
            result.is_compliant = False
            result.issues.append(
                f"UV intensity insufficient: {self.chamber_specs.uv_intensity_max} W/m² "
                f"< {std['intensity']} W/m² required"
            )
            result.recommendations.append(f"Upgrade UV system to achieve {std['intensity']} W/m²")

        # Check wavelength range
        if (self.chamber_specs.uv_wavelength_range[0] > std['wavelength_min'] or
            self.chamber_specs.uv_wavelength_range[1] < std['wavelength_max']):
            result.is_compliant = False
            result.issues.append(
                f"UV wavelength range incompatible: "
                f"{self.chamber_specs.uv_wavelength_range} vs required "
                f"({std['wavelength_min']}, {std['wavelength_max']}) nm"
            )
            result.recommendations.append("Use broadband UV LEDs covering 280-400nm spectrum")

        # Check temperature capability
        temp_required = std['temperature']
        if (self.chamber_specs.temp_min > temp_required or
            self.chamber_specs.temp_max < temp_required):
            result.is_compliant = False
            result.issues.append(
                f"Cannot maintain {temp_required}°C (chamber range: "
                f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C)"
            )

        return result

    def check_thermal_cycling_compliance(self) -> ComplianceResult:
        """Check IEC 61215 MST 12 Thermal Cycling compliance"""
        std = self.standards_data["IEC_61215"]["MST_12_Thermal_Cycling"]
        result = ComplianceResult(
            test_id="IEC_61215_MST_12",
            test_name=std["name"],
            is_compliant=True,
            requirements={
                "Cycles": std['cycles'],
                "Temperature Low": f"{std['temp_low']}°C",
                "Temperature High": f"{std['temp_high']}°C",
                "Dwell Time": f"{std['dwell_time_minutes']} minutes",
                "Ramp Rate": f"{std['ramp_rate_min']}-{std['ramp_rate_max']}°C/min"
            },
            chamber_capabilities={
                "Temp Range": f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C",
                "Ramp Rate": f"{self.chamber_specs.ramp_rate}°C/min"
            }
        )

        # Check low temperature capability
        if self.chamber_specs.temp_min > std['temp_low']:
            result.is_compliant = False
            result.issues.append(
                f"Low temperature insufficient: {self.chamber_specs.temp_min}°C > "
                f"{std['temp_low']}°C required"
            )
            result.recommendations.append(
                f"Upgrade refrigeration to achieve {std['temp_low']}°C"
            )

        # Check high temperature capability
        if self.chamber_specs.temp_max < std['temp_high']:
            result.is_compliant = False
            result.issues.append(
                f"High temperature insufficient: {self.chamber_specs.temp_max}°C < "
                f"{std['temp_high']}°C required"
            )
            result.recommendations.append(
                f"Upgrade heating system to achieve {std['temp_high']}°C"
            )

        # Check ramp rate
        if (self.chamber_specs.ramp_rate < std['ramp_rate_min'] or
            self.chamber_specs.ramp_rate > std['ramp_rate_max']):
            result.is_compliant = False
            result.issues.append(
                f"Ramp rate out of range: {self.chamber_specs.ramp_rate}°C/min "
                f"(required: {std['ramp_rate_min']}-{std['ramp_rate_max']}°C/min)"
            )
            result.recommendations.append(
                f"Adjust ramp rate to {std['ramp_rate_min']}-{std['ramp_rate_max']}°C/min"
            )

        return result

    def check_humidity_freeze_compliance(self) -> ComplianceResult:
        """Check IEC 61215 MST 13 Humidity-Freeze compliance"""
        std = self.standards_data["IEC_61215"]["MST_13_Humidity_Freeze"]
        result = ComplianceResult(
            test_id="IEC_61215_MST_13",
            test_name=std["name"],
            is_compliant=True,
            requirements={
                "Cycles": std['cycles'],
                "High Temp": f"{std['temp_high']}°C",
                "High Humidity": f"{std['humidity_high']}%RH",
                "Low Temp": f"{std['temp_low']}°C",
                "Dwell High": f"{std['dwell_high_hours']} hours",
                "Dwell Low": f"{std['dwell_low_hours']} hours"
            },
            chamber_capabilities={
                "Temp Range": f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C",
                "Humidity Range": f"{self.chamber_specs.humidity_min} to {self.chamber_specs.humidity_max}%RH"
            }
        )

        # Check temperature range
        if (self.chamber_specs.temp_min > std['temp_low'] or
            self.chamber_specs.temp_max < std['temp_high']):
            result.is_compliant = False
            result.issues.append(
                f"Temperature range insufficient for {std['temp_low']}°C to {std['temp_high']}°C"
            )

        # Check humidity capability
        if self.chamber_specs.humidity_max < std['humidity_high']:
            result.is_compliant = False
            result.issues.append(
                f"Humidity capability insufficient: {self.chamber_specs.humidity_max}%RH < "
                f"{std['humidity_high']}%RH required"
            )
            result.recommendations.append("Upgrade humidification system")

        return result

    def check_damp_heat_compliance(self) -> ComplianceResult:
        """Check IEC 61215 MST 14 Damp Heat compliance"""
        std = self.standards_data["IEC_61215"]["MST_14_Damp_Heat"]
        result = ComplianceResult(
            test_id="IEC_61215_MST_14",
            test_name=std["name"],
            is_compliant=True,
            requirements={
                "Temperature": f"{std['temperature']}±{std['temp_tolerance']}°C",
                "Humidity": f"{std['humidity']}±{std['humidity_tolerance']}%RH",
                "Duration": f"{std['duration_hours']} hours"
            },
            chamber_capabilities={
                "Temp Range": f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C",
                "Temp Uniformity": f"±{self.chamber_specs.temp_uniformity}°C",
                "Humidity Range": f"{self.chamber_specs.humidity_min} to {self.chamber_specs.humidity_max}%RH"
            }
        )

        # Check temperature capability
        temp_req = std['temperature']
        if (self.chamber_specs.temp_min > temp_req or
            self.chamber_specs.temp_max < temp_req):
            result.is_compliant = False
            result.issues.append(
                f"Cannot maintain {temp_req}°C (chamber range: "
                f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C)"
            )

        # Check temperature uniformity
        if self.chamber_specs.temp_uniformity > std['temp_tolerance']:
            result.is_compliant = False
            result.issues.append(
                f"Temperature uniformity insufficient: ±{self.chamber_specs.temp_uniformity}°C > "
                f"±{std['temp_tolerance']}°C required"
            )
            result.recommendations.append("Improve air circulation for better uniformity")

        # Check humidity capability
        hum_req = std['humidity']
        if (self.chamber_specs.humidity_min > hum_req or
            self.chamber_specs.humidity_max < hum_req):
            result.is_compliant = False
            result.issues.append(
                f"Cannot maintain {hum_req}%RH (chamber range: "
                f"{self.chamber_specs.humidity_min} to {self.chamber_specs.humidity_max}%RH)"
            )

        return result

    # ========== IEC 61730 Compliance Validation ==========

    def validate_iec_61730_capability(self) -> List[ComplianceResult]:
        """
        Validate chamber capability for IEC 61730 safety tests

        Returns:
            List of ComplianceResult objects
        """
        results = []

        # Check safety-specific tests
        for test_id in ["MST_23_Hot_Spot", "MST_34_UV_Conditioning",
                        "MST_44_Thermal_Cycling", "MST_50_Damp_Heat"]:
            results.append(self._check_iec_61730_test(test_id))

        self.compliance_results.extend(results)
        return results

    def _check_iec_61730_test(self, test_id: str) -> ComplianceResult:
        """Generic checker for IEC 61730 tests"""
        std = self.standards_data["IEC_61730"][test_id]
        result = ComplianceResult(
            test_id=f"IEC_61730_{test_id}",
            test_name=std["name"],
            is_compliant=True
        )

        # Build requirements dict based on available keys
        requirements = {}
        if 'temperature' in std:
            requirements["Temperature"] = f"{std['temperature']}°C"
        if 'temp_low' in std and 'temp_high' in std:
            requirements["Temp Range"] = f"{std['temp_low']} to {std['temp_high']}°C"
        if 'humidity' in std:
            requirements["Humidity"] = f"{std['humidity']}%RH"
        if 'duration_hours' in std:
            requirements["Duration"] = f"{std['duration_hours']} hours"
        if 'cycles' in std:
            requirements["Cycles"] = std['cycles']
        if 'uv_dose' in std:
            requirements["UV Dose"] = f"{std['uv_dose']} kWh/m²"

        result.requirements = requirements
        result.chamber_capabilities = {
            "Temp Range": f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C",
            "Humidity Range": f"{self.chamber_specs.humidity_min} to {self.chamber_specs.humidity_max}%RH"
        }

        # Perform basic checks
        if 'temp_low' in std and self.chamber_specs.temp_min > std['temp_low']:
            result.is_compliant = False
            result.issues.append(f"Low temp insufficient: {self.chamber_specs.temp_min}°C > {std['temp_low']}°C")

        if 'temp_high' in std and self.chamber_specs.temp_max < std['temp_high']:
            result.is_compliant = False
            result.issues.append(f"High temp insufficient: {self.chamber_specs.temp_max}°C < {std['temp_high']}°C")

        if 'humidity' in std and self.chamber_specs.humidity_max < std['humidity']:
            result.is_compliant = False
            result.issues.append(f"Humidity insufficient: {self.chamber_specs.humidity_max}%RH < {std['humidity']}%RH")

        if 'uv_dose' in std and not self.chamber_specs.has_uv_system:
            result.is_compliant = False
            result.issues.append("UV system not available")
            result.recommendations.append("Install UV system")

        return result

    def check_safety_requirements(self) -> ComplianceResult:
        """Check general safety requirements for IEC 61730"""
        result = ComplianceResult(
            test_id="IEC_61730_SAFETY",
            test_name="General Safety Requirements",
            is_compliant=True,
            requirements={
                "Electrical Safety": "Over-current protection, grounding",
                "Fire Safety": "Fire-resistant materials, emergency shutoff",
                "Mechanical Safety": "Door interlocks, safety guards"
            }
        )

        result.recommendations.extend([
            "Ensure all electrical components are properly grounded",
            "Install emergency stop button accessible from all sides",
            "Use fire-resistant insulation materials",
            "Implement door interlock system to stop operation when opened",
            "Regular safety audits and maintenance"
        ])

        return result

    # ========== IEC 60068 Compliance Validation ==========

    def validate_chamber_uniformity(self, uniformity_data: Optional[Dict] = None) -> ComplianceResult:
        """
        Validate chamber temperature uniformity per IEC 60068-3-5

        Args:
            uniformity_data: Optional dict with measured uniformity data

        Returns:
            ComplianceResult object
        """
        std = self.standards_data["IEC_60068"]["temp_uniformity"]
        result = ComplianceResult(
            test_id="IEC_60068_UNIFORMITY",
            test_name=std["name"],
            is_compliant=True,
            requirements={
                "Max Temperature Deviation": f"±{std['max_deviation']}°C"
            },
            chamber_capabilities={
                "Specified Uniformity": f"±{self.chamber_specs.temp_uniformity}°C"
            }
        )

        # Check specified uniformity
        if self.chamber_specs.temp_uniformity > std['max_deviation']:
            result.is_compliant = False
            result.issues.append(
                f"Temperature uniformity exceeds limit: ±{self.chamber_specs.temp_uniformity}°C > "
                f"±{std['max_deviation']}°C"
            )
            result.recommendations.append("Improve air circulation system")
            result.recommendations.append("Add more circulation fans or optimize airflow pattern")

        # If actual measurements provided, validate them
        if uniformity_data:
            if 'max_deviation' in uniformity_data:
                actual_dev = uniformity_data['max_deviation']
                result.chamber_capabilities["Measured Uniformity"] = f"±{actual_dev}°C"

                if actual_dev > std['max_deviation']:
                    result.is_compliant = False
                    result.issues.append(
                        f"Measured uniformity exceeds limit: ±{actual_dev}°C > ±{std['max_deviation']}°C"
                    )
                    result.recommendations.append("Recalibrate chamber or adjust airflow")

        return result

    def check_air_velocity(self, velocity_data: Optional[Dict] = None) -> ComplianceResult:
        """
        Validate air velocity at test specimen per IEC 60068-3-6

        Args:
            velocity_data: Optional dict with measured velocity data

        Returns:
            ComplianceResult object
        """
        std = self.standards_data["IEC_60068"]["air_velocity"]
        result = ComplianceResult(
            test_id="IEC_60068_AIR_VELOCITY",
            test_name=std["name"],
            is_compliant=True,
            requirements={
                "Max Air Velocity": f"{std['max_velocity']} m/s at specimen"
            },
            chamber_capabilities={
                "Specified Air Velocity": f"{self.chamber_specs.air_velocity} m/s"
            }
        )

        # Check specified velocity
        if self.chamber_specs.air_velocity > std['max_velocity']:
            result.is_compliant = False
            result.issues.append(
                f"Air velocity exceeds limit: {self.chamber_specs.air_velocity} m/s > "
                f"{std['max_velocity']} m/s"
            )
            result.recommendations.append("Reduce fan speed or install diffusers")
            result.recommendations.append("Reposition specimen away from direct airflow")

        # If actual measurements provided, validate them
        if velocity_data:
            if 'max_velocity' in velocity_data:
                actual_vel = velocity_data['max_velocity']
                result.chamber_capabilities["Measured Velocity"] = f"{actual_vel} m/s"

                if actual_vel > std['max_velocity']:
                    result.is_compliant = False
                    result.issues.append(
                        f"Measured velocity exceeds limit: {actual_vel} m/s > {std['max_velocity']} m/s"
                    )

        return result

    def validate_recovery_time(self, ramp_data: Optional[Dict] = None) -> ComplianceResult:
        """
        Validate temperature recovery time per IEC 60068

        Args:
            ramp_data: Optional dict with measured recovery time data

        Returns:
            ComplianceResult object
        """
        std = self.standards_data["IEC_60068"]["recovery_time"]
        result = ComplianceResult(
            test_id="IEC_60068_RECOVERY",
            test_name=std["name"],
            is_compliant=True,
            requirements={
                "Max Recovery Time": f"{std['max_time_minutes']} minutes"
            },
            chamber_capabilities={
                "Specified Recovery Time": f"{self.chamber_specs.recovery_time} minutes"
            }
        )

        # Check specified recovery time
        if self.chamber_specs.recovery_time > std['max_time_minutes']:
            result.is_compliant = False
            result.issues.append(
                f"Recovery time exceeds limit: {self.chamber_specs.recovery_time} min > "
                f"{std['max_time_minutes']} min"
            )
            result.recommendations.append("Increase heating/cooling capacity")
            result.recommendations.append("Reduce thermal mass of test specimen if possible")

        # If actual measurements provided, validate them
        if ramp_data:
            if 'recovery_time' in ramp_data:
                actual_time = ramp_data['recovery_time']
                result.chamber_capabilities["Measured Recovery Time"] = f"{actual_time} minutes"

                if actual_time > std['max_time_minutes']:
                    result.is_compliant = False
                    result.issues.append(
                        f"Measured recovery time exceeds limit: {actual_time} min > "
                        f"{std['max_time_minutes']} min"
                    )

        return result

    # ========== Report Generation ==========

    def generate_compliance_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive compliance summary

        Returns:
            Dictionary with compliance summary data
        """
        total_tests = len(self.compliance_results)
        compliant_tests = sum(1 for r in self.compliance_results if r.is_compliant)
        compliance_rate = (compliant_tests / total_tests * 100) if total_tests > 0 else 0

        summary = {
            "timestamp": datetime.now().isoformat(),
            "chamber_specs": {
                "temp_range": f"{self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C",
                "humidity_range": f"{self.chamber_specs.humidity_min} to {self.chamber_specs.humidity_max}%RH",
                "temp_uniformity": f"±{self.chamber_specs.temp_uniformity}°C",
                "air_velocity": f"{self.chamber_specs.air_velocity} m/s",
                "ramp_rate": f"{self.chamber_specs.ramp_rate}°C/min",
                "has_uv_system": self.chamber_specs.has_uv_system,
                "uv_intensity_max": f"{self.chamber_specs.uv_intensity_max} W/m²"
            },
            "overall_compliance": {
                "total_tests": total_tests,
                "compliant_tests": compliant_tests,
                "non_compliant_tests": total_tests - compliant_tests,
                "compliance_rate": f"{compliance_rate:.1f}%"
            },
            "test_results": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "status": "PASS" if r.is_compliant else "FAIL",
                    "issues": r.issues,
                    "recommendations": r.recommendations
                }
                for r in self.compliance_results
            ]
        }

        return summary

    def identify_gaps(self) -> List[Dict[str, Any]]:
        """
        Identify non-compliant areas and gaps

        Returns:
            List of gaps with recommendations
        """
        gaps = []

        for result in self.compliance_results:
            if not result.is_compliant:
                gap = {
                    "test_id": result.test_id,
                    "test_name": result.test_name,
                    "issues": result.issues,
                    "recommendations": result.recommendations,
                    "priority": "HIGH" if "UV" in result.test_id or "Thermal" in result.test_id else "MEDIUM"
                }
                gaps.append(gap)

        return gaps

    def generate_iec_61215_report(self) -> str:
        """
        Generate detailed IEC 61215 compliance report

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("IEC 61215 COMPLIANCE REPORT")
        report.append("Terrestrial PV Modules - Design Qualification and Type Approval")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Chamber specifications
        report.append("CHAMBER SPECIFICATIONS:")
        report.append(f"  Temperature Range: {self.chamber_specs.temp_min} to {self.chamber_specs.temp_max}°C")
        report.append(f"  Humidity Range: {self.chamber_specs.humidity_min} to {self.chamber_specs.humidity_max}%RH")
        report.append(f"  Temperature Uniformity: ±{self.chamber_specs.temp_uniformity}°C")
        report.append(f"  Ramp Rate: {self.chamber_specs.ramp_rate}°C/min")
        report.append(f"  UV System: {'Available' if self.chamber_specs.has_uv_system else 'Not Available'}")
        report.append("")

        # Test results
        report.append("TEST COMPLIANCE RESULTS:")
        report.append("-" * 80)

        for result in self.compliance_results:
            if "IEC_61215" in result.test_id:
                status = "✓ PASS" if result.is_compliant else "✗ FAIL"
                report.append(f"\n{result.test_id}: {result.test_name}")
                report.append(f"  Status: {status}")

                if result.issues:
                    report.append("  Issues:")
                    for issue in result.issues:
                        report.append(f"    - {issue}")

                if result.recommendations:
                    report.append("  Recommendations:")
                    for rec in result.recommendations:
                        report.append(f"    - {rec}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)
