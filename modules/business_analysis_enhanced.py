"""
Business Analysis Enhanced Module
Comprehensive TCO, ROI, competitive analysis, and investment justification tools.
"""

import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import os

from .financial_calculator import (
    calculate_npv,
    calculate_irr,
    calculate_payback_period,
    calculate_roi_percentage,
    escalate_cost,
    calculate_depreciation_straight_line,
    break_even_units
)


@dataclass
class ChamberConfig:
    """Chamber configuration parameters."""
    equipment_cost: float = 8500000
    installation_cost: float = 500000
    training_cost: float = 200000
    spare_parts_cost: float = 300000
    initial_calibration_cost: float = 150000
    volume_m3: float = 14.784
    power_rating_kw: float = 45.0
    expected_lifetime_years: int = 10


@dataclass
class OperatingCosts:
    """Annual operating costs."""
    energy_cost: float = 180000
    maintenance_cost: float = 250000
    calibration_cost: float = 120000
    consumables_cost: float = 150000
    insurance_cost: float = 85000
    operator_salary: float = 600000
    downtime_cost_per_day: float = 50000


@dataclass
class RevenueParams:
    """Revenue generation parameters."""
    tests_per_year: int = 200
    revenue_per_test: float = 25000
    outsource_cost_per_test: float = 35000
    quality_improvement_savings: float = 200000


@dataclass
class FinancialAssumptions:
    """Financial modeling assumptions."""
    discount_rate: float = 0.10
    inflation_rate: float = 0.06
    energy_escalation_rate: float = 0.05
    maintenance_escalation_rate: float = 0.04
    tax_rate: float = 0.25
    salvage_value_percent: float = 0.10


