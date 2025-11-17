# Business Analysis & ROI Calculator - Technical Documentation

## Overview

The Business Analysis module provides comprehensive financial analysis tools for evaluating the investment in a UV+TC+HF+DH environmental test chamber for PV module testing. This module enables data-driven decision-making through detailed Total Cost of Ownership (TCO), Return on Investment (ROI), competitive comparison, and risk analysis.

**Version:** 1.0
**Last Updated:** 2025-11-17

---

## Table of Contents

1. [Methodology](#methodology)
2. [Financial Metrics](#financial-metrics)
3. [Formulas & Calculations](#formulas--calculations)
4. [Assumptions](#assumptions)
5. [Usage Guide](#usage-guide)
6. [Interpretation Guide](#interpretation-guide)
7. [API Reference](#api-reference)

---

## Methodology

### Total Cost of Ownership (TCO)

TCO analysis captures all costs associated with acquiring, operating, and disposing of the chamber over a 10-year period.

**Components:**

1. **Capital Expenditure (CAPEX)** - Year 0
   - Equipment cost
   - Installation and commissioning
   - Training costs
   - Initial spare parts inventory
   - Initial calibration

2. **Operating Expenditure (OPEX)** - Years 1-10
   - Energy costs (electricity, cooling water)
   - Preventive maintenance (labor + parts)
   - Annual calibration (ISO 17025 certification)
   - Consumables (UV lamps, filters, refrigerants)
   - Insurance premiums
   - Operator salaries (if dedicated)
   - Downtime costs

3. **End-of-Life Costs** - Year 10
   - Disposal/recycling costs

**Cost Escalation:**
- Energy costs: 5% per annum
- Maintenance costs: 4% per annum
- Other costs: 6% per annum (general inflation)

### Return on Investment (ROI)

ROI analysis evaluates the financial returns from the chamber investment.

**Revenue Sources:**
1. **Testing Revenue** - Direct revenue from tests performed
2. **Outsourcing Savings** - Cost avoided by not outsourcing tests
3. **Quality Improvement Savings** - Reduced failures, faster time-to-market

**Key Metrics:**
- Net Present Value (NPV)
- Internal Rate of Return (IRR)
- Payback Period
- Total ROI (%)
- Cost per test

---

## Financial Metrics

### 1. Net Present Value (NPV)

**Definition:** The present value of all future cash flows, discounted at the cost of capital.

**Decision Rule:**
- NPV > 0: Investment adds value (ACCEPT)
- NPV = 0: Investment breaks even
- NPV < 0: Investment destroys value (REJECT)

**Typical Range:** ₹10M to ₹30M (positive)

### 2. Internal Rate of Return (IRR)

**Definition:** The discount rate at which NPV equals zero; the effective annual return on investment.

**Decision Rule:**
- IRR > Cost of Capital: Investment is attractive (ACCEPT)
- IRR = Cost of Capital: Investment breaks even
- IRR < Cost of Capital: Investment is unattractive (REJECT)

**Typical Range:** 15% - 40%

### 3. Payback Period

**Definition:** The time required to recover the initial investment from cash flows.

**Decision Rule:**
- < 2 years: Excellent
- 2-3 years: Very good
- 3-5 years: Good
- > 5 years: Review carefully

**Typical Range:** 2.5 - 4.0 years

### 4. ROI Percentage

**Definition:** Total return as a percentage of total investment.

**Formula:** ROI% = (Total Benefits - Total Costs) / Total Costs × 100

**Decision Rule:**
- > 100%: Excellent (investment doubles)
- 50-100%: Very good
- 25-50%: Good
- < 25%: Review

**Typical Range:** 40% - 120% (10-year)

### 5. Cost per Test

**Definition:** Total cost of ownership divided by total tests over lifetime.

**Benchmark:**
- In-house chamber: ₹6,000 - ₹8,000 per test
- Outsourced testing: ₹35,000 per test
- **Savings:** ~75-80%

---

## Formulas & Calculations

### 1. Net Present Value (NPV)

```
NPV = Σ [CFt / (1 + r)^t]

Where:
- CFt = Cash flow in year t
- r = Discount rate (WACC)
- t = Year (0 to 10)
```

**Example:**
```
Year 0: -₹9,650,000 (CAPEX)
Year 1-10: ₹3,615,000 average annual net cash flow
Discount rate: 10%

NPV = -9,650,000 + Σ(3,615,000 / (1.10)^t)
    ≈ ₹12,545,000
```

### 2. Internal Rate of Return (IRR)

```
0 = Σ [CFt / (1 + IRR)^t]

Solved iteratively using Newton-Raphson method
```

**Calculation Method:**
1. Start with initial guess (e.g., 10%)
2. Calculate NPV at guess rate
3. Calculate derivative (dNPV/dr)
4. Update guess: new_rate = old_rate - NPV/derivative
5. Repeat until NPV ≈ 0

### 3. Payback Period

```
Payback = Year when Σ(Cash Flows) ≥ Initial Investment

With interpolation for fractional year:
Payback = Last_Full_Year + (Remaining / CF_Next_Year)
```

**Example:**
```
Initial Investment: ₹9,650,000
Year 1 CF: ₹3,200,000 (Cumulative: ₹3,200,000)
Year 2 CF: ₹3,400,000 (Cumulative: ₹6,600,000)
Year 3 CF: ₹3,615,000 (Cumulative: ₹10,215,000)

Payback = 2 + (9,650,000 - 6,600,000) / 3,615,000
        = 2.84 years
```

### 4. Cost Escalation

```
Future_Cost = Base_Cost × (1 + escalation_rate)^years

Energy (Year 5) = ₹180,000 × (1.05)^5 = ₹229,729
```

### 5. Break-Even Analysis

```
Break_Even_Units = Fixed_Costs / (Price - Variable_Cost)

Fixed Costs: ₹1,350,000/year (amortized CAPEX + fixed OPEX)
Price per test: ₹25,000
Variable cost per test: ₹900 (energy)

Break_Even = 1,350,000 / (25,000 - 900) ≈ 56 tests/year
```

### 6. Depreciation (Straight-Line)

```
Annual_Depreciation = (Cost - Salvage_Value) / Useful_Life

Cost: ₹8,500,000
Salvage (10%): ₹850,000
Life: 10 years

Annual_Depreciation = (8,500,000 - 850,000) / 10 = ₹765,000/year
```

---

## Assumptions

### Financial Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Discount Rate (WACC)** | 10% | Corporate cost of capital in India |
| **Inflation Rate** | 6% | India CPI average |
| **Energy Escalation** | 5% | Historical electricity price trends |
| **Maintenance Escalation** | 4% | Labor and parts inflation |
| **Tax Rate** | 25% | Corporate tax rate (India) |
| **Equipment Lifetime** | 10 years | Industry standard for chambers |
| **Salvage Value** | 10% | Residual value after 10 years |

### Operational Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Tests per Year** | 200 | Based on 4 tests/week, 50 weeks |
| **Test Duration** | 10 hours | Average across IEC 61215/61730 |
| **Operating Hours** | 2,000 hrs/yr | Single-shift operation |
| **Utilization Rate** | 50% | Conservative estimate |
| **Downtime** | 80 hrs/yr | 40 hrs planned + 40 hrs unplanned |

### Cost Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| **Equipment Cost** | ₹8,500,000 | Supplier quotation |
| **Energy Rate** | ₹8/kWh | Industrial tariff (Tamil Nadu) |
| **Outsource Cost/Test** | ₹35,000 | Market rate (external labs) |
| **Operator Salary** | ₹600,000/yr | Market rate for technician |

---

## Usage Guide

### 1. Basic Analysis

```python
from modules.business_analysis_enhanced import BusinessAnalysisEnhanced

# Initialize with default parameters
analysis = BusinessAnalysisEnhanced()

# Calculate TCO
tco_df = analysis.calculate_tco_detailed(years=10)
print(f"10-Year TCO: ₹{tco_df['cumulative_cost'].iloc[-1]:,.0f}")

# Calculate ROI metrics
roi = analysis.calculate_roi_metrics(years=10)
print(f"NPV: ₹{roi['npv']:,.0f}")
print(f"IRR: {roi['irr']*100:.1f}%")
print(f"Payback: {roi['payback_period']:.2f} years")
```

### 2. Custom Configuration

```python
from modules.business_analysis_enhanced import (
    BusinessAnalysisEnhanced,
    ChamberConfig,
    OperatingCosts,
    RevenueParams,
    FinancialAssumptions
)

# Custom chamber config
chamber = ChamberConfig(
    equipment_cost=9000000,  # ₹90 lakhs
    installation_cost=550000,
    expected_lifetime_years=12
)

# Custom operating costs
opex = OperatingCosts(
    energy_cost=200000,  # ₹2 lakhs/year
    maintenance_cost=280000
)

# Custom revenue
revenue = RevenueParams(
    tests_per_year=250,  # Higher volume
    revenue_per_test=30000  # Higher price
)

# Initialize
analysis = BusinessAnalysisEnhanced(
    chamber_config=chamber,
    operating_costs=opex,
    revenue_params=revenue
)

# Run analysis
roi = analysis.calculate_roi_metrics(10)
```

### 3. Sensitivity Analysis

```python
# Analyze impact of test volume
sens_df = analysis.sensitivity_analysis('test_volume', range_percent=30)

# Tornado chart (all variables)
tornado_df = analysis.tornado_chart_data()
print(tornado_df.sort_values('impact', ascending=False))
```

### 4. Monte Carlo Simulation

```python
# Run 1000 iterations
mc_results = analysis.monte_carlo_simulation(iterations=1000)

print(f"Mean NPV: ₹{mc_results['npv_mean']:,.0f}")
print(f"Std Dev: ₹{mc_results['npv_std']:,.0f}")
print(f"P10: ₹{mc_results['npv_p10']:,.0f}")
print(f"P90: ₹{mc_results['npv_p90']:,.0f}")
print(f"Success Probability: {mc_results['probability_positive_npv']:.1f}%")
```

### 5. Export to Excel

```python
# Export comprehensive analysis
analysis.export_to_excel('business_analysis_report.xlsx')
```

---

## Interpretation Guide

### NPV Interpretation

| NPV Range | Interpretation | Action |
|-----------|----------------|--------|
| > ₹20M | Highly attractive | Strongly recommend |
| ₹10M - ₹20M | Attractive | Recommend |
| ₹5M - ₹10M | Marginally attractive | Recommend with conditions |
| ₹0 - ₹5M | Weak case | Review assumptions carefully |
| < ₹0 | Negative value | Not recommended |

### IRR Interpretation

| IRR Range | Interpretation | Decision |
|-----------|----------------|----------|
| > 30% | Exceptional | Approve immediately |
| 20% - 30% | Excellent | Approve |
| 15% - 20% | Good | Approve if strategic fit |
| 10% - 15% | Acceptable | Review carefully |
| < 10% | Below hurdle rate | Reject |

### Sensitivity Analysis Interpretation

**Tornado Chart Rankings:**

1. **Test Volume** - Highest impact
   - Focus on maximizing utilization
   - Marketing and sales critical

2. **Revenue per Test** - High impact
   - Pricing strategy important
   - Value-added services

3. **Energy Price** - Medium impact
   - Hedge with efficiency upgrades
   - Consider solar integration

4. **Maintenance Cost** - Medium impact
   - Preventive maintenance program
   - Warranty optimization

5. **Equipment Cost** - Lower impact
   - One-time impact
   - Negotiate carefully but not critical

### Risk Assessment (Monte Carlo)

| Success Probability | Risk Level | Recommendation |
|---------------------|------------|----------------|
| > 90% | Very Low Risk | Proceed with confidence |
| 75% - 90% | Low Risk | Proceed |
| 60% - 75% | Moderate Risk | Proceed with risk mitigation |
| 40% - 60% | High Risk | Review carefully |
| < 40% | Very High Risk | Not recommended |

---

## API Reference

### BusinessAnalysisEnhanced Class

#### Methods

**TCO Analysis:**
- `breakdown_capex()` → Dict[str, float]
- `calculate_annual_opex(year: int)` → Dict[str, float]
- `calculate_tco_detailed(years: int)` → pd.DataFrame
- `estimate_downtime_cost(hours_per_year: float)` → float

**ROI Calculation:**
- `calculate_roi_metrics(years: int)` → Dict
- `break_even_analysis()` → Dict

**Competitive Analysis:**
- `compare_with_competitors(competitor_data: List[Dict])` → pd.DataFrame
- `compare_with_outsourcing()` → Dict

**Sensitivity & Risk:**
- `sensitivity_analysis(variable: str, range_percent: float)` → pd.DataFrame
- `tornado_chart_data()` → pd.DataFrame
- `monte_carlo_simulation(iterations: int)` → Dict
- `scenario_analysis()` → pd.DataFrame

**Reporting:**
- `generate_financial_dashboard()` → Dict
- `generate_investment_justification()` → Dict
- `export_to_excel(output_path: str)` → None

### Financial Calculator Functions

```python
from modules.financial_calculator import (
    calculate_npv,
    calculate_irr,
    calculate_payback_period,
    calculate_roi_percentage,
    escalate_cost,
    present_value,
    future_value,
    break_even_units,
    calculate_depreciation_straight_line
)
```

---

## Best Practices

### 1. Data Quality
- Use actual supplier quotations for equipment costs
- Verify energy tariffs with utility provider
- Validate maintenance costs with similar chambers
- Use conservative revenue estimates

### 2. Assumption Validation
- Document all assumptions clearly
- Sensitivity test critical assumptions
- Update assumptions annually
- Benchmark against industry standards

### 3. Scenario Planning
- Always run Best/Expected/Worst scenarios
- Focus management attention on Expected case
- Use Best case for opportunity planning
- Use Worst case for risk mitigation

### 4. Reporting
- Lead with executive summary (NPV, IRR, Payback)
- Show visual dashboards before detailed tables
- Highlight key risks and sensitivities
- Provide clear recommendation with rationale

### 5. Updates
- Review assumptions quarterly
- Update analysis with actual costs annually
- Recalculate NPV with actual cash flows
- Adjust forecasts based on actuals

---

## References

### Standards & Guidelines
- IEC 61215: PV module design qualification and type approval
- IEC 61730: PV module safety qualification
- ISO 17025: Calibration and testing laboratory requirements

### Financial Methods
- Capital Budgeting Techniques (Brealey & Myers)
- NPV/IRR Analysis (Corporate Finance textbooks)
- Monte Carlo Simulation (Risk Analysis methodologies)

### Industry Benchmarks
- Environmental chamber manufacturers (Espec, Weiss, Binder)
- PV testing service providers
- Energy cost trends (India)

---

## Troubleshooting

### Common Issues

**1. Negative NPV**
- Check discount rate (may be too high)
- Verify revenue assumptions (may be too conservative)
- Review cost escalation rates
- Consider longer analysis period

**2. IRR Not Converging**
- Check cash flow pattern (should have sign change)
- Verify initial investment is negative
- Try different initial guess
- May indicate multiple IRRs (non-conventional cash flows)

**3. Unrealistic Payback Period**
- Verify annual cash flows are positive
- Check revenue and cost assumptions
- Ensure escalation is applied correctly

**4. Monte Carlo Results Too Variable**
- Check distribution parameters (std dev may be too high)
- Increase number of iterations
- Review input variable ranges

---

## Support

For questions or issues with the business analysis module:

1. Check this documentation
2. Review test cases in `tests/test_business_analysis_enhanced.py`
3. Examine example configurations in `data/financial_assumptions.json`
4. Contact: info@zenitek.com

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Author:** PV Chamber Configurator Team
