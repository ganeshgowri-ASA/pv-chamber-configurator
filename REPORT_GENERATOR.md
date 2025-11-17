# Report Generator Documentation

## Overview

The PV Chamber Configurator Report Generator is a comprehensive system for creating professional PDF and Excel reports that aggregate data from all modules. It supports multiple report types with customizable templates and branding.

## Features

- **Multiple Report Types**: Technical Specification, Test Execution, Compliance, Commercial Proposal, Business Analysis
- **Dual Formats**: Generate reports in PDF and/or Excel formats
- **Template System**: Customizable templates with white-label branding
- **Data Aggregation**: Automatically collects data from all system modules
- **Professional Formatting**: Corporate-style layouts with headers, footers, and branding
- **Metadata Tracking**: Automatic report metadata and history logging

## Installation

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Required packages:
- `reportlab>=4.0.0` - PDF generation
- `openpyxl>=3.1.0` - Excel generation
- `Pillow>=10.0.0` - Image processing
- `pandas>=2.1.0` - Data manipulation
- `streamlit>=1.28.0` - Web interface

### Directory Structure

```
pv-chamber-configurator/
├── modules/
│   ├── __init__.py
│   ├── pdf_builder.py           # PDF utilities
│   ├── excel_builder.py         # Excel utilities
│   ├── report_templates.py      # Template management
│   └── report_generator.py      # Main report engine
├── templates/
│   └── report_templates/
│       ├── technical_spec_template.json
│       ├── test_execution_template.json
│       ├── compliance_template.json
│       ├── commercial_proposal_template.json
│       └── business_analysis_template.json
├── assets/
│   ├── logo.png
│   ├── watermark.png
│   └── signature_placeholder.png
├── generated_reports/
│   └── metadata/
└── tests/
    └── test_report_generator.py
```

## Quick Start

### Using the Streamlit Interface

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Navigate to the Reports tab**

3. **Configure your report**:
   - Select report type
   - Choose output format (PDF/Excel/Both)
   - Enter report details
   - Click "Generate Report"

4. **Download the generated report**

### Using the Python API

```python
from modules.report_generator import ReportGenerator

# Configure branding
white_label_config = {
    'company_name': 'Your Company',
    'company_address': 'Your Address',
    'company_email': 'info@company.com',
    'user_name': 'Your Name'
}

# Prepare data sources
data_sources = {
    'chamber_specs': {
        'dimensions': '3200 x 2100 x 2200 mm',
        'volume': '14.8 m³',
        'temp_range': '-45°C to +105°C'
    }
}

# Create generator
generator = ReportGenerator(white_label_config, data_sources)

# Generate PDF
generator.generate_pdf_report(
    'technical_specification',
    'output/tech_spec.pdf'
)

# Generate Excel
generator.generate_excel_report(
    'technical_specification',
    'output/tech_spec.xlsx'
)
```

## Report Types

### 1. Technical Specification Report

**Purpose**: Comprehensive technical documentation of chamber design and specifications

**Sections**:
- Executive Summary
- Chamber Specifications
- Performance Characteristics
- CFD Simulation Results
- UV System Analysis
- Component List
- Appendices

**Usage**:
```python
generator.generate_pdf_report('technical_specification', 'output.pdf')
```

### 2. Test Execution Report

**Purpose**: Document test runs, data logs, and validation results

**Sections**:
- Test Parameters
- Data Logs Summary
- Uniformity Measurements (9-point grid)
- Alarm History
- Operator Notes
- Pass/Fail Status

**Usage**:
```python
generator.generate_pdf_report('test_execution', 'test_report.pdf')
```

### 3. Compliance & Calibration Report

**Purpose**: IEC compliance documentation and calibration certificates

**Sections**:
- IEC 61215/61730 Compliance Checklist
- ISO 17025 Calibration Certificates
- Uncertainty Budgets
- Traceability Chain
- Next Calibration Due Dates

**Usage**:
```python
generator.generate_pdf_report('compliance', 'compliance.pdf')
```

### 4. Commercial Proposal Report

**Purpose**: Sales proposals with technical specs and pricing

**Sections**:
- Executive Summary
- Technical Specifications
- Quote and Pricing Breakdown
- ROI Analysis
- Payment Terms
- Delivery Timeline

**Usage**:
```python
generator.generate_pdf_report('commercial_proposal', 'proposal.pdf')
```

### 5. Business Analysis Report

**Purpose**: Financial analysis, TCO, and ROI calculations

**Sections**:
- TCO Breakdown (10-year)
- ROI Metrics (NPV, IRR, Payback Period)
- Competitive Comparison
- Sensitivity Analysis
- Investment Justification

**Usage**:
```python
generator.generate_pdf_report('business_analysis', 'business.pdf')
```

## Template Customization

### Creating a Custom Template

Templates are defined in JSON format. Example:

