"""
Database Initialization Script
Loads Indian suppliers seed data into the database.
"""

import json
import os
from supplier_database import SupplierDatabaseManager


def initialize_database(db_path='data/suppliers.db', seed_file='data/indian_suppliers_seed.json'):
    """
    Initialize database with seed data from JSON file.

    Args:
        db_path: Path to database file
        seed_file: Path to seed data JSON file
    """
    # Check if database already has data
    db = SupplierDatabaseManager(db_path)

    stats = db.get_statistics()
    if stats['total_suppliers'] > 0:
        print(f"Database already initialized with {stats['total_suppliers']} suppliers.")
        return db

    # Load seed data
    if not os.path.exists(seed_file):
        print(f"Seed file not found: {seed_file}")
        return db

    with open(seed_file, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    # Create supplier name to ID mapping
    supplier_map = {}

    # Add suppliers
    print("Initializing suppliers...")
    for supplier_data in seed_data.get('suppliers', []):
        supplier_id = db.add_supplier(supplier_data)
        supplier_map[supplier_data['name']] = supplier_id
        print(f"  Added: {supplier_data['name']} (ID: {supplier_id})")

    # Add components
    print("\nInitializing components...")
    for component_data in seed_data.get('components', []):
        # Replace supplier name with supplier ID
        if 'supplier' in component_data:
            supplier_name = component_data.pop('supplier')
            if supplier_name in supplier_map:
                component_data['supplier_id'] = supplier_map[supplier_name]
            else:
                print(f"  Warning: Supplier '{supplier_name}' not found for component '{component_data['name']}'")
                continue

        component_id = db.add_component(component_data)
        print(f"  Added: {component_data['category']} - {component_data['name']} (ID: {component_id})")

    # Print statistics
    stats = db.get_statistics()
    print("\n" + "="*60)
    print("Database Initialization Complete!")
    print("="*60)
    print(f"Total Suppliers: {stats['total_suppliers']}")
    print(f"Total Components: {stats['total_components']}")
    print(f"Average Supplier Rating: {stats['avg_supplier_rating']:.2f}/5.0")
    print("\nComponents by Category:")
    for category, count in stats['components_by_category'].items():
        print(f"  {category}: {count}")
    print("="*60)

    return db


if __name__ == '__main__':
    # Run initialization
    db = initialize_database()
    db.close()
