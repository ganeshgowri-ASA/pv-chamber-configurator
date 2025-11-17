# Supplier Database Manager - User Guide

## Overview

The Supplier Database Manager is a comprehensive system for managing suppliers, components, quotes, and procurement decisions for PV chamber configurators. It provides automated quote parsing, intelligent price comparison, and data-driven procurement recommendations.

## Features

### 1. Supplier Management
- Store and manage supplier information (contact, location, ratings, delivery times, payment terms)
- Track supplier performance metrics
- View supplier statistics and analytics

### 2. Component Catalog
- Maintain a comprehensive catalog of components by category
- Track pricing, lead times, warranty periods, and MOQ
- Link components to suppliers
- Monitor price history over time

### 3. Quote Upload & Parsing
- **Supported Formats:**
  - PDF quotes (using pdfplumber or PyPDF2)
  - Excel files (.xlsx, .xls)
  - CSV files

- **Auto-Extraction Features:**
  - Component descriptions
  - Quantities and unit prices
  - Total prices and subtotals
  - Lead times and delivery schedules
  - Warranty terms
  - Quote metadata (number, date, validity)
  - Payment terms

### 4. Price Comparison
- Compare prices across multiple suppliers for the same component category
- Weighted scoring system considering:
  - Price (30%)
  - Lead time (25%)
  - Supplier rating (20%)
  - Warranty (15%)
  - Payment terms (10%)
- Visual comparison charts
- Best value recommendations

### 5. Procurement Recommendation Engine
- Define component requirements
- Get optimal supplier selection based on:
  - Total cost minimization
  - Lead time optimization
  - Supplier diversification
- Risk assessment (supplier dependency analysis)
- Delivery schedule calculation

---

## Database Schema

### Suppliers Table
```sql
- id: Unique identifier
- name: Supplier name
- contact: Contact phone number
- email: Email address
- location: City/state location
- rating: Supplier rating (0-5.0)
- avg_delivery_days: Average delivery time
- payment_terms: Payment terms (Net 30, Net 45, etc.)
- currency: Currency code (default: INR)
```

### Components Table
```sql
- id: Unique identifier
- category: Component category (Heaters, Fans, UV LEDs, etc.)
- name: Component name
- specification: Technical specifications
- supplier_id: Foreign key to suppliers
- price: Unit price
- lead_time_days: Lead time in days
- warranty_months: Warranty period
- moq: Minimum order quantity
```

### Quotes Table
```sql
- id: Unique identifier
- supplier_id: Foreign key to suppliers
- quote_number: Quote reference number
- quote_date: Date of quote
- validity_days: Quote validity period
- total_cost: Total quote amount
- tax_amount: Tax/GST amount
- delivery_cost: Delivery charges
- status: Quote status (pending/active/expired)
```

### Quote Items Table
```sql
- id: Unique identifier
- quote_id: Foreign key to quotes
- component_id: Foreign key to components (optional)
- description: Item description
- quantity: Quantity ordered
- unit_price: Price per unit
- total_price: Total line item price
```

### Price History Table
```sql
- id: Unique identifier
- component_id: Foreign key to components
- price: Historical price
- date: Date of price record
- supplier_id: Foreign key to suppliers
```

---

## Usage Guide

### 1. Initializing the Database

The database is automatically initialized when you first run the application. It loads pre-configured Indian suppliers for PV chamber components.

```python
from modules.supplier_database import SupplierDatabaseManager

# Initialize database
db = SupplierDatabaseManager('data/suppliers.db')
```

### 2. Adding Suppliers

**Via Python:**
```python
supplier_data = {
    'name': 'Watlow India Pvt Ltd',
    'contact': '+91-80-4132-5400',
    'email': 'india@watlow.com',
    'location': 'Bangalore, Karnataka',
    'rating': 4.5,
    'avg_delivery_days': 25,
    'payment_terms': 'Net 30'
}

supplier_id = db.add_supplier(supplier_data)
```

**Via Web Interface:**
1. Navigate to "Supplier Database" tab
2. Go to "Suppliers" subtab
3. Click "Add New Supplier" expander
4. Fill in supplier details and submit

### 3. Adding Components

```python
component_data = {
    'category': 'Heaters',
    'name': 'Finned Tubular Heater 10kW',
    'specification': '10kW, 415V, SS304, Flange mounted',
    'supplier_id': supplier_id,
    'price': 85000,
    'lead_time_days': 25,
    'warranty_months': 24,
    'moq': 1
}

component_id = db.add_component(component_data)
```

### 4. Uploading and Parsing Quotes

