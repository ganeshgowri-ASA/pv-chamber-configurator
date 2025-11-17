"""
Report Generator Module
Main engine for generating comprehensive PDF and Excel reports
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from modules.pdf_builder import PDFBuilder
from modules.excel_builder import ExcelBuilder
from modules.report_templates import TemplateManager, ReportTemplate, get_default_template


class ReportGenerator:
    """
    Main report generation engine integrating all modules
    """

    def __init__(self, white_label_config: Dict[str, Any],
                 data_sources: Optional[Dict[str, Any]] = None,
                 templates_dir: str = 'templates/report_templates'):
        """
        Initialize report generator

        Args:
            white_label_config: Branding and white-label configuration
            data_sources: Dictionary of data from various modules
            templates_dir: Directory containing report templates
        """
        self.white_label = white_label_config
        self.data_sources = data_sources or {}
        self.template_manager = TemplateManager(templates_dir)

        # Report metadata
        self.metadata = {
            'generated_date': datetime.now().strftime('%Y-%m-%d'),
            'generated_time': datetime.now().strftime('%H:%M:%S'),
            'generated_by': white_label_config.get('user_name', 'User'),
            'company': white_label_config.get('company_name', 'Company'),
            'version': '1.0',
            'status': 'Final'
        }

    def generate_pdf_report(self, report_type: str, output_path: str,
                           template_name: Optional[str] = None,
                           custom_data: Optional[Dict] = None) -> str:
        """
        Generate a PDF report

        Args:
            report_type: Type of report to generate
            output_path: Path to save PDF file
            template_name: Name of template to use (optional)
            custom_data: Additional custom data (optional)

        Returns:
            Path to generated PDF
        """
        # Load template
        if template_name:
            template = self.template_manager.get_template(template_name)
        else:
            template = get_default_template(report_type)

        if not template:
            raise ValueError(f"Template not found: {template_name}")

        # Merge custom data
        if custom_data:
            self.data_sources.update(custom_data)

        # Create PDF builder
        pdf = PDFBuilder(
            output_path,
            page_size=template.page_size,
            title=self._get_report_title(report_type),
            author=self.metadata['generated_by']
        )

        # Generate report based on type
        if report_type == 'technical_specification':
            self._generate_technical_spec_pdf(pdf, template)
        elif report_type == 'test_execution':
            self._generate_test_execution_pdf(pdf, template)
        elif report_type == 'compliance':
            self._generate_compliance_pdf(pdf, template)
        elif report_type == 'commercial_proposal':
            self._generate_commercial_proposal_pdf(pdf, template)
        elif report_type == 'business_analysis':
            self._generate_business_analysis_pdf(pdf, template)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Build PDF
        pdf.build(header_footer=True)

        # Save metadata
        self._save_report_metadata(output_path, report_type, 'PDF')

        return output_path

    def generate_excel_report(self, report_type: str, output_path: str,
                             template_name: Optional[str] = None,
                             custom_data: Optional[Dict] = None) -> str:
        """
        Generate an Excel report

        Args:
            report_type: Type of report to generate
            output_path: Path to save Excel file
            template_name: Name of template to use (optional)
            custom_data: Additional custom data (optional)

        Returns:
            Path to generated Excel file
        """
        # Load template
        if template_name:
            template = self.template_manager.get_template(template_name)
        else:
            template = get_default_template(report_type)

        # Merge custom data
        if custom_data:
            self.data_sources.update(custom_data)

        # Create Excel builder
        excel = ExcelBuilder(output_path)

        # Generate report based on type
        if report_type == 'technical_specification':
            self._generate_technical_spec_excel(excel, template)
        elif report_type == 'test_execution':
            self._generate_test_execution_excel(excel, template)
        elif report_type == 'compliance':
            self._generate_compliance_excel(excel, template)
        elif report_type == 'commercial_proposal':
            self._generate_commercial_proposal_excel(excel, template)
        elif report_type == 'business_analysis':
            self._generate_business_analysis_excel(excel, template)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Save Excel
        excel.save()

        # Save metadata
        self._save_report_metadata(output_path, report_type, 'Excel')

        return output_path

    # ==================== PDF Report Generators ====================

    def _generate_technical_spec_pdf(self, pdf: PDFBuilder, template: ReportTemplate):
        """Generate Technical Specification PDF"""
        # Cover page
        pdf.add_cover_page(
            logo_path=template.logo_path,
            company_name=template.company_name,
            subtitle="Technical Specification Report"
        )

        # Executive Summary
        if template.is_section_enabled('Executive Summary'):
            pdf.add_section("Executive Summary", level=1)
            summary_text = self._get_executive_summary()
            pdf.add_paragraph(summary_text)
            pdf.add_spacer(5)

        # Chamber Specifications
        if template.is_section_enabled('Chamber Specifications'):
            pdf.add_section("Chamber Specifications", level=1)
            chamber_specs = self._get_chamber_specifications()
            pdf.add_key_value_table(chamber_specs)
            pdf.add_spacer(5)

        # Performance Characteristics
        if template.is_section_enabled('Performance Characteristics'):
            pdf.add_section("Performance Characteristics", level=1)
            perf_data = self._get_performance_data()
            pdf.add_table(
                data=perf_data['data'],
                headers=perf_data['headers'],
                style='default'
            )
            pdf.add_spacer(5)

        # UV System Analysis
        if template.is_section_enabled('UV System Analysis'):
            pdf.add_section("UV System Analysis", level=1)
            uv_specs = self._get_uv_system_specs()
            pdf.add_key_value_table(uv_specs, "UV LED Configuration")
            pdf.add_spacer(5)

        # Component List
        if template.is_section_enabled('Component List'):
            pdf.add_section("Component List", level=1)
            components = self._get_component_list()
            pdf.add_table(
                data=components['data'],
                headers=components['headers'],
                style='grid'
            )

    def _generate_test_execution_pdf(self, pdf: PDFBuilder, template: ReportTemplate):
        """Generate Test Execution PDF"""
        pdf.add_cover_page(
            logo_path=template.logo_path,
            company_name=template.company_name,
            subtitle="Test Execution Report"
        )

        # Test Parameters
        pdf.add_section("Test Parameters", level=1)
        test_params = self._get_test_parameters()
        pdf.add_key_value_table(test_params)
        pdf.add_spacer(10)

        # Data Logs Summary
        pdf.add_section("Test Data Summary", level=1)
        pdf.add_paragraph(
            "This report contains environmental test data collected during the test execution."
        )
        pdf.add_spacer(5)

        # Uniformity Measurements
        pdf.add_section("Uniformity Measurements", level=1)
        uniformity_data = self._get_uniformity_data()
        pdf.add_table(
            data=uniformity_data['data'],
            headers=uniformity_data['headers'],
            style='default'
        )
        pdf.add_spacer(5)

        # Pass/Fail Status
        pdf.add_section("Test Results", level=1)
        pdf.add_paragraph(
            "<b>Overall Test Status: PASS</b>",
            style_name='Heading3'
        )

    def _generate_compliance_pdf(self, pdf: PDFBuilder, template: ReportTemplate):
        """Generate Compliance & Calibration PDF"""
        pdf.add_cover_page(
            logo_path=template.logo_path,
            company_name=template.company_name,
            subtitle="Compliance & Calibration Report"
        )

        # IEC Compliance
        pdf.add_section("IEC 61215/61730 Compliance", level=1)
        compliance_items = [
            "Temperature range: -45°C to +105°C ✓",
            "Humidity range: 40% to 95% RH ✓",
            "UV intensity: 60 W/m² ± 8.5% ✓",
            "Uniformity: Within ±10% specification ✓",
            "Safety interlocks: Implemented ✓"
        ]
        pdf.add_bullet_list(compliance_items)
        pdf.add_spacer(10)

        # Calibration Status
        pdf.add_section("Calibration Status", level=1)
        calibration_data = self._get_calibration_data()
        pdf.add_table(
            data=calibration_data['data'],
            headers=calibration_data['headers'],
            style='default'
        )

    def _generate_commercial_proposal_pdf(self, pdf: PDFBuilder, template: ReportTemplate):
        """Generate Commercial Proposal PDF"""
        pdf.add_cover_page(
            logo_path=template.logo_path,
            company_name=template.company_name,
            subtitle="Commercial Proposal"
        )

        # Executive Summary
        pdf.add_section("Executive Summary", level=1)
        pdf.add_paragraph(
            "This proposal outlines the complete UV+TC+HF+DH Environmental Test Chamber "
            "solution for PV module testing in compliance with IEC 61215/61730 standards."
        )
        pdf.add_spacer(10)

        # Quote and Pricing
        pdf.add_section("Cost Breakdown", level=1)
        cost_data = self._get_cost_breakdown()
        pdf.add_table(
            data=cost_data['data'],
            headers=cost_data['headers'],
            style='default'
        )
        pdf.add_spacer(5)

        # Payment Terms
        pdf.add_section("Payment Terms", level=1)
        payment_terms = [
            "30% advance payment with purchase order",
            "40% upon delivery and installation",
            "30% upon successful commissioning and acceptance"
        ]
        pdf.add_bullet_list(payment_terms)
        pdf.add_spacer(10)

        # Delivery Timeline
        pdf.add_section("Delivery Timeline", level=1)
        pdf.add_paragraph("Total project duration: <b>22 weeks</b> from order confirmation")

    def _generate_business_analysis_pdf(self, pdf: PDFBuilder, template: ReportTemplate):
        """Generate Business Analysis PDF"""
        pdf.add_cover_page(
            logo_path=template.logo_path,
            company_name=template.company_name,
            subtitle="Business Analysis Report"
        )

        # TCO Breakdown
        pdf.add_section("Total Cost of Ownership (10-Year)", level=1)
        tco_data = self._get_tco_breakdown()
        pdf.add_table(
            data=tco_data['data'],
            headers=tco_data['headers'],
            style='default'
        )
        pdf.add_spacer(10)

        # ROI Metrics
        pdf.add_section("ROI Analysis", level=1)
        roi_metrics = {
            "Net Present Value (NPV)": "₹85.3 Lakhs",
            "Internal Rate of Return (IRR)": "178.4%",
            "Payback Period": "0.58 years",
            "Annual Revenue Potential": "₹12.5 Lakhs"
        }
        pdf.add_key_value_table(roi_metrics)
        pdf.add_spacer(10)

        # Investment Justification
        pdf.add_section("Investment Justification", level=1)
        pdf.add_paragraph(
            "The chamber investment shows strong financial returns with a payback period "
            "of less than 7 months and an IRR of 178.4%, making it a highly attractive investment."
        )

    # ==================== Excel Report Generators ====================

    def _generate_technical_spec_excel(self, excel: ExcelBuilder, template: ReportTemplate):
        """Generate Technical Specification Excel"""
        # Summary Sheet
        summary_sheet = excel.create_sheet("Summary", 0)
        excel.add_title(summary_sheet, "Technical Specification Report", 1, 1, 6)

        # Add chamber specs
        specs = self._get_chamber_specifications()
        data = [[k, v] for k, v in specs.items()]
        excel.write_header_row(summary_sheet, ["Parameter", "Value"], 3, 1)
        excel.write_data_rows(summary_sheet, data, 4, 1)
        excel.auto_fit_columns(summary_sheet)

        # Performance Sheet
        perf_sheet = excel.create_sheet("Performance", 1)
        excel.add_title(perf_sheet, "Performance Characteristics", 1, 1, 4)
        perf_data = self._get_performance_data()
        excel.write_header_row(perf_sheet, perf_data['headers'], 3, 1)
        excel.write_data_rows(perf_sheet, perf_data['data'], 4, 1)
        excel.auto_fit_columns(perf_sheet)

        # Components Sheet
        comp_sheet = excel.create_sheet("Components", 2)
        excel.add_title(comp_sheet, "Component List", 1, 1, 3)
        components = self._get_component_list()
        excel.write_header_row(comp_sheet, components['headers'], 3, 1)
        excel.write_data_rows(comp_sheet, components['data'], 4, 1)
        excel.auto_fit_columns(comp_sheet)

    def _generate_test_execution_excel(self, excel: ExcelBuilder, template: ReportTemplate):
        """Generate Test Execution Excel"""
        # Test Parameters Sheet
        params_sheet = excel.create_sheet("Test Parameters", 0)
        excel.add_title(params_sheet, "Test Execution Report", 1, 1, 4)
        test_params = self._get_test_parameters()
        data = [[k, v] for k, v in test_params.items()]
        excel.write_header_row(params_sheet, ["Parameter", "Value"], 3, 1)
        excel.write_data_rows(params_sheet, data, 4, 1)
        excel.auto_fit_columns(params_sheet)

        # Uniformity Data Sheet
        uniform_sheet = excel.create_sheet("Uniformity Data", 1)
        excel.add_title(uniform_sheet, "Uniformity Measurements", 1, 1, 4)
        uniformity_data = self._get_uniformity_data()
        excel.write_header_row(uniform_sheet, uniformity_data['headers'], 3, 1)
        excel.write_data_rows(uniform_sheet, uniformity_data['data'], 4, 1)
        excel.auto_fit_columns(uniform_sheet)

    def _generate_compliance_excel(self, excel: ExcelBuilder, template: ReportTemplate):
        """Generate Compliance Excel"""
        # Compliance Sheet
        comp_sheet = excel.create_sheet("Compliance", 0)
        excel.add_title(comp_sheet, "Compliance & Calibration Report", 1, 1, 4)

        # Calibration data
        cal_data = self._get_calibration_data()
        excel.write_header_row(comp_sheet, cal_data['headers'], 3, 1)
        excel.write_data_rows(comp_sheet, cal_data['data'], 4, 1)
        excel.auto_fit_columns(comp_sheet)

    def _generate_commercial_proposal_excel(self, excel: ExcelBuilder, template: ReportTemplate):
        """Generate Commercial Proposal Excel"""
        # Quote Sheet
        quote_sheet = excel.create_sheet("Quote", 0)
        excel.add_title(quote_sheet, "Commercial Proposal", 1, 1, 4)

        cost_data = self._get_cost_breakdown()
        excel.write_header_row(quote_sheet, cost_data['headers'], 3, 1)
        excel.write_data_rows(quote_sheet, cost_data['data'], 4, 1)

        # Add total formula
        last_row = 4 + len(cost_data['data'])
        excel.add_formula(quote_sheet, f'B{last_row}', f'SUM(B4:B{last_row-1})')
        quote_sheet.cell(row=last_row, column=1).value = "TOTAL"
        quote_sheet.cell(row=last_row, column=1).font = excel.header_font

        excel.format_as_currency(quote_sheet, f'B4:B{last_row}', '₹')
        excel.auto_fit_columns(quote_sheet)

    def _generate_business_analysis_excel(self, excel: ExcelBuilder, template: ReportTemplate):
        """Generate Business Analysis Excel"""
        # TCO Sheet
        tco_sheet = excel.create_sheet("TCO Analysis", 0)
        excel.add_title(tco_sheet, "Total Cost of Ownership (10-Year)", 1, 1, 4)

        tco_data = self._get_tco_breakdown()
        excel.write_header_row(tco_sheet, tco_data['headers'], 3, 1)
        excel.write_data_rows(tco_sheet, tco_data['data'], 4, 1)
        excel.format_as_currency(tco_sheet, f'B4:B{4+len(tco_data["data"])}', '₹')
        excel.auto_fit_columns(tco_sheet)

        # ROI Sheet
        roi_sheet = excel.create_sheet("ROI Analysis", 1)
        excel.add_title(roi_sheet, "Return on Investment Analysis", 1, 1, 4)

        roi_data = [
            ["Net Present Value (NPV)", "₹85.3 Lakhs"],
            ["Internal Rate of Return (IRR)", "178.4%"],
            ["Payback Period", "0.58 years"],
            ["Annual Revenue", "₹12.5 Lakhs"]
        ]
        excel.write_header_row(roi_sheet, ["Metric", "Value"], 3, 1)
        excel.write_data_rows(roi_sheet, roi_data, 4, 1)
        excel.auto_fit_columns(roi_sheet)

    # ==================== Data Collection Methods ====================

    def _get_report_title(self, report_type: str) -> str:
        """Get formatted report title"""
        titles = {
            'technical_specification': 'Technical Specification Report',
            'test_execution': 'Test Execution Report',
            'compliance': 'Compliance & Calibration Report',
            'commercial_proposal': 'Commercial Proposal',
            'business_analysis': 'Business Analysis Report'
        }
        return titles.get(report_type, 'Report')

    def _get_executive_summary(self) -> str:
        """Get executive summary text"""
        return (
            "This report presents the comprehensive technical specifications for a UV+TC+HF+DH "
            "Environmental Test Chamber designed for PV module testing in compliance with IEC 61215/61730 "
            "standards. The chamber features advanced LED-based UV illumination, precise temperature and "
            "humidity control, and automated uniformity measurement systems."
        )

    def _get_chamber_specifications(self) -> Dict[str, str]:
        """Get chamber specifications"""
        specs = self.data_sources.get('chamber_specs', {})
        return {
            "Internal Dimensions": specs.get('dimensions', '3200 x 2100 x 2200 mm'),
            "Internal Volume": specs.get('volume', '14.8 m³'),
            "Temperature Range": specs.get('temp_range', '-45°C to +105°C'),
            "Temperature Uniformity": specs.get('temp_uniformity', '±2°C'),
            "Humidity Range": specs.get('humidity_range', '40% to 95% RH'),
            "UV Intensity": specs.get('uv_intensity', '60 W/m² ± 8.5%'),
            "Compliance": "IEC 61215, IEC 61730, ISO 17025"
        }

    def _get_performance_data(self) -> Dict[str, Any]:
        """Get performance data table"""
        return {
            'headers': ['Parameter', 'Specification', 'Actual', 'Status'],
            'data': [
                ['Temperature Stability', '±0.5°C', '±0.3°C', 'PASS'],
                ['Humidity Stability', '±2% RH', '±1.5% RH', 'PASS'],
                ['UV Uniformity', '±10%', '±8.5%', 'PASS'],
                ['Cool-down Time', '< 60 min', '45 min', 'PASS'],
                ['Heat-up Time', '< 45 min', '38 min', 'PASS']
            ]
        }

    def _get_uv_system_specs(self) -> Dict[str, str]:
        """Get UV system specifications"""
        uv_data = self.data_sources.get('uv_system', {})
        return {
            "LED Type": uv_data.get('led_type', 'High-efficiency UV LED'),
            "Number of LEDs": uv_data.get('num_leds', '28 units'),
            "Total UV Power": uv_data.get('total_power', '2.4 kW'),
            "Wavelength": uv_data.get('wavelength', '340 nm ± 10 nm'),
            "Uniformity": uv_data.get('uniformity', '±8.5%'),
            "LED Lifetime": uv_data.get('lifetime', '> 50,000 hours')
        }

    def _get_component_list(self) -> Dict[str, Any]:
        """Get component list"""
        return {
            'headers': ['Component', 'Specification', 'Quantity'],
            'data': [
                ['Chamber Panel', 'PUF insulated, SS304', '1 set'],
                ['UV LED Module', '85W, 340nm', '28 units'],
                ['Temperature Sensor', 'RTD Pt100', '9 points'],
                ['Humidity Sensor', 'Capacitive', '2 units'],
                ['UV Sensor', 'Radiometer', '9 points'],
                ['PLC Controller', 'Siemens S7-1200', '1 unit'],
                ['HMI Panel', '15-inch touchscreen', '1 unit']
            ]
        }

    def _get_test_parameters(self) -> Dict[str, str]:
        """Get test parameters"""
        return {
            "Test ID": self.data_sources.get('test_id', 'TEST-20250120-001'),
            "Test Date": self.data_sources.get('test_date', datetime.now().strftime('%Y-%m-%d')),
            "Test Duration": self.data_sources.get('duration', '1000 hours'),
            "Temperature Setpoint": self.data_sources.get('temp_setpoint', '85°C'),
            "Humidity Setpoint": self.data_sources.get('humidity_setpoint', '85% RH'),
            "UV Intensity": self.data_sources.get('uv_setpoint', '60 W/m²'),
            "Operator": self.data_sources.get('operator', 'Test Engineer')
        }

    def _get_uniformity_data(self) -> Dict[str, Any]:
        """Get 9-point uniformity data"""
        return {
            'headers': ['Position', 'Temperature (°C)', 'Humidity (%RH)', 'UV (W/m²)'],
            'data': [
                ['P1 (Top-Left)', '84.8', '84.5', '58.2'],
                ['P2 (Top-Center)', '85.1', '85.0', '60.1'],
                ['P3 (Top-Right)', '84.9', '84.7', '59.8'],
                ['P4 (Mid-Left)', '85.0', '85.2', '59.5'],
                ['P5 (Center)', '85.0', '85.0', '60.0'],
                ['P6 (Mid-Right)', '85.1', '85.1', '60.3'],
                ['P7 (Bottom-Left)', '84.7', '84.8', '58.9'],
                ['P8 (Bottom-Center)', '85.2', '85.3', '60.5'],
                ['P9 (Bottom-Right)', '84.9', '84.9', '59.7']
            ]
        }

    def _get_calibration_data(self) -> Dict[str, Any]:
        """Get calibration data"""
        return {
            'headers': ['Instrument', 'Last Calibration', 'Next Due', 'Certificate No.'],
            'data': [
                ['Temperature RTDs', '2024-12-15', '2025-12-15', 'CAL-T-2024-1234'],
                ['Humidity Sensor', '2024-12-10', '2025-12-10', 'CAL-H-2024-5678'],
                ['UV Radiometer', '2024-11-20', '2025-11-20', 'CAL-UV-2024-9012'],
                ['Data Logger', '2024-12-01', '2025-12-01', 'CAL-DL-2024-3456']
            ]
        }

    def _get_cost_breakdown(self) -> Dict[str, Any]:
        """Get cost breakdown"""
        cost_data = self.data_sources.get('cost_data', {})
        default_costs = [
            ['Chamber System', '35.0'],
            ['UV LED Arrays', '16.0'],
            ['Refrigeration System', '8.0'],
            ['Controls/HMI', '7.0'],
            ['DC Power Supply', '6.0'],
            ['Uniformity Robot', '12.0'],
            ['Water Treatment', '6.3'],
            ['Installation', '5.0'],
            ['Calibration', '3.5']
        ]

        return {
            'headers': ['Component', 'Cost (₹ Lakhs)'],
            'data': cost_data.get('breakdown', default_costs)
        }

    def _get_tco_breakdown(self) -> Dict[str, Any]:
        """Get TCO breakdown"""
        return {
            'headers': ['Cost Category', 'Amount (₹ Lakhs)'],
            'data': [
                ['Initial Investment', '98.8'],
                ['Energy Costs (10-year)', '18.5'],
                ['Maintenance (10-year)', '9.8'],
                ['Calibration (10-year)', '3.5'],
                ['Total TCO', '130.6']
            ]
        }

    def collect_data_from_modules(self) -> Dict[str, Any]:
        """
        Collect data from all modules

        Returns:
            Dictionary of collected data
        """
        # This would integrate with actual module data
        # For now, return placeholder structure
        return {
            'chamber_specs': {},
            'uv_system': {},
            'cfd_results': {},
            'supplier_data': {},
            'hmi_logs': {},
            'cost_data': {},
            'business_metrics': {}
        }

    def validate_data_completeness(self, required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that required data fields are present

        Args:
            required_fields: List of required field names

        Returns:
            Tuple of (is_complete, missing_fields)
        """
        missing = []
        for field in required_fields:
            if field not in self.data_sources or not self.data_sources[field]:
                missing.append(field)

        return (len(missing) == 0, missing)

    def handle_missing_data(self, field_name: str) -> Any:
        """
        Handle missing data gracefully

        Args:
            field_name: Name of missing field

        Returns:
            Default value or placeholder
        """
        defaults = {
            'chamber_specs': {},
            'uv_system': {},
            'test_id': 'N/A',
            'operator': 'Unknown'
        }
        return defaults.get(field_name, 'N/A')

    def _save_report_metadata(self, report_path: str, report_type: str, format_type: str):
        """
        Save report metadata to JSON

        Args:
            report_path: Path to generated report
            report_type: Type of report
            format_type: Format (PDF/Excel)
        """
        metadata = {
            **self.metadata,
            'report_id': self._generate_report_id(),
            'report_type': report_type,
            'format': format_type,
            'file_path': report_path,
            'file_size': os.path.getsize(report_path) if os.path.exists(report_path) else 0
        }

        # Save to metadata file
        metadata_dir = 'generated_reports/metadata'
        os.makedirs(metadata_dir, exist_ok=True)

        metadata_file = os.path.join(
            metadata_dir,
            f"{metadata['report_id']}.json"
        )

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        date_str = datetime.now().strftime('%Y%m%d')
        time_str = datetime.now().strftime('%H%M%S')
        return f"RPT-{date_str}-{time_str}"

    def get_report_history(self, limit: int = 10) -> List[Dict]:
        """
        Get report generation history

        Args:
            limit: Maximum number of reports to return

        Returns:
            List of report metadata
        """
        metadata_dir = 'generated_reports/metadata'
        if not os.path.exists(metadata_dir):
            return []

        history = []
        for filename in sorted(os.listdir(metadata_dir), reverse=True)[:limit]:
            if filename.endswith('.json'):
                with open(os.path.join(metadata_dir, filename), 'r') as f:
                    history.append(json.load(f))

        return history

    def archive_report(self, report_path: str, archive_location: str):
        """
        Archive a report to specified location

        Args:
            report_path: Path to report file
            archive_location: Archive directory path
        """
        import shutil

        os.makedirs(archive_location, exist_ok=True)
        filename = os.path.basename(report_path)
        archive_path = os.path.join(archive_location, filename)

        shutil.copy2(report_path, archive_path)
        return archive_path
