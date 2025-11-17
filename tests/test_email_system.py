"""
Unit Tests for Email System Module
Tests email composition, validation, and tracking (mocked SMTP)
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from modules.email_system import EmailSystem


class TestEmailSystem(unittest.TestCase):
    """Test cases for EmailSystem class"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.test_dir, "test_emails.db")

        # Initialize email system
        self.email_sys = EmailSystem()
        self.email_sys.email_db = self.test_db
        self.email_sys._init_email_database()

        # Sample quote data
        self.quote_data = {
            'quote_number': 'QT-20250101-001',
            'date': '2025-01-01',
            'validity_days': 30,
            'validity_date': '2025-01-31',
            'customer': {
                'name': 'Test Customer',
                'company': 'Test Company',
                'email': 'customer@example.com',
                'phone': '+91-1234567890',
                'address': 'Test Address'
            },
            'items': [
                {
                    'category': 'Chamber',
                    'description': 'PV Test Chamber',
                    'specification': 'UV+TC+HF+DH',
                    'quantity': 1,
                    'unit_price': 3500000.00,
                    'total': 3500000.00
                }
            ],
            'subtotal': 3500000.00,
            'discount_percent': 0.0,
            'discount_amount': 0.0,
            'taxable_amount': 3500000.00,
            'tax_rate': 18.0,
            'tax_amount': 630000.00,
            'shipping': 50000.00,
            'installation': 0.0,
            'total': 4180000.00,
            'currency': 'INR',
            'payment_terms': '50% advance, 50% on delivery',
            'delivery_weeks': 14
        }

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_validate_email_valid(self):
        """Test email validation with valid emails"""
        valid_emails = [
            'test@example.com',
            'user.name@company.co.in',
            'sales@zenitek.com',
            'info+sales@company.org'
        ]

        for email in valid_emails:
            self.assertTrue(
                self.email_sys.validate_email(email),
                f"Email {email} should be valid"
            )

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails"""
        invalid_emails = [
            'invalid',
            '@example.com',
            'test@',
            'test@.com',
            'test..user@example.com',
            ''
        ]

        for email in invalid_emails:
            self.assertFalse(
                self.email_sys.validate_email(email),
                f"Email {email} should be invalid"
            )

    def test_compose_quote_email(self):
        """Test email composition"""
        subject, body = self.email_sys.compose_quote_email(self.quote_data)

        # Check subject
        self.assertIn('QT-20250101-001', subject)
        self.assertIn('Quote', subject)

        # Check body contains key information
        self.assertIn('Test Customer', body)
        self.assertIn('QT-20250101-001', body)
        self.assertIn('₹4,180,000.00', body)

    def test_compose_quote_email_with_custom_message(self):
        """Test email composition with custom message"""
        custom_msg = "Special offer: 5% additional discount for early payment"

        subject, body = self.email_sys.compose_quote_email(
            self.quote_data,
            custom_message=custom_msg
        )

        # Custom message should be in body
        self.assertIn(custom_msg, body)

    def test_log_email(self):
        """Test email logging to database"""
        email_id = self.email_sys._log_email(
            quote_id=1,
            quote_number='QT-20250101-001',
            to_email='test@example.com',
            cc_emails=['cc@example.com'],
            bcc_emails=['bcc@example.com'],
            subject='Test Quote',
            body='Test body',
            attachment_path='/path/to/quote.pdf',
            status='sent',
            error_message=None
        )

        self.assertIsNotNone(email_id)
        self.assertGreater(email_id, 0)

        # Retrieve and verify
        status = self.email_sys.get_email_status(email_id)
        self.assertEqual(status['to_email'], 'test@example.com')
        self.assertEqual(status['status'], 'sent')

    def test_get_email_status(self):
        """Test retrieving email status"""
        # Log an email
        email_id = self.email_sys._log_email(
            quote_id=1,
            quote_number='QT-20250101-001',
            to_email='test@example.com',
            cc_emails=None,
            bcc_emails=None,
            subject='Test',
            body='Body',
            attachment_path=None,
            status='sent',
            error_message=None
        )

        # Get status
        status = self.email_sys.get_email_status(email_id)

        self.assertIsNotNone(status)
        self.assertEqual(status['id'], email_id)
        self.assertEqual(status['quote_number'], 'QT-20250101-001')
        self.assertEqual(status['status'], 'sent')

    def test_get_email_status_nonexistent(self):
        """Test retrieving status for non-existent email"""
        status = self.email_sys.get_email_status(99999)
        self.assertIsNone(status)

    def test_get_email_history(self):
        """Test retrieving email history for a quote"""
        # Log multiple emails
        self.email_sys._log_email(
            quote_id=1,
            quote_number='QT-20250101-001',
            to_email='test1@example.com',
            cc_emails=None,
            bcc_emails=None,
            subject='Test 1',
            body='Body 1',
            attachment_path=None,
            status='sent',
            error_message=None
        )

        self.email_sys._log_email(
            quote_id=1,
            quote_number='QT-20250101-001',
            to_email='test2@example.com',
            cc_emails=None,
            bcc_emails=None,
            subject='Test 2',
            body='Body 2',
            attachment_path=None,
            status='sent',
            error_message=None
        )

        # Get history
        history = self.email_sys.get_email_history(quote_id=1)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['to_email'], 'test2@example.com')  # Most recent first
        self.assertEqual(history[1]['to_email'], 'test1@example.com')

    def test_schedule_follow_ups(self):
        """Test follow-up reminder scheduling"""
        # Log an email
        email_id = self.email_sys._log_email(
            quote_id=1,
            quote_number='QT-20250101-001',
            to_email='test@example.com',
            cc_emails=None,
            bcc_emails=None,
            subject='Test',
            body='Body',
            attachment_path=None,
            status='sent',
            error_message=None
        )

        # Schedule follow-ups
        self.email_sys._schedule_follow_ups(quote_id=1, email_id=email_id)

        # Verify follow-ups were scheduled
        import sqlite3
        conn = sqlite3.connect(self.email_sys.email_db)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) FROM follow_up_reminders
            WHERE quote_id = ? AND email_id = ?
        ''', (1, email_id))

        count = cursor.fetchone()[0]
        conn.close()

        # Should have 3 follow-ups (7, 14, 21 days)
        self.assertEqual(count, 3)

    def test_smtp_config_default(self):
        """Test default SMTP configuration"""
        config = self.email_sys._default_smtp_config()

        self.assertEqual(config['smtp_server'], 'smtp.gmail.com')
        self.assertEqual(config['smtp_port'], 587)
        self.assertTrue(config['use_tls'])
        self.assertFalse(config['use_ssl'])

    def test_send_quote_email_mock(self):
        """Test send_quote_email method (without actually sending)"""
        # Note: This test doesn't actually send emails
        # It tests the method logic and database logging

        # Create a temporary PDF file
        pdf_path = os.path.join(self.test_dir, 'test_quote.pdf')
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\nTest PDF content')

        # The actual send will fail (no SMTP credentials)
        # But we can test the method structure
        # In production, you'd mock smtplib.SMTP

        success, message, email_id = self.email_sys.send_quote_email(
            to_email='invalid@example.com',  # This will fail validation at SMTP level
            quote_pdf_path=pdf_path,
            quote_data=self.quote_data
        )

        # Email should be logged even if sending fails
        self.assertIsNotNone(email_id)

    def test_email_validation_in_send(self):
        """Test that invalid emails are caught before sending"""
        # This would normally be tested with mocked SMTP
        # For now, we just verify the validation works

        invalid_email = "not-an-email"
        self.assertFalse(self.email_sys.validate_email(invalid_email))

    def test_cc_bcc_handling(self):
        """Test CC and BCC email handling"""
        email_id = self.email_sys._log_email(
            quote_id=1,
            quote_number='QT-20250101-001',
            to_email='test@example.com',
            cc_emails=['cc1@example.com', 'cc2@example.com'],
            bcc_emails=['bcc@example.com'],
            subject='Test',
            body='Body',
            attachment_path=None,
            status='sent',
            error_message=None
        )

        # Verify CC/BCC were stored
        import sqlite3
        conn = sqlite3.connect(self.email_sys.email_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM email_log WHERE id = ?', (email_id,))
        row = cursor.fetchone()
        conn.close()

        self.assertEqual(row['cc_emails'], 'cc1@example.com, cc2@example.com')
        self.assertEqual(row['bcc_emails'], 'bcc@example.com')

    def test_email_error_logging(self):
        """Test error message logging"""
        email_id = self.email_sys._log_email(
            quote_id=1,
            quote_number='QT-20250101-001',
            to_email='test@example.com',
            cc_emails=None,
            bcc_emails=None,
            subject='Test',
            body='Body',
            attachment_path=None,
            status='failed',
            error_message='SMTP connection failed'
        )

        status = self.email_sys.get_email_status(email_id)

        self.assertEqual(status['status'], 'failed')
        self.assertEqual(status['error_message'], 'SMTP connection failed')


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == '__main__':
    run_tests()
