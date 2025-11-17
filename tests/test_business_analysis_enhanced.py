"""
Test Cases for Business Analysis Enhanced Module
Comprehensive testing of TCO, ROI, NPV, IRR, sensitivity analysis, and reporting.
"""

import unittest
import sys
import os
import numpy as np
import pandas as pd
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.business_analysis_enhanced import (
    BusinessAnalysisEnhanced,
    ChamberConfig,
    OperatingCosts,
    RevenueParams,
    FinancialAssumptions
)
from modules.financial_calculator import (
    calculate_npv,
    calculate_irr,
    calculate_payback_period,
    calculate_roi_percentage,
    escalate_cost,
    break_even_units
)


class TestFinancialCalculator(unittest.TestCase):
    """Test financial calculation utilities."""

    def test_npv_calculation(self):
        """Test NPV calculation."""
        cash_flows = [-1000000, 300000, 350000, 400000, 450000]
        discount_rate = 0.10

        npv = calculate_npv(cash_flows, discount_rate)

        # Expected NPV calculation
        expected = sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows))

        self.assertAlmostEqual(npv, expected, places=2)
        self.assertGreater(npv, 0)  # Should be positive for this case

    def test_npv_negative_case(self):
        """Test NPV with negative result."""
        cash_flows = [-1000000, 50000, 50000, 50000]
        discount_rate = 0.10

        npv = calculate_npv(cash_flows, discount_rate)
        self.assertLess(npv, 0)  # Should be negative

    def test_irr_calculation(self):
        """Test IRR calculation."""
        cash_flows = [-1000000, 300000, 350000, 400000, 450000]

        irr = calculate_irr(cash_flows)

        self.assertIsNotNone(irr)
        self.assertGreater(irr, 0)
        self.assertLess(irr, 1)  # IRR should be reasonable

        # Verify IRR by checking NPV at IRR is close to zero
        npv_at_irr = calculate_npv(cash_flows, irr)
        self.assertAlmostEqual(npv_at_irr, 0, places=2)

    def test_payback_period(self):
        """Test payback period calculation."""
        initial_investment = 1000000
        cash_flows = [300000, 350000, 400000, 450000]

        payback = calculate_payback_period(initial_investment, cash_flows)

        self.assertIsNotNone(payback)
        self.assertGreater(payback, 2)  # Should be between 2 and 3 years
        self.assertLess(payback, 3)

    def test_roi_percentage(self):
        """Test ROI percentage calculation."""
        total_benefits = 2000000
        total_costs = 1500000

        roi = calculate_roi_percentage(total_benefits, total_costs)

        expected = ((2000000 - 1500000) / 1500000) * 100
        self.assertAlmostEqual(roi, expected, places=2)
        self.assertAlmostEqual(roi, 33.33, places=1)

    def test_cost_escalation(self):
        """Test cost escalation calculation."""
        base_cost = 100000
        escalation_rate = 0.05
        year = 3

        escalated = escalate_cost(base_cost, escalation_rate, year)

        expected = 100000 * (1.05 ** 3)
        self.assertAlmostEqual(escalated, expected, places=2)
        self.assertAlmostEqual(escalated, 115762.5, places=1)

    def test_break_even_units(self):
        """Test break-even unit calculation."""
        fixed_costs = 1000000
        price_per_unit = 25000
        variable_cost = 5000

        be_units = break_even_units(fixed_costs, price_per_unit, variable_cost)

        self.assertEqual(be_units, 50.0)