```json
{
  "name": "Custom Technical Template",
  "report_type": "technical_specification",
  "version": "1.0",
  "branding": {
    "company_name": "Your Company",
    "logo_path": "assets/custom_logo.png",
    "primary_color": "#2c5aa0",
    "secondary_color": "#1f4788"
  },
  "layout": {
    "page_size": "A4",
    "orientation": "portrait",
    "margins": {
      "top": 20,
      "bottom": 20,
      "left": 15,
      "right": 15
    }
  },
  "typography": {
    "font_family": "Helvetica",
    "font_sizes": {
      "title": 24,
      "header": 16,
      "subheader": 14,
      "body": 11
    }
  },
  "sections": [
    {
      "name": "Executive Summary",
      "enabled": true,
      "order": 1
    }
  ]
}
```

### Loading Custom Templates

```python
from modules.report_templates import TemplateManager

template_manager = TemplateManager('templates/report_templates')
template = template_manager.get_template('Custom Technical Template')

generator.generate_pdf_report(
    'technical_specification',
    'output.pdf',
    template_name='Custom Technical Template'
)
```

### Enabling/Disabling Sections

Modify the `sections` array in the template JSON:

```json
{
  "name": "CFD Simulation Results",
  "enabled": false,  // Disable this section
  "order": 4
}
```

## Data Mapping

### Chamber Specifications

```python
data_sources = {
    'chamber_specs': {
        'dimensions': '3200 x 2100 x 2200 mm',
        'volume': '14.8 m³',
        'temp_range': '-45°C to +105°C',
        'temp_uniformity': '±2°C',
        'humidity_range': '40% to 95% RH',
        'uv_intensity': '60 W/m²'
    }
}
```

### UV System Data

```python
data_sources = {
    'uv_system': {
        'led_type': 'High-efficiency UV LED',
        'num_leds': '28 units',
        'total_power': '2.4 kW',
        'wavelength': '340 nm ± 10 nm',
        'uniformity': '±8.5%',
        'lifetime': '> 50,000 hours'
    }
}
```

### Test Parameters

```python
data_sources = {
    'test_id': 'TEST-20250120-001',
    'test_date': '2025-01-20',
    'duration': '1000 hours',
    'temp_setpoint': '85°C',
    'humidity_setpoint': '85% RH',
    'uv_setpoint': '60 W/m²',
    'operator': 'Test Engineer'
}
```

### Cost Data

```python
data_sources = {
    'cost_data': {
        'breakdown': [
            ['Chamber System', '35.0'],
            ['UV LED Arrays', '16.0'],
            ['Refrigeration System', '8.0']
        ]
    }
}
```

## PDF Customization

### Custom PDF Layout

```python
from modules.pdf_builder import PDFBuilder

pdf = PDFBuilder(
    'custom_report.pdf',
    page_size='A4',
    title='Custom Report',
    author='Your Name'
)

# Add cover page
pdf.add_cover_page(
    logo_path='assets/logo.png',
    company_name='Your Company',
    subtitle='Custom Subtitle'
)

# Add sections
pdf.add_section('Introduction', level=1)
pdf.add_paragraph('This is the introduction text.')

# Add table
data = [['A', 'B'], ['C', 'D']]
pdf.add_table(data, headers=['Col1', 'Col2'])

# Add image
pdf.add_image('path/to/image.png', caption='Figure 1')

# Build PDF
pdf.build()
```

### PDF Features

- **Cover Pages**: With logo and branding
- **Headers/Footers**: Automatic page numbering
- **Tables**: Multiple styles (default, grid, minimal)
- **Images**: With captions and auto-sizing
- **Bullet Lists**: For itemized content
- **Key-Value Tables**: For specifications
- **Page Breaks**: Manual control
- **Watermarks**: Draft/Confidential overlays

## Excel Customization

### Custom Excel Workbook

```python
from modules.excel_builder import ExcelBuilder

excel = ExcelBuilder('custom_report.xlsx')

# Create sheet
sheet = excel.create_sheet('Data', 0)

# Add title
excel.add_title(sheet, 'Report Title', row=1, span=5)

# Add data
headers = ['Parameter', 'Value', 'Status']
data = [
    ['Temperature', '85°C', 'PASS'],
    ['Humidity', '85%', 'PASS']
]

excel.write_header_row(sheet, headers, row=3)
excel.write_data_rows(sheet, data, start_row=4)

# Format
excel.auto_fit_columns(sheet)
excel.freeze_panes(sheet, row=4, col=1)

# Add chart
excel.add_bar_chart(
    sheet,
    data_range='B4:B5',
    categories_range='A4:A5',
    chart_position='E3',
    title='Values'
)

# Save
excel.save()
```

### Excel Features

- **Multi-Sheet Workbooks**: Organize data across sheets
- **Formatting**: Headers, colors, borders, fonts
- **Charts**: Bar, Line, Pie, Scatter
- **Formulas**: Excel formulas in cells
- **Conditional Formatting**: Color scales, data bars, pass/fail
- **Data Validation**: Dropdowns for inputs
- **Auto-Fit Columns**: Automatic width adjustment
- **Freeze Panes**: Lock headers while scrolling
- **Sheet Protection**: Lock cells with password

## Testing

### Run All Tests

```bash
python tests/test_report_generator.py
```

