"""
Comprehensive Test Suite for PV Chamber Configurator
Compliance & Calibration Modules

Tests for:
- IEC Compliance Checker
- ISO 17025 Calibration
- Uncertainty Calculator
- Compliance Checklist
"""

import sys
import os
import unittest
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from modules.iec_compliance import (
    IECComplianceChecker,
    ChamberSpecifications,
    ComplianceResult
)
from modules.iso17025_calibration import (
    ISO17025Calibration,
    LabAccreditation,
    AccreditationBody,
    InstrumentData,
    InstrumentType,
    CalibrationResults,
    CalibrationPoint,
    EnvironmentalConditions,
    ReferenceStandard
)
from modules.uncertainty_calculator import (
    UncertaintyCalculator,
    UncertaintySource,
    UncertaintyType,
    DistributionType
)
from modules.compliance_checklist import (
    ComplianceChecklist,
    ChecklistStatus,
    ChecklistCategory
)


class TestIECCompliance(unittest.TestCase):
    """Test IEC Compliance Checker"""

    def setUp(self):
        """Set up test chamber specifications"""
        self.chamber_specs = ChamberSpecifications(
            temp_min=-45.0,
            temp_max=105.0,
            humidity_min=40.0,
            humidity_max=95.0,
            temp_uniformity=2.0,
            air_velocity=1.5,
            ramp_rate=2.0,
            recovery_time=25.0,
            volume=14.78,
            has_uv_system=True,
            uv_intensity_max=250.0,
            uv_wavelength_range=(280, 400),
            uv_uniformity=8.5
        )
        self.checker = IECComplianceChecker(self.chamber_specs)

    def test_chamber_specs_creation(self):
        """Test chamber specifications creation"""
        self.assertEqual(self.chamber_specs.temp_min, -45.0)
        self.assertEqual(self.chamber_specs.temp_max, 105.0)
        self.assertTrue(self.chamber_specs.has_uv_system)

    def test_uv_preconditioning_compliance_pass(self):
        """Test UV preconditioning compliance - PASS scenario"""
        result = self.checker.check_uv_preconditioning_compliance()
        self.assertEqual(result.test_id, "IEC_61215_MST_11")
        self.assertIsInstance(result, ComplianceResult)
        # Should pass with our chamber specs
        self.assertTrue(result.is_compliant)

    def test_uv_preconditioning_compliance_fail_no_uv(self):
        """Test UV preconditioning compliance - FAIL scenario (no UV system)"""
        chamber_no_uv = ChamberSpecifications(
            temp_min=-45.0,
            temp_max=105.0,
            humidity_min=40.0,
            humidity_max=95.0,
            temp_uniformity=2.0,
            air_velocity=1.5,
            ramp_rate=2.0,
            recovery_time=25.0,
            volume=14.78,
            has_uv_system=False  # No UV system
        )
        checker_no_uv = IECComplianceChecker(chamber_no_uv)
        result = checker_no_uv.check_uv_preconditioning_compliance()
        self.assertFalse(result.is_compliant)
        self.assertGreater(len(result.issues), 0)
        self.assertIn("UV system not available", result.issues[0])

    def test_thermal_cycling_compliance(self):
        """Test thermal cycling compliance"""
        result = self.checker.check_thermal_cycling_compliance()
        self.assertEqual(result.test_id, "IEC_61215_MST_12")
        self.assertTrue(result.is_compliant)
        self.assertIn("Ramp Rate", result.requirements)

    def test_damp_heat_compliance(self):
        """Test damp heat compliance"""
        result = self.checker.check_damp_heat_compliance()
        self.assertEqual(result.test_id, "IEC_61215_MST_14")
        self.assertTrue(result.is_compliant)

    def test_humidity_freeze_compliance(self):
        """Test humidity-freeze compliance"""
        result = self.checker.check_humidity_freeze_compliance()
        self.assertEqual(result.test_id, "IEC_61215_MST_13")
        self.assertTrue(result.is_compliant)

    def test_iec_61215_full_validation(self):
        """Test full IEC 61215 validation"""
        results = self.checker.validate_iec_61215_capability()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 4)  # 4 main tests
        for result in results:
            self.assertIsInstance(result, ComplianceResult)

    def test_iec_61730_validation(self):
        """Test IEC 61730 safety validation"""
        results = self.checker.validate_iec_61730_capability()
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_iec_60068_uniformity(self):
        """Test IEC 60068 temperature uniformity"""
        result = self.checker.validate_chamber_uniformity()
        self.assertEqual(result.test_id, "IEC_60068_UNIFORMITY")
        self.assertTrue(result.is_compliant)  # ±2°C meets requirement

    def test_iec_60068_air_velocity(self):
        """Test IEC 60068 air velocity"""
        result = self.checker.check_air_velocity()
        self.assertEqual(result.test_id, "IEC_60068_AIR_VELOCITY")
        self.assertTrue(result.is_compliant)  # 1.5 m/s meets ≤2 m/s

    def test_iec_60068_recovery_time(self):
        """Test IEC 60068 recovery time"""
        result = self.checker.validate_recovery_time()
        self.assertEqual(result.test_id, "IEC_60068_RECOVERY")
        self.assertTrue(result.is_compliant)  # 25 min meets ≤30 min

    def test_compliance_summary_generation(self):
        """Test compliance summary generation"""
        # Run all tests first
        self.checker.validate_iec_61215_capability()
        self.checker.validate_iec_61730_capability()

        summary = self.checker.generate_compliance_summary()

        self.assertIn('overall_compliance', summary)
        self.assertIn('test_results', summary)
        self.assertIn('chamber_specs', summary)
        self.assertGreater(summary['overall_compliance']['total_tests'], 0)

    def test_gaps_identification(self):
        """Test compliance gaps identification"""
        # Create chamber with known gaps
        bad_chamber = ChamberSpecifications(
            temp_min=0.0,  # Can't reach -40°C
            temp_max=80.0,  # Can't reach 85°C
            humidity_min=50.0,
            humidity_max=80.0,  # Can't reach 85%RH
            temp_uniformity=3.0,  # Exceeds ±2°C
            air_velocity=1.5,
            ramp_rate=0.5,  # Below 1-3°C/min range
            recovery_time=40.0,  # Exceeds 30 min
            volume=14.78,
            has_uv_system=False
        )

        bad_checker = IECComplianceChecker(bad_chamber)
        bad_checker.validate_iec_61215_capability()

        gaps = bad_checker.identify_gaps()
        self.assertGreater(len(gaps), 0)
        # Should have multiple gaps
        for gap in gaps:
            self.assertIn('test_id', gap)
            self.assertIn('issues', gap)
            self.assertIn('recommendations', gap)

    def test_report_generation(self):
        """Test IEC 61215 report generation"""
        self.checker.validate_iec_61215_capability()
        report = self.checker.generate_iec_61215_report()

        self.assertIsInstance(report, str)
        self.assertIn("IEC 61215 COMPLIANCE REPORT", report)
        self.assertIn("CHAMBER SPECIFICATIONS", report)
        self.assertGreater(len(report), 100)