class TestBusinessAnalysisEnhanced(unittest.TestCase):
    """Test BusinessAnalysisEnhanced class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analysis = BusinessAnalysisEnhanced(
            chamber_config=ChamberConfig(),
            operating_costs=OperatingCosts(),
            revenue_params=RevenueParams(),
            financial_assumptions=FinancialAssumptions()
        )

    def test_initialization(self):
        """Test proper initialization."""
        self.assertIsNotNone(self.analysis.chamber)
        self.assertIsNotNone(self.analysis.opex)
        self.assertIsNotNone(self.analysis.revenue)
        self.assertIsNotNone(self.analysis.assumptions)

    def test_capex_breakdown(self):
        """Test CAPEX breakdown calculation."""
        capex = self.analysis.breakdown_capex()

        self.assertIn('equipment', capex)
        self.assertIn('installation', capex)
        self.assertIn('training', capex)
        self.assertIn('total', capex)

        # Check total calculation
        expected_total = (
            capex['equipment'] +
            capex['installation'] +
            capex['training'] +
            capex['spare_parts'] +
            capex['initial_calibration']
        )
        self.assertEqual(capex['total'], expected_total)

    def test_annual_opex(self):
        """Test annual OPEX calculation."""
        # Year 0
        opex_year0 = self.analysis.calculate_annual_opex(0)
        self.assertIn('energy', opex_year0)
        self.assertIn('maintenance', opex_year0)
        self.assertIn('total', opex_year0)

        # Year 5 (should be escalated)
        opex_year5 = self.analysis.calculate_annual_opex(5)

        # Energy should be higher in year 5 due to escalation
        self.assertGreater(opex_year5['energy'], opex_year0['energy'])

    def test_tco_calculation(self):
        """Test TCO calculation."""
        tco_df = self.analysis.calculate_tco_detailed(10)

        # Check DataFrame structure
        self.assertEqual(len(tco_df), 11)  # Year 0 + 10 years
        self.assertIn('year', tco_df.columns)
        self.assertIn('capex', tco_df.columns)
        self.assertIn('opex', tco_df.columns)
        self.assertIn('cumulative_cost', tco_df.columns)

        # Year 0 should have CAPEX, no OPEX
        self.assertGreater(tco_df.loc[0, 'capex'], 0)
        self.assertEqual(tco_df.loc[0, 'opex'], 0)

        # Year 1+ should have OPEX, no CAPEX
        self.assertEqual(tco_df.loc[1, 'capex'], 0)
        self.assertGreater(tco_df.loc[1, 'opex'], 0)

        # Cumulative should be increasing
        self.assertTrue((tco_df['cumulative_cost'].diff()[1:] > 0).all())

    def test_roi_metrics(self):
        """Test ROI metrics calculation."""
        roi = self.analysis.calculate_roi_metrics(10)

        self.assertIn('npv', roi)
        self.assertIn('irr', roi)
        self.assertIn('payback_period', roi)
        self.assertIn('roi_percent', roi)
        self.assertIn('cash_flows', roi)

        # NPV should be positive for default parameters
        self.assertGreater(roi['npv'], 0)

        # IRR should be reasonable
        if roi['irr']:
            self.assertGreater(roi['irr'], 0)
            self.assertLess(roi['irr'], 2)  # Less than 200%

        # Payback period should be reasonable
        if roi['payback_period']:
            self.assertGreater(roi['payback_period'], 0)
            self.assertLess(roi['payback_period'], 10)

    def test_break_even_analysis(self):
        """Test break-even analysis."""
        breakeven = self.analysis.break_even_analysis()

        self.assertIn('break_even_tests', breakeven)
        self.assertIn('current_tests', breakeven)
        self.assertIn('utilization_at_breakeven', breakeven)

        # Break-even should be positive
        self.assertGreater(breakeven['break_even_tests'], 0)

        # Current tests should exceed break-even
        self.assertGreater(
            breakeven['current_tests'],
            breakeven['break_even_tests']
        )

    def test_scenario_analysis(self):
        """Test scenario analysis."""
        scenarios = self.analysis.scenario_analysis()

        # Should have 3 scenarios
        self.assertEqual(len(scenarios), 3)

        # Check scenario names
        scenario_names = scenarios['scenario'].tolist()
        self.assertIn('Expected', scenario_names)
        self.assertIn('Best Case', scenario_names)
        self.assertIn('Worst Case', scenario_names)

        # Best case should have highest NPV
        best_npv = scenarios[scenarios['scenario'] == 'Best Case']['npv'].values[0]
        expected_npv = scenarios[scenarios['scenario'] == 'Expected']['npv'].values[0]
        worst_npv = scenarios[scenarios['scenario'] == 'Worst Case']['npv'].values[0]

        self.assertGreater(best_npv, expected_npv)
        self.assertGreater(expected_npv, worst_npv)

    def test_sensitivity_analysis(self):
        """Test sensitivity analysis."""
        sens_df = self.analysis.sensitivity_analysis('energy_price', 20)

        # Check DataFrame structure
        self.assertGreater(len(sens_df), 5)
        self.assertIn('variation_percent', sens_df.columns)
        self.assertIn('npv', sens_df.columns)
        self.assertIn('roi_percent', sens_df.columns)

        # Variations should range from -20% to +20%
        self.assertAlmostEqual(sens_df['variation_percent'].min(), -20, places=0)
        self.assertAlmostEqual(sens_df['variation_percent'].max(), 20, places=0)

    def test_tornado_chart_data(self):
        """Test tornado chart data generation."""
        tornado_df = self.analysis.tornado_chart_data()

        # Check DataFrame structure
        self.assertGreater(len(tornado_df), 0)
        self.assertIn('variable', tornado_df.columns)
        self.assertIn('impact', tornado_df.columns)
        self.assertIn('npv_low', tornado_df.columns)
        self.assertIn('npv_high', tornado_df.columns)

        # Should be sorted by impact (descending)
        impacts = tornado_df['impact'].tolist()
        self.assertEqual(impacts, sorted(impacts, reverse=True))

    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation."""
        # Run with small number of iterations for speed
        mc_results = self.analysis.monte_carlo_simulation(100)

        self.assertIn('npv_mean', mc_results)
        self.assertIn('npv_std', mc_results)
        self.assertIn('npv_p10', mc_results)
        self.assertIn('npv_p50', mc_results)
        self.assertIn('npv_p90', mc_results)
        self.assertIn('probability_positive_npv', mc_results)
        self.assertIn('npv_distribution', mc_results)

        # Check distribution size
        self.assertEqual(len(mc_results['npv_distribution']), 100)

        # Std should be positive
        self.assertGreater(mc_results['npv_std'], 0)

        # Percentiles should be ordered
        self.assertLess(mc_results['npv_p10'], mc_results['npv_p50'])
        self.assertLess(mc_results['npv_p50'], mc_results['npv_p90'])

        # Probability should be between 0 and 100
        self.assertGreaterEqual(mc_results['probability_positive_npv'], 0)
        self.assertLessEqual(mc_results['probability_positive_npv'], 100)

    def test_competitive_comparison(self):
        """Test competitive comparison."""
        # Load competitor data
        try:
            with open('data/competitor_data.json', 'r') as f:
                data = json.load(f)
            competitor_data = data['competitors']
        except:
            # Use dummy data if file not found
            competitor_data = [
                {
                    'supplier': 'Test Competitor',
                    'model': 'TC-100',
                    'initial_cost': 9000000,
                    'tco_10_year': 24000000,
                    'npv': 18000000,
                    'payback_years': 3.0,
                    'tests_per_year': 180,
                    'energy_cost_annual': 200000,
                    'maintenance_cost_annual': 270000
                }
            ]

        comp_df = self.analysis.compare_with_competitors(competitor_data)

        # Should have our solution + competitors
        self.assertGreaterEqual(len(comp_df), 2)

        # Check our solution is included
        our_solution = comp_df[comp_df['supplier'] == 'Our Solution']
        self.assertEqual(len(our_solution), 1)

    def test_outsourcing_comparison(self):
        """Test outsourcing comparison."""
        comparison = self.analysis.compare_with_outsourcing()

        self.assertIn('inhouse_tco_10yr', comparison)
        self.assertIn('outsource_cost_10yr', comparison)
        self.assertIn('savings', comparison)
        self.assertIn('savings_percent', comparison)

        # In-house should be cheaper
        self.assertGreater(
            comparison['outsource_cost_10yr'],
            comparison['inhouse_tco_10yr']
        )

        # Savings should be positive
        self.assertGreater(comparison['savings'], 0)

    def test_financial_dashboard(self):
        """Test financial dashboard generation."""
        dashboard = self.analysis.generate_financial_dashboard()

        required_metrics = [
            'payback_period_years',
            'roi_annual_percent',
            'npv',
            'irr_percent',
            'cost_per_test',
            'energy_cost_per_test',
            'utilization_rate_percent',
            'tco_10_year',
            'break_even_tests'
        ]

        for metric in required_metrics:
            self.assertIn(metric, dashboard)
            self.assertIsNotNone(dashboard[metric])

    def test_investment_justification(self):
        """Test investment justification report generation."""
        report = self.analysis.generate_investment_justification()

        self.assertIn('executive_summary', report)
        self.assertIn('financial_analysis', report)
        self.assertIn('risk_analysis', report)

        # Check executive summary
        exec_summary = report['executive_summary']
        self.assertIn('npv', exec_summary)
        self.assertIn('recommendation', exec_summary)

        # Recommendation should be APPROVED or REVIEW
        self.assertIn(exec_summary['recommendation'], ['APPROVED', 'REVIEW'])

    def test_excel_export(self):
        """Test Excel export functionality."""
        output_path = 'test_export.xlsx'

        try:
            self.analysis.export_to_excel(output_path)
            self.assertTrue(os.path.exists(output_path))

            # Verify file is not empty
            file_size = os.path.getsize(output_path)
            self.assertGreater(file_size, 0)

        finally:
            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_json_save_load(self):
        """Test JSON save and load."""
        output_path = 'test_config.json'

        try:
            # Save
            self.analysis.save_to_json(output_path)
            self.assertTrue(os.path.exists(output_path))

            # Load
            new_analysis = BusinessAnalysisEnhanced()
            new_analysis.load_from_json(output_path)

            # Verify data matches
            self.assertEqual(
                self.analysis.chamber.equipment_cost,
                new_analysis.chamber.equipment_cost
            )
            self.assertEqual(
                self.analysis.opex.energy_cost,
                new_analysis.opex.energy_cost
            )

        finally:
            # Cleanup
            if os.path.exists(output_path):
                os.remove(output_path)


