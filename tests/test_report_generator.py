"""
Comprehensive Test Suite for Report Generator Module
"""

import unittest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.report_generator import ReportGenerator
from modules.report_templates import TemplateManager, get_default_template
from modules.pdf_builder import PDFBuilder
from modules.excel_builder import ExcelBuilder


class TestPDFBuilder(unittest.TestCase):
    """Test PDF builder utilities"""

    def setUp(self):
        """Set up test fixtures"""
        self.output_dir = 'tests/output'
        os.makedirs(self.output_dir, exist_ok=True)
        self.test_pdf_path = os.path.join(self.output_dir, 'test_report.pdf')

    def test_pdf_creation(self):
        """Test basic PDF creation"""
        pdf = PDFBuilder(self.test_pdf_path, title="Test Report")
        pdf.add_cover_page(company_name="Test Company", subtitle="Test Subtitle")
        pdf.add_section("Test Section", "This is a test section content.")
        pdf.build()

        self.assertTrue(os.path.exists(self.test_pdf_path))
        self.assertGreater(os.path.getsize(self.test_pdf_path), 0)

    def test_pdf_with_tables(self):
        """Test PDF with tables"""
        pdf = PDFBuilder(self.test_pdf_path, title="Table Test")
        pdf.add_section("Data Table")

        data = [
            ['Item 1', '100', 'PASS'],
            ['Item 2', '200', 'PASS'],
            ['Item 3', '150', 'FAIL']
        ]
        headers = ['Item', 'Value', 'Status']

        pdf.add_table(data, headers=headers)
        pdf.build()

        self.assertTrue(os.path.exists(self.test_pdf_path))

    def test_pdf_with_key_value(self):
        """Test PDF with key-value tables"""
        pdf = PDFBuilder(self.test_pdf_path, title="Key-Value Test")

        data = {
            "Temperature": "85°C",
            "Humidity": "85% RH",
            "UV Intensity": "60 W/m²"
        }

        pdf.add_key_value_table(data, "Test Parameters")
        pdf.build()

        self.assertTrue(os.path.exists(self.test_pdf_path))

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)


class TestExcelBuilder(unittest.TestCase):
    """Test Excel builder utilities"""

    def setUp(self):
        """Set up test fixtures"""
        self.output_dir = 'tests/output'
        os.makedirs(self.output_dir, exist_ok=True)
        self.test_excel_path = os.path.join(self.output_dir, 'test_report.xlsx')

    def test_excel_creation(self):
        """Test basic Excel creation"""
        excel = ExcelBuilder(self.test_excel_path)
        sheet = excel.create_sheet("Test Sheet")

        headers = ['Column 1', 'Column 2', 'Column 3']
        data = [
            ['A1', 'B1', 'C1'],
            ['A2', 'B2', 'C2']
        ]

        excel.write_header_row(sheet, headers)
        excel.write_data_rows(sheet, data)
        excel.save()

        self.assertTrue(os.path.exists(self.test_excel_path))

    def test_excel_formatting(self):
        """Test Excel formatting"""
        excel = ExcelBuilder(self.test_excel_path)
        sheet = excel.create_sheet("Formatted Sheet")

        headers = ['Name', 'Value']
        data = [['Item 1', '100'], ['Item 2', '200']]

        excel.write_header_row(sheet, headers)
        excel.write_data_rows(sheet, data, alternating_colors=True)
        excel.auto_fit_columns(sheet)
        excel.save()

        self.assertTrue(os.path.exists(self.test_excel_path))

    def test_excel_formulas(self):
        """Test Excel formulas"""
        excel = ExcelBuilder(self.test_excel_path)
        sheet = excel.create_sheet("Formula Sheet")

        excel.write_header_row(sheet, ['Value', 'Total'])
        excel.write_data_rows(sheet, [['100'], ['200'], ['300']], start_row=2)
        excel.add_formula(sheet, 'B5', 'SUM(A2:A4)')
        excel.save()

        self.assertTrue(os.path.exists(self.test_excel_path))

    def tearDown(self):
        """Clean up test files"""
        if os.path.exists(self.test_excel_path):
            os.remove(self.test_excel_path)


class TestTemplateManager(unittest.TestCase):
    """Test template management"""

    def test_get_default_template(self):
        """Test getting default templates"""
        template = get_default_template('technical_specification')
        self.assertIsNotNone(template)
        self.assertEqual(template.report_type, 'technical_specification')

    def test_template_sections(self):
        """Test template section management"""
        template = get_default_template('technical_specification')
        sections = template.get_section_order()
        self.assertIsInstance(sections, list)
        self.assertGreater(len(sections), 0)

    def test_section_enabled(self):
        """Test section enabled check"""
        template = get_default_template('technical_specification')
        is_enabled = template.is_section_enabled('Executive Summary')
        self.assertTrue(is_enabled)


