"""
Financial Calculator Module
Provides utilities for NPV, IRR, payback period, and other financial calculations.
"""

import numpy as np
from typing import List, Tuple, Optional


def calculate_npv(cash_flows: List[float], discount_rate: float) -> float:
    """
    Calculate Net Present Value (NPV) of cash flows.

    Args:
        cash_flows: List of cash flows where cash_flows[0] is initial investment (negative)
        discount_rate: Annual discount rate (e.g., 0.10 for 10%)

    Returns:
        NPV in the same currency as cash flows

    Example:
        >>> cash_flows = [-1000000, 200000, 250000, 300000]
        >>> calculate_npv(cash_flows, 0.10)
        -359328.33
    """
    npv = 0.0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** t)
    return npv


def calculate_irr(cash_flows: List[float], initial_guess: float = 0.1) -> Optional[float]:
    """
    Calculate Internal Rate of Return (IRR) using Newton-Raphson method.

    Args:
        cash_flows: List of cash flows where cash_flows[0] is initial investment (negative)
        initial_guess: Starting guess for IRR (default 0.1)

    Returns:
        IRR as decimal (e.g., 0.15 for 15%) or None if not found

    Example:
        >>> cash_flows = [-1000000, 300000, 350000, 400000, 450000]
        >>> calculate_irr(cash_flows)
        0.156
    """
    # Newton-Raphson method for finding IRR
    rate = initial_guess
    max_iterations = 100
    tolerance = 1e-6

    for _ in range(max_iterations):
        # Calculate NPV at current rate
        npv = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))

        # Calculate derivative (dNPV/dr)
        dnpv = sum(-t * cf / ((1 + rate) ** (t + 1)) for t, cf in enumerate(cash_flows))

        # Check convergence
        if abs(npv) < tolerance:
            return rate

        # Newton-Raphson update
        if abs(dnpv) < 1e-10:
            return None  # Derivative too small

        rate = rate - npv / dnpv

        # Check bounds
        if rate < -0.99 or rate > 10:
            return None  # IRR outside reasonable range

    return None  # Did not converge


def calculate_payback_period(initial_investment: float, cash_flows: List[float]) -> Optional[float]:
    """
    Calculate payback period in years (including fractional years).

    Args:
        initial_investment: Initial investment (positive value)
        cash_flows: Annual cash flows (positive values)

    Returns:
        Payback period in years or None if never paid back

    Example:
        >>> calculate_payback_period(1000000, [300000, 350000, 400000])
        2.875
    """
    cumulative = 0.0

    for year, cf in enumerate(cash_flows):
        cumulative += cf

        if cumulative >= initial_investment:
            # Interpolate for fractional year
            excess = cumulative - initial_investment
            fraction = 1 - (excess / cf)
            return year + fraction

    return None  # Not paid back within period


def calculate_simple_payback(initial_investment: float, annual_cash_flow: float) -> float:
    """
    Calculate simple payback period assuming constant annual cash flow.

    Args:
        initial_investment: Initial investment (positive value)
        annual_cash_flow: Annual cash flow (positive value)

    Returns:
        Payback period in years

    Example:
        >>> calculate_simple_payback(1000000, 250000)
        4.0
    """
    if annual_cash_flow <= 0:
        return float('inf')
    return initial_investment / annual_cash_flow


def present_value(future_value: float, rate: float, periods: int) -> float:
    """
    Calculate present value of a future amount.

    Args:
        future_value: Future value to discount
        rate: Discount rate per period (e.g., 0.10 for 10%)
        periods: Number of periods

    Returns:
        Present value

    Example:
        >>> present_value(1000000, 0.10, 5)
        620921.32
    """
    return future_value / ((1 + rate) ** periods)


def future_value(present_value_amt: float, rate: float, periods: int) -> float:
    """
    Calculate future value of a present amount.

    Args:
        present_value_amt: Present value to compound
        rate: Growth rate per period (e.g., 0.10 for 10%)
        periods: Number of periods

    Returns:
        Future value

    Example:
        >>> future_value(1000000, 0.10, 5)
        1610510.00
    """
    return present_value_amt * ((1 + rate) ** periods)


