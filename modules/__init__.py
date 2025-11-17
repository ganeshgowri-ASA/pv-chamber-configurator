"""
PV Chamber Configurator Modules
Comprehensive report generation and data processing modules
"""

from .pdf_builder import PDFBuilder, create_pdf_canvas, add_watermark
from .excel_builder import ExcelBuilder, create_workbook
from .report_templates import (
    ReportTemplate, TemplateManager, load_template, get_default_template
)
from .report_generator import ReportGenerator

__all__ = [
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

__version__ = '1.0.0'