class TestISO17025Calibration(unittest.TestCase):
    """Test ISO 17025 Calibration Module"""

    def setUp(self):
        """Set up test lab and calibration system"""
        self.lab_acc = LabAccreditation(
            lab_name="Test PV Laboratory",
            accreditation_body=AccreditationBody.NABL,
            certificate_number="TC-TEST-001",
            scope="Temperature, Humidity, UV Calibration",
            address="Test Address, India",
            contact="+91-123-456-7890",
            email="test@lab.com"
        )

        self.cal_system = ISO17025Calibration(self.lab_acc)

        # Add a reference standard
        self.ref_std = ReferenceStandard(
            id="RTD-TEST-001",
            name="Test Reference RTD",
            make="Fluke",
            model="5608",
            serial_number="TEST123",
            certificate_number="NIST-TEST-001",
            calibration_date="2024-01-01",
            next_calibration_date="2025-01-01",
            uncertainty=0.05,
            uncertainty_unit="°C",
            traceability="NIST",
            parameter_type="Temperature",
            range_min=-50.0,
            range_max=150.0
        )

        self.cal_system.add_reference_standard(self.ref_std)

    def test_lab_accreditation_creation(self):
        """Test lab accreditation creation"""
        self.assertEqual(self.lab_acc.lab_name, "Test PV Laboratory")
        self.assertEqual(self.lab_acc.accreditation_body, AccreditationBody.NABL)

    def test_add_reference_standard(self):
        """Test adding reference standard"""
        std = self.cal_system.get_reference_standard("RTD-TEST-001")
        self.assertIsNotNone(std)
        self.assertEqual(std.make, "Fluke")
        self.assertEqual(std.traceability, "NIST")

    def test_calibration_certificate_generation(self):
        """Test calibration certificate generation"""
        # Create instrument data
        instrument = InstrumentData(
            id="INST-001",
            instrument_type=InstrumentType.TEMPERATURE_RTD,
            make="Test Mfg",
            model="RTD-100",
            serial_number="SN12345",
            identification_number="ID-001",
            owner="Test Customer",
            location="Chamber 1"
        )

        # Create calibration points
        cal_points = [
            CalibrationPoint(-40.0, -40.05, -40.03, -40.04, -40.04, -0.04, 0.15),
            CalibrationPoint(0.0, 0.02, 0.01, 0.02, 0.017, 0.017, 0.15),
            CalibrationPoint(85.0, 85.10, 85.08, 85.09, 85.09, 0.09, 0.15)
        ]

        env_conditions = EnvironmentalConditions(
            temperature=23.0,
            temperature_uncertainty=0.5,
            humidity=50.0,
            humidity_uncertainty=5.0,
            pressure=101.3,
            pressure_uncertainty=0.5
        )

        cal_results = CalibrationResults(
            calibration_points=cal_points,
            parameter="Temperature",
            unit="°C",
            procedure_reference="CAL-TEMP-001",
            environmental_conditions=env_conditions
        )

        # Generate certificate
        certificate = self.cal_system.generate_calibration_certificate(
            instrument_data=instrument,
            reference_standard_id="RTD-TEST-001",
            calibration_results=cal_results,
            calibrated_by="Test Technician",
            reviewed_by="Test Supervisor",
            approved_by="Test Director"
        )

        self.assertIsNotNone(certificate)
        self.assertIn("CAL-", certificate.certificate_number)
        self.assertEqual(len(certificate.calibration_results.calibration_points), 3)

    def test_next_calibration_date_calculation(self):
        """Test next calibration date calculation"""
        current_date = datetime(2024, 1, 1)
        next_date = self.cal_system.calculate_next_calibration_date(current_date, 12)
        self.assertIn("2024-12", next_date)  # Approximately 12 months later

    def test_certificate_html_generation(self):
        """Test HTML certificate generation"""
        # Create minimal certificate
        instrument = InstrumentData(
            id="INST-001",
            instrument_type=InstrumentType.TEMPERATURE_RTD,
            make="Test",
            model="MODEL",
            serial_number="SN",
            identification_number="ID",
            owner="Owner",
            location="Location"
        )

        cal_point = CalibrationPoint(25.0, 25.05, 25.04, 25.05, 25.047, 0.047, 0.15)
        env = EnvironmentalConditions(23.0, 0.5, 50.0, 5.0, 101.3, 0.5)

        cal_results = CalibrationResults(
            calibration_points=[cal_point],
            parameter="Temperature",
            unit="°C",
            procedure_reference="TEST-001",
            environmental_conditions=env
        )

        certificate = self.cal_system.generate_calibration_certificate(
            instrument_data=instrument,
            reference_standard_id="RTD-TEST-001",
            calibration_results=cal_results,
            calibrated_by="Tech",
            reviewed_by="Sup",
            approved_by="Dir"
        )

        html = self.cal_system.create_certificate_html(certificate)

        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("CALIBRATION CERTIFICATE", html)
        self.assertIn(certificate.certificate_number, html)

    def test_cmc_table_generation(self):
        """Test CMC table generation"""
        temp_cmc = self.cal_system.generate_cmc_table("temperature")
        self.assertGreater(len(temp_cmc), 0)
        self.assertEqual(temp_cmc[0].parameter, "Temperature")

        humidity_cmc = self.cal_system.generate_cmc_table("humidity")
        self.assertGreater(len(humidity_cmc), 0)

        uv_cmc = self.cal_system.generate_cmc_table("uv_intensity")
        self.assertGreater(len(uv_cmc), 0)

    def test_cmc_compliance_validation(self):
        """Test CMC compliance validation"""
        # Test compliant measurement
        is_compliant, msg = self.cal_system.validate_cmc_compliance(
            measurement_uncertainty=0.10,
            parameter_type="temperature",
            measurement_value=25.0
        )
        self.assertTrue(is_compliant)

        # Test non-compliant measurement
        is_compliant, msg = self.cal_system.validate_cmc_compliance(
            measurement_uncertainty=0.50,  # Exceeds CMC
            parameter_type="temperature",
            measurement_value=25.0
        )
        self.assertFalse(is_compliant)


