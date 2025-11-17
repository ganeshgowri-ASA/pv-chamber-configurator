"""
PV Chamber Configurator - Modules Package

Comprehensive modules for UV optical system design, CFD simulation, supplier database,
virtual HMI, robot control, quote generation, email system, payment calculation, and analysis.
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

__all__ = [
    'SupplierDatabaseManager',
    'parse_pdf_quote',
    'parse_excel_quote',
    'parse_csv_quote',
    'auto_detect_and_parse',
    'parse_indian_currency',
    'extract_component_prices'
]

__version__ = "6.0.0"
