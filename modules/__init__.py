"""
PV Chamber Configurator - Modules Package

Comprehensive modules for UV optical system design, CFD simulation, supplier database,
virtual HMI, robot control, quote generation, email system, payment calculation,
business analysis, financial modeling, comprehensive report generation,
integration layer, white-labeling, internationalization,
IEC/ISO compliance validation, and ISO/IEC 17025 calibration management.
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
from .iec_compliance import IECComplianceChecker, ChamberSpecifications, ComplianceResult
from .iso17025_calibration import (
    ISO17025Calibration,
    LabAccreditation,
    AccreditationBody,
    InstrumentData,
    InstrumentType,
    CalibrationCertificate
)
from .uncertainty_calculator import UncertaintyCalculator, UncertaintyBudget, UncertaintySource
from .compliance_checklist import ComplianceChecklist, ChecklistItem, ChecklistStatus

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
    'ConfigManager',
    'IECComplianceChecker',
    'ChamberSpecifications',
    'ComplianceResult',
    'ISO17025Calibration',
    'LabAccreditation',
    'AccreditationBody',
    'InstrumentData',
    'InstrumentType',
    'CalibrationCertificate',
    'UncertaintyCalculator',
    'UncertaintyBudget',
    'UncertaintySource',
    'ComplianceChecklist',
    'ChecklistItem',
    'ChecklistStatus'
]

__version__ = "10.0.0"
