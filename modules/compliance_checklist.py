"""
Compliance Checklist Generator Module

This module generates comprehensive checklists for:
- IEC 61215/61730 test procedures
- Pre-test verification
- During-test monitoring
- Post-test validation
- Non-conformance tracking

Author: PV Chamber Configurator
Version: 1.0.0
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ChecklistStatus(Enum):
    """Status of checklist items"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NOT_APPLICABLE = "na"
    FAILED = "failed"


class ChecklistCategory(Enum):
    """Category of checklist"""
    PRE_TEST = "pre_test"
    DURING_TEST = "during_test"
    POST_TEST = "post_test"
    CALIBRATION = "calibration"
    SAFETY = "safety"


@dataclass
class ChecklistItem:
    """Individual checklist item"""
    id: str
    description: str
    category: ChecklistCategory
    status: ChecklistStatus = ChecklistStatus.NOT_STARTED
    required: bool = True
    completed_by: str = ""
    completed_date: str = ""
    notes: str = ""
    verification_method: str = ""


@dataclass
class NonConformance:
    """Non-conformance record"""
    id: str
    test_id: str
    description: str
    severity: str  # CRITICAL, MAJOR, MINOR
    detected_date: str
    detected_by: str
    root_cause: str = ""
    corrective_action: str = ""
    preventive_action: str = ""
    status: str = "OPEN"  # OPEN, IN_PROGRESS, CLOSED
    closed_date: str = ""
    verified_by: str = ""