class BusinessAnalysisEnhanced:
    """
    Enhanced business analysis engine for PV chamber investment.
    """

    def __init__(
        self,
        chamber_config: Optional[ChamberConfig] = None,
        operating_costs: Optional[OperatingCosts] = None,
        revenue_params: Optional[RevenueParams] = None,
        financial_assumptions: Optional[FinancialAssumptions] = None
    ):
        """
        Initialize business analysis with configuration parameters.

        Args:
            chamber_config: Chamber technical and cost configuration
            operating_costs: Annual operating cost parameters
            revenue_params: Revenue generation parameters
            financial_assumptions: Financial modeling assumptions
        """
        self.chamber = chamber_config or ChamberConfig()
        self.opex = operating_costs or OperatingCosts()
        self.revenue = revenue_params or RevenueParams()
        self.assumptions = financial_assumptions or FinancialAssumptions()

    # ========== TCO ANALYSIS ==========

    def breakdown_capex(self) -> Dict[str, float]:
        """
        Calculate detailed CAPEX breakdown.

        Returns:
            Dictionary with CAPEX components
        """
        capex = {
            'equipment': self.chamber.equipment_cost,
            'installation': self.chamber.installation_cost,
            'training': self.chamber.training_cost,
            'spare_parts': self.chamber.spare_parts_cost,
            'initial_calibration': self.chamber.initial_calibration_cost
        }
        capex['total'] = sum(capex.values())
        return capex

    def calculate_annual_opex(self, year: int) -> Dict[str, float]:
        """
        Calculate operating expenses for a specific year with escalation.

        Args:
            year: Year number (0-indexed, where 0 is year 1)

        Returns:
            Dictionary with OPEX components for the year
        """
        # Energy with escalation
        energy = escalate_cost(
            self.opex.energy_cost,
            self.assumptions.energy_escalation_rate,
            year
        )

        # Maintenance with escalation
        maintenance = escalate_cost(
            self.opex.maintenance_cost,
            self.assumptions.maintenance_escalation_rate,
            year
        )

        # Other costs with general inflation
        calibration = escalate_cost(
            self.opex.calibration_cost,
            self.assumptions.inflation_rate,
            year
        )

        consumables = escalate_cost(
            self.opex.consumables_cost,
            self.assumptions.inflation_rate,
            year
        )

        insurance = escalate_cost(
            self.opex.insurance_cost,
            self.assumptions.inflation_rate,
            year
        )

        operator_salary = escalate_cost(
            self.opex.operator_salary,
            self.assumptions.inflation_rate,
            year
        )

        opex = {
            'energy': energy,
            'maintenance': maintenance,
            'calibration': calibration,
            'consumables': consumables,
            'insurance': insurance,
            'operator_salary': operator_salary
        }

        opex['total'] = sum(opex.values())
        return opex

    def estimate_downtime_cost(self, hours_per_year: float = 80) -> float:
        """
        Estimate annual cost of downtime.

        Args:
            hours_per_year: Expected downtime hours annually

        Returns:
            Annual downtime cost
        """
        days_per_year = hours_per_year / 24
        return days_per_year * self.opex.downtime_cost_per_day

    def calculate_disposal_cost(self) -> float:
        """
        Calculate end-of-life disposal cost.

        Returns:
            Disposal cost (typically 1-2% of equipment cost)
        """
        return self.chamber.equipment_cost * 0.01

    def calculate_tco_detailed(self, years: int = 10) -> pd.DataFrame:
        """
        Calculate detailed Total Cost of Ownership over specified period.

        Args:
            years: Analysis period in years

        Returns:
            DataFrame with year-by-year TCO breakdown
        """
        tco_data = []

        # Year 0: CAPEX
        capex = self.breakdown_capex()
        tco_data.append({
            'year': 0,
            'capex': capex['total'],
            'opex': 0,
            'downtime_cost': 0,
            'total_cost': capex['total'],
            'cumulative_cost': capex['total']
        })

        cumulative = capex['total']

        # Years 1 to N: OPEX
        for year in range(years):
            opex = self.calculate_annual_opex(year)
            downtime = self.estimate_downtime_cost()

            year_cost = opex['total'] + downtime
            cumulative += year_cost

            tco_data.append({
                'year': year + 1,
                'capex': 0,
                'opex': opex['total'],
                'downtime_cost': downtime,
                'total_cost': year_cost,
                'cumulative_cost': cumulative
            })

        # Add disposal cost in final year
        disposal = self.calculate_disposal_cost()
        tco_data[-1]['opex'] += disposal
        tco_data[-1]['total_cost'] += disposal
        tco_data[-1]['cumulative_cost'] += disposal

        return pd.DataFrame(tco_data)

    # ========== ROI CALCULATION ==========

    def calculate_annual_revenue(self, year: int) -> Dict[str, float]:
        """
        Calculate annual revenue and savings.

        Args:
            year: Year number (0-indexed)

        Returns:
            Dictionary with revenue components
        """
        # Testing revenue with inflation
        test_revenue = escalate_cost(
            self.revenue.tests_per_year * self.revenue.revenue_per_test,
            self.assumptions.inflation_rate,
            year
        )

        # Outsourcing savings
        outsource_savings = escalate_cost(
            self.revenue.tests_per_year * (
                self.revenue.outsource_cost_per_test - self.revenue.revenue_per_test
            ),
            self.assumptions.inflation_rate,
            year
        )

        # Quality improvement savings
        quality_savings = escalate_cost(
            self.revenue.quality_improvement_savings,
            self.assumptions.inflation_rate,
            year
        )

        return {
            'test_revenue': test_revenue,
            'outsource_savings': outsource_savings,
            'quality_savings': quality_savings,
            'total': test_revenue + outsource_savings + quality_savings
        }

    def calculate_roi_metrics(self, years: int = 10) -> Dict[str, any]:
        """
        Calculate comprehensive ROI metrics.

        Args:
            years: Analysis period in years

        Returns:
            Dictionary with ROI, NPV, IRR, payback period
        """
        # Get TCO data
        tco_df = self.calculate_tco_detailed(years)

        # Calculate cash flows
        cash_flows = []
        annual_data = []

        # Year 0: Initial investment (negative)
        capex = self.breakdown_capex()
        cash_flows.append(-capex['total'])

        # Years 1 to N
        for year in range(years):
            revenue = self.calculate_annual_revenue(year)
            opex = self.calculate_annual_opex(year)
            downtime = self.estimate_downtime_cost()

            net_cash_flow = revenue['total'] - opex['total'] - downtime
            cash_flows.append(net_cash_flow)

            annual_data.append({
                'year': year + 1,
                'revenue': revenue['total'],
                'opex': opex['total'] + downtime,
                'net_cash_flow': net_cash_flow
            })

        # Add salvage value in final year
        salvage_value = capex['total'] * self.assumptions.salvage_value_percent
        cash_flows[-1] += salvage_value

        # Calculate metrics
        npv = calculate_npv(cash_flows, self.assumptions.discount_rate)
        irr = calculate_irr(cash_flows)

        # Payback period
        payback = calculate_payback_period(
            capex['total'],
            [cf for cf in cash_flows[1:]]
        )

        # Total ROI
        total_benefits = sum(cash_flows[1:])
        total_costs = capex['total'] + sum(
            tco_df[tco_df['year'] > 0]['opex']
        )
        roi_percent = calculate_roi_percentage(total_benefits, total_costs)

        return {
            'npv': npv,
            'irr': irr,
            'payback_period': payback,
            'roi_percent': roi_percent,
            'annual_roi': roi_percent / years,
            'total_revenue': sum([cf for cf in cash_flows[1:]]),
            'total_costs': total_costs,
            'cash_flows': cash_flows,
            'annual_data': annual_data,
            'salvage_value': salvage_value
        }

    def break_even_analysis(self) -> Dict[str, float]:
        """
        Calculate break-even point in number of tests.

        Returns:
            Break-even metrics
        """
        capex = self.breakdown_capex()
        annual_opex = self.calculate_annual_opex(0)

        # Fixed costs (CAPEX amortized over lifetime + annual fixed OPEX)
        annual_capex = capex['total'] / self.chamber.expected_lifetime_years
        fixed_costs = annual_capex + annual_opex['total']

        # Variable costs per test (minimal for chamber - mostly energy)
        energy_per_test = self.opex.energy_cost / self.revenue.tests_per_year
        variable_cost_per_test = energy_per_test

        # Revenue per test
        revenue_per_test = self.revenue.revenue_per_test

        # Break-even units
        be_units = break_even_units(
            fixed_costs,
            revenue_per_test,
            variable_cost_per_test
        )

        return {
            'break_even_tests': be_units,
            'current_tests': self.revenue.tests_per_year,
            'utilization_at_breakeven': (be_units / self.revenue.tests_per_year) * 100,
            'fixed_costs': fixed_costs,
            'variable_cost_per_test': variable_cost_per_test,
            'revenue_per_test': revenue_per_test
        }

    # ========== COMPETITIVE COMPARISON ==========

    def compare_with_competitors(self, competitor_data: List[Dict]) -> pd.DataFrame:
        """
        Compare with competitor chambers.

        Args:
            competitor_data: List of competitor specifications

        Returns:
            Comparison DataFrame
        """
        # Our chamber data
        our_tco = self.calculate_tco_detailed(10)
        our_roi = self.calculate_roi_metrics(10)

        comparison = []

        # Add our chamber
        comparison.append({
            'supplier': 'Our Solution',
            'model': 'Custom UV+TC+HF+DH',
            'initial_cost': self.breakdown_capex()['total'],
            'tco_10_year': our_tco['cumulative_cost'].iloc[-1],
            'npv': our_roi['npv'],
            'payback_years': our_roi['payback_period'],
            'tests_per_year': self.revenue.tests_per_year,
            'energy_cost_annual': self.opex.energy_cost,
            'maintenance_cost_annual': self.opex.maintenance_cost
        })

        # Add competitors
        for comp in competitor_data:
            comparison.append({
                'supplier': comp.get('supplier', 'Unknown'),
                'model': comp.get('model', 'N/A'),
                'initial_cost': comp.get('initial_cost', 0),
                'tco_10_year': comp.get('tco_10_year', 0),
                'npv': comp.get('npv', 0),
                'payback_years': comp.get('payback_years', 0),
                'tests_per_year': comp.get('tests_per_year', 0),
                'energy_cost_annual': comp.get('energy_cost_annual', 0),
                'maintenance_cost_annual': comp.get('maintenance_cost_annual', 0)
            })

        df = pd.DataFrame(comparison)

        # Add rankings
        df['cost_rank'] = df['initial_cost'].rank()
        df['tco_rank'] = df['tco_10_year'].rank()
        df['npv_rank'] = df['npv'].rank(ascending=False)

        return df

    def compare_with_outsourcing(self) -> Dict[str, float]:
        """
        Compare in-house chamber vs outsourced testing.

        Returns:
            Comparison metrics
        """
        years = 10

        # In-house costs
        tco = self.calculate_tco_detailed(years)
        total_inhouse = tco['cumulative_cost'].iloc[-1]

        # Outsourcing costs (escalated)
        outsource_total = 0
        for year in range(years):
            yearly_cost = escalate_cost(
                self.revenue.tests_per_year * self.revenue.outsource_cost_per_test,
                self.assumptions.inflation_rate,
                year
            )
            outsource_total += yearly_cost

        # Comparison
        savings = outsource_total - total_inhouse
        savings_percent = (savings / outsource_total) * 100

        return {
            'inhouse_tco_10yr': total_inhouse,
            'outsource_cost_10yr': outsource_total,
            'savings': savings,
            'savings_percent': savings_percent,
            'payback_years': self.calculate_roi_metrics(years)['payback_period']
        }

    def generate_comparison_matrix(self, competitor_data: List[Dict]) -> pd.DataFrame:
        """
        Generate comprehensive comparison matrix.

        Args:
            competitor_data: List of competitor specifications

        Returns:
            Comparison matrix DataFrame
        """
        comp_df = self.compare_with_competitors(competitor_data)

        # Add capability scores (0-10 scale)
        capability_metrics = []

        for idx, row in comp_df.iterrows():
            if row['supplier'] == 'Our Solution':
                capability_metrics.append({
                    'uv_capability': 10,
                    'temp_range': 10,
                    'humidity_range': 10,
                    'automation': 9,
                    'support_quality': 8
                })
            else:
                # Placeholder - would be from competitor data
                capability_metrics.append({
                    'uv_capability': 7,
                    'temp_range': 8,
                    'humidity_range': 8,
                    'automation': 6,
                    'support_quality': 7
                })

        capability_df = pd.DataFrame(capability_metrics)
        result = pd.concat([comp_df, capability_df], axis=1)

        return result

    # ========== SENSITIVITY ANALYSIS ==========

    def sensitivity_analysis(
        self,
        variable: str,
        range_percent: float = 20
    ) -> pd.DataFrame:
        """
        Perform sensitivity analysis on a variable.

        Args:
            variable: Variable to analyze ('energy_price', 'test_volume', etc.)
            range_percent: Range to vary (+/- %)

        Returns:
            DataFrame with sensitivity results
        """
        # Define test points
        variations = np.linspace(
            1 - range_percent / 100,
            1 + range_percent / 100,
            11
        )

        results = []

        for var in variations:
            # Create modified instance
            temp_analysis = BusinessAnalysisEnhanced(
                chamber_config=ChamberConfig(),
                operating_costs=OperatingCosts(),
                revenue_params=RevenueParams(),
                financial_assumptions=self.assumptions
            )

            # Modify the variable
            if variable == 'energy_price':
                temp_analysis.opex.energy_cost = self.opex.energy_cost * var
            elif variable == 'test_volume':
                temp_analysis.revenue.tests_per_year = int(self.revenue.tests_per_year * var)
            elif variable == 'maintenance_cost':
                temp_analysis.opex.maintenance_cost = self.opex.maintenance_cost * var
            elif variable == 'revenue_per_test':
                temp_analysis.revenue.revenue_per_test = self.revenue.revenue_per_test * var
            elif variable == 'equipment_cost':
                temp_analysis.chamber.equipment_cost = self.chamber.equipment_cost * var

            # Calculate ROI metrics
            roi = temp_analysis.calculate_roi_metrics(10)

            results.append({
                'variation_percent': (var - 1) * 100,
                'variable_value': var,
                'npv': roi['npv'],
                'irr': roi['irr'] if roi['irr'] else 0,
                'payback_period': roi['payback_period'] if roi['payback_period'] else 999,
                'roi_percent': roi['roi_percent']
            })

        return pd.DataFrame(results)

    def tornado_chart_data(self) -> pd.DataFrame:
        """
        Generate tornado chart data showing impact of each variable.

        Returns:
            DataFrame sorted by impact magnitude
        """
        variables = [
            ('test_volume', 30),
            ('revenue_per_test', 25),
            ('energy_price', 20),
            ('maintenance_cost', 15),
            ('equipment_cost', 20)
        ]

        impacts = []

        base_roi = self.calculate_roi_metrics(10)
        base_npv = base_roi['npv']

        for var_name, var_range in variables:
            sens_df = self.sensitivity_analysis(var_name, var_range)

            # Get NPV at extremes
            npv_low = sens_df.iloc[0]['npv']
            npv_high = sens_df.iloc[-1]['npv']

            impact = abs(npv_high - npv_low)

            impacts.append({
                'variable': var_name,
                'base_npv': base_npv,
                'npv_low': npv_low,
                'npv_high': npv_high,
                'impact': impact,
                'impact_percent': (impact / abs(base_npv)) * 100 if base_npv != 0 else 0
            })

        df = pd.DataFrame(impacts)
        return df.sort_values('impact', ascending=False)

    def monte_carlo_simulation(self, iterations: int = 1000, seed: int = 42) -> Dict:
        """
        Perform Monte Carlo simulation for risk analysis.

        Args:
            iterations: Number of simulation runs
            seed: Random seed for reproducibility

        Returns:
            Dictionary with simulation results
        """
        np.random.seed(seed)

        npv_results = []
        irr_results = []

        for _ in range(iterations):
            # Randomly vary parameters within ranges
            temp_analysis = BusinessAnalysisEnhanced(
                chamber_config=ChamberConfig(),
                operating_costs=OperatingCosts(),
                revenue_params=RevenueParams(),
                financial_assumptions=self.assumptions
            )

            # Random variations (normal distribution)
            temp_analysis.opex.energy_cost *= np.random.normal(1.0, 0.10)
            temp_analysis.opex.maintenance_cost *= np.random.normal(1.0, 0.075)
            temp_analysis.revenue.tests_per_year = int(
                temp_analysis.revenue.tests_per_year * np.random.normal(1.0, 0.15)
            )
            temp_analysis.revenue.revenue_per_test *= np.random.normal(1.0, 0.125)

            # Calculate metrics
            roi = temp_analysis.calculate_roi_metrics(10)
            npv_results.append(roi['npv'])
            if roi['irr']:
                irr_results.append(roi['irr'])

        return {
            'npv_mean': np.mean(npv_results),
            'npv_std': np.std(npv_results),
            'npv_min': np.min(npv_results),
            'npv_max': np.max(npv_results),
            'npv_p10': np.percentile(npv_results, 10),
            'npv_p50': np.percentile(npv_results, 50),
            'npv_p90': np.percentile(npv_results, 90),
            'probability_positive_npv': (np.array(npv_results) > 0).sum() / iterations * 100,
            'npv_distribution': npv_results,
            'irr_mean': np.mean(irr_results) if irr_results else 0,
            'irr_std': np.std(irr_results) if irr_results else 0
        }

    def scenario_analysis(self) -> pd.DataFrame:
        """
        Generate best/worst/expected case scenarios.

        Returns:
            DataFrame with scenario results
        """
        scenarios = []

        # Base case (expected)
        base_roi = self.calculate_roi_metrics(10)
        scenarios.append({
            'scenario': 'Expected',
            'npv': base_roi['npv'],
            'irr': base_roi['irr'],
            'payback_years': base_roi['payback_period'],
            'roi_percent': base_roi['roi_percent']
        })

        # Best case (+20% revenue, -10% costs)
        best_analysis = BusinessAnalysisEnhanced(
            chamber_config=ChamberConfig(),
            operating_costs=OperatingCosts(),
            revenue_params=RevenueParams(),
            financial_assumptions=self.assumptions
        )
        best_analysis.revenue.tests_per_year = int(self.revenue.tests_per_year * 1.2)
        best_analysis.opex.energy_cost = self.opex.energy_cost * 0.9
        best_analysis.opex.maintenance_cost = self.opex.maintenance_cost * 0.9

        best_roi = best_analysis.calculate_roi_metrics(10)
        scenarios.append({
            'scenario': 'Best Case',
            'npv': best_roi['npv'],
            'irr': best_roi['irr'],
            'payback_years': best_roi['payback_period'],
            'roi_percent': best_roi['roi_percent']
        })

        # Worst case (-20% revenue, +10% costs)
        worst_analysis = BusinessAnalysisEnhanced(
            chamber_config=ChamberConfig(),
            operating_costs=OperatingCosts(),
            revenue_params=RevenueParams(),
            financial_assumptions=self.assumptions
        )
        worst_analysis.revenue.tests_per_year = int(self.revenue.tests_per_year * 0.8)
        worst_analysis.opex.energy_cost = self.opex.energy_cost * 1.1
        worst_analysis.opex.maintenance_cost = self.opex.maintenance_cost * 1.1

        worst_roi = worst_analysis.calculate_roi_metrics(10)
        scenarios.append({
            'scenario': 'Worst Case',
            'npv': worst_roi['npv'],
            'irr': worst_roi['irr'],
            'payback_years': worst_roi['payback_period'],
            'roi_percent': worst_roi['roi_percent']
        })

        return pd.DataFrame(scenarios)

    # ========== REPORTING ==========

    def generate_financial_dashboard(self) -> Dict:
        """
        Generate KPIs for financial dashboard.

        Returns:
            Dictionary with dashboard metrics
        """
        roi_metrics = self.calculate_roi_metrics(10)
        tco = self.calculate_tco_detailed(10)
        breakeven = self.break_even_analysis()

        # Calculate cost per test
        total_tests = self.revenue.tests_per_year * 10
        cost_per_test = tco['cumulative_cost'].iloc[-1] / total_tests

        # Energy cost per test
        energy_per_test = self.opex.energy_cost / self.revenue.tests_per_year

        # Utilization rate (assume chamber operates 8 hours/day, 250 days/year)
        # Each test takes ~10 hours on average
        available_hours = 8 * 250
        test_hours = self.revenue.tests_per_year * 10
        utilization_rate = (test_hours / available_hours) * 100

        return {
            'payback_period_years': roi_metrics['payback_period'],
            'roi_annual_percent': roi_metrics['annual_roi'],
            'npv': roi_metrics['npv'],
            'irr_percent': roi_metrics['irr'] * 100 if roi_metrics['irr'] else 0,
            'cost_per_test': cost_per_test,
            'energy_cost_per_test': energy_per_test,
            'utilization_rate_percent': utilization_rate,
            'tco_10_year': tco['cumulative_cost'].iloc[-1],
            'total_revenue_10_year': roi_metrics['total_revenue'],
            'break_even_tests': breakeven['break_even_tests']
        }

    def generate_investment_justification(self) -> Dict:
        """
        Generate comprehensive investment justification report data.

        Returns:
            Dictionary with report sections
        """
        dashboard = self.generate_financial_dashboard()
        roi_metrics = self.calculate_roi_metrics(10)
        tco = self.calculate_tco_detailed(10)
        scenarios = self.scenario_analysis()
        monte_carlo = self.monte_carlo_simulation(1000)

        return {
            'executive_summary': {
                'npv': roi_metrics['npv'],
                'irr': roi_metrics['irr'],
                'payback_period': roi_metrics['payback_period'],
                'roi_10_year': roi_metrics['roi_percent'],
                'recommendation': 'APPROVED' if roi_metrics['npv'] > 0 else 'REVIEW'
            },
            'financial_analysis': {
                'capex': self.breakdown_capex(),
                'tco_10_year': tco.to_dict('records'),
                'roi_metrics': roi_metrics,
                'dashboard_kpis': dashboard
            },
            'risk_analysis': {
                'scenarios': scenarios.to_dict('records'),
                'monte_carlo': monte_carlo,
                'probability_success': monte_carlo['probability_positive_npv']
            },
            'generated_date': datetime.now().isoformat()
        }

    def export_to_excel(self, output_path: str):
        """
        Export comprehensive analysis to Excel file.

        Args:
            output_path: Path for output Excel file
        """
        with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
            # TCO Analysis
            tco_df = self.calculate_tco_detailed(10)
            tco_df.to_excel(writer, sheet_name='TCO Analysis', index=False)

            # ROI Metrics
            roi = self.calculate_roi_metrics(10)
            roi_df = pd.DataFrame([{
                'NPV': roi['npv'],
                'IRR': roi['irr'],
                'Payback Period': roi['payback_period'],
                'ROI %': roi['roi_percent']
            }])
            roi_df.to_excel(writer, sheet_name='ROI Metrics', index=False)

            # Annual Cash Flows
            cash_flow_df = pd.DataFrame(roi['annual_data'])
            cash_flow_df.to_excel(writer, sheet_name='Cash Flows', index=False)

            # Scenario Analysis
            scenarios_df = self.scenario_analysis()
            scenarios_df.to_excel(writer, sheet_name='Scenarios', index=False)

            # Dashboard KPIs
            dashboard = self.generate_financial_dashboard()
            dashboard_df = pd.DataFrame([dashboard])
            dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)

            # CAPEX Breakdown
            capex = self.breakdown_capex()
            capex_df = pd.DataFrame([capex])
            capex_df.to_excel(writer, sheet_name='CAPEX', index=False)

    def load_from_json(self, file_path: str):
        """
        Load configuration from JSON file.

        Args:
            file_path: Path to JSON configuration file
        """
        with open(file_path, 'r') as f:
            config = json.load(f)

        if 'chamber_config' in config:
            self.chamber = ChamberConfig(**config['chamber_config'])
        if 'operating_costs' in config:
            self.opex = OperatingCosts(**config['operating_costs'])
        if 'revenue_params' in config:
            self.revenue = RevenueParams(**config['revenue_params'])
        if 'financial_assumptions' in config:
            self.assumptions = FinancialAssumptions(**config['financial_assumptions'])

    def save_to_json(self, file_path: str):
        """
        Save configuration to JSON file.

        Args:
            file_path: Path for output JSON file
        """
        config = {
            'chamber_config': asdict(self.chamber),
            'operating_costs': asdict(self.opex),
            'revenue_params': asdict(self.revenue),
            'financial_assumptions': asdict(self.assumptions)
        }

        with open(file_path, 'w') as f:
            json.dump(config, f, indent=2)
