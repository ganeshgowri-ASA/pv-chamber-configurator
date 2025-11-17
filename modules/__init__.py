"""
PV Chamber Configurator - Modules Package

Comprehensive calculation and simulation modules for UV+TC+HF+DH chamber design
including UV optical system design, CFD analysis, chamber performance evaluation,
supplier database management, and virtual HMI controls.
"""

__version__ = "1.0.0"

from .supplier_database import SupplierDatabaseManager
from .quote_parser import (
    parse_pdf_quote,
    parse_excel_quote,
    parse_csv_quote,
    auto_detect_and_parse,
    parse_indian_currency,
    extract_component_prices
)

__all__ = [
    'SupplierDatabaseManager',
    'parse_pdf_quote',
    'parse_excel_quote',
    'parse_csv_quote',
    'auto_detect_and_parse',
    'parse_indian_currency',
    'extract_component_prices'
]
