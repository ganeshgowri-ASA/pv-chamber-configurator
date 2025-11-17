"""
ISO 17025 Calibration Module

This module implements calibration certificate generation and management
compliant with ISO/IEC 17025:2017 requirements.

Features:
- Calibration certificate generation
- CMC (Calibration and Measurement Capability) tables
- Traceability chain management
- Calibration history tracking
- Reference standard database

Author: PV Chamber Configurator
Version: 1.0.0
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import io

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, PageBreak, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class AccreditationBody(Enum):
    """Accreditation bodies"""
    NABL = "NABL"  # National Accreditation Board for Testing and Calibration Laboratories (India)
    A2LA = "A2LA"  # American Association for Laboratory Accreditation
    ILAC = "ILAC"  # International Laboratory Accreditation Cooperation
    UKAS = "UKAS"  # United Kingdom Accreditation Service


class InstrumentType(Enum):
    """Types of instruments for calibration"""
    TEMPERATURE_RTD = "RTD Temperature Sensor"
    TEMPERATURE_TC = "Thermocouple"
    HUMIDITY = "Humidity Sensor"
    UV_RADIOMETER = "UV Radiometer"
    PRESSURE = "Pressure Sensor"
    AIRFLOW = "Airflow Sensor"
    MULTIMETER = "Digital Multimeter"


@dataclass
class LabAccreditation:
    """Laboratory accreditation information"""
    lab_name: str
    accreditation_body: AccreditationBody
    certificate_number: str
    scope: str
    address: str
    contact: str
    email: str
    logo_path: Optional[str] = None


@dataclass
class ReferenceStandard:
    """Reference standard used for calibration"""
    id: str
    name: str
    make: str
    model: str
    serial_number: str
    certificate_number: str
    calibration_date: str
    next_calibration_date: str
    uncertainty: float  # k=2
    uncertainty_unit: str
    traceability: str  # e.g., "NIST", "NPL"
    parameter_type: str
    range_min: float
    range_max: float


@dataclass
class InstrumentData:
    """Instrument being calibrated"""
    id: str
    instrument_type: InstrumentType
    make: str
    model: str
    serial_number: str
    identification_number: str
    owner: str
    location: str


@dataclass
class EnvironmentalConditions:
    """Environmental conditions during calibration"""
    temperature: float  # °C
    temperature_uncertainty: float
    humidity: float  # %RH
    humidity_uncertainty: float
    pressure: float  # kPa
    pressure_uncertainty: float


@dataclass
class CalibrationPoint:
    """Single calibration point"""
    reference_value: float
    reading_1: float
    reading_2: float
    reading_3: float
    mean_reading: float
    error: float
    uncertainty: float  # k=2


@dataclass
class CalibrationResults:
    """Complete calibration results"""
    calibration_points: List[CalibrationPoint]
    parameter: str
    unit: str
    procedure_reference: str
    environmental_conditions: EnvironmentalConditions


@dataclass
class CalibrationCertificate:
    """Complete calibration certificate"""
    certificate_number: str
    issue_date: str
    calibration_date: str
    next_calibration_date: str
    lab_accreditation: LabAccreditation
    instrument_data: InstrumentData
    reference_standard: ReferenceStandard
    calibration_results: CalibrationResults
    calibrated_by: str
    reviewed_by: str
    approved_by: str
    remarks: str = ""


@dataclass
class CMCEntry:
    """Calibration and Measurement Capability entry"""
    parameter: str
    range_min: float
    range_max: float
    unit: str
    best_measurement_capability: float  # Expanded uncertainty, k=2
    remarks: str = ""


class ISO17025Calibration:
    """
    ISO 17025 Calibration management system
    """

    def __init__(self, lab_accreditation: LabAccreditation):
        """
        Initialize calibration system

        Args:
            lab_accreditation: Laboratory accreditation information
        """
        self.lab_accreditation = lab_accreditation
        self.reference_standards: Dict[str, ReferenceStandard] = {}
        self.calibration_history: Dict[str, List[CalibrationCertificate]] = {}
        self._load_reference_standards()

    def _load_reference_standards(self):
        """Load reference standards from JSON database"""
        try:
            data_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'data',
                'reference_standards.json'
            )
            with open(data_path, 'r') as f:
                data = json.load(f)
                for std_data in data.get('standards', []):
                    std = ReferenceStandard(**std_data)
                    self.reference_standards[std.id] = std
        except FileNotFoundError:
            # Initialize with empty database
            pass

    def add_reference_standard(self, standard: ReferenceStandard) -> bool:
        """
        Add a reference standard to the database

        Args:
            standard: ReferenceStandard object

        Returns:
            True if added successfully
        """
        if standard.id in self.reference_standards:
            return False  # Already exists

        self.reference_standards[standard.id] = standard
        return True

    def get_reference_standard(self, standard_id: str) -> Optional[ReferenceStandard]:
        """Get reference standard by ID"""
        return self.reference_standards.get(standard_id)

    def validate_traceability(self, instrument_id: str) -> Tuple[bool, str]:
        """
        Validate calibration traceability chain

        Args:
            instrument_id: Instrument ID

        Returns:
            Tuple of (is_valid, message)
        """
        if instrument_id not in self.calibration_history:
            return False, "No calibration history found"

        history = self.calibration_history[instrument_id]
        if not history:
            return False, "Calibration history is empty"

        latest_cert = history[-1]
        ref_std = latest_cert.reference_standard

        # Check reference standard calibration validity
        next_cal_date = datetime.strptime(ref_std.next_calibration_date, "%Y-%m-%d")
        if datetime.now() > next_cal_date:
            return False, f"Reference standard {ref_std.id} calibration expired"

        # Check traceability to national/international standard
        if ref_std.traceability not in ["NIST", "NPL", "PTB", "NMIJ"]:
            return False, f"Invalid traceability: {ref_std.traceability}"

        return True, f"Valid traceability chain to {ref_std.traceability}"

    def get_calibration_history(self, instrument_id: str) -> List[CalibrationCertificate]:
        """
        Get calibration history for an instrument

        Args:
            instrument_id: Instrument ID

        Returns:
            List of CalibrationCertificate objects
        """
        return self.calibration_history.get(instrument_id, [])

    def calculate_next_calibration_date(
        self,
        current_date: datetime,
        interval_months: int = 12
    ) -> str:
        """
        Calculate next calibration due date

        Args:
            current_date: Current calibration date
            interval_months: Calibration interval in months

        Returns:
            Next calibration date as ISO string
        """
        next_date = current_date + timedelta(days=interval_months * 30)
        return next_date.strftime("%Y-%m-%d")

    def generate_calibration_certificate(
        self,
        instrument_data: InstrumentData,
        reference_standard_id: str,
        calibration_results: CalibrationResults,
        calibrated_by: str,
        reviewed_by: str,
        approved_by: str,
        calibration_interval_months: int = 12,
        remarks: str = ""
    ) -> CalibrationCertificate:
        """
        Generate calibration certificate

        Args:
            instrument_data: InstrumentData object
            reference_standard_id: ID of reference standard used
            calibration_results: CalibrationResults object
            calibrated_by: Name of calibration technician
            reviewed_by: Name of reviewer
            approved_by: Name of approver
            calibration_interval_months: Calibration interval
            remarks: Additional remarks

        Returns:
            CalibrationCertificate object
        """
        # Get reference standard
        ref_std = self.reference_standards.get(reference_standard_id)
        if not ref_std:
            raise ValueError(f"Reference standard {reference_standard_id} not found")

        # Generate certificate number
        now = datetime.now()
        cert_number = f"CAL-{now.strftime('%Y%m%d')}-{instrument_data.id}"

        # Calculate dates
        cal_date = now.strftime("%Y-%m-%d")
        next_cal_date = self.calculate_next_calibration_date(now, calibration_interval_months)

        certificate = CalibrationCertificate(
            certificate_number=cert_number,
            issue_date=now.strftime("%Y-%m-%d"),
            calibration_date=cal_date,
            next_calibration_date=next_cal_date,
            lab_accreditation=self.lab_accreditation,
            instrument_data=instrument_data,
            reference_standard=ref_std,
            calibration_results=calibration_results,
            calibrated_by=calibrated_by,
            reviewed_by=reviewed_by,
            approved_by=approved_by,
            remarks=remarks
        )

        # Add to calibration history
        if instrument_data.id not in self.calibration_history:
            self.calibration_history[instrument_data.id] = []
        self.calibration_history[instrument_data.id].append(certificate)

        return certificate

    def create_certificate_html(self, certificate: CalibrationCertificate) -> str:
        """
        Create HTML version of calibration certificate

        Args:
            certificate: CalibrationCertificate object

        Returns:
            HTML string
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Calibration Certificate {certificate.certificate_number}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    font-size: 11pt;
                }}
                .header {{
                    text-align: center;
                    border-bottom: 2px solid #000;
                    padding-bottom: 20px;
                    margin-bottom: 20px;
                }}
                .title {{
                    font-size: 18pt;
                    font-weight: bold;
                    color: #003366;
                }}
                .cert-number {{
                    font-size: 14pt;
                    color: #666;
                    margin-top: 10px;
                }}
                .section {{
                    margin: 20px 0;
                }}
                .section-title {{
                    font-weight: bold;
                    font-size: 12pt;
                    background-color: #f0f0f0;
                    padding: 5px;
                    margin-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }}
                table, th, td {{
                    border: 1px solid #ccc;
                }}
                th {{
                    background-color: #e0e0e0;
                    padding: 8px;
                    text-align: left;
                }}
                td {{
                    padding: 8px;
                }}
                .info-table td {{
                    border: none;
                }}
                .info-table td:first-child {{
                    font-weight: bold;
                    width: 200px;
                }}
                .signatures {{
                    margin-top: 40px;
                    display: flex;
                    justify-content: space-between;
                }}
                .signature {{
                    text-align: center;
                    width: 30%;
                }}
                .signature-line {{
                    border-top: 1px solid #000;
                    margin-top: 50px;
                    padding-top: 5px;
                }}
                .footer {{
                    margin-top: 40px;
                    font-size: 9pt;
                    text-align: center;
                    color: #666;
                    border-top: 1px solid #ccc;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">{certificate.lab_accreditation.lab_name}</div>
                <div>{certificate.lab_accreditation.address}</div>
                <div>{certificate.lab_accreditation.contact} | {certificate.lab_accreditation.email}</div>
                <div style="margin-top:10px; color:#003366;">
                    Accredited by {certificate.lab_accreditation.accreditation_body.value}
                    | Certificate No: {certificate.lab_accreditation.certificate_number}
                </div>
                <div class="cert-number">CALIBRATION CERTIFICATE<br>{certificate.certificate_number}</div>
            </div>

            <div class="section">
                <div class="section-title">Instrument Information</div>
                <table class="info-table">
                    <tr><td>Instrument Type:</td><td>{certificate.instrument_data.instrument_type.value}</td></tr>
                    <tr><td>Manufacturer:</td><td>{certificate.instrument_data.make}</td></tr>
                    <tr><td>Model:</td><td>{certificate.instrument_data.model}</td></tr>
                    <tr><td>Serial Number:</td><td>{certificate.instrument_data.serial_number}</td></tr>
                    <tr><td>ID Number:</td><td>{certificate.instrument_data.identification_number}</td></tr>
                    <tr><td>Owner:</td><td>{certificate.instrument_data.owner}</td></tr>
                    <tr><td>Location:</td><td>{certificate.instrument_data.location}</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">Calibration Information</div>
                <table class="info-table">
                    <tr><td>Calibration Date:</td><td>{certificate.calibration_date}</td></tr>
                    <tr><td>Next Calibration Due:</td><td>{certificate.next_calibration_date}</td></tr>
                    <tr><td>Procedure Reference:</td><td>{certificate.calibration_results.procedure_reference}</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">Reference Standard</div>
                <table class="info-table">
                    <tr><td>Standard:</td><td>{certificate.reference_standard.name}</td></tr>
                    <tr><td>Make/Model:</td><td>{certificate.reference_standard.make} / {certificate.reference_standard.model}</td></tr>
                    <tr><td>Serial Number:</td><td>{certificate.reference_standard.serial_number}</td></tr>
                    <tr><td>Certificate Number:</td><td>{certificate.reference_standard.certificate_number}</td></tr>
                    <tr><td>Calibration Date:</td><td>{certificate.reference_standard.calibration_date}</td></tr>
                    <tr><td>Uncertainty (k=2):</td><td>±{certificate.reference_standard.uncertainty} {certificate.reference_standard.uncertainty_unit}</td></tr>
                    <tr><td>Traceability:</td><td>{certificate.reference_standard.traceability}</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">Environmental Conditions</div>
                <table class="info-table">
                    <tr><td>Temperature:</td><td>{certificate.calibration_results.environmental_conditions.temperature} ± {certificate.calibration_results.environmental_conditions.temperature_uncertainty} °C</td></tr>
                    <tr><td>Humidity:</td><td>{certificate.calibration_results.environmental_conditions.humidity} ± {certificate.calibration_results.environmental_conditions.humidity_uncertainty} %RH</td></tr>
                    <tr><td>Pressure:</td><td>{certificate.calibration_results.environmental_conditions.pressure} ± {certificate.calibration_results.environmental_conditions.pressure_uncertainty} kPa</td></tr>
                </table>
            </div>

            <div class="section">
                <div class="section-title">Calibration Results - {certificate.calibration_results.parameter}</div>
                <table>
                    <tr>
                        <th>Reference Value<br>({certificate.calibration_results.unit})</th>
                        <th>Reading 1<br>({certificate.calibration_results.unit})</th>
                        <th>Reading 2<br>({certificate.calibration_results.unit})</th>
                        <th>Reading 3<br>({certificate.calibration_results.unit})</th>
                        <th>Mean<br>({certificate.calibration_results.unit})</th>
                        <th>Error<br>({certificate.calibration_results.unit})</th>
                        <th>Uncertainty (k=2)<br>({certificate.calibration_results.unit})</th>
                    </tr>
        """

        for point in certificate.calibration_results.calibration_points:
            html += f"""
                    <tr>
                        <td>{point.reference_value:.2f}</td>
                        <td>{point.reading_1:.2f}</td>
                        <td>{point.reading_2:.2f}</td>
                        <td>{point.reading_3:.2f}</td>
                        <td>{point.mean_reading:.2f}</td>
                        <td>{point.error:.2f}</td>
                        <td>±{point.uncertainty:.2f}</td>
                    </tr>
            """

        html += """
                </table>
            </div>
        """

        if certificate.remarks:
            html += f"""
            <div class="section">
                <div class="section-title">Remarks</div>
                <p>{certificate.remarks}</p>
            </div>
            """

        html += f"""
            <div class="signatures">
                <div class="signature">
                    <div class="signature-line">{certificate.calibrated_by}</div>
                    <div>Calibrated By</div>
                </div>
                <div class="signature">
                    <div class="signature-line">{certificate.reviewed_by}</div>
                    <div>Reviewed By</div>
                </div>
                <div class="signature">
                    <div class="signature-line">{certificate.approved_by}</div>
                    <div>Approved By</div>
                </div>
            </div>

            <div class="footer">
                This certificate is issued in accordance with ISO/IEC 17025:2017<br>
                Measurement uncertainties are expressed as expanded uncertainties with coverage factor k=2 (~95% confidence level)<br>
                This certificate may not be reproduced except in full without written approval
            </div>
        </body>
        </html>
        """

        return html

    def generate_cmc_table(self, parameter_type: str) -> List[CMCEntry]:
        """
        Generate Calibration and Measurement Capability table

        Args:
            parameter_type: Type of parameter (temperature, humidity, etc.)

        Returns:
            List of CMCEntry objects
        """
        cmc_tables = {
            "temperature": [
                CMCEntry("Temperature", -50, 150, "°C", 0.15, "RTD/Thermocouple"),
                CMCEntry("Temperature", -100, -50, "°C", 0.30, "Thermocouple only"),
                CMCEntry("Temperature", 150, 600, "°C", 0.50, "Thermocouple only"),
            ],
            "humidity": [
                CMCEntry("Relative Humidity", 10, 95, "%RH", 2.0, "At 23±5°C"),
                CMCEntry("Relative Humidity", 5, 10, "%RH", 3.0, "At 23±5°C"),
            ],
            "uv_intensity": [
                CMCEntry("UV Irradiance", 10, 250, "W/m²", 5.0, "280-400nm range"),
            ],
            "pressure": [
                CMCEntry("Absolute Pressure", 0, 200, "kPa", 0.5, ""),
            ],
            "airflow": [
                CMCEntry("Air Velocity", 0.1, 10, "m/s", 0.1, "Hot wire anemometer"),
            ]
        }

        return cmc_tables.get(parameter_type.lower(), [])

    def validate_cmc_compliance(
        self,
        measurement_uncertainty: float,
        parameter_type: str,
        measurement_value: float
    ) -> Tuple[bool, str]:
        """
        Validate if measurement complies with CMC

        Args:
            measurement_uncertainty: Achieved measurement uncertainty
            parameter_type: Type of parameter
            measurement_value: Measured value

        Returns:
            Tuple of (is_compliant, message)
        """
        cmc_table = self.generate_cmc_table(parameter_type)

        for entry in cmc_table:
            if entry.range_min <= measurement_value <= entry.range_max:
                if measurement_uncertainty <= entry.best_measurement_capability:
                    return True, f"Compliant with CMC: {entry.best_measurement_capability} {entry.unit}"
                else:
                    return False, (
                        f"Exceeds CMC: {measurement_uncertainty} > "
                        f"{entry.best_measurement_capability} {entry.unit}"
                    )

        return False, f"Value {measurement_value} outside CMC range"

    def export_certificate_data(self, certificate: CalibrationCertificate) -> Dict:
        """Export certificate as dictionary for JSON/database storage"""
        return {
            "certificate_number": certificate.certificate_number,
            "issue_date": certificate.issue_date,
            "calibration_date": certificate.calibration_date,
            "next_calibration_date": certificate.next_calibration_date,
            "instrument": {
                "id": certificate.instrument_data.id,
                "type": certificate.instrument_data.instrument_type.value,
                "make": certificate.instrument_data.make,
                "model": certificate.instrument_data.model,
                "serial_number": certificate.instrument_data.serial_number
            },
            "calibrated_by": certificate.calibrated_by,
            "approved_by": certificate.approved_by
        }
