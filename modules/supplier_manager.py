"""
Supplier Database and Quote Management Module
Manages built-in supplier database and custom quote uploads
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd


@dataclass
class SupplierQuote:
    """Supplier quote information"""
    supplier_name: str
    category: str  # UV_LEDs, Chamber, Refrigeration, Controls, etc.
    product_model: str
    specification: str
    price_inr: float
    lead_time_weeks: int
    warranty_years: int
    notes: str = ""
    contact_person: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    quote_date: str = ""
    quote_valid_until: str = ""
    custom_upload: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class SupplierDatabase:
    """Manages built-in and custom supplier databases"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.builtin_db_path = os.path.join(data_dir, "suppliers_builtin.json")
        self.custom_db_path = os.path.join(data_dir, "suppliers_custom.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize databases
        self._initialize_builtin_database()
        self._load_custom_database()

    def _initialize_builtin_database(self):
        """Initialize built-in Indian supplier database"""

        builtin_suppliers = {
            "uv_leds": [
                {
                    "supplier_name": "OSRAM India",
                    "category": "UV_LEDs",
                    "product_model": "OSLON UV 3535",
                    "specification": "280-400nm, 10W per LED, 30% efficiency, IP65",
                    "price_inr": 1600000,
                    "lead_time_weeks": 12,
                    "warranty_years": 3,
                    "notes": "Premium quality, excellent uniformity, German technology",
                    "contact_person": "Rajesh Kumar",
                    "contact_email": "sales.india@osram.com",
                    "contact_phone": "+91-80-4567-8900",
                    "quote_date": "2024-01-15",
                    "quote_valid_until": "2024-04-15",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Excelitas Technologies India",
                    "category": "UV_LEDs",
                    "product_model": "UV LED Array Series 300",
                    "specification": "285-395nm, 15W per LED, 28% efficiency, IP67",
                    "price_inr": 1800000,
                    "lead_time_weeks": 14,
                    "warranty_years": 2,
                    "notes": "High power density, excellent thermal management",
                    "contact_person": "Amit Sharma",
                    "contact_email": "india.sales@excelitas.com",
                    "contact_phone": "+91-124-456-7800",
                    "quote_date": "2024-01-20",
                    "quote_valid_until": "2024-04-20",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Violumas India",
                    "category": "UV_LEDs",
                    "product_model": "VioLED Industrial UV-365",
                    "specification": "300-400nm, 12W per LED, 32% efficiency, IP66",
                    "price_inr": 1400000,
                    "lead_time_weeks": 10,
                    "warranty_years": 2,
                    "notes": "Cost-effective solution, good for budget projects",
                    "contact_person": "Priya Desai",
                    "contact_email": "sales@violumas.in",
                    "contact_phone": "+91-22-2345-6789",
                    "quote_date": "2024-02-01",
                    "quote_valid_until": "2024-05-01",
                    "custom_upload": False
                }
            ],
            "chambers": [
                {
                    "supplier_name": "HIACC Testing Technology India",
                    "category": "Chamber",
                    "product_model": "HIACC-PV-3200",
                    "specification": "3.2m×2.1m×2.2m, -45°C to +105°C, 40-95% RH, SS304 interior",
                    "price_inr": 3500000,
                    "lead_time_weeks": 16,
                    "warranty_years": 2,
                    "notes": "Complete turnkey solution, includes calibration",
                    "contact_person": "Suresh Reddy",
                    "contact_email": "sales@hiacc.in",
                    "contact_phone": "+91-40-2345-6789",
                    "quote_date": "2024-01-10",
                    "quote_valid_until": "2024-06-10",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Envisys Technologies Pvt Ltd",
                    "category": "Chamber",
                    "product_model": "ENV-PV-MASTER-3200",
                    "specification": "3.2m×2.1m×2.2m, -50°C to +110°C, 35-98% RH, SS316L interior",
                    "price_inr": 3800000,
                    "lead_time_weeks": 18,
                    "warranty_years": 3,
                    "notes": "Premium build quality, extended range, NABL calibration",
                    "contact_person": "Anil Gupta",
                    "contact_email": "sales@envisys.co.in",
                    "contact_phone": "+91-11-4567-8900",
                    "quote_date": "2024-01-25",
                    "quote_valid_until": "2024-07-25",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Testronix Instruments",
                    "category": "Chamber",
                    "product_model": "TRX-PV-3200-ECO",
                    "specification": "3.2m×2.1m×2.2m, -40°C to +100°C, 40-95% RH, SS304 interior",
                    "price_inr": 3200000,
                    "lead_time_weeks": 14,
                    "warranty_years": 2,
                    "notes": "Value for money, proven track record in solar industry",
                    "contact_person": "Vikram Singh",
                    "contact_email": "sales@testronix.in",
                    "contact_phone": "+91-124-789-0123",
                    "quote_date": "2024-02-05",
                    "quote_valid_until": "2024-08-05",
                    "custom_upload": False
                }
            ],
            "refrigeration": [
                {
                    "supplier_name": "Bitzer India",
                    "category": "Refrigeration",
                    "product_model": "BITZER Ecoline+ 4TES-12Y",
                    "specification": "12 kW cooling @ -45°C, R134a, Semi-hermetic compressor",
                    "price_inr": 800000,
                    "lead_time_weeks": 8,
                    "warranty_years": 3,
                    "notes": "Industry standard, excellent efficiency, global support",
                    "contact_person": "Mohammed Ali",
                    "contact_email": "india@bitzer.de",
                    "contact_phone": "+91-44-2345-6789",
                    "quote_date": "2024-01-18",
                    "quote_valid_until": "2024-04-18",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Copeland (Emerson) India",
                    "category": "Refrigeration",
                    "product_model": "Copeland Scroll ZF13K4E",
                    "specification": "11 kW cooling @ -45°C, R404A, Scroll compressor",
                    "price_inr": 750000,
                    "lead_time_weeks": 6,
                    "warranty_years": 2,
                    "notes": "Scroll technology, quieter operation, good efficiency",
                    "contact_person": "Sanjay Patel",
                    "contact_email": "copeland.india@emerson.com",
                    "contact_phone": "+91-20-6789-0123",
                    "quote_date": "2024-01-22",
                    "quote_valid_until": "2024-04-22",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Danfoss India",
                    "category": "Refrigeration",
                    "product_model": "Danfoss Turbocor TT300",
                    "specification": "105 kW cooling, Magnetic bearing, Oil-free, VFD integrated",
                    "price_inr": 950000,
                    "lead_time_weeks": 10,
                    "warranty_years": 3,
                    "notes": "Oil-free technology, highest efficiency, premium price",
                    "contact_person": "Lars Hansen",
                    "contact_email": "india.sales@danfoss.com",
                    "contact_phone": "+91-44-6789-1234",
                    "quote_date": "2024-02-10",
                    "quote_valid_until": "2024-05-10",
                    "custom_upload": False
                }
            ],
            "controls": [
                {
                    "supplier_name": "Siemens India",
                    "category": "Controls_PLC",
                    "product_model": "SIMATIC S7-1500 PLC + WinCC HMI",
                    "specification": "CPU 1515-2 PN, 15\" Touch Panel, TIA Portal V17",
                    "price_inr": 450000,
                    "lead_time_weeks": 6,
                    "warranty_years": 2,
                    "notes": "Industry leading, excellent support, easy programming",
                    "contact_person": "Karthik Krishnan",
                    "contact_email": "siemens.india@siemens.com",
                    "contact_phone": "+91-80-3456-7890",
                    "quote_date": "2024-01-12",
                    "quote_valid_until": "2024-04-12",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Schneider Electric India",
                    "category": "Controls_PLC",
                    "product_model": "Modicon M580 + Vijeo Citect SCADA",
                    "specification": "BMEP584040 CPU, 15\" HMI, EcoStruxure software",
                    "price_inr": 420000,
                    "lead_time_weeks": 5,
                    "warranty_years": 2,
                    "notes": "Competitive pricing, good ecosystem, cybersecurity features",
                    "contact_person": "Deepak Mehta",
                    "contact_email": "india@schneider-electric.com",
                    "contact_phone": "+91-11-2345-6789",
                    "quote_date": "2024-01-28",
                    "quote_valid_until": "2024-04-28",
                    "custom_upload": False
                }
            ],
            "sensors": [
                {
                    "supplier_name": "Vaisala India",
                    "category": "Sensors",
                    "product_model": "HMP7 Humidity/Temp Probes (Set of 9)",
                    "specification": "±1% RH, ±0.1°C accuracy, -80°C to +180°C range",
                    "price_inr": 270000,
                    "lead_time_weeks": 4,
                    "warranty_years": 2,
                    "notes": "Best-in-class accuracy, NIST traceable calibration",
                    "contact_person": "Naveen Kumar",
                    "contact_email": "sales.india@vaisala.com",
                    "contact_phone": "+91-80-4123-4567",
                    "quote_date": "2024-01-15",
                    "quote_valid_until": "2024-04-15",
                    "custom_upload": False
                },
                {
                    "supplier_name": "Rotronic India",
                    "category": "Sensors",
                    "product_model": "HC2A-S Probe Set (9 probes)",
                    "specification": "±0.8% RH, ±0.1°C accuracy, -100°C to +200°C range",
                    "price_inr": 240000,
                    "lead_time_weeks": 3,
                    "warranty_years": 2,
                    "notes": "Swiss quality, excellent long-term stability",
                    "contact_person": "Rajeev Nair",
                    "contact_email": "india@rotronic.com",
                    "contact_phone": "+91-22-6789-0123",
                    "quote_date": "2024-02-01",
                    "quote_valid_until": "2024-05-01",
                    "custom_upload": False
                }
            ]
        }

        # Save to file
        with open(self.builtin_db_path, 'w') as f:
            json.dump(builtin_suppliers, f, indent=2)

    def _load_custom_database(self):
        """Load custom uploaded quotes"""
        if os.path.exists(self.custom_db_path):
            with open(self.custom_db_path, 'r') as f:
                self.custom_db = json.load(f)
        else:
            self.custom_db = {}
            self._save_custom_database()

    def _save_custom_database(self):
        """Save custom database to file"""
        with open(self.custom_db_path, 'w') as f:
            json.dump(self.custom_db, f, indent=2)

    def get_builtin_suppliers(self) -> Dict:
        """Get all built-in suppliers"""
        with open(self.builtin_db_path, 'r') as f:
            return json.load(f)

    def get_custom_suppliers(self) -> Dict:
        """Get all custom suppliers"""
        return self.custom_db

    def get_all_suppliers(self) -> Dict:
        """Get combined built-in and custom suppliers"""
        builtin = self.get_builtin_suppliers()
        custom = self.get_custom_suppliers()

        # Merge dictionaries
        all_suppliers = builtin.copy()
        for category, quotes in custom.items():
            if category in all_suppliers:
                all_suppliers[category].extend(quotes)
            else:
                all_suppliers[category] = quotes

        return all_suppliers

    def add_custom_quote(self, quote: SupplierQuote) -> bool:
        """
        Add a custom supplier quote

        Args:
            quote: SupplierQuote object

        Returns:
            Success status
        """
        try:
            quote.custom_upload = True
            category = quote.category

            if category not in self.custom_db:
                self.custom_db[category] = []

            self.custom_db[category].append(quote.to_dict())
            self._save_custom_database()
            return True
        except Exception as e:
            print(f"Error adding custom quote: {e}")
            return False

    def remove_custom_quote(self, supplier_name: str, product_model: str) -> bool:
        """Remove a custom quote"""
        try:
            for category, quotes in self.custom_db.items():
                self.custom_db[category] = [
                    q for q in quotes
                    if not (q['supplier_name'] == supplier_name and
                           q['product_model'] == product_model)
                ]
            self._save_custom_database()
            return True
        except Exception as e:
            print(f"Error removing custom quote: {e}")
            return False

    def get_quotes_by_category(self, category: str) -> List[Dict]:
        """Get all quotes for a specific category"""
        all_suppliers = self.get_all_suppliers()
        return all_suppliers.get(category, [])

    def get_cheapest_quote(self, category: str) -> Optional[Dict]:
        """Get the cheapest quote for a category"""
        quotes = self.get_quotes_by_category(category)
        if not quotes:
            return None
        return min(quotes, key=lambda x: x['price_inr'])

    def get_fastest_delivery(self, category: str) -> Optional[Dict]:
        """Get quote with fastest delivery"""
        quotes = self.get_quotes_by_category(category)
        if not quotes:
            return None
        return min(quotes, key=lambda x: x['lead_time_weeks'])

    def compare_quotes(self, category: str) -> pd.DataFrame:
        """
        Compare all quotes in a category

        Args:
            category: Category to compare

        Returns:
            DataFrame with comparison
        """
        quotes = self.get_quotes_by_category(category)
        if not quotes:
            return pd.DataFrame()

        df = pd.DataFrame(quotes)

        # Select relevant columns for comparison
        comparison_cols = [
            'supplier_name', 'product_model', 'specification',
            'price_inr', 'lead_time_weeks', 'warranty_years',
            'custom_upload'
        ]

        available_cols = [col for col in comparison_cols if col in df.columns]
        df_comparison = df[available_cols].copy()

        # Add derived columns
        if 'price_inr' in df_comparison.columns:
            df_comparison['price_lakhs'] = df_comparison['price_inr'] / 100000

        # Sort by price
        if 'price_inr' in df_comparison.columns:
            df_comparison = df_comparison.sort_values('price_inr')

        return df_comparison

    def generate_bom(self, selected_quotes: Dict[str, str]) -> pd.DataFrame:
        """
        Generate Bill of Materials from selected quotes

        Args:
            selected_quotes: Dict of {category: product_model}

        Returns:
            DataFrame with BOM
        """
        bom_items = []
        all_suppliers = self.get_all_suppliers()

        for category, product_model in selected_quotes.items():
            if category in all_suppliers:
                for quote in all_suppliers[category]:
                    if quote['product_model'] == product_model:
                        bom_items.append({
                            'Category': category,
                            'Supplier': quote['supplier_name'],
                            'Product Model': quote['product_model'],
                            'Specification': quote['specification'],
                            'Price (₹)': quote['price_inr'],
                            'Price (Lakhs)': quote['price_inr'] / 100000,
                            'Lead Time (weeks)': quote['lead_time_weeks'],
                            'Warranty (years)': quote['warranty_years'],
                            'Contact': quote.get('contact_person', 'N/A')
                        })

        bom_df = pd.DataFrame(bom_items)

        if not bom_df.empty:
            # Add totals row
            total_row = {
                'Category': 'TOTAL',
                'Supplier': '',
                'Product Model': '',
                'Specification': '',
                'Price (₹)': bom_df['Price (₹)'].sum(),
                'Price (Lakhs)': bom_df['Price (Lakhs)'].sum(),
                'Lead Time (weeks)': bom_df['Lead Time (weeks)'].max(),
                'Warranty (years)': '',
                'Contact': ''
            }
            bom_df = pd.concat([bom_df, pd.DataFrame([total_row])], ignore_index=True)

        return bom_df


def parse_uploaded_quote_excel(file) -> Optional[List[SupplierQuote]]:
    """
    Parse uploaded Excel file with quote information

    Expected columns:
    - Supplier Name
    - Category
    - Product Model
    - Specification
    - Price (INR)
    - Lead Time (weeks)
    - Warranty (years)
    - Notes
    - Contact Person
    - Contact Email
    - Contact Phone

    Args:
        file: Uploaded file object

    Returns:
        List of SupplierQuote objects
    """
    try:
        df = pd.read_excel(file)

        quotes = []
        for _, row in df.iterrows():
            quote = SupplierQuote(
                supplier_name=str(row.get('Supplier Name', '')),
                category=str(row.get('Category', '')),
                product_model=str(row.get('Product Model', '')),
                specification=str(row.get('Specification', '')),
                price_inr=float(row.get('Price (INR)', 0)),
                lead_time_weeks=int(row.get('Lead Time (weeks)', 0)),
                warranty_years=int(row.get('Warranty (years)', 0)),
                notes=str(row.get('Notes', '')),
                contact_person=str(row.get('Contact Person', '')),
                contact_email=str(row.get('Contact Email', '')),
                contact_phone=str(row.get('Contact Phone', '')),
                quote_date=datetime.now().strftime('%Y-%m-%d'),
                quote_valid_until='',
                custom_upload=True
            )
            quotes.append(quote)

        return quotes

    except Exception as e:
        print(f"Error parsing Excel file: {e}")
        return None


def parse_uploaded_quote_csv(file) -> Optional[List[SupplierQuote]]:
    """Parse uploaded CSV file with quote information"""
    try:
        df = pd.read_csv(file)

        quotes = []
        for _, row in df.iterrows():
            quote = SupplierQuote(
                supplier_name=str(row.get('Supplier Name', '')),
                category=str(row.get('Category', '')),
                product_model=str(row.get('Product Model', '')),
                specification=str(row.get('Specification', '')),
                price_inr=float(row.get('Price (INR)', 0)),
                lead_time_weeks=int(row.get('Lead Time (weeks)', 0)),
                warranty_years=int(row.get('Warranty (years)', 0)),
                notes=str(row.get('Notes', '')),
                contact_person=str(row.get('Contact Person', '')),
                contact_email=str(row.get('Contact Email', '')),
                contact_phone=str(row.get('Contact Phone', '')),
                quote_date=datetime.now().strftime('%Y-%m-%d'),
                quote_valid_until='',
                custom_upload=True
            )
            quotes.append(quote)

        return quotes

    except Exception as e:
        print(f"Error parsing CSV file: {e}")
        return None
