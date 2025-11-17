"""
PV Chamber Configurator - Modules Package

Comprehensive modules for UV optical system design, CFD simulation, supplier database,
virtual HMI, robot control, quote generation, email system, payment calculation,
business analysis, financial modeling, comprehensive report generation,
integration layer, white-labeling, and internationalization.
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
from .integration_layer import IntegrationLayer
from .white_label_manager import WhiteLabelManager
from .i18n_manager import I18nManager
from .config_manager import ConfigManager

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
    'get_default_template',
    'IntegrationLayer',
    'WhiteLabelManager',
    'I18nManager',
    'ConfigManager'
]

__version__ = "9.0.0"