def calculate_roi_percentage(total_benefits: float, total_costs: float) -> float:
    """
    Calculate ROI as a percentage.

    Args:
        total_benefits: Total benefits over period
        total_costs: Total costs (initial + operating)

    Returns:
        ROI as percentage (e.g., 25.5 for 25.5%)

    Example:
        >>> calculate_roi_percentage(2000000, 1500000)
        33.33
    """
    if total_costs == 0:
        return 0.0
    return ((total_benefits - total_costs) / total_costs) * 100


def calculate_annual_roi(total_benefits: float, total_costs: float, years: int) -> float:
    """
    Calculate annualized ROI.

    Args:
        total_benefits: Total benefits over period
        total_costs: Total costs
        years: Number of years

    Returns:
        Annualized ROI as percentage

    Example:
        >>> calculate_annual_roi(2000000, 1500000, 5)
        6.67
    """
    total_roi = calculate_roi_percentage(total_benefits, total_costs)
    if years == 0:
        return 0.0
    return total_roi / years


def break_even_units(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> float:
    """
    Calculate break-even point in units.

    Args:
        fixed_costs: Fixed costs
        price_per_unit: Revenue per unit
        variable_cost_per_unit: Variable cost per unit

    Returns:
        Number of units to break even

    Example:
        >>> break_even_units(1000000, 25000, 5000)
        50.0
    """
    contribution_margin = price_per_unit - variable_cost_per_unit
    if contribution_margin <= 0:
        return float('inf')
    return fixed_costs / contribution_margin


def escalate_cost(base_cost: float, escalation_rate: float, year: int) -> float:
    """
    Calculate escalated cost for a future year.

    Args:
        base_cost: Base cost in year 0
        escalation_rate: Annual escalation rate (e.g., 0.05 for 5%)
        year: Year number (0-indexed)

    Returns:
        Escalated cost

    Example:
        >>> escalate_cost(100000, 0.05, 3)
        115762.50
    """
    return base_cost * ((1 + escalation_rate) ** year)


def calculate_cagr(beginning_value: float, ending_value: float, years: int) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Args:
        beginning_value: Starting value
        ending_value: Ending value
        years: Number of years

    Returns:
        CAGR as decimal (e.g., 0.15 for 15%)

    Example:
        >>> calculate_cagr(1000000, 2000000, 5)
        0.1487
    """
    if beginning_value <= 0 or years <= 0:
        return 0.0
    return (ending_value / beginning_value) ** (1 / years) - 1


def annuity_present_value(payment: float, rate: float, periods: int) -> float:
    """
    Calculate present value of an annuity (equal periodic payments).

    Args:
        payment: Payment amount per period
        rate: Discount rate per period
        periods: Number of periods

    Returns:
        Present value of annuity

    Example:
        >>> annuity_present_value(100000, 0.10, 10)
        614457.13
    """
    if rate == 0:
        return payment * periods
    return payment * (1 - (1 + rate) ** -periods) / rate


def calculate_depreciation_straight_line(
    cost: float,
    salvage_value: float,
    useful_life: int,
    year: int
) -> Tuple[float, float]:
    """
    Calculate straight-line depreciation for a given year.

    Args:
        cost: Initial cost of asset
        salvage_value: Salvage value at end of life
        useful_life: Useful life in years
        year: Year for depreciation (1-indexed)

    Returns:
        Tuple of (annual_depreciation, accumulated_depreciation)

    Example:
        >>> calculate_depreciation_straight_line(1000000, 100000, 10, 5)
        (90000.0, 450000.0)
    """
    annual_depreciation = (cost - salvage_value) / useful_life
    accumulated_depreciation = annual_depreciation * min(year, useful_life)
    return annual_depreciation, accumulated_depreciation


def calculate_loan_payment(principal: float, annual_rate: float, years: int) -> float:
    """
    Calculate monthly loan payment using amortization formula.

    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate (e.g., 0.10 for 10%)
        years: Loan term in years

    Returns:
        Monthly payment amount

    Example:
        >>> calculate_loan_payment(1000000, 0.10, 5)
        21247.04
    """
    if annual_rate == 0:
        return principal / (years * 12)

    monthly_rate = annual_rate / 12
    num_payments = years * 12

    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)

    return payment
