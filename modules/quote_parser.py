"""
Quote Parser Module for PV Chamber Configurator
Handles parsing of quotes from PDF, Excel, and CSV formats.
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Tuple
import io


def parse_indian_currency(text: str) -> Optional[float]:
    """
    Parse Indian currency formats (₹, Rs., INR, lakhs, crores).

    Args:
        text: Text containing currency value

    Returns:
        Float value or None if parsing fails
    """
    if not text or not isinstance(text, str):
        return None

    # Remove common currency symbols and prefixes
    text = text.replace('₹', '').replace('Rs.', '').replace('Rs', '')
    text = text.replace('INR', '').replace('USD', '').replace('$', '')
    text = text.strip()

    # Handle lakhs and crores
    lakh_match = re.search(r'([\d,\.]+)\s*(?:L|lakh|lakhs)', text, re.IGNORECASE)
    if lakh_match:
        value = lakh_match.group(1).replace(',', '')
        try:
            return float(value) * 100000
        except ValueError:
            pass

    crore_match = re.search(r'([\d,\.]+)\s*(?:Cr|crore|crores)', text, re.IGNORECASE)
    if crore_match:
        value = crore_match.group(1).replace(',', '')
        try:
            return float(value) * 10000000
        except ValueError:
            pass

    # Standard numeric parsing
    # Remove commas and parse as float
    numeric_match = re.search(r'[\d,]+\.?\d*', text)
    if numeric_match:
        value = numeric_match.group(0).replace(',', '')
        try:
            return float(value)
        except ValueError:
            pass

    return None


def extract_component_prices(text: str) -> List[Dict]:
    """
    Extract component names and prices from text.

    Args:
        text: Text to parse

    Returns:
        List of dictionaries with 'description', 'quantity', 'unit_price', 'total_price'
    """
    components = []

    # Common patterns for line items in quotes
    # Pattern: Description ... Qty ... Unit Price ... Total
    patterns = [
        # Pattern 1: "Item description    10    Rs. 5000    Rs. 50000"
        r'([A-Za-z][\w\s\-\/\.]+?)\s+(\d+)\s+(?:Rs\.?|₹|INR)?\s*([\d,\.]+)\s+(?:Rs\.?|₹|INR)?\s*([\d,\.]+)',
        # Pattern 2: "Description | Qty | Rate | Amount"
        r'([A-Za-z][\w\s\-\/\.]+?)\s*[|\t]\s*(\d+)\s*[|\t]\s*(?:Rs\.?|₹|INR)?\s*([\d,\.]+)\s*[|\t]\s*(?:Rs\.?|₹|INR)?\s*([\d,\.]+)',
        # Pattern 3: Simple "Description - Qty x Rate = Total"
        r'([A-Za-z][\w\s\-\/\.]+?)\s*-?\s*(\d+)\s*x\s*(?:Rs\.?|₹|INR)?\s*([\d,\.]+)\s*=\s*(?:Rs\.?|₹|INR)?\s*([\d,\.]+)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.MULTILINE)
        for match in matches:
            description = match.group(1).strip()
            # Filter out header rows
            if any(keyword in description.lower() for keyword in
                   ['description', 'item', 'particular', 'sr.', 's.no', 'total', 'subtotal']):
                continue

            try:
                quantity = int(match.group(2))
                unit_price = parse_indian_currency(match.group(3))
                total_price = parse_indian_currency(match.group(4))

                if unit_price and total_price:
                    components.append({
                        'description': description,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': total_price
                    })
            except (ValueError, IndexError):
                continue

    return components


def extract_lead_times(text: str) -> Optional[int]:
    """
    Extract lead time in days from text.

    Args:
        text: Text to parse

    Returns:
        Lead time in days or None
    """
    # Patterns for lead time
    patterns = [
        r'(?:lead\s*time|delivery|dispatch)[\s:]*(\d+)\s*(?:days?|working\s*days?)',
        r'(?:within|in)[\s:]*(\d+)\s*(?:days?|working\s*days?)',
        r'(\d+)\s*(?:days?|working\s*days?)\s*(?:lead\s*time|delivery)',
        r'(\d+)\s*weeks?',  # Convert weeks to days
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            days = int(match.group(1))
            # If pattern matched weeks, convert to days
            if 'week' in pattern:
                days *= 7
            return days

    return None


def extract_warranty_terms(text: str) -> Optional[int]:
    """
    Extract warranty period in months from text.

    Args:
        text: Text to parse

    Returns:
        Warranty period in months or None
    """
    # Patterns for warranty
    patterns = [
        r'(?:warranty|guarantee)[\s:]*(\d+)\s*(?:months?|mnths?)',
        r'(?:warranty|guarantee)[\s:]*(\d+)\s*years?',
        r'(\d+)\s*(?:months?|mnths?)\s*(?:warranty|guarantee)',
        r'(\d+)\s*years?\s*(?:warranty|guarantee)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            # If pattern matched years, convert to months
            if 'year' in pattern:
                value *= 12
            return value

    return None


def extract_quote_metadata(text: str) -> Dict:
    """
    Extract quote metadata (quote number, date, validity, etc.).

    Args:
        text: Text to parse

    Returns:
        Dictionary with metadata
    """
    metadata = {}

    # Quote number
    quote_patterns = [
        r'(?:quote|quotation)\s*(?:no\.?|number|#)[\s:]*([A-Z0-9\-/]+)',
        r'ref(?:erence)?[\s:]*([A-Z0-9\-/]+)',
    ]
    for pattern in quote_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['quote_number'] = match.group(1)
            break

    # Date
    date_patterns = [
        r'(?:date|dated)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['quote_date'] = match.group(1)
            break

    # Validity
    validity_patterns = [
        r'valid(?:ity)?[\s:]*(\d+)\s*days?',
        r'valid\s*(?:for|till|until)[\s:]*(\d+)\s*days?',
    ]
    for pattern in validity_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['validity_days'] = int(match.group(1))
            break

    # Total amount
    total_patterns = [
        r'(?:grand\s*)?total[\s:]*(?:Rs\.?|₹|INR)?\s*([\d,\.]+)',
        r'net\s*amount[\s:]*(?:Rs\.?|₹|INR)?\s*([\d,\.]+)',
    ]
    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['total_cost'] = parse_indian_currency(match.group(1))
            break

    # GST/Tax
    tax_patterns = [
        r'(?:GST|tax|CGST|SGST|IGST)[\s:]*(?:@\s*)?(\d+)%',
        r'(?:GST|tax)[\s:]*(?:Rs\.?|₹|INR)?\s*([\d,\.]+)',
    ]
    for pattern in tax_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            # Check if it's a percentage or amount
            if '%' in pattern or match.group(0).count('%') > 0:
                metadata['tax_rate'] = float(value) / 100
            else:
                metadata['tax_amount'] = parse_indian_currency(value)
            break

    # Payment terms
    payment_patterns = [
        r'(?:payment|terms)[\s:]*([^\n\.]+(?:advance|delivery|net\s*\d+)[^\n\.]*)',
    ]
    for pattern in payment_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata['payment_terms'] = match.group(1).strip()
            break

    return metadata


# ==================== Format-Specific Parsers ====================


def parse_pdf_quote(pdf_path: str) -> Dict:
    """
    Parse quote from PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with parsed quote data
    """
    try:
        import pdfplumber
    except ImportError:
        # Fallback to PyPDF2 if pdfplumber not available
        try:
            import PyPDF2
            return _parse_pdf_with_pypdf2(pdf_path)
        except ImportError:
            raise ImportError("Neither pdfplumber nor PyPDF2 is installed")

    result = {
        'success': False,
        'metadata': {},
        'items': [],
        'raw_text': ''
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ''
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + '\n'

            result['raw_text'] = full_text

            # Extract metadata
            result['metadata'] = extract_quote_metadata(full_text)

            # Extract line items
            result['items'] = extract_component_prices(full_text)

            # Extract lead time and warranty
            lead_time = extract_lead_times(full_text)
            if lead_time:
                result['metadata']['lead_time_days'] = lead_time

            warranty = extract_warranty_terms(full_text)
            if warranty:
                result['metadata']['warranty_months'] = warranty

            result['success'] = True

    except Exception as e:
        result['error'] = str(e)

    return result


def _parse_pdf_with_pypdf2(pdf_path: str) -> Dict:
    """Fallback PDF parser using PyPDF2."""
    import PyPDF2

    result = {
        'success': False,
        'metadata': {},
        'items': [],
        'raw_text': ''
    }

    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ''
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + '\n'

            result['raw_text'] = full_text
            result['metadata'] = extract_quote_metadata(full_text)
            result['items'] = extract_component_prices(full_text)

            lead_time = extract_lead_times(full_text)
            if lead_time:
                result['metadata']['lead_time_days'] = lead_time

            warranty = extract_warranty_terms(full_text)
            if warranty:
                result['metadata']['warranty_months'] = warranty

            result['success'] = True

    except Exception as e:
        result['error'] = str(e)

    return result


def parse_excel_quote(excel_path: str, sheet_name: Optional[str] = None) -> Dict:
    """
    Parse quote from Excel file.

    Args:
        excel_path: Path to Excel file
        sheet_name: Specific sheet to parse (None for first sheet)

    Returns:
        Dictionary with parsed quote data
    """
    result = {
        'success': False,
        'metadata': {},
        'items': [],
        'raw_text': ''
    }

    try:
        # Read Excel file
        if sheet_name:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(excel_path)

        # Try to identify columns
        columns = {col.lower().strip(): col for col in df.columns}

        # Find description column
        desc_col = None
        for key in ['description', 'item', 'particular', 'product', 'component']:
            if key in columns:
                desc_col = columns[key]
                break

        # Find quantity column
        qty_col = None
        for key in ['quantity', 'qty', 'no', 'nos', 'units']:
            if key in columns:
                qty_col = columns[key]
                break

        # Find unit price column
        unit_price_col = None
        for key in ['unit price', 'rate', 'price', 'unit_price', 'unit rate']:
            if key in columns:
                unit_price_col = columns[key]
                break

        # Find total price column
        total_col = None
        for key in ['total', 'amount', 'total price', 'total_price', 'value']:
            if key in columns:
                total_col = columns[key]
                break

        # Extract items
        if desc_col:
            for idx, row in df.iterrows():
                desc = row.get(desc_col)
                if pd.isna(desc) or not str(desc).strip():
                    continue

                # Skip header-like rows
                if any(keyword in str(desc).lower() for keyword in
                       ['total', 'subtotal', 'grand total', 'description']):
                    continue

                item = {
                    'description': str(desc).strip()
                }

                if qty_col and not pd.isna(row.get(qty_col)):
                    try:
                        item['quantity'] = int(float(row[qty_col]))
                    except (ValueError, TypeError):
                        item['quantity'] = 1
                else:
                    item['quantity'] = 1

                if unit_price_col and not pd.isna(row.get(unit_price_col)):
                    try:
                        unit_price = float(row[unit_price_col])
                        item['unit_price'] = unit_price
                    except (ValueError, TypeError):
                        pass

                if total_col and not pd.isna(row.get(total_col)):
                    try:
                        total_price = float(row[total_col])
                        item['total_price'] = total_price
                    except (ValueError, TypeError):
                        pass

                # Calculate missing values
                if 'unit_price' in item and 'total_price' not in item:
                    item['total_price'] = item['unit_price'] * item['quantity']
                elif 'total_price' in item and 'unit_price' not in item:
                    item['unit_price'] = item['total_price'] / item['quantity'] if item['quantity'] > 0 else 0

                if 'unit_price' in item and 'total_price' in item:
                    result['items'].append(item)

        # Try to extract metadata from Excel
        # Look for cells with keywords
        for col in df.columns:
            for idx, value in df[col].items():
                if pd.isna(value):
                    continue
                value_str = str(value).lower()

                if 'quote' in value_str or 'quotation' in value_str:
                    # Next cell might be the quote number
                    if idx + 1 < len(df):
                        next_val = df[col].iloc[idx + 1]
                        if not pd.isna(next_val):
                            result['metadata']['quote_number'] = str(next_val)

                if 'date' in value_str:
                    if idx + 1 < len(df):
                        next_val = df[col].iloc[idx + 1]
                        if not pd.isna(next_val):
                            result['metadata']['quote_date'] = str(next_val)

        # Calculate total if items found
        if result['items']:
            result['metadata']['total_cost'] = sum(item['total_price'] for item in result['items'])

        result['success'] = len(result['items']) > 0

    except Exception as e:
        result['error'] = str(e)

    return result


def parse_csv_quote(csv_path: str) -> Dict:
    """
    Parse quote from CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        Dictionary with parsed quote data
    """
    result = {
        'success': False,
        'metadata': {},
        'items': [],
        'raw_text': ''
    }

    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None

        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue

        if df is None:
            raise ValueError("Could not read CSV file with any standard encoding")

        # Use the same column mapping logic as Excel parser
        columns = {col.lower().strip(): col for col in df.columns}

        desc_col = None
        for key in ['description', 'item', 'particular', 'product', 'component']:
            if key in columns:
                desc_col = columns[key]
                break

        qty_col = None
        for key in ['quantity', 'qty', 'no', 'nos', 'units']:
            if key in columns:
                qty_col = columns[key]
                break

        unit_price_col = None
        for key in ['unit price', 'rate', 'price', 'unit_price', 'unit rate']:
            if key in columns:
                unit_price_col = columns[key]
                break

        total_col = None
        for key in ['total', 'amount', 'total price', 'total_price', 'value']:
            if key in columns:
                total_col = columns[key]
                break

        # Extract items
        if desc_col:
            for idx, row in df.iterrows():
                desc = row.get(desc_col)
                if pd.isna(desc) or not str(desc).strip():
                    continue

                if any(keyword in str(desc).lower() for keyword in
                       ['total', 'subtotal', 'grand total', 'description']):
                    continue

                item = {
                    'description': str(desc).strip()
                }

                if qty_col and not pd.isna(row.get(qty_col)):
                    try:
                        item['quantity'] = int(float(row[qty_col]))
                    except (ValueError, TypeError):
                        item['quantity'] = 1
                else:
                    item['quantity'] = 1

                if unit_price_col and not pd.isna(row.get(unit_price_col)):
                    try:
                        item['unit_price'] = float(row[unit_price_col])
                    except (ValueError, TypeError):
                        pass

                if total_col and not pd.isna(row.get(total_col)):
                    try:
                        item['total_price'] = float(row[total_col])
                    except (ValueError, TypeError):
                        pass

                if 'unit_price' in item and 'total_price' not in item:
                    item['total_price'] = item['unit_price'] * item['quantity']
                elif 'total_price' in item and 'unit_price' not in item:
                    item['unit_price'] = item['total_price'] / item['quantity'] if item['quantity'] > 0 else 0

                if 'unit_price' in item and 'total_price' in item:
                    result['items'].append(item)

        if result['items']:
            result['metadata']['total_cost'] = sum(item['total_price'] for item in result['items'])

        result['success'] = len(result['items']) > 0

    except Exception as e:
        result['error'] = str(e)

    return result


def auto_detect_and_parse(file_path: str) -> Dict:
    """
    Automatically detect file type and parse accordingly.

    Args:
        file_path: Path to file

    Returns:
        Parsed quote data
    """
    file_lower = file_path.lower()

    if file_lower.endswith('.pdf'):
        return parse_pdf_quote(file_path)
    elif file_lower.endswith(('.xlsx', '.xls')):
        return parse_excel_quote(file_path)
    elif file_lower.endswith('.csv'):
        return parse_csv_quote(file_path)
    else:
        return {
            'success': False,
            'error': f'Unsupported file format: {file_path}'
        }
