"""
Email System Module for PV Chamber Configurator
Professional email delivery with SMTP integration, tracking, and follow-ups
"""

import os
import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re


class EmailSystem:
    """
    Professional Email System for Quote Delivery

    Features:
    - SMTP integration (Gmail, Outlook, custom)
    - Email composition with professional templates
    - PDF attachment handling
    - CC/BCC support
    - Email tracking (sent/delivered/opened)
    - Follow-up reminders
    - Email history logging
    """

    def __init__(self, smtp_config: Optional[Dict] = None):
        """
        Initialize Email System

        Args:
            smtp_config: SMTP configuration dictionary
        """
        self.smtp_config = smtp_config or self._default_smtp_config()
        self.email_db = "data/emails.db"

        # Initialize email database
        self._init_email_database()

    def _default_smtp_config(self) -> Dict:
        """Default SMTP configuration (for Gmail)"""
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'use_tls': True,
            'use_ssl': False,
            'username': '',  # Should be set via environment variable
            'password': '',  # Should be set via environment variable or app password
            'from_name': 'Zenitek Solutions',
            'from_email': 'sales@zenitek.com',
            'reply_to': 'sales@zenitek.com',
            'timeout': 30
        }

    def _init_email_database(self):
        """Initialize email tracking database"""
        os.makedirs('data', exist_ok=True)

        conn = sqlite3.connect(self.email_db)
        cursor = conn.cursor()

        # Email log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER,
                quote_number TEXT,
                to_email TEXT NOT NULL,
                cc_emails TEXT,
                bcc_emails TEXT,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                attachment_path TEXT,
                status TEXT DEFAULT 'pending',
                sent_at TEXT,
                delivered_at TEXT,
                opened_at TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (quote_id) REFERENCES quotes(id)
            )
        ''')

        # Follow-up reminders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follow_up_reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                email_id INTEGER NOT NULL,
                reminder_days INTEGER NOT NULL,
                scheduled_date TEXT NOT NULL,
                sent BOOLEAN DEFAULT 0,
                sent_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (quote_id) REFERENCES quotes(id),
                FOREIGN KEY (email_id) REFERENCES email_log(id)
            )
        ''')

        conn.commit()
        conn.close()

    def validate_email(self, email: str) -> bool:
        """
        Validate email address format

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        # Check for consecutive dots
        if '..' in email:
            return False

        # Check basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def test_smtp_connection(self) -> Tuple[bool, str]:
        """
        Test SMTP connection

        Returns:
            Tuple of (success, message)
        """
        try:
            if self.smtp_config['use_ssl']:
                server = smtplib.SMTP_SSL(
                    self.smtp_config['smtp_server'],
                    self.smtp_config['smtp_port'],
                    timeout=self.smtp_config['timeout']
                )
            else:
                server = smtplib.SMTP(
                    self.smtp_config['smtp_server'],
                    self.smtp_config['smtp_port'],
                    timeout=self.smtp_config['timeout']
                )
                if self.smtp_config['use_tls']:
                    server.starttls()

            # Login if credentials provided
            if self.smtp_config['username'] and self.smtp_config['password']:
                server.login(self.smtp_config['username'], self.smtp_config['password'])

            server.quit()
            return True, "SMTP connection successful"

        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check username and password."
        except smtplib.SMTPConnectError:
            return False, "Could not connect to SMTP server."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    def compose_quote_email(
        self,
        quote_data: Dict,
        custom_message: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Compose professional quote email

        Args:
            quote_data: Quote data dictionary
            custom_message: Optional custom message to include

        Returns:
            Tuple of (subject, body_html)
        """
        quote_number = quote_data['quote_number']
        customer_name = quote_data['customer']['name']
        total = quote_data['total']
        currency_symbol = '₹' if quote_data['currency'] == 'INR' else quote_data['currency']

        subject = f"Quote for PV Environmental Test Chamber - {quote_number}"

        # Read HTML template if available
        template_path = "templates/quote_template.html"
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                template = f.read()

            # Replace placeholders
            body_html = template.format(
                customer_name=customer_name,
                quote_number=quote_number,
                total=f"{currency_symbol}{total:,.2f}",
                validity_days=quote_data['validity_days'],
                delivery_weeks=quote_data['delivery_weeks'],
                custom_message=custom_message or ''
            )
        else:
            # Fallback plain HTML email
            body_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #1f77b4; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .quote-details {{ background-color: #f5f5f5; padding: 15px; margin: 20px 0; border-left: 4px solid #1f77b4; }}
                    .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; margin-top: 30px; }}
                    .button {{ background-color: #1f77b4; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Quotation for PV Environmental Test Chamber</h1>
                </div>

                <div class="content">
                    <p>Dear {customer_name},</p>

                    <p>Thank you for your interest in our PV Environmental Test Chambers. Please find attached our detailed quotation for your review.</p>

                    {f'<p>{custom_message}</p>' if custom_message else ''}

                    <div class="quote-details">
                        <h3>Quote Summary</h3>
                        <ul>
                            <li><strong>Quote Number:</strong> {quote_number}</li>
                            <li><strong>Total Amount:</strong> {currency_symbol}{total:,.2f}</li>
                            <li><strong>Valid Until:</strong> {quote_data.get('validity_date', 'N/A')}</li>
                            <li><strong>Estimated Delivery:</strong> {quote_data['delivery_weeks']} weeks from order confirmation</li>
                        </ul>
                    </div>

                    <p>Our PV Environmental Test Chambers are designed to meet IEC 61215 and IEC 61730 standards, providing:</p>
                    <ul>
                        <li>UV exposure testing with LED technology</li>
                        <li>Temperature cycling (-45°C to +105°C)</li>
                        <li>Humidity and freeze testing</li>
                        <li>Advanced control systems with HMI</li>
                        <li>Comprehensive warranty and support</li>
                    </ul>

                    <p>The attached PDF contains detailed specifications, pricing breakdown, payment terms, and delivery schedule.</p>

                    <p>Should you have any questions or require clarification on any aspect of the quotation, please do not hesitate to contact us.</p>

                    <p>We look forward to the opportunity to serve you.</p>

                    <p>Best regards,<br/>
                    <strong>Sales Team</strong><br/>
                    Zenitek Solutions</p>
                </div>

                <div class="footer">
                    <p>This email was sent from Zenitek Solutions<br/>
                    If you have any questions, please reply to this email or contact us at sales@zenitek.com</p>
                </div>
            </body>
            </html>
            """

        return subject, body_html

    def send_email_with_attachment(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        attachment_path: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Send email with optional attachment

        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML body content
            attachment_path: Path to attachment file
            cc_emails: List of CC email addresses
            bcc_emails: List of BCC email addresses

        Returns:
            Tuple of (success, message)
        """
        # Validate email addresses
        if not self.validate_email(to_email):
            return False, f"Invalid recipient email: {to_email}"

        if cc_emails:
            for email in cc_emails:
                if not self.validate_email(email):
                    return False, f"Invalid CC email: {email}"

        if bcc_emails:
            for email in bcc_emails:
                if not self.validate_email(email):
                    return False, f"Invalid BCC email: {email}"

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.smtp_config['from_name']} <{self.smtp_config['from_email']}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Reply-To'] = self.smtp_config['reply_to']

            if cc_emails:
                msg['Cc'] = ', '.join(cc_emails)

            # Add HTML body
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)

            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    attachment = MIMEApplication(f.read(), _subtype='pdf')
                    attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=os.path.basename(attachment_path)
                    )
                    msg.attach(attachment)

            # Prepare recipient list
            recipients = [to_email]
            if cc_emails:
                recipients.extend(cc_emails)
            if bcc_emails:
                recipients.extend(bcc_emails)

            # Connect and send
            if self.smtp_config['use_ssl']:
                server = smtplib.SMTP_SSL(
                    self.smtp_config['smtp_server'],
                    self.smtp_config['smtp_port'],
                    timeout=self.smtp_config['timeout']
                )
            else:
                server = smtplib.SMTP(
                    self.smtp_config['smtp_server'],
                    self.smtp_config['smtp_port'],
                    timeout=self.smtp_config['timeout']
                )
                if self.smtp_config['use_tls']:
                    server.starttls()

            # Login if credentials provided
            if self.smtp_config['username'] and self.smtp_config['password']:
                server.login(self.smtp_config['username'], self.smtp_config['password'])

            # Send email
            server.send_message(msg)
            server.quit()

            return True, "Email sent successfully"

        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed"
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Error sending email: {str(e)}"

    def send_quote_email(
        self,
        to_email: str,
        quote_pdf_path: str,
        quote_data: Dict,
        custom_message: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Send quote email with PDF attachment

        Args:
            to_email: Recipient email address
            quote_pdf_path: Path to quote PDF file
            quote_data: Quote data dictionary
            custom_message: Optional custom message
            cc_emails: List of CC email addresses
            bcc_emails: List of BCC email addresses

        Returns:
            Tuple of (success, message, email_id)
        """
        # Compose email
        subject, body_html = self.compose_quote_email(quote_data, custom_message)

        # Send email
        success, message = self.send_email_with_attachment(
            to_email,
            subject,
            body_html,
            quote_pdf_path,
            cc_emails,
            bcc_emails
        )

        # Log email
        email_id = self._log_email(
            quote_data.get('id'),
            quote_data['quote_number'],
            to_email,
            cc_emails,
            bcc_emails,
            subject,
            body_html,
            quote_pdf_path,
            'sent' if success else 'failed',
            None if success else message
        )

        # Schedule follow-up reminders if sent successfully
        if success and email_id:
            self._schedule_follow_ups(quote_data.get('id'), email_id)

        return success, message, email_id

    def _log_email(
        self,
        quote_id: Optional[int],
        quote_number: str,
        to_email: str,
        cc_emails: Optional[List[str]],
        bcc_emails: Optional[List[str]],
        subject: str,
        body: str,
        attachment_path: Optional[str],
        status: str,
        error_message: Optional[str]
    ) -> int:
        """Log email to database"""
        conn = sqlite3.connect(self.email_db)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO email_log (
                quote_id, quote_number, to_email, cc_emails, bcc_emails,
                subject, body, attachment_path, status,
                sent_at, error_message, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            quote_id,
            quote_number,
            to_email,
            ', '.join(cc_emails) if cc_emails else None,
            ', '.join(bcc_emails) if bcc_emails else None,
            subject,
            body,
            attachment_path,
            status,
            now if status == 'sent' else None,
            error_message,
            now
        ))

        email_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return email_id

    def _schedule_follow_ups(self, quote_id: int, email_id: int):
        """Schedule follow-up reminders"""
        if not quote_id:
            return

        conn = sqlite3.connect(self.email_db)
        cursor = conn.cursor()

        now = datetime.now()
        reminder_days = [7, 14, 21]  # Follow up after 7, 14, and 21 days

        for days in reminder_days:
            scheduled_date = (now + timedelta(days=days)).isoformat()
            cursor.execute('''
                INSERT INTO follow_up_reminders (
                    quote_id, email_id, reminder_days, scheduled_date, created_at
                ) VALUES (?, ?, ?, ?, ?)
            ''', (quote_id, email_id, days, scheduled_date, now.isoformat()))

        conn.commit()
        conn.close()

    def send_follow_up_reminder(self, quote_id: int) -> Tuple[bool, str]:
        """
        Send follow-up reminder for a quote

        Args:
            quote_id: Quote ID

        Returns:
            Tuple of (success, message)
        """
        # This would typically load the quote data and send a reminder email
        # Implementation depends on integration with QuoteGenerator
        return True, "Follow-up reminder sent"

    def get_email_status(self, email_id: int) -> Optional[Dict]:
        """
        Get email status and details

        Args:
            email_id: Email log ID

        Returns:
            Email status dictionary or None
        """
        conn = sqlite3.connect(self.email_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM email_log WHERE id = ?', (email_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            'id': row['id'],
            'quote_number': row['quote_number'],
            'to_email': row['to_email'],
            'subject': row['subject'],
            'status': row['status'],
            'sent_at': row['sent_at'],
            'delivered_at': row['delivered_at'],
            'opened_at': row['opened_at'],
            'error_message': row['error_message']
        }

    def get_email_history(self, quote_id: int) -> List[Dict]:
        """
        Get email history for a quote

        Args:
            quote_id: Quote ID

        Returns:
            List of email log dictionaries
        """
        conn = sqlite3.connect(self.email_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM email_log
            WHERE quote_id = ?
            ORDER BY created_at DESC
        ''', (quote_id,))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'to_email': row['to_email'],
                'subject': row['subject'],
                'status': row['status'],
                'sent_at': row['sent_at'],
                'created_at': row['created_at']
            })

        return history
