"""
Customer Database Module for PV Chamber Configurator
Customer profile management and history tracking
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class CustomerDatabase:
    """
    Customer Database Management

    Features:
    - Customer profile management
    - Contact history tracking
    - Quote history per customer
    - Export customer list
    """

    def __init__(self, db_path: str = "data/customers.db"):
        """
        Initialize Customer Database

        Args:
            db_path: Path to customer database
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize customer database with required tables"""
        os.makedirs('data', exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                address TEXT,
                city TEXT,
                state TEXT,
                country TEXT DEFAULT 'India',
                postal_code TEXT,
                gstin TEXT,
                pan TEXT,
                contact_person TEXT,
                designation TEXT,
                industry TEXT,
                customer_type TEXT DEFAULT 'prospect',
                status TEXT DEFAULT 'active',
                credit_limit REAL DEFAULT 0,
                payment_terms TEXT DEFAULT '100% advance',
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Contact history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                contact_type TEXT NOT NULL,
                subject TEXT,
                notes TEXT,
                contacted_by TEXT,
                contact_date TEXT NOT NULL,
                follow_up_required BOOLEAN DEFAULT 0,
                follow_up_date TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        ''')

        # Customer tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    def add_customer(self, customer_data: Dict) -> int:
        """
        Add new customer

        Args:
            customer_data: Customer information dictionary

        Returns:
            Customer ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO customers (
                name, company, email, phone, address,
                city, state, country, postal_code,
                gstin, pan, contact_person, designation,
                industry, customer_type, status,
                credit_limit, payment_terms, notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_data['name'],
            customer_data.get('company', ''),
            customer_data['email'],
            customer_data.get('phone', ''),
            customer_data.get('address', ''),
            customer_data.get('city', ''),
            customer_data.get('state', ''),
            customer_data.get('country', 'India'),
            customer_data.get('postal_code', ''),
            customer_data.get('gstin', ''),
            customer_data.get('pan', ''),
            customer_data.get('contact_person', ''),
            customer_data.get('designation', ''),
            customer_data.get('industry', ''),
            customer_data.get('customer_type', 'prospect'),
            customer_data.get('status', 'active'),
            customer_data.get('credit_limit', 0),
            customer_data.get('payment_terms', '100% advance'),
            customer_data.get('notes', ''),
            now,
            now
        ))

        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return customer_id

    def get_customer(self, customer_id: int) -> Optional[Dict]:
        """
        Get customer by ID

        Args:
            customer_id: Customer ID

        Returns:
            Customer dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return dict(row)

    def get_customer_by_email(self, email: str) -> Optional[Dict]:
        """
        Get customer by email

        Args:
            email: Customer email

        Returns:
            Customer dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM customers WHERE email = ?', (email,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return dict(row)

    def update_customer(self, customer_id: int, customer_data: Dict) -> bool:
        """
        Update customer information

        Args:
            customer_id: Customer ID
            customer_data: Updated customer data

        Returns:
            Success boolean
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        # Build UPDATE query dynamically
        fields = []
        values = []

        for key, value in customer_data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)

        fields.append("updated_at = ?")
        values.append(now)
        values.append(customer_id)

        query = f"UPDATE customers SET {', '.join(fields)} WHERE id = ?"

        cursor.execute(query, values)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return success

    def list_customers(
        self,
        status: Optional[str] = None,
        customer_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        List customers with optional filters

        Args:
            status: Filter by status ('active', 'inactive')
            customer_type: Filter by type ('prospect', 'customer', 'partner')
            limit: Limit number of results

        Returns:
            List of customer dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM customers WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if customer_type:
            query += " AND customer_type = ?"
            params.append(customer_type)

        query += " ORDER BY created_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def add_contact_history(
        self,
        customer_id: int,
        contact_type: str,
        subject: str,
        notes: str,
        contacted_by: str
    ) -> int:
        """
        Add contact history entry

        Args:
            customer_id: Customer ID
            contact_type: Type of contact ('email', 'call', 'meeting', 'quote')
            subject: Contact subject
            notes: Contact notes
            contacted_by: Name of person who made contact

        Returns:
            Contact history ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT INTO contact_history (
                customer_id, contact_type, subject, notes,
                contacted_by, contact_date, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, contact_type, subject, notes, contacted_by, now, now))

        history_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return history_id

    def get_contact_history(self, customer_id: int) -> List[Dict]:
        """
        Get contact history for customer

        Args:
            customer_id: Customer ID

        Returns:
            List of contact history dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM contact_history
            WHERE customer_id = ?
            ORDER BY contact_date DESC
        ''', (customer_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def export_customers_csv(self, output_path: str) -> bool:
        """
        Export customers to CSV file

        Args:
            output_path: Output CSV file path

        Returns:
            Success boolean
        """
        import csv

        customers = self.list_customers()

        if not customers:
            return False

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=customers[0].keys())
                writer.writeheader()
                writer.writerows(customers)

            return True

        except Exception as e:
            print(f"Error exporting customers: {e}")
            return False