**Via Web Interface:**
1. Navigate to "Supplier Database" tab
2. Go to "Upload Quote" subtab
3. Select supplier from dropdown
4. Upload PDF/Excel/CSV file
5. Click "Parse Quote"
6. Review parsed data
7. Click "Save Quote to Database"

**Supported Quote Formats:**

**Excel Format:**
```
Description         | Qty | Unit Price | Total
--------------------|-----|------------|-------
Heater 10kW        |  2  |  85,000    | 1,70,000
Fan EC 800mm       |  4  |  28,000    | 1,12,000
```

**CSV Format:**
Same structure as Excel, with comma-separated values.

**PDF Format:**
The parser automatically extracts text and identifies:
- Line items with descriptions, quantities, and prices
- Quote metadata (number, date, validity)
- Terms and conditions

### 5. Price Comparison

```python
# Compare prices for a category
comparison_df = db.get_best_value_supplier('UV LEDs')

# View with weighted scores
print(comparison_df[['supplier_name', 'price', 'total_score']])
```

**Via Web Interface:**
1. Go to "Price Comparison" subtab
2. Select component category
3. View comparison table with scores
4. See visual chart and recommendation

### 6. Procurement Recommendations

```python
# Define requirements
requirements = [
    {'category': 'Heaters', 'quantity': 2},
    {'category': 'Fans', 'quantity': 4},
    {'category': 'UV LEDs', 'quantity': 28}
]

# Get recommendation
recommendation = db.generate_procurement_recommendation(requirements)

print(f"Total Cost: ₹{recommendation['total_cost']:,.2f}")
print(f"Risk Level: {recommendation['risk_level']}")
print(f"Number of Suppliers: {recommendation['num_suppliers']}")
```

**Via Web Interface:**
1. Go to "Procurement Recommendation" subtab
2. Enter number of components required
3. Select categories and quantities
4. Click "Generate Recommendation"
5. View summary, recommendations, and risk assessment

---

## API Reference

### SupplierDatabaseManager Class

#### Initialization
```python
db = SupplierDatabaseManager(db_path='data/suppliers.db')
```

#### Supplier Methods
- `add_supplier(supplier_data: Dict) -> int`
- `get_suppliers(filters: Optional[Dict] = None) -> pd.DataFrame`
- `update_supplier(supplier_id: int, updates: Dict) -> bool`

#### Component Methods
- `add_component(component_data: Dict) -> int`
- `get_components(category: Optional[str] = None, supplier_id: Optional[int] = None) -> pd.DataFrame`
- `get_categories() -> List[str]`

#### Quote Methods
- `add_quote(quote_data: Dict, items: Optional[List[Dict]] = None) -> int`
- `add_quote_item(item_data: Dict) -> int`
- `get_quotes(supplier_id: Optional[int] = None, status: Optional[str] = None) -> pd.DataFrame`
- `get_quote_items(quote_id: int) -> pd.DataFrame`
- `validate_quote_data(quote_data: Dict) -> Tuple[bool, List[str]]`

#### Price Comparison Methods
- `compare_prices(component_list: List[str]) -> pd.DataFrame`
- `calculate_total_cost(quote_id: int, include_taxes: bool = True, tax_rate: float = 0.18) -> Dict`
- `get_best_value_supplier(component_category: str, weights: Optional[Dict] = None) -> pd.DataFrame`
- `get_price_trends(component_id: int, days: int = 90) -> pd.DataFrame`

#### Procurement Methods
- `generate_procurement_recommendation(required_components: List[Dict]) -> Dict`
- `calculate_delivery_schedule(quote_ids: List[int]) -> pd.DataFrame`

#### Utility Methods
- `export_comparison_report(comparison_data: pd.DataFrame, format: str = 'excel', output_path: str = 'data/comparison_report') -> str`
- `get_statistics() -> Dict`

---

## Quote Parser Module

### Functions

#### `parse_indian_currency(text: str) -> Optional[float]`
Parses Indian currency formats including ₹, Rs., lakhs, and crores.

**Examples:**
```python
parse_indian_currency("Rs. 1,00,000")  # Returns: 100000.0
parse_indian_currency("2.5 lakhs")      # Returns: 250000.0
parse_indian_currency("1.5 Cr")         # Returns: 15000000.0
```

#### `extract_component_prices(text: str) -> List[Dict]`
Extracts component line items with prices from text.

#### `extract_lead_times(text: str) -> Optional[int]`
Extracts lead time in days from text.

#### `extract_warranty_terms(text: str) -> Optional[int]`
Extracts warranty period in months from text.

#### `parse_pdf_quote(pdf_path: str) -> Dict`
Parses a PDF quote file.

#### `parse_excel_quote(excel_path: str, sheet_name: Optional[str] = None) -> Dict`
Parses an Excel quote file.

