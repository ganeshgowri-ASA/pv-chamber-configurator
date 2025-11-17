"""
Quote Generator Module for PV Chamber Configurator
Professional PDF quote generation with branding, calculations, and templates
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class QuoteGenerator:
    """
    Professional Quote Generator for PV Environmental Test Chambers

    Features:
    - Component selection and pricing
    - Discount management (bulk, seasonal, custom)
    - Tax calculation (GST 18%)
    - Shipping and installation charges
    - Warranty packages
    - Professional PDF generation
    - Quote versioning and status tracking
    """

    def __init__(self, supplier_db: Optional[str] = None, white_label_config: Optional[Dict] = None):
        """
        Initialize Quote Generator

        Args:
            supplier_db: Path to supplier database (SQLite)
            white_label_config: White label branding configuration
        """
        self.supplier_db = supplier_db or "data/suppliers.db"
        self.quotes_db = "data/quotes.db"
        self.white_label_config = white_label_config or self._default_white_label()

        # Initialize databases
        self._init_quotes_database()

        # Quote number counter
        self.quote_prefix = "QT"

    def _default_white_label(self) -> Dict:
        """Default white label configuration"""
        return {
            'company_name': 'Zenitek Solutions',
            'address': 'Tamil Nadu, India',
            'email': 'info@zenitek.com',
            'phone': '+91-XXX-XXX-XXXX',
            'website': 'www.zenitek.com',
            'logo_path': None,
            'primary_color': '#1f77b4',
            'secondary_color': '#ff7f0e',
            'footer_text': 'Professional Environmental Test Chambers'
        }

    def _init_quotes_database(self):
        """Initialize quotes database with required tables"""
        os.makedirs('data', exist_ok=True)

        conn = sqlite3.connect(self.quotes_db)
        cursor = conn.cursor()

        # Quotes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_number TEXT UNIQUE NOT NULL,
                date TEXT NOT NULL,
                validity_days INTEGER DEFAULT 30,
                customer_id INTEGER,
                customer_name TEXT NOT NULL,
                customer_company TEXT,
                customer_email TEXT NOT NULL,
                customer_phone TEXT,
                customer_address TEXT,
                subtotal REAL NOT NULL,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                taxable_amount REAL NOT NULL,
                tax_rate REAL DEFAULT 18.0,
                tax_amount REAL NOT NULL,
                shipping REAL DEFAULT 0,
                installation REAL DEFAULT 0,
                total REAL NOT NULL,
                currency TEXT DEFAULT 'INR',
                payment_terms TEXT,
                delivery_weeks INTEGER DEFAULT 14,
                status TEXT DEFAULT 'draft',
                version INTEGER DEFAULT 1,
                parent_quote_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                sent_at TEXT,
                viewed_at TEXT,
                accepted_at TEXT,
                FOREIGN KEY (parent_quote_id) REFERENCES quotes(id)
            )
        ''')

        # Quote items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quote_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                specification TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
            )
        ''')

        # Quote notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quote_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    def generate_quote_number(self) -> str:
        """
        Generate unique quote number in format: QT-YYYYMMDD-XXX

        Returns:
            Unique quote number string
        """
        today = datetime.now().strftime('%Y%m%d')

        conn = sqlite3.connect(self.quotes_db)
        cursor = conn.cursor()

        # Find the highest sequence number for today
        cursor.execute('''
            SELECT quote_number FROM quotes
            WHERE quote_number LIKE ?
            ORDER BY quote_number DESC LIMIT 1
        ''', (f'{self.quote_prefix}-{today}-%',))

        result = cursor.fetchone()
        conn.close()

        if result:
            # Extract sequence number and increment
            last_seq = int(result[0].split('-')[-1])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f'{self.quote_prefix}-{today}-{new_seq:03d}'

    def create_quote(
        self,
        customer_info: Dict,
        items: List[Dict],
        discount_percent: float = 0.0,
        discount_type: str = 'percentage',
        custom_discount: float = 0.0,
        shipping: float = 50000.0,
        installation: float = 0.0,
        tax_rate: float = 18.0,
        payment_terms: str = '50% advance, 50% on delivery',
        delivery_weeks: int = 14,
        currency: str = 'INR',
        validity_days: int = 30
    ) -> Dict:
        """
        Create a new quote with all calculations

        Args:
            customer_info: Dict with customer details (name, company, email, phone, address)
            items: List of item dicts (category, description, specification, quantity, unit_price)
            discount_percent: Discount percentage
            discount_type: Type of discount ('percentage', 'bulk', 'seasonal', 'custom')
            custom_discount: Custom discount amount (overrides percentage)
            shipping: Shipping cost
            installation: Installation charges
            tax_rate: Tax rate percentage (default 18% GST)
            payment_terms: Payment terms string
            delivery_weeks: Estimated delivery in weeks
            currency: Currency code (INR, USD, EUR)
            validity_days: Quote validity in days

        Returns:
            Complete quote data dictionary
        """
        quote_number = self.generate_quote_number()
        quote_date = datetime.now().strftime('%Y-%m-%d')

        # Calculate item totals
        processed_items = []
        subtotal = 0.0

        for item in items:
            item_total = item['quantity'] * item['unit_price']
            processed_item = {
                'category': item['category'],
                'description': item['description'],
                'specification': item.get('specification', ''),
                'quantity': item['quantity'],
                'unit_price': item['unit_price'],
                'total': item_total
            }
            processed_items.append(processed_item)
            subtotal += item_total

        # Apply discount
        if discount_type == 'bulk':
            total_quantity = sum(item['quantity'] for item in items)
            if total_quantity > 5:
                discount_percent = 10.0
            elif total_quantity > 3:
                discount_percent = 5.0

        if custom_discount > 0:
            discount_amount = custom_discount
            discount_percent = (discount_amount / subtotal * 100) if subtotal > 0 else 0
        else:
            discount_amount = subtotal * (discount_percent / 100)

        # Calculate tax
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * (tax_rate / 100)

        # Calculate total
        total = taxable_amount + tax_amount + shipping + installation

        quote_data = {
            'quote_number': quote_number,
            'date': quote_date,
            'validity_days': validity_days,
            'validity_date': (datetime.now() + timedelta(days=validity_days)).strftime('%Y-%m-%d'),
            'customer': customer_info,
            'items': processed_items,
            'subtotal': subtotal,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'taxable_amount': taxable_amount,
            'tax_rate': tax_rate,
            'tax_amount': tax_amount,
            'shipping': shipping,
            'installation': installation,
            'total': total,
            'currency': currency,
            'payment_terms': payment_terms,
            'delivery_weeks': delivery_weeks,
            'status': 'draft'
        }

        return quote_data

    def calculate_totals(
        self,
        items: List[Dict],
        discount_percent: float = 0.0,
        tax_rate: float = 18.0,
        shipping: float = 50000.0,
        installation: float = 0.0
    ) -> Dict:
        """
        Calculate quote totals

        Args:
            items: List of items with quantity and unit_price
            discount_percent: Discount percentage
            tax_rate: Tax rate percentage
            shipping: Shipping cost
            installation: Installation cost

        Returns:
            Dictionary with all calculated values
        """
        subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
        discount_amount = subtotal * (discount_percent / 100)
        taxable_amount = subtotal - discount_amount
        tax_amount = taxable_amount * (tax_rate / 100)
        total = taxable_amount + tax_amount + shipping + installation

        return {
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'taxable_amount': taxable_amount,
            'tax_amount': tax_amount,
            'total': total
        }

    def apply_discount(
        self,
        subtotal: float,
        discount_type: str,
        value: float
    ) -> Tuple[float, float]:
        """
        Apply discount to subtotal

        Args:
            subtotal: Subtotal amount
            discount_type: 'percentage' or 'fixed'
            value: Discount value (percentage or fixed amount)

        Returns:
            Tuple of (discount_amount, discount_percent)
        """
        if discount_type == 'percentage':
            discount_amount = subtotal * (value / 100)
            discount_percent = value
        else:  # fixed
            discount_amount = value
            discount_percent = (value / subtotal * 100) if subtotal > 0 else 0

        return discount_amount, discount_percent

    def calculate_tax(self, taxable_amount: float, tax_rate: float = 18.0) -> float:
        """
        Calculate tax amount

        Args:
            taxable_amount: Amount to calculate tax on
            tax_rate: Tax rate percentage

        Returns:
            Tax amount
        """
        return taxable_amount * (tax_rate / 100)

    def save_quote(self, quote_data: Dict) -> int:
        """
        Save quote to database

        Args:
            quote_data: Complete quote data dictionary

        Returns:
            Quote ID
        """
        conn = sqlite3.connect(self.quotes_db)
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        customer = quote_data['customer']

        # Insert quote
        cursor.execute('''
            INSERT INTO quotes (
                quote_number, date, validity_days,
                customer_name, customer_company, customer_email, customer_phone, customer_address,
                subtotal, discount_percent, discount_amount,
                taxable_amount, tax_rate, tax_amount,
                shipping, installation, total,
                currency, payment_terms, delivery_weeks,
                status, version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            quote_data['quote_number'],
            quote_data['date'],
            quote_data['validity_days'],
            customer['name'],
            customer.get('company', ''),
            customer['email'],
            customer.get('phone', ''),
            customer.get('address', ''),
            quote_data['subtotal'],
            quote_data['discount_percent'],
            quote_data['discount_amount'],
            quote_data['taxable_amount'],
            quote_data['tax_rate'],
            quote_data['tax_amount'],
            quote_data['shipping'],
            quote_data['installation'],
            quote_data['total'],
            quote_data['currency'],
            quote_data['payment_terms'],
            quote_data['delivery_weeks'],
            quote_data['status'],
            1,  # version
            now,
            now
        ))

        quote_id = cursor.lastrowid

        # Insert items
        for item in quote_data['items']:
            cursor.execute('''
                INSERT INTO quote_items (
                    quote_id, category, description, specification,
                    quantity, unit_price, total
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                quote_id,
                item['category'],
                item['description'],
                item['specification'],
                item['quantity'],
                item['unit_price'],
                item['total']
            ))

        conn.commit()
        conn.close()

        return quote_id

    def load_quote(self, quote_id: int) -> Optional[Dict]:
        """
        Load quote from database

        Args:
            quote_id: Quote ID

        Returns:
            Quote data dictionary or None if not found
        """
        conn = sqlite3.connect(self.quotes_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Load quote
        cursor.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,))
        quote_row = cursor.fetchone()

        if not quote_row:
            conn.close()
            return None

        # Load items
        cursor.execute('SELECT * FROM quote_items WHERE quote_id = ?', (quote_id,))
        items_rows = cursor.fetchall()

        conn.close()

        # Build quote data
        quote_data = {
            'id': quote_row['id'],
            'quote_number': quote_row['quote_number'],
            'date': quote_row['date'],
            'validity_days': quote_row['validity_days'],
            'customer': {
                'name': quote_row['customer_name'],
                'company': quote_row['customer_company'],
                'email': quote_row['customer_email'],
                'phone': quote_row['customer_phone'],
                'address': quote_row['customer_address']
            },
            'items': [
                {
                    'category': item['category'],
                    'description': item['description'],
                    'specification': item['specification'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price'],
                    'total': item['total']
                }
                for item in items_rows
            ],
            'subtotal': quote_row['subtotal'],
            'discount_percent': quote_row['discount_percent'],
            'discount_amount': quote_row['discount_amount'],
            'taxable_amount': quote_row['taxable_amount'],
            'tax_rate': quote_row['tax_rate'],
            'tax_amount': quote_row['tax_amount'],
            'shipping': quote_row['shipping'],
            'installation': quote_row['installation'],
            'total': quote_row['total'],
            'currency': quote_row['currency'],
            'payment_terms': quote_row['payment_terms'],
            'delivery_weeks': quote_row['delivery_weeks'],
            'status': quote_row['status'],
            'version': quote_row['version']
        }

        return quote_data

    def update_quote_status(self, quote_id: int, status: str) -> bool:
        """
        Update quote status

        Args:
            quote_id: Quote ID
            status: New status ('draft', 'sent', 'viewed', 'negotiating', 'accepted', 'rejected', 'expired')

        Returns:
            Success boolean
        """
        conn = sqlite3.connect(self.quotes_db)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        # Update status and timestamp
        timestamp_field = None
        if status == 'sent':
            timestamp_field = 'sent_at'
        elif status == 'viewed':
            timestamp_field = 'viewed_at'
        elif status == 'accepted':
            timestamp_field = 'accepted_at'

        if timestamp_field:
            cursor.execute(f'''
                UPDATE quotes
                SET status = ?, {timestamp_field} = ?, updated_at = ?
                WHERE id = ?
            ''', (status, now, now, quote_id))
        else:
            cursor.execute('''
                UPDATE quotes
                SET status = ?, updated_at = ?
                WHERE id = ?
            ''', (status, now, quote_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def get_quotes_by_customer(self, customer_email: str) -> List[Dict]:
        """
        Get all quotes for a customer

        Args:
            customer_email: Customer email address

        Returns:
            List of quote data dictionaries
        """
        conn = sqlite3.connect(self.quotes_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM quotes
            WHERE customer_email = ?
            ORDER BY date DESC
        ''', (customer_email,))

        rows = cursor.fetchall()
        conn.close()

        quotes = []
        for row in rows:
            quotes.append({
                'id': row['id'],
                'quote_number': row['quote_number'],
                'date': row['date'],
                'total': row['total'],
                'currency': row['currency'],
                'status': row['status']
            })

        return quotes

    def get_expiring_quotes(self, days: int = 7) -> List[Dict]:
        """
        Get quotes expiring within specified days

        Args:
            days: Number of days to look ahead

        Returns:
            List of expiring quote data
        """
        conn = sqlite3.connect(self.quotes_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Calculate expiry date
        expiry_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')

        cursor.execute('''
            SELECT * FROM quotes
            WHERE status IN ('sent', 'viewed', 'negotiating')
            AND date(date, '+' || validity_days || ' days') <= ?
            ORDER BY date ASC
        ''', (expiry_date,))

        rows = cursor.fetchall()
        conn.close()

        quotes = []
        for row in rows:
            quotes.append({
                'id': row['id'],
                'quote_number': row['quote_number'],
                'date': row['date'],
                'customer_email': row['customer_email'],
                'customer_name': row['customer_name'],
                'total': row['total'],
                'status': row['status']
            })

        return quotes

    def generate_pdf(self, quote_data: Dict, output_path: str) -> bool:
        """
        Generate professional PDF quote

        Args:
            quote_data: Complete quote data dictionary
            output_path: Output PDF file path

        Returns:
            Success boolean
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )

            # Container for PDF elements
            elements = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor(self.white_label_config['primary_color']),
                spaceAfter=12,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor(self.white_label_config['primary_color']),
                spaceAfter=6,
                spaceBefore=12
            )

            # Add logo if available
            if self.white_label_config.get('logo_path') and os.path.exists(self.white_label_config['logo_path']):
                logo = Image(self.white_label_config['logo_path'], width=200, height=80)
                elements.append(logo)
                elements.append(Spacer(1, 12))

            # Title
            elements.append(Paragraph("QUOTATION", title_style))
            elements.append(Spacer(1, 6))

            # Company header
            company_info = f"""
            <b>{self.white_label_config['company_name']}</b><br/>
            {self.white_label_config['address']}<br/>
            Email: {self.white_label_config['email']} | Phone: {self.white_label_config['phone']}<br/>
            Website: {self.white_label_config['website']}
            """
            elements.append(Paragraph(company_info, styles['Normal']))
            elements.append(Spacer(1, 12))

            # Quote details table
            quote_details_data = [
                ['Quote Number:', quote_data['quote_number'], 'Date:', quote_data['date']],
                ['Valid Until:', quote_data.get('validity_date', 'N/A'), 'Delivery:', f"{quote_data['delivery_weeks']} weeks"]
            ]

            quote_details_table = Table(quote_details_data, colWidths=[80, 120, 80, 120])
            quote_details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(quote_details_table)
            elements.append(Spacer(1, 12))

            # Customer section
            elements.append(Paragraph("Bill To:", heading_style))
            customer = quote_data['customer']
            customer_info = f"""
            <b>{customer['name']}</b><br/>
            {customer.get('company', '')}<br/>
            {customer.get('address', '')}<br/>
            Email: {customer['email']}<br/>
            Phone: {customer.get('phone', 'N/A')}
            """
            elements.append(Paragraph(customer_info, styles['Normal']))
            elements.append(Spacer(1, 12))

            # Items table
            elements.append(Paragraph("Items:", heading_style))

            items_data = [['#', 'Description', 'Specification', 'Qty', 'Unit Price', 'Total']]

            currency_symbol = '₹' if quote_data['currency'] == 'INR' else quote_data['currency']

            for i, item in enumerate(quote_data['items'], 1):
                items_data.append([
                    str(i),
                    item['description'],
                    item['specification'][:50] if len(item['specification']) > 50 else item['specification'],
                    str(item['quantity']),
                    f"{currency_symbol}{item['unit_price']:,.2f}",
                    f"{currency_symbol}{item['total']:,.2f}"
                ])

            items_table = Table(items_data, colWidths=[20, 120, 100, 30, 60, 70])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.white_label_config['primary_color'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (3, 0), (5, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 12))

            # Totals section
            totals_data = [
                ['Subtotal:', f"{currency_symbol}{quote_data['subtotal']:,.2f}"],
                [f"Discount ({quote_data['discount_percent']:.1f}%):", f"-{currency_symbol}{quote_data['discount_amount']:,.2f}"],
                ['Taxable Amount:', f"{currency_symbol}{quote_data['taxable_amount']:,.2f}"],
                [f"GST ({quote_data['tax_rate']:.0f}%):", f"{currency_symbol}{quote_data['tax_amount']:,.2f}"],
            ]

            if quote_data['shipping'] > 0:
                totals_data.append(['Shipping:', f"{currency_symbol}{quote_data['shipping']:,.2f}"])

            if quote_data['installation'] > 0:
                totals_data.append(['Installation:', f"{currency_symbol}{quote_data['installation']:,.2f}"])

            totals_data.append(['', ''])  # Blank line
            totals_data.append(['TOTAL:', f"{currency_symbol}{quote_data['total']:,.2f}"])

            totals_table = Table(totals_data, colWidths=[320, 80])
            totals_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 14),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(self.white_label_config['primary_color'])),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('LINEABOVE', (0, -2), (-1, -2), 1, colors.grey),
            ]))
            elements.append(totals_table)
            elements.append(Spacer(1, 12))

            # Payment terms
            elements.append(Paragraph("Payment Terms:", heading_style))
            elements.append(Paragraph(quote_data['payment_terms'], styles['Normal']))
            elements.append(Spacer(1, 12))

            # Terms and conditions
            elements.append(Paragraph("Terms & Conditions:", heading_style))
            terms = """
            1. This quotation is valid for 30 days from the date of issue.<br/>
            2. Delivery timeline is 12-16 weeks from order confirmation and advance payment receipt.<br/>
            3. Installation and calibration charges are additional unless specified.<br/>
            4. Standard warranty: 12 months from commissioning date.<br/>
            5. Prices are subject to change without prior notice.<br/>
            6. All disputes subject to jurisdiction of Tamil Nadu courts.<br/>
            7. Goods once sold will not be taken back or exchanged.
            """
            elements.append(Paragraph(terms, styles['Normal']))
            elements.append(Spacer(1, 12))

            # Footer
            footer_text = f"""
            <br/><br/>
            <b>Authorized Signature</b><br/>
            _________________________<br/>
            {self.white_label_config['company_name']}<br/>
            <i>{self.white_label_config['footer_text']}</i>
            """
            elements.append(Paragraph(footer_text, styles['Normal']))

            # Build PDF
            doc.build(elements)

            return True

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
