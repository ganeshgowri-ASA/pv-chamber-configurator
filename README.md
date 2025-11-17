# PV Chamber Configurator

Comprehensive UV+TC+HF+DH Combined Environmental Test Chamber Configurator & Quote Generation System for PV Module Testing with CFD Simulations, Virtual HMI, Supplier Database, and Business Analysis.

## Features

### Phase 4: Supplier Database Manager + Quote Comparison System ✅

**NEW in this release:**

- **Comprehensive Supplier Database**
  - 24 pre-loaded Indian suppliers for PV chamber components
  - Supplier ratings, delivery times, payment terms tracking
  - Contact information and location management

- **Automated Quote Parsing**
  - Multi-format support: PDF, Excel (.xlsx, .xls), CSV
  - Automated text extraction and price parsing
  - Support for Indian currency formats (₹, Rs., lakhs, crores)
  - Quote validation and completeness checking

- **Intelligent Price Comparison**
  - Component-wise price comparison across suppliers
  - Weighted scoring system (price, lead time, rating, warranty, payment terms)
  - Visual comparison charts and dashboards
  - Best value recommendations

- **Procurement Recommendation Engine**
  - Optimal supplier selection algorithm
  - Total cost calculation with taxes and delivery
  - Risk assessment (supplier diversification analysis)
  - Delivery schedule optimization

- **Component Categories:**
  - Heaters (Watlow, Chromalox, Omega)
  - Refrigeration (Emerson, Danfoss, Carrier)
  - Humidifiers (Condair, Carel, Armstrong)
  - UV LEDs (Seoul Semi, Nichia, Osram)
  - Fans (ebm-papst, Ziehl-Abegg, Oriental Motor)
  - Controllers (Eurotherm, Yokogawa, Honeywell)
  - Insulation (Armacell, Saint-Gobain, Kingspan)
  - Stainless Steel (Jindal, Tata, JSW)

### Other Features

- Chamber Design & Specification
- UV System Configuration
- Quote Generator
- Business Analysis & TCO
- Virtual HMI Interface

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

- streamlit >= 1.28.0
- pandas >= 2.1.0
- plotly >= 5.17.0
- openpyxl >= 3.1.0
- PyPDF2 >= 3.0.0
- pdfplumber >= 0.10.0
- sqlalchemy >= 2.0.0

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/ganeshgowri-ASA/pv-chamber-configurator.git
   cd pv-chamber-configurator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the app**
   - Open browser at `http://localhost:8501`
   - Navigate to "Supplier Database" tab

## Usage

### Supplier Database

1. **View Suppliers**
   - Navigate to "Supplier Database" → "Suppliers"
   - Browse 24 pre-loaded Indian suppliers
   - View ratings, delivery times, and contact info

2. **Upload Quote**
   - Go to "Upload Quote" subtab
   - Select supplier from dropdown
   - Upload PDF/Excel/CSV quote file
   - Click "Parse Quote" to auto-extract data
   - Review and save to database

3. **Compare Prices**
   - Go to "Price Comparison" subtab
   - Select component category
   - View comparison table with weighted scores
   - See visual charts and best value recommendation

4. **Get Procurement Recommendations**
   - Go to "Procurement Recommendation" subtab
   - Define your component requirements
   - Click "Generate Recommendation"
   - View optimal supplier selection, costs, and risk assessment

### Sample Quote Format (CSV)

```csv
Description,Quantity,Unit Price,Total
Finned Tubular Heater 10kW,2,85000,170000
EC Axial Fan 800mm,4,28000,112000
UV-A LED Module 100W,28,42000,1176000
```

## Database Schema

The system uses SQLite with the following tables:

- **suppliers**: Supplier information, ratings, delivery times
- **components**: Component catalog with prices, specs, warranties
- **quotes**: Quote metadata and totals
- **quote_items**: Individual line items in quotes
- **price_history**: Historical pricing data for trend analysis

## Testing

Run the test suite:

```bash
python -m unittest tests/test_supplier_database.py
```

Test coverage includes:
- Database CRUD operations
- Quote parsing (PDF/Excel/CSV)
- Price comparison algorithms
- Procurement recommendations
- Currency parsing
- Risk assessment

## Documentation

Detailed documentation available in:
- **SUPPLIER_DATABASE.md** - Complete user guide and API reference
- Code comments in modules
- Inline help in the Streamlit interface

## Project Structure

```
pv-chamber-configurator/
├── app.py                          # Main Streamlit application
├── modules/
│   ├── __init__.py
│   ├── supplier_database.py        # Database manager class
│   ├── quote_parser.py             # Quote parsing utilities
│   └── init_database.py            # Database initialization
├── data/
│   ├── suppliers.db                # SQLite database (auto-created)
│   ├── indian_suppliers_seed.json  # Pre-loaded supplier data
│   └── sample_quote.csv            # Sample quote file
├── tests/
│   └── test_supplier_database.py   # Test suite
├── requirements.txt                # Python dependencies
├── SUPPLIER_DATABASE.md            # Detailed documentation
└── README.md                       # This file
```

## API Reference

### SupplierDatabaseManager

```python
from modules.supplier_database import SupplierDatabaseManager

# Initialize
db = SupplierDatabaseManager('data/suppliers.db')

# Get suppliers
suppliers = db.get_suppliers()

# Compare prices
comparison = db.get_best_value_supplier('UV LEDs')

# Get procurement recommendation
requirements = [
    {'category': 'Heaters', 'quantity': 2},
    {'category': 'Fans', 'quantity': 4}
]
recommendation = db.generate_procurement_recommendation(requirements)
```

### Quote Parser

```python
from modules.quote_parser import auto_detect_and_parse

# Parse quote file
result = auto_detect_and_parse('quote.pdf')

if result['success']:
    print(f"Found {len(result['items'])} items")
    print(f"Total: ₹{result['metadata']['total_cost']:,.2f}")
```

## Contributing

This is a commercial project for Zenitek Solutions. For feature requests or issues, contact: info@zenitek.com

## Version History

**v1.0.0** (2024-01-15) - Phase 4 Complete
- Supplier database with 24 Indian suppliers
- Quote parsing (PDF/Excel/CSV)
- Price comparison engine
- Procurement recommendations
- 32 pre-loaded components across 10 categories

## License

See LICENSE file for details.

## Contact

**Zenitek Solutions**
- Location: Tamil Nadu, India
- Email: info@zenitek.com
- Website: www.zenitek.com

---

*White-labeled PV Chamber Configurator v1.0*