class TestUncertaintyCalculator(unittest.TestCase):
    """Test Uncertainty Calculator Module"""

    def test_type_a_uncertainty_calculation(self):
        """Test Type A uncertainty calculation"""
        measurements = [25.0, 25.1, 24.9, 25.0, 25.1, 24.95, 25.05, 25.0, 25.02, 24.98]
        u_a, dof = UncertaintyCalculator.calculate_type_a_uncertainty(measurements)

        self.assertGreater(u_a, 0)
        self.assertEqual(dof, len(measurements) - 1)

    def test_type_b_uncertainty_calculation(self):
        """Test Type B uncertainty calculation"""
        # Rectangular distribution
        u_rect = UncertaintyCalculator.calculate_type_b_uncertainty(
            value=0.1,
            distribution=DistributionType.RECTANGULAR
        )
        self.assertAlmostEqual(u_rect, 0.1 / (3 ** 0.5), places=5)

        # Normal distribution
        u_norm = UncertaintyCalculator.calculate_type_b_uncertainty(
            value=0.1,
            distribution=DistributionType.NORMAL
        )
        self.assertAlmostEqual(u_norm, 0.1 / 2.0, places=5)

    def test_resolution_uncertainty(self):
        """Test resolution uncertainty calculation"""
        resolution = 0.1
        u_res = UncertaintyCalculator.calculate_resolution_uncertainty(resolution)
        expected = resolution / (2 * (3 ** 0.5))
        self.assertAlmostEqual(u_res, expected, places=6)

    def test_combined_uncertainty(self):
        """Test combined uncertainty calculation"""
        sources = [
            UncertaintySource(
                name="Source 1",
                value=0.05,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.NORMAL,
                sensitivity_coefficient=1.0
            ),
            UncertaintySource(
                name="Source 2",
                value=0.1,
                uncertainty_type=UncertaintyType.TYPE_B,
                distribution=DistributionType.RECTANGULAR,
                sensitivity_coefficient=1.0
            )
        ]

        uc = UncertaintyCalculator.calculate_combined_uncertainty(sources)
        self.assertGreater(uc, 0)
        # Should be greater than individual components
        self.assertGreater(uc, 0.025)  # 0.05/2

    def test_expanded_uncertainty(self):
        """Test expanded uncertainty calculation"""
        uc = 0.05
        k = 2.0
        U = UncertaintyCalculator.calculate_expanded_uncertainty(uc, k)
        self.assertEqual(U, uc * k)

    def test_temperature_sensor_budget(self):
        """Test complete temperature sensor uncertainty budget"""
        budget = UncertaintyCalculator.create_temperature_sensor_budget(
            measured_temp=85.0,
            reference_uncertainty=0.05,
            resolution=0.1,
            repeatability_stdev=0.08,
            drift=0.03,
            num_readings=10
        )

        self.assertEqual(budget.parameter_name, "Temperature")
        self.assertEqual(budget.measured_value, 85.0)
        self.assertEqual(budget.unit, "°C")
        self.assertGreater(budget.combined_standard_uncertainty, 0)
        self.assertGreater(budget.expanded_uncertainty, budget.combined_standard_uncertainty)
        self.assertEqual(budget.coverage_factor, 2.0)

    def test_humidity_sensor_budget(self):
        """Test humidity sensor uncertainty budget"""
        budget = UncertaintyCalculator.create_humidity_sensor_budget(
            measured_rh=85.0,
            reference_uncertainty=1.0,
            resolution=0.1,
            repeatability_stdev=0.5,
            num_readings=10
        )

        self.assertEqual(budget.parameter_name, "Relative Humidity")
        self.assertEqual(budget.unit, "%RH")
        self.assertGreater(budget.expanded_uncertainty, 0)

    def test_uv_intensity_budget(self):
        """Test UV intensity uncertainty budget"""
        budget = UncertaintyCalculator.create_uv_intensity_budget(
            measured_intensity=60.0,
            reference_uncertainty=2.0,
            resolution=1.0,
            repeatability_stdev=1.5,
            uniformity=5.0,
            num_readings=10
        )

        self.assertEqual(budget.parameter_name, "UV Irradiance")
        self.assertEqual(budget.unit, "W/m²")
        self.assertEqual(len(budget.sources), 4)  # 4 uncertainty sources

    def test_budget_table_generation(self):
        """Test uncertainty budget table generation"""
        budget = UncertaintyCalculator.create_temperature_sensor_budget(
            measured_temp=25.0,
            num_readings=5
        )

        table = UncertaintyCalculator.generate_budget_table(budget)

        self.assertIn("UNCERTAINTY BUDGET", table)
        self.assertIn("Temperature", table)
        self.assertIn("Combined Standard Uncertainty", table)
        self.assertIn("Expanded Uncertainty", table)