class ComplianceChecklist:
    """
    Compliance checklist generator and tracker
    """

    def __init__(self):
        """Initialize checklist system"""
        self.checklists: Dict[str, List[ChecklistItem]] = {}
        self.non_conformances: List[NonConformance] = []
        self.nc_counter = 0

    def generate_iec_61215_checklist(self, test_id: str) -> List[ChecklistItem]:
        """
        Generate IEC 61215 test-specific checklist

        Args:
            test_id: Test identifier (e.g., MST_11_UV, MST_12_Thermal_Cycling)

        Returns:
            List of ChecklistItem objects
        """
        checklists_map = {
            "MST_11_UV": self._mst_11_uv_checklist,
            "MST_12_Thermal_Cycling": self._mst_12_thermal_cycling_checklist,
            "MST_13_Humidity_Freeze": self._mst_13_humidity_freeze_checklist,
            "MST_14_Damp_Heat": self._mst_14_damp_heat_checklist,
        }

        generator = checklists_map.get(test_id, self._generic_test_checklist)
        checklist = generator()

        self.checklists[test_id] = checklist
        return checklist

    def _mst_11_uv_checklist(self) -> List[ChecklistItem]:
        """Generate MST 11 UV Preconditioning checklist"""
        return [
            # Pre-test
            ChecklistItem(
                id="MST11_PRE_01",
                description="Verify UV system calibration certificate is valid",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Check calibration date on certificate"
            ),
            ChecklistItem(
                id="MST11_PRE_02",
                description="Measure UV intensity uniformity across test plane",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Use calibrated UV radiometer at 9 points"
            ),
            ChecklistItem(
                id="MST11_PRE_03",
                description="Verify UV spectrum (280-400nm, UVA 90-97%, UVB 3-10%)",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Spectroradiometer measurement"
            ),
            ChecklistItem(
                id="MST11_PRE_04",
                description="Check chamber temperature control at 60±5°C",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Run temperature profile test"
            ),
            ChecklistItem(
                id="MST11_PRE_05",
                description="Install and position PV modules correctly",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Per IEC 61215 positioning requirements"
            ),
            # During-test
            ChecklistItem(
                id="MST11_DUR_01",
                description="Monitor UV intensity continuously (target: 60 W/m²)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Data logger with 1-minute intervals"
            ),
            ChecklistItem(
                id="MST11_DUR_02",
                description="Monitor chamber temperature (60±5°C)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Calibrated temperature sensors"
            ),
            ChecklistItem(
                id="MST11_DUR_03",
                description="Calculate accumulated UV dose (target: 15 kWh/m²)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Integrate UV intensity over time"
            ),
            ChecklistItem(
                id="MST11_DUR_04",
                description="Verify no UV lamp failures or degradation",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Visual inspection and intensity monitoring"
            ),
            # Post-test
            ChecklistItem(
                id="MST11_POST_01",
                description="Verify total UV dose = 15±0.5 kWh/m²",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Review data logs and calculate"
            ),
            ChecklistItem(
                id="MST11_POST_02",
                description="Perform visual inspection of modules",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Per IEC 61215 MST 01 criteria"
            ),
            ChecklistItem(
                id="MST11_POST_03",
                description="Measure module maximum power (Pmax)",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="STC conditions per IEC 61215 MST 02"
            ),
            ChecklistItem(
                id="MST11_POST_04",
                description="Document test results and deviations",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Complete test report form"
            ),
        ]

    def _mst_12_thermal_cycling_checklist(self) -> List[ChecklistItem]:
        """Generate MST 12 Thermal Cycling checklist"""
        return [
            # Pre-test
            ChecklistItem(
                id="MST12_PRE_01",
                description="Verify chamber temperature range: -40°C to +85°C",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Run temperature profile verification"
            ),
            ChecklistItem(
                id="MST12_PRE_02",
                description="Verify ramp rate capability: 1-3°C/min",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Measure actual ramp rate"
            ),
            ChecklistItem(
                id="MST12_PRE_03",
                description="Install temperature sensors on module rear surface",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Per IEC 61215 attachment method"
            ),
            ChecklistItem(
                id="MST12_PRE_04",
                description="Program test cycle: -40°C (30min) → +85°C (30min)",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Verify controller program"
            ),
            # During-test
            ChecklistItem(
                id="MST12_DUR_01",
                description="Monitor module temperature continuously",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Data logger with 1-minute intervals"
            ),
            ChecklistItem(
                id="MST12_DUR_02",
                description="Verify temperature dwells at -40°C and +85°C",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Check temperature logs"
            ),
            ChecklistItem(
                id="MST12_DUR_03",
                description="Track cycle count (target: 200 cycles)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Controller cycle counter"
            ),
            ChecklistItem(
                id="MST12_DUR_04",
                description="Perform interim visual inspections (every 50 cycles)",
                category=ChecklistCategory.DURING_TEST,
                required=False,
                verification_method="Visual examination during dwell periods"
            ),
            # Post-test
            ChecklistItem(
                id="MST12_POST_01",
                description="Verify 200 cycles completed successfully",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Review test logs"
            ),
            ChecklistItem(
                id="MST12_POST_02",
                description="Perform visual inspection per MST 01",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="IEC 61215 visual criteria"
            ),
            ChecklistItem(
                id="MST12_POST_03",
                description="Measure Pmax degradation (<5% required)",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="STC measurements before/after"
            ),
            ChecklistItem(
                id="MST12_POST_04",
                description="Perform wet leakage current test (MST 16)",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Per IEC 61215 MST 16 procedure"
            ),
        ]

    def _mst_13_humidity_freeze_checklist(self) -> List[ChecklistItem]:
        """Generate MST 13 Humidity-Freeze checklist"""
        return [
            # Pre-test
            ChecklistItem(
                id="MST13_PRE_01",
                description="Verify chamber capabilities: 85°C/85%RH and -40°C",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Temperature and humidity profile test"
            ),
            ChecklistItem(
                id="MST13_PRE_02",
                description="Calibrate humidity sensors",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Check calibration certificates"
            ),
            ChecklistItem(
                id="MST13_PRE_03",
                description="Install modules with proper drainage orientation",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Per IEC 61215 requirements"
            ),
            # During-test
            ChecklistItem(
                id="MST13_DUR_01",
                description="Monitor humidity during high-temp phase (85%RH)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Continuous data logging"
            ),
            ChecklistItem(
                id="MST13_DUR_02",
                description="Verify 20-hour dwell at 85°C/85%RH",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Review temperature/humidity logs"
            ),
            ChecklistItem(
                id="MST13_DUR_03",
                description="Verify 4-hour dwell at -40°C (no humidity control)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Review temperature logs"
            ),
            ChecklistItem(
                id="MST13_DUR_04",
                description="Track cycle count (target: 10 cycles)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Controller cycle counter"
            ),
            # Post-test
            ChecklistItem(
                id="MST13_POST_01",
                description="Verify 10 cycles completed",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Review test logs"
            ),
            ChecklistItem(
                id="MST13_POST_02",
                description="Visual inspection (no corrosion, delamination)",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="IEC 61215 MST 01 criteria"
            ),
            ChecklistItem(
                id="MST13_POST_03",
                description="Measure Pmax degradation",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="STC measurements"
            ),
        ]

    def _mst_14_damp_heat_checklist(self) -> List[ChecklistItem]:
        """Generate MST 14 Damp Heat checklist"""
        return [
            # Pre-test
            ChecklistItem(
                id="MST14_PRE_01",
                description="Verify chamber can maintain 85°C/85%RH for 1000 hours",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Run 24-hour stability test"
            ),
            ChecklistItem(
                id="MST14_PRE_02",
                description="Verify temperature uniformity (±2°C)",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Multi-point temperature mapping"
            ),
            ChecklistItem(
                id="MST14_PRE_03",
                description="Verify humidity uniformity (±3%RH)",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Multi-point humidity mapping"
            ),
            ChecklistItem(
                id="MST14_PRE_04",
                description="Install modules with proper spacing",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Ensure airflow not blocked"
            ),
            # During-test
            ChecklistItem(
                id="MST14_DUR_01",
                description="Monitor temperature continuously (85±2°C)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Data logging every 5 minutes"
            ),
            ChecklistItem(
                id="MST14_DUR_02",
                description="Monitor humidity continuously (85±5%RH)",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Data logging every 5 minutes"
            ),
            ChecklistItem(
                id="MST14_DUR_03",
                description="Log any deviations from setpoint",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Automated alarm system"
            ),
            ChecklistItem(
                id="MST14_DUR_04",
                description="Perform weekly visual inspections",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Check for condensation, damage"
            ),
            # Post-test
            ChecklistItem(
                id="MST14_POST_01",
                description="Verify 1000±2 hours exposure completed",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Review total test time"
            ),
            ChecklistItem(
                id="MST14_POST_02",
                description="Calculate actual temperature and humidity exposure",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Statistical analysis of logs"
            ),
            ChecklistItem(
                id="MST14_POST_03",
                description="Visual inspection (no corrosion, delamination, bubbles)",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="IEC 61215 MST 01 criteria"
            ),
            ChecklistItem(
                id="MST14_POST_04",
                description="Measure Pmax degradation (<5%)",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="STC measurements"
            ),
            ChecklistItem(
                id="MST14_POST_05",
                description="Perform insulation test (MST 05)",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Per IEC 61215 MST 05"
            ),
        ]

    def _generic_test_checklist(self) -> List[ChecklistItem]:
        """Generate generic test checklist"""
        return [
            ChecklistItem(
                id="GEN_PRE_01",
                description="Review test procedure and requirements",
                category=ChecklistCategory.PRE_TEST,
                required=True
            ),
            ChecklistItem(
                id="GEN_PRE_02",
                description="Verify all equipment calibrated",
                category=ChecklistCategory.PRE_TEST,
                required=True
            ),
            ChecklistItem(
                id="GEN_DUR_01",
                description="Monitor test parameters continuously",
                category=ChecklistCategory.DURING_TEST,
                required=True
            ),
            ChecklistItem(
                id="GEN_POST_01",
                description="Review and analyze test data",
                category=ChecklistCategory.POST_TEST,
                required=True
            ),
        ]

    def generate_pre_test_checklist(self) -> List[ChecklistItem]:
        """Generate generic pre-test verification checklist"""
        return [
            ChecklistItem(
                id="PRE_01",
                description="Equipment calibration certificates verified (within validity)",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Check all calibration dates"
            ),
            ChecklistItem(
                id="PRE_02",
                description="Chamber cleaned and free from contamination",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Visual inspection"
            ),
            ChecklistItem(
                id="PRE_03",
                description="Test specimens identified and documented",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Serial numbers recorded"
            ),
            ChecklistItem(
                id="PRE_04",
                description="Environmental conditions within acceptable limits",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Measure lab temp/humidity"
            ),
            ChecklistItem(
                id="PRE_05",
                description="Data acquisition system tested and operational",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Run test recording"
            ),
            ChecklistItem(
                id="PRE_06",
                description="Safety systems checked (door interlocks, alarms)",
                category=ChecklistCategory.SAFETY,
                required=True,
                verification_method="Functional test"
            ),
            ChecklistItem(
                id="PRE_07",
                description="Test procedure reviewed and understood",
                category=ChecklistCategory.PRE_TEST,
                required=True,
                verification_method="Team briefing completed"
            ),
        ]

    def generate_during_test_checklist(self) -> List[ChecklistItem]:
        """Generate generic during-test monitoring checklist"""
        return [
            ChecklistItem(
                id="DUR_01",
                description="Test parameters within specification",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Real-time monitoring"
            ),
            ChecklistItem(
                id="DUR_02",
                description="Data logging functioning correctly",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Verify data files created"
            ),
            ChecklistItem(
                id="DUR_03",
                description="No alarm conditions present",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Check alarm log"
            ),
            ChecklistItem(
                id="DUR_04",
                description="Test specimens visually normal",
                category=ChecklistCategory.DURING_TEST,
                required=True,
                verification_method="Periodic visual inspection"
            ),
        ]

    def generate_post_test_checklist(self) -> List[ChecklistItem]:
        """Generate generic post-test validation checklist"""
        return [
            ChecklistItem(
                id="POST_01",
                description="Test duration requirements met",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Review total time"
            ),
            ChecklistItem(
                id="POST_02",
                description="All data files saved and backed up",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Verify file integrity"
            ),
            ChecklistItem(
                id="POST_03",
                description="Test specimens removed and identified",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Match serial numbers"
            ),
            ChecklistItem(
                id="POST_04",
                description="Post-test measurements completed",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="All required data collected"
            ),
            ChecklistItem(
                id="POST_05",
                description="Test report drafted",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="Report template completed"
            ),
            ChecklistItem(
                id="POST_06",
                description="Non-conformances documented",
                category=ChecklistCategory.POST_TEST,
                required=True,
                verification_method="NCR forms completed if applicable"
            ),
        ]

    def track_non_conformances(
        self,
        test_id: str,
        description: str,
        severity: str,
        detected_by: str
    ) -> NonConformance:
        """
        Create and track a non-conformance

        Args:
            test_id: Test identifier
            description: Description of non-conformance
            severity: CRITICAL, MAJOR, or MINOR
            detected_by: Name of person who detected it

        Returns:
            NonConformance object
        """
        self.nc_counter += 1
        nc_id = f"NC-{datetime.now().strftime('%Y%m%d')}-{self.nc_counter:04d}"

        nc = NonConformance(
            id=nc_id,
            test_id=test_id,
            description=description,
            severity=severity,
            detected_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            detected_by=detected_by
        )

        self.non_conformances.append(nc)
        return nc

    def update_checklist_item(
        self,
        test_id: str,
        item_id: str,
        status: ChecklistStatus,
        completed_by: str = "",
        notes: str = ""
    ) -> bool:
        """
        Update a checklist item status

        Args:
            test_id: Test identifier
            item_id: Checklist item ID
            status: New status
            completed_by: Name of person completing the item
            notes: Additional notes

        Returns:
            True if updated successfully
        """
        if test_id not in self.checklists:
            return False

        for item in self.checklists[test_id]:
            if item.id == item_id:
                item.status = status
                item.completed_by = completed_by
                item.completed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                item.notes = notes
                return True

        return False

    def get_checklist_progress(self, test_id: str) -> Dict[str, Any]:
        """
        Get progress summary for a checklist

        Args:
            test_id: Test identifier

        Returns:
            Dictionary with progress statistics
        """
        if test_id not in self.checklists:
            return {}

        checklist = self.checklists[test_id]
        total = len(checklist)
        completed = sum(1 for item in checklist if item.status == ChecklistStatus.COMPLETED)
        in_progress = sum(1 for item in checklist if item.status == ChecklistStatus.IN_PROGRESS)
        failed = sum(1 for item in checklist if item.status == ChecklistStatus.FAILED)

        return {
            "total_items": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "not_started": total - completed - in_progress - failed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0
        }

    def export_checklist_report(self, test_id: str) -> str:
        """
        Export checklist as formatted report

        Args:
            test_id: Test identifier

        Returns:
            Formatted report string
        """
        if test_id not in self.checklists:
            return "Checklist not found"

        checklist = self.checklists[test_id]
        progress = self.get_checklist_progress(test_id)

        report = []
        report.append("=" * 80)
        report.append(f"COMPLIANCE CHECKLIST REPORT: {test_id}")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append("PROGRESS SUMMARY:")
        report.append(f"  Total Items: {progress['total_items']}")
        report.append(f"  Completed: {progress['completed']}")
        report.append(f"  In Progress: {progress['in_progress']}")
        report.append(f"  Failed: {progress['failed']}")
        report.append(f"  Completion: {progress['completion_percentage']:.1f}%")
        report.append("")
        report.append("CHECKLIST ITEMS:")
        report.append("-" * 80)

        # Group by category
        categories = {}
        for item in checklist:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        for category, items in categories.items():
            report.append(f"\n{category.value.upper().replace('_', ' ')}:")
            for item in items:
                status_symbol = {
                    ChecklistStatus.COMPLETED: "✓",
                    ChecklistStatus.IN_PROGRESS: "○",
                    ChecklistStatus.NOT_STARTED: "☐",
                    ChecklistStatus.FAILED: "✗",
                    ChecklistStatus.NOT_APPLICABLE: "—"
                }.get(item.status, "?")

                report.append(f"  [{status_symbol}] {item.id}: {item.description}")
                if item.completed_by:
                    report.append(f"      Completed by: {item.completed_by} on {item.completed_date}")
                if item.notes:
                    report.append(f"      Notes: {item.notes}")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)
