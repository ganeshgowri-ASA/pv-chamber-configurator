"""
Unit Tests for Quote Generator Module
Tests quote creation, calculation, PDF generation, and database operations
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.quote_generator import QuoteGenerator


class TestQuoteGenerator(unittest.TestCase):
    """Test cases for QuoteGenerator class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test databases
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, "test_quotes.db")

        # Initialize quote generator
        self.qg = QuoteGenerator()
        self.qg.quotes_db = self.test_db
        self.qg._init_quotes_database()

        # Sample customer data
        self.customer_info = {
            'name': 'Test Customer',
            'company': 'Test Company Ltd',
            'email': 'test@example.com',
            'phone': '+91-1234567890',
            'address': 'Test Address, Test City'
        }

        # Sample items
        self.items = [
            {
                'category': 'Chamber',
                'description': 'PV Test Chamber',
                'specification': 'UV+TC+HF+DH',
                'quantity': 1,
                'unit_price': 3500000.00
            },
            {
                'category': 'UV System',
                'description': 'UV LED Array',
                'specification': '60 W/m²',
                'quantity': 1,
                'unit_price': 1600000.00
            }
        ]

    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_generate_quote_number(self):
        """Test quote number generation"""
        # Generate and save first quote to register the number
        quote1 = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )
        quote_num1 = quote1['quote_number']
        self.qg.save_quote(quote1)

        # Generate second quote - should have incremented sequence
        quote2 = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )
        quote_num2 = quote2['quote_number']

        # Check format: QT-YYYYMMDD-XXX (15 characters total)
        self.assertTrue(quote_num1.startswith('QT-'))
        self.assertEqual(len(quote_num1), 15)

        # Quote numbers should be different (sequence incremented)
        self.assertNotEqual(quote_num1, quote_num2)

    def test_create_quote_basic(self):
        """Test basic quote creation"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )

        # Check required fields
        self.assertIn('quote_number', quote)
        self.assertIn('date', quote)
        self.assertIn('customer', quote)
        self.assertIn('items', quote)
        self.assertIn('subtotal', quote)
        self.assertIn('total', quote)

        # Check customer info
        self.assertEqual(quote['customer']['name'], 'Test Customer')
        self.assertEqual(quote['customer']['email'], 'test@example.com')

        # Check items
        self.assertEqual(len(quote['items']), 2)

    def test_calculate_totals(self):
        """Test totals calculation"""
        totals = self.qg.calculate_totals(
            items=self.items,
            discount_percent=10.0,
            tax_rate=18.0,
            shipping=50000.0
        )

        expected_subtotal = 3500000.00 + 1600000.00
        self.assertEqual(totals['subtotal'], expected_subtotal)

        expected_discount = expected_subtotal * 0.10
        self.assertEqual(totals['discount_amount'], expected_discount)

        expected_taxable = expected_subtotal - expected_discount
        self.assertEqual(totals['taxable_amount'], expected_taxable)

        expected_tax = expected_taxable * 0.18
        self.assertEqual(totals['tax_amount'], expected_tax)

    def test_apply_discount_percentage(self):
        """Test percentage discount application"""
        discount_amount, discount_percent = self.qg.apply_discount(
            subtotal=100000.0,
            discount_type='percentage',
            value=10.0
        )

        self.assertEqual(discount_amount, 10000.0)
        self.assertEqual(discount_percent, 10.0)

    def test_apply_discount_fixed(self):
        """Test fixed discount application"""
        discount_amount, discount_percent = self.qg.apply_discount(
            subtotal=100000.0,
            discount_type='fixed',
            value=15000.0
        )

        self.assertEqual(discount_amount, 15000.0)
        self.assertEqual(discount_percent, 15.0)

    def test_calculate_tax(self):
        """Test tax calculation"""
        tax = self.qg.calculate_tax(
            taxable_amount=100000.0,
            tax_rate=18.0
        )

        self.assertEqual(tax, 18000.0)

    def test_save_and_load_quote(self):
        """Test saving and loading quotes from database"""
        # Create quote
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )

        # Save quote
        quote_id = self.qg.save_quote(quote)
        self.assertIsNotNone(quote_id)
        self.assertGreater(quote_id, 0)

        # Load quote
        loaded_quote = self.qg.load_quote(quote_id)
        self.assertIsNotNone(loaded_quote)

        # Check loaded data matches
        self.assertEqual(loaded_quote['quote_number'], quote['quote_number'])
        self.assertEqual(loaded_quote['customer']['name'], quote['customer']['name'])
        self.assertEqual(len(loaded_quote['items']), len(quote['items']))
        self.assertEqual(loaded_quote['total'], quote['total'])

    def test_update_quote_status(self):
        """Test updating quote status"""
        # Create and save quote
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )
        quote_id = self.qg.save_quote(quote)

        # Update status
        success = self.qg.update_quote_status(quote_id, 'sent')
        self.assertTrue(success)

        # Verify status update
        loaded_quote = self.qg.load_quote(quote_id)
        self.assertEqual(loaded_quote['status'], 'sent')

    def test_get_quotes_by_customer(self):
        """Test retrieving quotes by customer email"""
        # Create and save first quote
        quote1 = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )
        self.qg.save_quote(quote1)

        # Create and save second quote
        quote2 = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )
        self.qg.save_quote(quote2)

        # Get quotes by customer
        quotes = self.qg.get_quotes_by_customer('test@example.com')

        self.assertEqual(len(quotes), 2)

    def test_bulk_discount_calculation(self):
        """Test bulk discount calculation"""
        # Create items with quantity > 3
        bulk_items = [
            {
                'category': 'Chamber',
                'description': 'PV Test Chamber',
                'specification': 'UV+TC+HF+DH',
                'quantity': 4,
                'unit_price': 3500000.00
            }
        ]

        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=bulk_items,
            discount_type='bulk'
        )

        # Should apply 5% discount for quantity > 3
        self.assertEqual(quote['discount_percent'], 5.0)

    def test_custom_discount(self):
        """Test custom discount amount"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items,
            custom_discount=500000.0
        )

        self.assertEqual(quote['discount_amount'], 500000.0)

    def test_generate_pdf(self):
        """Test PDF generation"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items
        )

        # Generate PDF
        pdf_path = os.path.join(self.test_dir, 'test_quote.pdf')
        success = self.qg.generate_pdf(quote, pdf_path)

        # Check PDF was created
        self.assertTrue(success)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)

    def test_quote_validity_date(self):
        """Test quote validity date calculation"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items,
            validity_days=30
        )

        self.assertIn('validity_date', quote)
        # Validity date should be 30 days from today
        self.assertIsNotNone(quote['validity_date'])

    def test_payment_terms_storage(self):
        """Test payment terms are stored correctly"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items,
            payment_terms='30% advance, 40% on delivery, 30% after installation'
        )

        self.assertEqual(
            quote['payment_terms'],
            '30% advance, 40% on delivery, 30% after installation'
        )

    def test_currency_handling(self):
        """Test currency field handling"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items,
            currency='USD'
        )

        self.assertEqual(quote['currency'], 'USD')

    def test_empty_items_list(self):
        """Test handling of empty items list"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=[]
        )

        self.assertEqual(quote['subtotal'], 0.0)
        self.assertEqual(quote['total'], quote['tax_amount'] + quote['shipping'])

    def test_shipping_and_installation_costs(self):
        """Test shipping and installation cost handling"""
        quote = self.qg.create_quote(
            customer_info=self.customer_info,
            items=self.items,
            shipping=75000.0,
            installation=500000.0
        )

        self.assertEqual(quote['shipping'], 75000.0)
        self.assertEqual(quote['installation'], 500000.0)

        # Total should include both
        expected_total = (
            quote['taxable_amount'] +
            quote['tax_amount'] +
            quote['shipping'] +
            quote['installation']
        )
        self.assertEqual(quote['total'], expected_total)


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