### Test Individual Components

```python
# Test PDF generation
python -m unittest tests.test_report_generator.TestPDFBuilder

# Test Excel generation
python -m unittest tests.test_report_generator.TestExcelBuilder

# Test report generator
python -m unittest tests.test_report_generator.TestReportGenerator
```

### Test Coverage

The test suite includes:
- PDF creation and formatting
- Excel creation and formatting
- Template loading and validation
- All 5 report types (PDF and Excel)
- Data collection methods
- Error handling
- Missing data scenarios

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error

**Problem**: `ModuleNotFoundError: No module named 'PIL'`

**Solution**: Install dependencies
```bash
pip install Pillow reportlab openpyxl
```

#### 2. Font Not Found

**Problem**: PDF fonts not rendering correctly

**Solution**: Use default fonts or specify system fonts
```python
pdf = PDFBuilder('output.pdf')
# Uses Helvetica by default (always available)
```

#### 3. Image Not Loading

**Problem**: Images not appearing in reports

**Solution**: Check file paths are absolute or relative to working directory
```python
import os
logo_path = os.path.abspath('assets/logo.png')
```

#### 4. Excel File Corrupted

**Problem**: "Excel cannot open the file"

**Solution**: Ensure `excel.save()` is called before opening
```python
excel = ExcelBuilder('report.xlsx')
# ... add content ...
excel.save()  # Don't forget this!
```

#### 5. Missing Data in Reports

**Problem**: Empty sections in generated reports

**Solution**: Ensure data_sources contains required fields
```python
# Check required data
generator = ReportGenerator(config, data_sources)
is_valid, missing = generator.validate_data_completeness(['chamber_specs'])
print(f"Missing: {missing}")
```

### Debugging Tips

1. **Enable verbose logging**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check generated files**:
   - PDFs: Open in Adobe Reader or Preview
   - Excel: Open in Microsoft Excel or LibreOffice Calc

3. **Validate templates**:
   ```python
   from modules.report_templates import TemplateManager

   manager = TemplateManager()
   is_valid, errors = manager.validate_template(template_config)
   print(errors)
   ```

## API Reference

### ReportGenerator

```python
class ReportGenerator:
    def __init__(self, white_label_config, data_sources=None, templates_dir='templates/report_templates')

    def generate_pdf_report(self, report_type, output_path, template_name=None, custom_data=None) -> str
    def generate_excel_report(self, report_type, output_path, template_name=None, custom_data=None) -> str

    def validate_data_completeness(self, required_fields) -> Tuple[bool, List[str]]
    def handle_missing_data(self, field_name) -> Any
    def get_report_history(self, limit=10) -> List[Dict]
    def archive_report(self, report_path, archive_location) -> str
```

### PDFBuilder

```python
class PDFBuilder:
    def __init__(self, output_path, page_size='A4', title='', author='')

    def add_cover_page(self, logo_path=None, company_name='', subtitle='')
    def add_section(self, title, content='', level=1)
    def add_paragraph(self, text, style_name='CustomBody')
    def add_table(self, data, headers=None, col_widths=None, style='default')
    def add_image(self, image_path, caption='', width=150, height=None)
    def add_key_value_table(self, data, title='')
    def add_bullet_list(self, items)
    def build(self, header_footer=True)
```

### ExcelBuilder

```python
class ExcelBuilder:
    def __init__(self, output_path)

    def create_sheet(self, sheet_name, index=None) -> Worksheet
    def write_header_row(self, sheet, headers, row=1, start_col=1)
    def write_data_rows(self, sheet, data, start_row=2, start_col=1, alternating_colors=True)
    def auto_fit_columns(self, sheet, min_width=10, max_width=50)
    def add_bar_chart(self, sheet, data_range, categories_range, chart_position, title='')
    def add_conditional_formatting(self, sheet, cell_range, condition_type, value=None)
    def save() -> str
```

## Best Practices

1. **Always validate data before generation**:
   ```python
   is_valid, missing = generator.validate_data_completeness(['chamber_specs'])
   if not is_valid:
       print(f"Missing required data: {missing}")
   ```

2. **Use templates for consistency**:
   - Create organizational templates
   - Store in `templates/report_templates/`
   - Version control your templates

3. **Handle errors gracefully**:
   ```python
   try:
       generator.generate_pdf_report('technical_specification', 'output.pdf')
   except Exception as e:
       print(f"Error: {e}")
       # Fallback or retry logic
   ```

4. **Archive important reports**:
   ```python
   generator.archive_report('report.pdf', 'archive/2025/')
   ```

5. **Test report generation in development**:
   - Run test suite before deploying
   - Validate output files manually
   - Check all report types

## Support

For issues, questions, or contributions:
- GitHub: ganeshgowri-ASA/pv-chamber-configurator
- Email: info@zenitek.com
- Documentation: See this file

## License

MIT License - See LICENSE file for details

## Version History

- **v1.0.0** (2025-01-20): Initial release
  - 5 report types
  - PDF and Excel generation
  - Template system
  - Comprehensive testing
  - Full documentation