class TestReportGenerator(unittest.TestCase):
    """Test main report generator"""

    def setUp(self):
        """Set up test fixtures"""
        self.output_dir = 'tests/output'
        os.makedirs(self.output_dir, exist_ok=True)

        self.white_label_config = {
            'company_name': 'Test Company',
            'company_address': 'Test Address',
            'company_email': 'test@example.com',
            'user_name': 'Test User'
        }

        self.data_sources = {
            'chamber_specs': {
                'dimensions': '3200 x 2100 x 2200 mm',
                'volume': '14.8 m³',
                'temp_range': '-45°C to +105°C',
                'humidity_range': '40% to 95% RH',
                'uv_intensity': '60 W/m²'
            },
            'uv_system': {
                'led_type': 'High-efficiency UV LED',
                'num_leds': '28 units',
                'total_power': '2.4 kW'
            }
        }

    def test_pdf_technical_spec_generation(self):
        """Test Technical Specification PDF generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        pdf_path = os.path.join(self.output_dir, 'technical_spec.pdf')

        result = generator.generate_pdf_report('technical_specification', pdf_path)

        self.assertEqual(result, pdf_path)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)

    def test_pdf_test_execution_generation(self):
        """Test Test Execution PDF generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        pdf_path = os.path.join(self.output_dir, 'test_execution.pdf')

        result = generator.generate_pdf_report('test_execution', pdf_path)

        self.assertTrue(os.path.exists(pdf_path))

    def test_pdf_compliance_generation(self):
        """Test Compliance PDF generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        pdf_path = os.path.join(self.output_dir, 'compliance.pdf')

        result = generator.generate_pdf_report('compliance', pdf_path)

        self.assertTrue(os.path.exists(pdf_path))

    def test_pdf_commercial_proposal_generation(self):
        """Test Commercial Proposal PDF generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        pdf_path = os.path.join(self.output_dir, 'commercial_proposal.pdf')

        result = generator.generate_pdf_report('commercial_proposal', pdf_path)

        self.assertTrue(os.path.exists(pdf_path))

    def test_pdf_business_analysis_generation(self):
        """Test Business Analysis PDF generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        pdf_path = os.path.join(self.output_dir, 'business_analysis.pdf')

        result = generator.generate_pdf_report('business_analysis', pdf_path)

        self.assertTrue(os.path.exists(pdf_path))

    def test_excel_technical_spec_generation(self):
        """Test Technical Specification Excel generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        excel_path = os.path.join(self.output_dir, 'technical_spec.xlsx')

        result = generator.generate_excel_report('technical_specification', excel_path)

        self.assertEqual(result, excel_path)
        self.assertTrue(os.path.exists(excel_path))
        self.assertGreater(os.path.getsize(excel_path), 0)

    def test_excel_test_execution_generation(self):
        """Test Test Execution Excel generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        excel_path = os.path.join(self.output_dir, 'test_execution.xlsx')

        result = generator.generate_excel_report('test_execution', excel_path)

        self.assertTrue(os.path.exists(excel_path))

    def test_excel_business_analysis_generation(self):
        """Test Business Analysis Excel generation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        excel_path = os.path.join(self.output_dir, 'business_analysis.xlsx')

        result = generator.generate_excel_report('business_analysis', excel_path)

        self.assertTrue(os.path.exists(excel_path))

    def test_data_validation(self):
        """Test data validation"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)

        required_fields = ['chamber_specs', 'uv_system']
        is_complete, missing = generator.validate_data_completeness(required_fields)

        self.assertTrue(is_complete)
        self.assertEqual(len(missing), 0)

    def test_missing_data_handling(self):
        """Test missing data handling"""
        generator = ReportGenerator(self.white_label_config, {})

        default_value = generator.handle_missing_data('chamber_specs')
        self.assertIsNotNone(default_value)

    def test_invalid_report_type(self):
        """Test invalid report type"""
        generator = ReportGenerator(self.white_label_config, self.data_sources)
        pdf_path = os.path.join(self.output_dir, 'invalid.pdf')

        with self.assertRaises(ValueError):
            generator.generate_pdf_report('invalid_type', pdf_path)

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.output_dir):
            # Don't delete for inspection
            pass


class TestDataCollection(unittest.TestCase):
    """Test data collection methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.white_label_config = {
            'company_name': 'Test Company',
            'user_name': 'Test User'
        }
        self.generator = ReportGenerator(self.white_label_config)

    def test_chamber_specifications(self):
        """Test chamber specifications collection"""
        specs = self.generator._get_chamber_specifications()
        self.assertIsInstance(specs, dict)
        self.assertIn('Internal Dimensions', specs)

    def test_performance_data(self):
        """Test performance data collection"""
        perf_data = self.generator._get_performance_data()
        self.assertIn('headers', perf_data)
        self.assertIn('data', perf_data)

    def test_cost_breakdown(self):
        """Test cost breakdown collection"""
        cost_data = self.generator._get_cost_breakdown()
        self.assertIn('headers', cost_data)
        self.assertIn('data', cost_data)

    def test_tco_breakdown(self):
        """Test TCO breakdown collection"""
        tco_data = self.generator._get_tco_breakdown()
        self.assertIsInstance(tco_data, dict)


def run_all_tests():
    """Run all test suites"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPDFBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestExcelBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestReportGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDataCollection))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    print("=" * 70)
    print("COMPREHENSIVE REPORT GENERATOR TEST SUITE")
    print("=" * 70)
    print()

    result = run_all_tests()

    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