#### `parse_csv_quote(csv_path: str) -> Dict`
Parses a CSV quote file.

#### `auto_detect_and_parse(file_path: str) -> Dict`
Automatically detects file type and parses accordingly.

**Return Format:**
```python
{
    'success': True/False,
    'metadata': {
        'quote_number': 'Q-2024-001',
        'quote_date': '2024-01-15',
        'validity_days': 30,
        'total_cost': 500000
    },
    'items': [
        {
            'description': 'Component name',
            'quantity': 2,
            'unit_price': 85000,
            'total_price': 170000
        }
    ],
    'error': 'Error message if failed'
}
```

---

## Pre-loaded Indian Suppliers

The system comes pre-loaded with suppliers for the following categories:

### Heaters
- Watlow India Pvt Ltd
- Chromalox India
- Omega Engineering India

### Refrigeration
- Emerson Climate Technologies India
- Danfoss India Pvt Ltd
- Carrier Transicold India

### Humidifiers
- Condair India
- Carel India Pvt Ltd
- Armstrong India

### UV LEDs
- Seoul Semiconductor India
- Nichia India Pvt Ltd
- Osram India Pvt Ltd

### Fans
- ebm-papst India Pvt Ltd
- Ziehl-Abegg India
- Oriental Motor India

### Controllers
- Eurotherm India Ltd
- Yokogawa India Ltd
- Honeywell India

### Insulation
- Armacell India Pvt Ltd
- Saint-Gobain India
- Kingspan Insulation India

### Stainless Steel
- Jindal Stainless Ltd
- Tata Steel Ltd
- JSW Steel Ltd

---

## Sample Queries

### Get all suppliers in Bangalore
```python
bangalore_suppliers = db.get_suppliers({'location': 'Bangalore, Karnataka'})
```

### Find cheapest UV LED supplier
```python
uv_comparison = db.get_best_value_supplier('UV LEDs')
best_price = uv_comparison.iloc[0]
```

### Calculate project cost with multiple components
```python
requirements = [
    {'category': 'Heaters', 'quantity': 4},
    {'category': 'Refrigeration', 'quantity': 2},
    {'category': 'UV LEDs', 'quantity': 28},
    {'category': 'Controllers', 'quantity': 1}
]

recommendation = db.generate_procurement_recommendation(requirements)
print(f"Total Project Cost: ₹{recommendation['total_cost']:,.2f}")
```

### Export component catalog to Excel
```python
components = db.get_components()
export_path = db.export_comparison_report(components, format='excel')
```

---

## Best Practices

1. **Regular Database Backups:**
   - Keep periodic backups of `data/suppliers.db`
   - Export critical data to Excel/CSV

2. **Quote Parsing:**
   - Use consistent quote formats for better parsing accuracy
   - Review parsed data before saving to database
   - Use manual entry for complex quote formats

3. **Supplier Management:**
   - Update supplier ratings based on actual performance
   - Keep delivery time estimates current
   - Maintain accurate contact information

4. **Price Comparison:**
   - Customize scoring weights based on project priorities
   - Consider total cost of ownership, not just unit price
   - Factor in supplier reputation and reliability

5. **Procurement Planning:**
   - Diversify suppliers to reduce risk
   - Balance cost savings with delivery reliability
   - Maintain relationships with multiple suppliers per category

---

## Troubleshooting

### Quote Parsing Issues

**Problem:** PDF quote not parsing correctly
**Solution:**
- Ensure PDF is text-based (not scanned image)
- Try using Excel/CSV format instead
- Use manual entry if auto-parsing fails

**Problem:** Currency values not extracted
**Solution:**
- Check currency format (supports ₹, Rs., INR, lakhs, crores)
- Ensure proper spacing around values
- Manual override if needed

### Database Issues

**Problem:** Database locked error
**Solution:**
- Close other connections to database
- Restart application
- Check file permissions

**Problem:** Supplier/component not found
**Solution:**
- Verify database initialization completed
- Check filters applied
- Re-run seed data initialization if needed

---

## Testing

Run the test suite:
```bash
cd tests
python -m unittest test_supplier_database.py
```

Test coverage includes:
- Database creation and schema
- Supplier CRUD operations
- Component management
- Quote parsing and validation
- Price comparison algorithms
- Procurement recommendations
- Risk assessment
- Currency parsing

---

## Support & Contact

For issues, feature requests, or questions:
- Check this documentation first
- Review code comments in modules
- Contact: info@zenitek.com

---

## Version History

**v1.0.0** (2024-01-15)
- Initial release
- Supplier database management
- Quote parsing (PDF/Excel/CSV)
- Price comparison engine
- Procurement recommendations
- Pre-loaded Indian supplier database