class TestComplianceChecklist(unittest.TestCase):
    """Test Compliance Checklist Module"""

    def setUp(self):
        """Set up checklist system"""
        self.checklist_sys = ComplianceChecklist()

    def test_mst_11_uv_checklist_generation(self):
        """Test MST 11 UV checklist generation"""
        checklist = self.checklist_sys.generate_iec_61215_checklist("MST_11_UV")

        self.assertGreater(len(checklist), 0)
        # Should have pre-test, during-test, and post-test items
        categories = set(item.category for item in checklist)
        self.assertIn(ChecklistCategory.PRE_TEST, categories)
        self.assertIn(ChecklistCategory.DURING_TEST, categories)
        self.assertIn(ChecklistCategory.POST_TEST, categories)

    def test_mst_12_thermal_cycling_checklist(self):
        """Test MST 12 thermal cycling checklist"""
        checklist = self.checklist_sys.generate_iec_61215_checklist("MST_12_Thermal_Cycling")
        self.assertGreater(len(checklist), 0)

        # Check specific items exist
        item_ids = [item.id for item in checklist]
        self.assertIn("MST12_PRE_01", item_ids)
        self.assertIn("MST12_DUR_01", item_ids)
        self.assertIn("MST12_POST_01", item_ids)

    def test_mst_14_damp_heat_checklist(self):
        """Test MST 14 damp heat checklist"""
        checklist = self.checklist_sys.generate_iec_61215_checklist("MST_14_Damp_Heat")
        self.assertGreater(len(checklist), 0)

        # Damp heat should have specific monitoring requirements
        descriptions = [item.description for item in checklist]
        self.assertTrue(any("1000" in desc for desc in descriptions))

    def test_pre_test_checklist(self):
        """Test generic pre-test checklist"""
        checklist = self.checklist_sys.generate_pre_test_checklist()
        self.assertGreater(len(checklist), 0)

        # All items should be PRE_TEST or SAFETY category
        for item in checklist:
            self.assertIn(item.category, [ChecklistCategory.PRE_TEST, ChecklistCategory.SAFETY])

    def test_during_test_checklist(self):
        """Test during-test checklist"""
        checklist = self.checklist_sys.generate_during_test_checklist()
        self.assertGreater(len(checklist), 0)

        for item in checklist:
            self.assertEqual(item.category, ChecklistCategory.DURING_TEST)

    def test_post_test_checklist(self):
        """Test post-test checklist"""
        checklist = self.checklist_sys.generate_post_test_checklist()
        self.assertGreater(len(checklist), 0)

        for item in checklist:
            self.assertEqual(item.category, ChecklistCategory.POST_TEST)

    def test_checklist_item_update(self):
        """Test updating checklist item status"""
        checklist = self.checklist_sys.generate_iec_61215_checklist("MST_11_UV")

        # Update an item
        success = self.checklist_sys.update_checklist_item(
            test_id="MST_11_UV",
            item_id="MST11_PRE_01",
            status=ChecklistStatus.COMPLETED,
            completed_by="Test User",
            notes="Test completion"
        )

        self.assertTrue(success)

    def test_checklist_progress_tracking(self):
        """Test checklist progress tracking"""
        test_id = "MST_11_UV"
        checklist = self.checklist_sys.generate_iec_61215_checklist(test_id)

        # Mark some items as completed
        items = checklist[:3]
        for item in items:
            self.checklist_sys.update_checklist_item(
                test_id=test_id,
                item_id=item.id,
                status=ChecklistStatus.COMPLETED,
                completed_by="Tester"
            )

        progress = self.checklist_sys.get_checklist_progress(test_id)

        self.assertEqual(progress['completed'], 3)
        self.assertGreater(progress['total_items'], 0)
        self.assertGreater(progress['completion_percentage'], 0)

    def test_non_conformance_tracking(self):
        """Test non-conformance tracking"""
        nc = self.checklist_sys.track_non_conformances(
            test_id="MST_11_UV",
            description="UV intensity below specification",
            severity="MAJOR",
            detected_by="Inspector"
        )

        self.assertIsNotNone(nc)
        self.assertIn("NC-", nc.id)
        self.assertEqual(nc.severity, "MAJOR")
        self.assertEqual(nc.status, "OPEN")

        # Check it's in the list
        self.assertEqual(len(self.checklist_sys.non_conformances), 1)

    def test_checklist_report_export(self):
        """Test checklist report export"""
        test_id = "MST_11_UV"
        checklist = self.checklist_sys.generate_iec_61215_checklist(test_id)

        # Mark one item completed
        self.checklist_sys.update_checklist_item(
            test_id=test_id,
            item_id=checklist[0].id,
            status=ChecklistStatus.COMPLETED,
            completed_by="Tester"
        )

        report = self.checklist_sys.export_checklist_report(test_id)

        self.assertIn("COMPLIANCE CHECKLIST REPORT", report)
        self.assertIn(test_id, report)
        self.assertIn("PROGRESS SUMMARY", report)
        self.assertGreater(len(report), 100)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIECCompliance))
    suite.addTests(loader.loadTestsFromTestCase(TestISO17025Calibration))
    suite.addTests(loader.loadTestsFromTestCase(TestUncertaintyCalculator))
    suite.addTests(loader.loadTestsFromTestCase(TestComplianceChecklist))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