class TestDataClasses(unittest.TestCase):
    """Test data classes."""

    def test_chamber_config(self):
        """Test ChamberConfig dataclass."""
        config = ChamberConfig()

        self.assertGreater(config.equipment_cost, 0)
        self.assertGreater(config.volume_m3, 0)
        self.assertEqual(config.expected_lifetime_years, 10)

    def test_operating_costs(self):
        """Test OperatingCosts dataclass."""
        opex = OperatingCosts()

        self.assertGreater(opex.energy_cost, 0)
        self.assertGreater(opex.maintenance_cost, 0)
        self.assertGreater(opex.downtime_cost_per_day, 0)

    def test_revenue_params(self):
        """Test RevenueParams dataclass."""
        revenue = RevenueParams()

        self.assertGreater(revenue.tests_per_year, 0)
        self.assertGreater(revenue.revenue_per_test, 0)
        self.assertGreater(revenue.outsource_cost_per_test, revenue.revenue_per_test)

    def test_financial_assumptions(self):
        """Test FinancialAssumptions dataclass."""
        assumptions = FinancialAssumptions()

        self.assertGreater(assumptions.discount_rate, 0)
        self.assertLess(assumptions.discount_rate, 1)
        self.assertGreater(assumptions.inflation_rate, 0)
        self.assertEqual(assumptions.tax_rate, 0.25)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
