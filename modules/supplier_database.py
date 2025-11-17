"""
Supplier Database Manager for PV Chamber Configurator
Handles supplier data, components, quotes, and price comparison.
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os


class SupplierDatabaseManager:
    """
    Comprehensive supplier database manager with quote parsing,
    price comparison, and procurement recommendation capabilities.
    """

    def __init__(self, db_path: str = 'data/suppliers.db'):
        """
        Initialize the supplier database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self.create_database()

    def _connect(self):
        """Establish database connection."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_database(self):
        """Create all required database tables if they don't exist."""
        # Suppliers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                email TEXT,
                location TEXT,
                rating REAL DEFAULT 0.0,
                avg_delivery_days INTEGER DEFAULT 30,
                payment_terms TEXT DEFAULT 'Net 30',
                currency TEXT DEFAULT 'INR',
                website TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Components table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                specification TEXT,
                supplier_id INTEGER,
                price REAL NOT NULL,
                lead_time_days INTEGER DEFAULT 30,
                warranty_months INTEGER DEFAULT 12,
                moq INTEGER DEFAULT 1,
                unit TEXT DEFAULT 'piece',
                stock_available BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')

        # Quotes table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER NOT NULL,
                quote_number TEXT,
                quote_date DATE NOT NULL,
                validity_days INTEGER DEFAULT 30,
                total_cost REAL,
                tax_amount REAL DEFAULT 0,
                delivery_cost REAL DEFAULT 0,
                uploaded_file TEXT,
                parsed_data TEXT,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')

        # Quote items (linking quotes to components)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quote_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id INTEGER NOT NULL,
                component_id INTEGER,
                description TEXT,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                lead_time_days INTEGER,
                FOREIGN KEY (quote_id) REFERENCES quotes(id),
                FOREIGN KEY (component_id) REFERENCES components(id)
            )
        ''')

        # Price history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component_id INTEGER NOT NULL,
                price REAL NOT NULL,
                date DATE NOT NULL,
                supplier_id INTEGER NOT NULL,
                quote_id INTEGER,
                FOREIGN KEY (component_id) REFERENCES components(id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
                FOREIGN KEY (quote_id) REFERENCES quotes(id)
            )
        ''')

        self.conn.commit()

    # ==================== Supplier Operations ====================

    def add_supplier(self, supplier_data: Dict) -> int:
        """
        Add a new supplier to the database.

        Args:
            supplier_data: Dictionary with supplier information

        Returns:
            ID of newly created supplier
        """
        required_fields = ['name']
        for field in required_fields:
            if field not in supplier_data:
                raise ValueError(f"Missing required field: {field}")

        fields = ', '.join(supplier_data.keys())
        placeholders = ', '.join(['?' for _ in supplier_data])

        query = f"INSERT INTO suppliers ({fields}) VALUES ({placeholders})"
        self.cursor.execute(query, list(supplier_data.values()))
        self.conn.commit()

        return self.cursor.lastrowid

    def get_suppliers(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """
        Retrieve suppliers with optional filters.

        Args:
            filters: Dictionary of filter conditions

        Returns:
            DataFrame of suppliers
        """
        query = "SELECT * FROM suppliers"
        params = []

        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY rating DESC, name ASC"

        return pd.read_sql_query(query, self.conn, params=params)

    def update_supplier(self, supplier_id: int, updates: Dict) -> bool:
        """Update supplier information."""
        if not updates:
            return False

        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE suppliers SET {set_clause} WHERE id = ?"

        params = list(updates.values()) + [supplier_id]
        self.cursor.execute(query, params)
        self.conn.commit()

        return self.cursor.rowcount > 0

    # ==================== Component Operations ====================

    def add_component(self, component_data: Dict) -> int:
        """
        Add a new component to the database.

        Args:
            component_data: Dictionary with component information

        Returns:
            ID of newly created component
        """
        required_fields = ['category', 'name', 'supplier_id', 'price']
        for field in required_fields:
            if field not in component_data:
                raise ValueError(f"Missing required field: {field}")

        fields = ', '.join(component_data.keys())
        placeholders = ', '.join(['?' for _ in component_data])

        query = f"INSERT INTO components ({fields}) VALUES ({placeholders})"
        self.cursor.execute(query, list(component_data.values()))
        self.conn.commit()

        # Add to price history
        component_id = self.cursor.lastrowid
        self._add_price_history(
            component_id,
            component_data['price'],
            component_data['supplier_id']
        )

        return component_id

    def get_components(self, category: Optional[str] = None,
                       supplier_id: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieve components with optional filters.

        Args:
            category: Filter by component category
            supplier_id: Filter by supplier ID

        Returns:
            DataFrame of components with supplier info
        """
        query = """
            SELECT c.*, s.name as supplier_name, s.rating as supplier_rating,
                   s.location as supplier_location
            FROM components c
            LEFT JOIN suppliers s ON c.supplier_id = s.id
            WHERE 1=1
        """
        params = []

        if category:
            query += " AND c.category = ?"
            params.append(category)

        if supplier_id:
            query += " AND c.supplier_id = ?"
            params.append(supplier_id)

        query += " ORDER BY c.category, c.name"

        return pd.read_sql_query(query, self.conn, params=params)

    def _add_price_history(self, component_id: int, price: float,
                          supplier_id: int, quote_id: Optional[int] = None):
        """Add entry to price history."""
        self.cursor.execute('''
            INSERT INTO price_history (component_id, price, date, supplier_id, quote_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (component_id, price, datetime.now().date(), supplier_id, quote_id))
        self.conn.commit()

    # ==================== Quote Operations ====================

    def add_quote(self, quote_data: Dict, items: Optional[List[Dict]] = None) -> int:
        """
        Add a new quote to the database.

        Args:
            quote_data: Dictionary with quote information
            items: List of quote items

        Returns:
            ID of newly created quote
        """
        required_fields = ['supplier_id', 'quote_date']
        for field in required_fields:
            if field not in quote_data:
                raise ValueError(f"Missing required field: {field}")

        # Convert parsed_data to JSON if it's a dict
        if 'parsed_data' in quote_data and isinstance(quote_data['parsed_data'], dict):
            quote_data['parsed_data'] = json.dumps(quote_data['parsed_data'])

        fields = ', '.join(quote_data.keys())
        placeholders = ', '.join(['?' for _ in quote_data])

        query = f"INSERT INTO quotes ({fields}) VALUES ({placeholders})"
        self.cursor.execute(query, list(quote_data.values()))
        quote_id = self.cursor.lastrowid

        # Add quote items
        if items:
            for item in items:
                item['quote_id'] = quote_id
                self.add_quote_item(item)

        self.conn.commit()
        return quote_id

    def add_quote_item(self, item_data: Dict) -> int:
        """Add an item to a quote."""
        required_fields = ['quote_id', 'description', 'quantity', 'unit_price', 'total_price']
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Missing required field: {field}")

        fields = ', '.join(item_data.keys())
        placeholders = ', '.join(['?' for _ in item_data])

        query = f"INSERT INTO quote_items ({fields}) VALUES ({placeholders})"
        self.cursor.execute(query, list(item_data.values()))
        self.conn.commit()

        return self.cursor.lastrowid

    def get_quotes(self, supplier_id: Optional[int] = None,
                   status: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve quotes with optional filters.

        Args:
            supplier_id: Filter by supplier ID
            status: Filter by quote status

        Returns:
            DataFrame of quotes
        """
        query = """
            SELECT q.*, s.name as supplier_name, s.location as supplier_location
            FROM quotes q
            LEFT JOIN suppliers s ON q.supplier_id = s.id
            WHERE 1=1
        """
        params = []

        if supplier_id:
            query += " AND q.supplier_id = ?"
            params.append(supplier_id)

        if status:
            query += " AND q.status = ?"
            params.append(status)

        query += " ORDER BY q.quote_date DESC"

        return pd.read_sql_query(query, self.conn, params=params)

    def get_quote_items(self, quote_id: int) -> pd.DataFrame:
        """Get all items for a specific quote."""
        query = """
            SELECT qi.*, c.name as component_name, c.category
            FROM quote_items qi
            LEFT JOIN components c ON qi.component_id = c.id
            WHERE qi.quote_id = ?
            ORDER BY qi.id
        """
        return pd.read_sql_query(query, self.conn, params=[quote_id])

    def validate_quote_data(self, quote_data: Dict) -> Tuple[bool, List[str]]:
        """
        Validate quote data for completeness.

        Args:
            quote_data: Quote data to validate

        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []

        # Check required fields
        required = ['supplier_id', 'quote_date']
        for field in required:
            if field not in quote_data or not quote_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate supplier exists
        if 'supplier_id' in quote_data:
            self.cursor.execute("SELECT id FROM suppliers WHERE id = ?",
                              (quote_data['supplier_id'],))
            if not self.cursor.fetchone():
                errors.append(f"Invalid supplier_id: {quote_data['supplier_id']}")

        # Validate dates
        if 'quote_date' in quote_data:
            try:
                if isinstance(quote_data['quote_date'], str):
                    datetime.strptime(quote_data['quote_date'], '%Y-%m-%d')
            except ValueError:
                errors.append("Invalid quote_date format (use YYYY-MM-DD)")

        # Validate numeric fields
        numeric_fields = ['total_cost', 'tax_amount', 'delivery_cost']
        for field in numeric_fields:
            if field in quote_data and quote_data[field] is not None:
                try:
                    float(quote_data[field])
                except (ValueError, TypeError):
                    errors.append(f"Invalid {field}: must be numeric")

        return len(errors) == 0, errors

    # ==================== Price Comparison ====================

    def compare_prices(self, component_list: List[str]) -> pd.DataFrame:
        """
        Compare prices across suppliers for a list of components.

        Args:
            component_list: List of component names or categories

        Returns:
            DataFrame with price comparison
        """
        placeholders = ','.join(['?' for _ in component_list])
        query = f"""
            SELECT
                c.category,
                c.name,
                c.specification,
                s.name as supplier_name,
                c.price,
                c.lead_time_days,
                c.warranty_months,
                s.rating as supplier_rating,
                s.location,
                s.payment_terms
            FROM components c
            JOIN suppliers s ON c.supplier_id = s.id
            WHERE c.name IN ({placeholders}) OR c.category IN ({placeholders})
            ORDER BY c.category, c.name, c.price
        """
        params = component_list + component_list

        return pd.read_sql_query(query, self.conn, params=params)

    def calculate_total_cost(self, quote_id: int, include_taxes: bool = True,
                           tax_rate: float = 0.18) -> Dict:
        """
        Calculate total cost for a quote.

        Args:
            quote_id: Quote ID
            include_taxes: Whether to include tax calculation
            tax_rate: GST rate (default 18%)

        Returns:
            Dictionary with cost breakdown
        """
        # Get quote info
        quote = pd.read_sql_query(
            "SELECT * FROM quotes WHERE id = ?",
            self.conn,
            params=[quote_id]
        )

        if quote.empty:
            raise ValueError(f"Quote {quote_id} not found")

        # Get quote items
        items = pd.read_sql_query(
            "SELECT * FROM quote_items WHERE quote_id = ?",
            self.conn,
            params=[quote_id]
        )

        subtotal = items['total_price'].sum()

        # Get stored values or calculate
        delivery_cost = quote['delivery_cost'].iloc[0] or 0

        if include_taxes:
            tax_amount = quote['tax_amount'].iloc[0]
            if tax_amount is None or tax_amount == 0:
                tax_amount = subtotal * tax_rate
        else:
            tax_amount = 0

        total = subtotal + delivery_cost + tax_amount

        return {
            'quote_id': quote_id,
            'subtotal': subtotal,
            'delivery_cost': delivery_cost,
            'tax_amount': tax_amount,
            'tax_rate': tax_rate if include_taxes else 0,
            'total_cost': total,
            'currency': 'INR',
            'num_items': len(items)
        }

    def get_best_value_supplier(self, component_category: str,
                               weights: Optional[Dict] = None) -> pd.DataFrame:
        """
        Get best value supplier for a component category using weighted scoring.

        Args:
            component_category: Category to analyze
            weights: Custom weights for scoring (price, lead_time, rating, warranty, payment_terms)

        Returns:
            DataFrame with scored suppliers
        """
        # Default weights
        if weights is None:
            weights = {
                'price': 0.30,
                'lead_time': 0.25,
                'rating': 0.20,
                'warranty': 0.15,
                'payment_terms': 0.10
            }

        # Get components in category
        df = pd.read_sql_query("""
            SELECT
                c.*,
                s.name as supplier_name,
                s.rating,
                s.avg_delivery_days,
                s.payment_terms,
                s.location
            FROM components c
            JOIN suppliers s ON c.supplier_id = s.id
            WHERE c.category = ?
            ORDER BY c.price
        """, self.conn, params=[component_category])

        if df.empty:
            return df

        # Normalize and score
        # Price score (lower is better, so invert)
        max_price = df['price'].max()
        min_price = df['price'].min()
        if max_price > min_price:
            df['price_score'] = ((max_price - df['price']) / (max_price - min_price)) * 100
        else:
            df['price_score'] = 100

        # Lead time score (lower is better, so invert)
        max_lead = df['lead_time_days'].max()
        min_lead = df['lead_time_days'].min()
        if max_lead > min_lead:
            df['lead_time_score'] = ((max_lead - df['lead_time_days']) / (max_lead - min_lead)) * 100
        else:
            df['lead_time_score'] = 100

        # Rating score (higher is better)
        df['rating_score'] = (df['rating'] / 5.0) * 100

        # Warranty score (higher is better)
        max_warranty = df['warranty_months'].max()
        if max_warranty > 0:
            df['warranty_score'] = (df['warranty_months'] / max_warranty) * 100
        else:
            df['warranty_score'] = 0

        # Payment terms score (simple mapping)
        payment_scores = {
            'Net 15': 70,
            'Net 30': 85,
            'Net 45': 90,
            'Net 60': 100,
            '50% Advance': 60
        }
        df['payment_score'] = df['payment_terms'].map(payment_scores).fillna(75)

        # Calculate total weighted score
        df['total_score'] = (
            df['price_score'] * weights['price'] +
            df['lead_time_score'] * weights['lead_time'] +
            df['rating_score'] * weights['rating'] +
            df['warranty_score'] * weights['warranty'] +
            df['payment_score'] * weights['payment_terms']
        )

        # Sort by total score
        df = df.sort_values('total_score', ascending=False)

        return df

    def get_price_trends(self, component_id: int, days: int = 90) -> pd.DataFrame:
        """
        Get price trends for a component over time.

        Args:
            component_id: Component ID
            days: Number of days to look back

        Returns:
            DataFrame with price history
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).date()

        query = """
            SELECT
                ph.*,
                s.name as supplier_name,
                c.name as component_name
            FROM price_history ph
            JOIN suppliers s ON ph.supplier_id = s.id
            JOIN components c ON ph.component_id = c.id
            WHERE ph.component_id = ? AND ph.date >= ?
            ORDER BY ph.date DESC
        """

        return pd.read_sql_query(query, self.conn,
                                params=[component_id, cutoff_date])

    # ==================== Procurement Recommendation ====================

    def generate_procurement_recommendation(self,
                                           required_components: List[Dict]) -> Dict:
        """
        Generate procurement recommendation with optimal supplier selection.

        Args:
            required_components: List of dicts with 'category', 'name', 'quantity'

        Returns:
            Dictionary with recommendation details
        """
        recommendations = []
        total_cost = 0
        max_lead_time = 0
        supplier_counts = {}

        for req in required_components:
            category = req.get('category')
            name = req.get('name')
            quantity = req.get('quantity', 1)

            # Get best value supplier for this component
            if category:
                best_suppliers = self.get_best_value_supplier(category)
            else:
                # Search by name
                best_suppliers = pd.read_sql_query("""
                    SELECT c.*, s.name as supplier_name, s.rating
                    FROM components c
                    JOIN suppliers s ON c.supplier_id = s.id
                    WHERE c.name LIKE ?
                    ORDER BY c.price
                """, self.conn, params=[f"%{name}%"])

            if not best_suppliers.empty:
                best = best_suppliers.iloc[0]

                component_cost = best['price'] * quantity
                total_cost += component_cost

                if best['lead_time_days'] > max_lead_time:
                    max_lead_time = best['lead_time_days']

                supplier_name = best['supplier_name']
                supplier_counts[supplier_name] = supplier_counts.get(supplier_name, 0) + 1

                recommendations.append({
                    'component': best['name'],
                    'category': best['category'],
                    'supplier': supplier_name,
                    'quantity': quantity,
                    'unit_price': best['price'],
                    'total_price': component_cost,
                    'lead_time_days': best['lead_time_days'],
                    'warranty_months': best['warranty_months'],
                    'rating': best['rating']
                })
            else:
                recommendations.append({
                    'component': name or category,
                    'category': category or 'Unknown',
                    'supplier': 'NOT FOUND',
                    'quantity': quantity,
                    'unit_price': 0,
                    'total_price': 0,
                    'lead_time_days': 0,
                    'warranty_months': 0,
                    'rating': 0
                })

        # Risk assessment
        num_suppliers = len(supplier_counts)
        risk_level = "Low" if num_suppliers >= 3 else "Medium" if num_suppliers == 2 else "High"

        return {
            'recommendations': recommendations,
            'total_cost': total_cost,
            'max_lead_time_days': max_lead_time,
            'num_suppliers': num_suppliers,
            'supplier_distribution': supplier_counts,
            'risk_level': risk_level,
            'currency': 'INR'
        }

    def calculate_delivery_schedule(self, quote_ids: List[int]) -> pd.DataFrame:
        """
        Calculate delivery schedule for multiple quotes.

        Args:
            quote_ids: List of quote IDs

        Returns:
            DataFrame with delivery schedule
        """
        placeholders = ','.join(['?' for _ in quote_ids])
        query = f"""
            SELECT
                q.id as quote_id,
                q.quote_number,
                s.name as supplier_name,
                s.avg_delivery_days,
                q.quote_date,
                qi.description,
                qi.lead_time_days,
                qi.quantity
            FROM quotes q
            JOIN suppliers s ON q.supplier_id = s.id
            JOIN quote_items qi ON q.id = qi.quote_id
            WHERE q.id IN ({placeholders})
            ORDER BY qi.lead_time_days DESC, q.quote_date
        """

        df = pd.read_sql_query(query, self.conn, params=quote_ids)

        if not df.empty:
            # Calculate estimated delivery date
            df['estimated_delivery_date'] = pd.to_datetime(df['quote_date']) + \
                pd.to_timedelta(df['lead_time_days'].fillna(df['avg_delivery_days']), unit='D')

        return df

    def export_comparison_report(self, comparison_data: pd.DataFrame,
                                format: str = 'excel',
                                output_path: str = 'data/comparison_report') -> str:
        """
        Export price comparison report.

        Args:
            comparison_data: DataFrame with comparison data
            format: Output format ('excel' or 'csv')
            output_path: Output file path (without extension)

        Returns:
            Path to exported file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if format == 'excel':
            output_file = f"{output_path}.xlsx"
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                comparison_data.to_excel(writer, sheet_name='Price Comparison', index=False)
        elif format == 'csv':
            output_file = f"{output_path}.csv"
            comparison_data.to_csv(output_file, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return output_file

    # ==================== Utility Methods ====================

    def get_categories(self) -> List[str]:
        """Get all unique component categories."""
        self.cursor.execute("SELECT DISTINCT category FROM components ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """Get database statistics."""
        stats = {}

        self.cursor.execute("SELECT COUNT(*) FROM suppliers")
        stats['total_suppliers'] = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM components")
        stats['total_components'] = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM quotes")
        stats['total_quotes'] = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT AVG(rating) FROM suppliers")
        stats['avg_supplier_rating'] = self.cursor.fetchone()[0] or 0

        self.cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM components
            GROUP BY category
            ORDER BY count DESC
        """)
        stats['components_by_category'] = dict(self.cursor.fetchall())

        return stats

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close()
