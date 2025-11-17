# Quote Generator System - User Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Features](#features)
5. [User Guide](#user-guide)
6. [Email Setup](#email-setup)
7. [Customization](#customization)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## Overview

The **PV Chamber Quote Generator** is a comprehensive commercial quotation system for photovoltaic environmental test chambers. It provides:

- ✅ Professional PDF quote generation
- ✅ Email delivery with SMTP integration
- ✅ Customer database management
- ✅ Quote history and tracking
- ✅ Discount management (bulk, seasonal, custom)
- ✅ Payment terms configuration
- ✅ Multi-currency support
- ✅ White-label branding

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

- `streamlit>=1.28.0` - Web application framework
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.17.0` - Interactive charts
- `reportlab>=4.0.0` - PDF generation
- `Pillow>=10.0.0` - Image processing

### Initialize Databases

Run the application once to initialize databases:

```bash
streamlit run app.py
```

This will create:
- `data/quotes.db` - Quote storage
- `data/customers.db` - Customer database
- `data/emails.db` - Email tracking

---

## Quick Start

### 1. Launch Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### 2. Configure Company Branding

In the sidebar, enter:
- Company Name
- Address
- Email

### 3. Create Your First Quote

1. Navigate to **Quote Generator** tab
2. Go to **Create Quote** sub-tab
3. Fill in customer information:
   - Customer Name (required)
   - Customer Email (required)
   - Company, Phone, Address (optional)
4. Select items from the checklist
5. Adjust quantities as needed
6. Choose discount type and payment terms
7. Click **Generate Quote**

### 4. Generate PDF

1. After quote is created, click **Generate PDF**
2. Download the PDF using the download button

### 5. Send Email (Optional)

1. Go to **Email & Delivery** sub-tab
2. Configure SMTP settings (see [Email Setup](#email-setup))
3. Enter recipient details
4. Click **Send Email**

---

## Features

### Quote Generation

#### Automatic Calculations

- **Subtotal**: Sum of all items
- **Discounts**: Percentage, bulk, or custom amount
- **Tax**: GST 18% (configurable)
- **Shipping**: Weight-based estimation
- **Installation**: Optional charges
- **Total**: All-inclusive final amount

#### Discount Types

1. **Percentage Discount**
   - Manual percentage (0-50%)
   - Applied to subtotal

2. **Bulk Discount**
   - >3 units: 5% discount
   - >5 units: 10% discount
   - Automatic calculation

3. **Custom Discount**
   - Fixed amount in rupees
   - Overrides percentage

#### Payment Terms

Standard options:
- 100% advance
- 50% advance, 50% on delivery
- 30% advance, 40% on delivery, 30% after installation
- 30/60/90 day credit terms

### PDF Generation

Professional quote PDFs include:
- Company logo and branding
- Quote number (QT-YYYYMMDD-XXX format)
- Customer details
- Itemized component list with specifications
- Price breakdown (subtotal, discount, tax, total)
- Payment terms and schedule
- Delivery timeline
- Terms and conditions
- Digital signature area

### Email System

Features:
- Professional HTML email templates
- PDF attachment support
- CC/BCC functionality
- Email tracking (sent/delivered/opened)
- Follow-up reminders (7, 14, 21 days)
- Custom message support

### Customer Management

- Add/edit customer profiles
- Contact history tracking
- Quote history per customer
- Export to CSV
- Customer segmentation (prospect/customer/partner)

### Quote History

- View all quotes
- Filter by status (draft/sent/viewed/accepted/rejected)
- Export to CSV
- Side-by-side comparison
- Version control

---

## User Guide

### Creating a Quote

#### Step 1: Customer Information

Required fields:
- Customer Name
- Customer Email

Optional fields:
- Company Name
- Phone Number
- Full Address

💡 **Tip**: Customer information is automatically saved to the database for future quotes.

#### Step 2: Select Items

**Standard Items** (pre-selected):
- Chamber System
- UV LED Array
- Refrigeration System
- Control System & HMI
- DC Power Supply
- Calibration Services

**Optional Items**:
- UV Uniformity Robot
- Water Treatment System
- Installation & Commissioning
- Extended Warranty

Adjust quantities using the input boxes.

#### Step 3: Configure Pricing

**Discount Options**:

1. **Percentage**: Enter 0-50%
2. **Bulk**: Automatic based on quantity
3. **Custom**: Fixed amount in ₹

**Payment Terms**:
Choose from dropdown menu

**Shipping & Installation**:
Adjust costs as needed

#### Step 4: Generate Quote

Click **🧮 Generate Quote**

Review the quote summary showing:
- Quote number
- Total amount
- Validity period
- Itemized breakdown
- Payment terms

#### Step 5: Generate PDF

Click **📄 Generate PDF**

The PDF is:
- Saved to `data/quotes/QT-YYYYMMDD-XXX.pdf`
- Available for download
- Ready to email

### Sending Quotes via Email

⚠️ **Important**: Email functionality requires SMTP configuration (see [Email Setup](#email-setup))

1. Generate quote and PDF first
2. Go to **Email & Delivery** tab
3. Configure SMTP settings (one-time setup)
4. Enter recipient email
5. Add CC/BCC if needed
6. Write custom message (optional)
7. Click **📧 Send Email**

### Managing Customers

#### Add New Customer

1. Go to **Customers** tab
2. Click **➕ Add New Customer**
3. Fill in details:
   - Name (required)
   - Email (required)
   - Company, Phone, Address (optional)
4. Click **Add Customer**

#### View Customers

- See all customers in table format
- Export to CSV for external use
- Track customer type and status

#### Customer Types

- **Prospect**: Potential customer
- **Customer**: Active customer
- **Partner**: Strategic partner

---

## Email Setup

### Gmail Setup (Recommended)

#### 1. Enable 2-Factor Authentication

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification

#### 2. Generate App Password

1. Go to [App Passwords](https://myaccount.google.com/apppasswords)
2. Select "Mail" and "Other (Custom name)"
3. Name it "PV Quote System"
4. Copy the 16-character password

#### 3. Configure in Application

In the **Email & Delivery** tab, expand **SMTP Configuration**:

```
SMTP Server: smtp.gmail.com
SMTP Port: 587
Username: your-email@gmail.com
Password: [paste app password]
Use TLS: ✓ Checked
```

Click **Test Connection** to verify.

### Outlook/Office 365 Setup

```
SMTP Server: smtp-mail.outlook.com
SMTP Port: 587
Username: your-email@outlook.com
Password: [your password]
Use TLS: ✓ Checked
```

### Custom SMTP Setup

For other email providers:

1. Contact your email provider for SMTP settings
2. Common ports:
   - 587 (TLS)
   - 465 (SSL)
   - 25 (Unencrypted - not recommended)

### Security Recommendations

🔒 **Never commit SMTP credentials to version control**

Best practices:
1. Use environment variables:
   ```bash
   export SMTP_USERNAME="your-email@gmail.com"
   export SMTP_PASSWORD="your-app-password"
   ```

2. Use app-specific passwords (not account password)
3. Enable 2-factor authentication
4. Restrict SMTP access to specific IP addresses
5. Regularly rotate passwords

---

## Customization

### White Label Branding

#### Update Company Information

In sidebar:
- Company Name
- Address
- Email

This information appears on:
- PDF quotes
- Email signatures
- Application footer

#### Add Company Logo

1. Place logo image in project directory (PNG/JPG)
2. Edit `app.py`:
   ```python
   white_label_config = {
       'company_name': 'Your Company',
       'logo_path': 'path/to/logo.png',
       ...
   }
   ```

3. Recommended size: 200x80 pixels

#### Customize Colors

Edit `modules/quote_generator.py`:

```python
white_label_config = {
    'primary_color': '#1f77b4',  # Hex color code
    'secondary_color': '#ff7f0e',
    ...
}
```

### Modify Quote Items

Edit `data/quote_templates/sample_quote_config.json`:

```json
{
  "default_items": [
    {
      "category": "New Category",
      "description": "New Item",
      "specification": "Specs here",
      "quantity": 1,
      "unit_price": 100000.00
    }
  ]
}
```

### Change Tax Rate

Edit default settings:

```json
{
  "default_settings": {
    "tax_rate": 18.0
  }
}
```

### Customize Email Template

Edit `templates/quote_template.html`:

- Change HTML structure
- Modify styles (CSS)
- Update branding
- Add/remove sections

### Payment Terms

Add custom payment terms in `app.py`:

```python
payment_terms = st.selectbox(
    "Payment Terms",
    [
        "100% advance",
        "Your custom term",
        ...
    ]
)
```

---

## API Reference

### QuoteGenerator Class

```python
from modules.quote_generator import QuoteGenerator

# Initialize
qg = QuoteGenerator(white_label_config=config)

# Create quote
quote = qg.create_quote(
    customer_info=customer_dict,
    items=items_list,
    discount_percent=10.0,
    payment_terms='50% advance, 50% on delivery'
)

# Save quote
quote_id = qg.save_quote(quote)

# Load quote
quote = qg.load_quote(quote_id)

# Generate PDF
success = qg.generate_pdf(quote, 'output.pdf')

# Update status
qg.update_quote_status(quote_id, 'sent')
```

### EmailSystem Class

```python
from modules.email_system import EmailSystem

# Initialize
email_sys = EmailSystem(smtp_config=config)

# Test connection
success, message = email_sys.test_smtp_connection()

# Send quote email
success, message, email_id = email_sys.send_quote_email(
    to_email='customer@example.com',
    quote_pdf_path='quote.pdf',
    quote_data=quote_dict,
    custom_message='Special offer...'
)

# Get email status
status = email_sys.get_email_status(email_id)
```

### Payment Calculator

```python
from modules import payment_calculator

# Calculate payment schedule
schedule = payment_calculator.calculate_payment_schedule(
    total=1000000.0,
    terms='50% advance, 50% on delivery'
)

# Convert currency
result = payment_calculator.convert_currency(
    amount=1000000.0,
    from_currency='INR',
    to_currency='USD'
)

# Calculate late payment interest
interest = payment_calculator.calculate_late_payment_interest(
    amount=500000.0,
    days_late=30,
    annual_rate=18.0
)
```

---

## Troubleshooting

### Common Issues

#### PDF Generation Fails

**Error**: `ModuleNotFoundError: No module named 'reportlab'`

**Solution**:
```bash
pip install reportlab Pillow
```

#### Email Not Sending

**Error**: `SMTPAuthenticationError`

**Solutions**:
1. Verify username and password
2. Use app-specific password (Gmail)
3. Enable "Less secure apps" (if applicable)
4. Check SMTP server and port
5. Verify TLS/SSL settings

**Error**: `SMTPConnectError`

**Solutions**:
1. Check internet connection
2. Verify SMTP server address
3. Try different port (587, 465, 25)
4. Check firewall settings

#### Database Errors

**Error**: `no such table: quotes`

**Solution**: Delete `data/quotes.db` and restart app to reinitialize

**Error**: `database is locked`

**Solution**: Close other instances of the application

#### Quote Not Appearing in History

**Solution**:
1. Verify quote was saved (check for success message)
2. Refresh the Quote History tab
3. Check `data/quotes.db` exists

### Debug Mode

Enable debug output:

```python
# In app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

View logs in terminal while running application.

---

## Security Best Practices

### Credentials Management

❌ **Never do**:
```python
smtp_password = "my-password-123"  # Hardcoded
```

✅ **Always do**:
```python
import os
smtp_password = os.getenv('SMTP_PASSWORD')
```

### Environment Variables

Create `.env` file (add to `.gitignore`):

```bash
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Load in application:

```python
from dotenv import load_dotenv
load_dotenv()

smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')
```

### Database Security

1. **Backup regularly**:
   ```bash
   cp data/quotes.db backups/quotes_$(date +%Y%m%d).db
   ```

2. **Restrict file permissions**:
   ```bash
   chmod 600 data/*.db
   ```

3. **Encrypt sensitive data**:
   Use SQLCipher for encrypted databases

### Input Validation

All user inputs are validated:
- Email addresses (regex validation)
- Numeric values (type checking)
- File paths (sanitization)
- SQL injection prevention (parameterized queries)

### HTTPS Deployment

For production:
1. Deploy with HTTPS (SSL/TLS certificate)
2. Use reverse proxy (nginx, Apache)
3. Enable CORS protection
4. Implement rate limiting

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review error messages in terminal
3. Check application logs
4. Open GitHub issue with details:
   - Error message
   - Steps to reproduce
   - Environment (OS, Python version)

---

## License

See `LICENSE` file for details.

---

## Version History

### v2.0 (Current)
- Quote Generator System
- Email delivery
- Customer management
- PDF generation
- Payment calculator

### v1.0
- Basic chamber configurator
- Cost breakdown
- Business analysis
- Virtual HMI

---

**Made with ❤️ for PV Testing Industry**
