"""
PV Chamber Configurator - Modules Package

Comprehensive modules for UV optical system design, CFD simulation, supplier database,
virtual HMI, robot control, quote generation, email system, payment calculation,
business analysis, financial modeling, and comprehensive report generation.
"""

from .supplier_database import SupplierDatabaseManager
from .quote_parser import (
    parse_pdf_quote,
    parse_excel_quote,
    parse_csv_quote,
    auto_detect_and_parse,
    parse_indian_currency,
    extract_component_prices
)
from .pdf_builder import PDFBuilder, create_pdf_canvas, add_watermark
from .excel_builder import ExcelBuilder, create_workbook
from .report_templates import (
    ReportTemplate, TemplateManager, load_template, get_default_template
)
from .report_generator import ReportGenerator

__all__ = [
    'SupplierDatabaseManager',
    'parse_pdf_quote',
    'parse_excel_quote',
    'parse_csv_quote',
    'auto_detect_and_parse',
    'parse_indian_currency',
    'extract_component_prices',
    'PDFBuilder',
    'ExcelBuilder',
    'ReportTemplate',
    'TemplateManager',
    'ReportGenerator',
    'create_pdf_canvas',
    'add_watermark',
    'create_workbook',
    'load_template',
    'get_default_template'
]

__version__ = "8.0.0"
