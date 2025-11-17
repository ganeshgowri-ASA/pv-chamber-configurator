"""
Test cases for Supplier Database Manager
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

from supplier_database import SupplierDatabaseManager


class TestSupplierDatabaseManager(unittest.TestCase):
    """Test suite for SupplierDatabaseManager"""

    def setUp(self):
        """Set up test database before each test"""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, 'test_suppliers.db')
        self.db = SupplierDatabaseManager(self.db_path)

    def tearDown(self):
        """Clean up after each test"""
        self.db.close()
        shutil.rmtree(self.test_dir)

    # ==================== Database Creation Tests ====================

    def test_database_creation(self):
        """Test that database and tables are created successfully"""
        self.assertTrue(os.path.exists(self.db_path))

        # Check that all tables exist
        self.db.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in self.db.cursor.fetchall()]

        expected_tables = ['suppliers', 'components', 'quotes', 'quote_items', 'price_history']
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} not found")

    # ==================== Supplier Tests ====================

    def test_add_supplier(self):
        """Test adding a new supplier"""
        supplier_data = {
            'name': 'Test Supplier Ltd',
            'contact': '+91-80-1234-5678',
            'email': 'test@supplier.com',
            'location': 'Bangalore, Karnataka',
            'rating': 4.5,
            'avg_delivery_days': 30,
            'payment_terms': 'Net 30'
        }

        supplier_id = self.db.add_supplier(supplier_data)
        self.assertIsNotNone(supplier_id)
        self.assertGreater(supplier_id, 0)

        # Verify supplier was added
        suppliers_df = self.db.get_suppliers()
        self.assertEqual(len(suppliers_df), 1)
        self.assertEqual(suppliers_df.iloc[0]['name'], 'Test Supplier Ltd')

    def test_add_supplier_missing_required_field(self):
        """Test that adding supplier without required field raises error"""
        supplier_data = {
            'contact': '+91-80-1234-5678',
            'email': 'test@supplier.com'
        }

        with self.assertRaises(ValueError):
            self.db.add_supplier(supplier_data)

    def test_get_suppliers_with_filter(self):
        """Test filtering suppliers"""
        # Add multiple suppliers
        self.db.add_supplier({
            'name': 'Supplier A',
            'location': 'Bangalore'
        })
        self.db.add_supplier({
            'name': 'Supplier B',
            'location': 'Mumbai'
        })
        self.db.add_supplier({
            'name': 'Supplier C',
            'location': 'Bangalore'
        })

        # Filter by location
        filtered = self.db.get_suppliers({'location': 'Bangalore'})
        self.assertEqual(len(filtered), 2)

    def test_update_supplier(self):
        """Test updating supplier information"""
        supplier_id = self.db.add_supplier({
            'name': 'Test Supplier',
            'rating': 3.5
        })

        # Update rating
        updated = self.db.update_supplier(supplier_id, {'rating': 4.5})
        self.assertTrue(updated)

        # Verify update
        suppliers_df = self.db.get_suppliers()
        self.assertEqual(suppliers_df.iloc[0]['rating'], 4.5)

    # ==================== Component Tests ====================

    def test_add_component(self):
        """Test adding a new component"""
        # First add a supplier
        supplier_id = self.db.add_supplier({
            'name': 'Component Supplier'
        })

        component_data = {
            'category': 'Heaters',
            'name': 'Test Heater 10kW',
            'specification': '10kW, 415V, SS304',
            'supplier_id': supplier_id,
            'price': 85000,
            'lead_time_days': 25,
            'warranty_months': 24,
            'moq': 1
        }

        component_id = self.db.add_component(component_data)
        self.assertIsNotNone(component_id)
        self.assertGreater(component_id, 0)

        # Verify component was added
        components_df = self.db.get_components()
        self.assertEqual(len(components_df), 1)
        self.assertEqual(components_df.iloc[0]['name'], 'Test Heater 10kW')

    def test_get_components_by_category(self):
        """Test filtering components by category"""
        supplier_id = self.db.add_supplier({'name': 'Test Supplier'})

        # Add components in different categories
        self.db.add_component({
            'category': 'Heaters',
            'name': 'Heater 1',
            'supplier_id': supplier_id,
            'price': 10000
        })
        self.db.add_component({
            'category': 'Heaters',
            'name': 'Heater 2',
            'supplier_id': supplier_id,
            'price': 15000
        })
        self.db.add_component({
            'category': 'Fans',
            'name': 'Fan 1',
            'supplier_id': supplier_id,
            'price': 5000
        })

        # Filter by category
        heaters = self.db.get_components(category='Heaters')
        self.assertEqual(len(heaters), 2)

    def test_price_history_creation(self):
        """Test that price history is created when adding component"""
        supplier_id = self.db.add_supplier({'name': 'Test Supplier'})
        component_id = self.db.add_component({
            'category': 'Test',
            'name': 'Test Component',
            'supplier_id': supplier_id,
            'price': 1000
        })

        # Check price history
        history = self.db.get_price_trends(component_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history.iloc[0]['price'], 1000)

    # ==================== Quote Tests ====================

    def test_add_quote(self):
        """Test adding a quote"""
        supplier_id = self.db.add_supplier({'name': 'Test Supplier'})

        quote_data = {
            'supplier_id': supplier_id,
            'quote_date': '2024-01-15',
            'quote_number': 'Q-2024-001',
            'validity_days': 30,
            'total_cost': 100000,
            'status': 'active'
        }

        items = [
            {
                'description': 'Test Item 1',
                'quantity': 2,
                'unit_price': 25000,
                'total_price': 50000
            },
            {
                'description': 'Test Item 2',
                'quantity': 1,
                'unit_price': 50000,
                'total_price': 50000
            }
        ]

        quote_id = self.db.add_quote(quote_data, items)
        self.assertIsNotNone(quote_id)

        # Verify quote was added
        quotes_df = self.db.get_quotes()
        self.assertEqual(len(quotes_df), 1)
        self.assertEqual(quotes_df.iloc[0]['quote_number'], 'Q-2024-001')

        # Verify items were added
        items_df = self.db.get_quote_items(quote_id)
        self.assertEqual(len(items_df), 2)

    def test_validate_quote_data(self):
        """Test quote data validation"""
        supplier_id = self.db.add_supplier({'name': 'Test Supplier'})

        # Valid quote data
        valid_data = {
            'supplier_id': supplier_id,
            'quote_date': '2024-01-15'
        }
        is_valid, errors = self.db.validate_quote_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Invalid quote data (missing required fields)
        invalid_data = {
            'quote_number': 'Q-001'
        }
        is_valid, errors = self.db.validate_quote_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

    def test_calculate_total_cost(self):
        """Test total cost calculation for a quote"""
        supplier_id = self.db.add_supplier({'name': 'Test Supplier'})

        quote_data = {
            'supplier_id': supplier_id,
            'quote_date': '2024-01-15',
            'delivery_cost': 5000
        }

        items = [
            {
                'description': 'Item 1',
                'quantity': 2,
                'unit_price': 10000,
                'total_price': 20000
            },
            {
                'description': 'Item 2',
                'quantity': 3,
                'unit_price': 5000,
                'total_price': 15000
            }
        ]

        quote_id = self.db.add_quote(quote_data, items)

        # Calculate total cost with taxes
        cost_breakdown = self.db.calculate_total_cost(quote_id, include_taxes=True, tax_rate=0.18)

        self.assertEqual(cost_breakdown['subtotal'], 35000)
        self.assertEqual(cost_breakdown['delivery_cost'], 5000)
        self.assertAlmostEqual(cost_breakdown['tax_amount'], 6300, places=0)  # 18% of 35000
        self.assertAlmostEqual(cost_breakdown['total_cost'], 46300, places=0)

    # ==================== Price Comparison Tests ====================

    def test_compare_prices(self):
        """Test price comparison across suppliers"""
        # Add suppliers
        supplier1_id = self.db.add_supplier({'name': 'Supplier A'})
        supplier2_id = self.db.add_supplier({'name': 'Supplier B'})

        # Add same component from different suppliers
        self.db.add_component({
            'category': 'Heaters',
            'name': 'Heater 10kW',
            'supplier_id': supplier1_id,
            'price': 85000
        })
        self.db.add_component({
            'category': 'Heaters',
            'name': 'Heater 10kW',
            'supplier_id': supplier2_id,
            'price': 92000
        })

        # Compare prices
        comparison = self.db.compare_prices(['Heater 10kW'])
        self.assertEqual(len(comparison), 2)
        # Should be sorted by price
        self.assertEqual(comparison.iloc[0]['price'], 85000)

    def test_get_best_value_supplier(self):
        """Test best value supplier selection with weighted scoring"""
        # Add suppliers with different characteristics
        supplier1_id = self.db.add_supplier({
            'name': 'Cheap Supplier',
            'rating': 3.0,
            'avg_delivery_days': 45
        })
        supplier2_id = self.db.add_supplier({
            'name': 'Premium Supplier',
            'rating': 4.8,
            'avg_delivery_days': 20
        })

        # Add components
        self.db.add_component({
            'category': 'UV LEDs',
            'name': 'LED Module 100W',
            'supplier_id': supplier1_id,
            'price': 35000,
            'lead_time_days': 45,
            'warranty_months': 24
        })
        self.db.add_component({
            'category': 'UV LEDs',
            'name': 'LED Module 100W Premium',
            'supplier_id': supplier2_id,
            'price': 58000,
            'lead_time_days': 20,
            'warranty_months': 48
        })

        # Get best value
        best_value_df = self.db.get_best_value_supplier('UV LEDs')

        self.assertEqual(len(best_value_df), 2)
        # Check that scores are calculated
        self.assertIn('total_score', best_value_df.columns)
        self.assertGreater(best_value_df.iloc[0]['total_score'], 0)

    # ==================== Procurement Recommendation Tests ====================

    def test_generate_procurement_recommendation(self):
        """Test procurement recommendation generation"""
        # Set up test data
        supplier1_id = self.db.add_supplier({'name': 'Supplier A'})
        supplier2_id = self.db.add_supplier({'name': 'Supplier B'})

        self.db.add_component({
            'category': 'Heaters',
            'name': 'Heater 10kW',
            'supplier_id': supplier1_id,
            'price': 85000,
            'lead_time_days': 25,
            'warranty_months': 24
        })
        self.db.add_component({
            'category': 'Fans',
            'name': 'EC Fan 800mm',
            'supplier_id': supplier2_id,
            'price': 28000,
            'lead_time_days': 22,
            'warranty_months': 36
        })

        # Generate recommendation
        requirements = [
            {'category': 'Heaters', 'quantity': 2},
            {'category': 'Fans', 'quantity': 4}
        ]

        recommendation = self.db.generate_procurement_recommendation(requirements)

        self.assertIn('recommendations', recommendation)
        self.assertIn('total_cost', recommendation)
        self.assertIn('num_suppliers', recommendation)
        self.assertIn('risk_level', recommendation)

        # Check calculations
        expected_cost = (85000 * 2) + (28000 * 4)
        self.assertEqual(recommendation['total_cost'], expected_cost)
        self.assertEqual(recommendation['num_suppliers'], 2)
        self.assertEqual(recommendation['risk_level'], 'Medium')

    def test_risk_assessment(self):
        """Test risk level assessment based on number of suppliers"""
        supplier1_id = self.db.add_supplier({'name': 'Supplier A'})
        supplier2_id = self.db.add_supplier({'name': 'Supplier B'})
        supplier3_id = self.db.add_supplier({'name': 'Supplier C'})

        # Add components from different suppliers
        self.db.add_component({
            'category': 'Cat1',
            'name': 'Item 1',
            'supplier_id': supplier1_id,
            'price': 1000
        })
        self.db.add_component({
            'category': 'Cat2',
            'name': 'Item 2',
            'supplier_id': supplier2_id,
            'price': 2000
        })
        self.db.add_component({
            'category': 'Cat3',
            'name': 'Item 3',
            'supplier_id': supplier3_id,
            'price': 3000
        })

        # Test with 3 suppliers (Low risk)
        requirements = [
            {'category': 'Cat1', 'quantity': 1},
            {'category': 'Cat2', 'quantity': 1},
            {'category': 'Cat3', 'quantity': 1}
        ]
        recommendation = self.db.generate_procurement_recommendation(requirements)
        self.assertEqual(recommendation['risk_level'], 'Low')

    # ==================== Utility Tests ====================

    def test_get_categories(self):
        """Test getting all unique categories"""
        supplier_id = self.db.add_supplier({'name': 'Test Supplier'})

        self.db.add_component({
            'category': 'Heaters',
            'name': 'Item 1',
            'supplier_id': supplier_id,
            'price': 1000
        })
        self.db.add_component({
            'category': 'Fans',
            'name': 'Item 2',
            'supplier_id': supplier_id,
            'price': 2000
        })
        self.db.add_component({
            'category': 'Heaters',
            'name': 'Item 3',
            'supplier_id': supplier_id,
            'price': 3000
        })

        categories = self.db.get_categories()
        self.assertEqual(len(categories), 2)
        self.assertIn('Heaters', categories)
        self.assertIn('Fans', categories)

    def test_get_statistics(self):
        """Test database statistics"""
        supplier_id = self.db.add_supplier({'name': 'Test Supplier', 'rating': 4.5})
        self.db.add_component({
            'category': 'Heaters',
            'name': 'Item 1',
            'supplier_id': supplier_id,
            'price': 1000
        })

        stats = self.db.get_statistics()

        self.assertEqual(stats['total_suppliers'], 1)
        self.assertEqual(stats['total_components'], 1)
        self.assertEqual(stats['avg_supplier_rating'], 4.5)
        self.assertIn('components_by_category', stats)


class TestQuoteParser(unittest.TestCase):
    """Test suite for quote parsing functions"""

    def setUp(self):
        """Set up test data"""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'modules'))

    def test_parse_indian_currency(self):
        """Test parsing Indian currency formats"""
        from quote_parser import parse_indian_currency

        # Test basic rupee formats
        self.assertEqual(parse_indian_currency("Rs. 1000"), 1000)
        self.assertEqual(parse_indian_currency("₹1,000"), 1000)
        self.assertEqual(parse_indian_currency("INR 1000.50"), 1000.50)

        # Test lakhs
        self.assertEqual(parse_indian_currency("5 lakhs"), 500000)
        self.assertEqual(parse_indian_currency("2.5 L"), 250000)

        # Test crores
        self.assertEqual(parse_indian_currency("1 crore"), 10000000)
        self.assertEqual(parse_indian_currency("1.5 Cr"), 15000000)

    def test_extract_component_prices(self):
        """Test extracting component prices from text"""
        from quote_parser import extract_component_prices

        text = """
        Heater 10kW    2    Rs. 85000    Rs. 170000
        Fan EC 800mm   4    Rs. 28000    Rs. 112000
        """

        components = extract_component_prices(text)
        self.assertGreater(len(components), 0)

        # Check first component
        if len(components) > 0:
            self.assertIn('description', components[0])
            self.assertIn('quantity', components[0])
            self.assertIn('unit_price', components[0])
            self.assertIn('total_price', components[0])


if __name__ == '__main__':
    unittest.main()
