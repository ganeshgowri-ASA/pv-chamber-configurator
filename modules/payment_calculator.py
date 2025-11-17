"""
Payment Calculator Module for PV Chamber Configurator
Payment schedule calculation, currency conversion, and interest calculations
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional


# Exchange rates (approximate, should be updated from API in production)
EXCHANGE_RATES = {
    'INR': 1.0,
    'USD': 0.012,  # 1 INR = 0.012 USD
    'EUR': 0.011,  # 1 INR = 0.011 EUR
    'GBP': 0.0095,  # 1 INR = 0.0095 GBP
    'AED': 0.044,  # 1 INR = 0.044 AED
    'SGD': 0.016,  # 1 INR = 0.016 SGD
}


def calculate_payment_schedule(
    total: float,
    terms: str,
    currency: str = 'INR',
    order_date: Optional[datetime] = None
) -> List[Dict]:
    """
    Calculate payment schedule based on payment terms

    Args:
        total: Total amount
        terms: Payment terms string
        currency: Currency code
        order_date: Order date (defaults to today)

    Returns:
        List of payment milestone dictionaries
    """
    if order_date is None:
        order_date = datetime.now()

    schedule = []
    currency_symbol = '₹' if currency == 'INR' else currency

    # Standard payment terms
    if terms == '100% advance':
        schedule.append({
            'milestone': 'Order Confirmation',
            'percentage': 100.0,
            'amount': total,
            'due_date': order_date.strftime('%Y-%m-%d'),
            'description': '100% payment in advance'
        })

    elif terms == '50% advance, 50% on delivery':
        schedule.append({
            'milestone': 'Order Confirmation',
            'percentage': 50.0,
            'amount': total * 0.5,
            'due_date': order_date.strftime('%Y-%m-%d'),
            'description': '50% advance payment'
        })
        delivery_date = order_date + timedelta(weeks=14)
        schedule.append({
            'milestone': 'On Delivery',
            'percentage': 50.0,
            'amount': total * 0.5,
            'due_date': delivery_date.strftime('%Y-%m-%d'),
            'description': '50% before delivery'
        })

    elif terms == '30% advance, 40% on delivery, 30% after installation':
        schedule.append({
            'milestone': 'Order Confirmation',
            'percentage': 30.0,
            'amount': total * 0.3,
            'due_date': order_date.strftime('%Y-%m-%d'),
            'description': '30% advance payment'
        })
        delivery_date = order_date + timedelta(weeks=14)
        schedule.append({
            'milestone': 'On Delivery',
            'percentage': 40.0,
            'amount': total * 0.4,
            'due_date': delivery_date.strftime('%Y-%m-%d'),
            'description': '40% before delivery'
        })
        installation_date = delivery_date + timedelta(weeks=2)
        schedule.append({
            'milestone': 'After Installation',
            'percentage': 30.0,
            'amount': total * 0.3,
            'due_date': installation_date.strftime('%Y-%m-%d'),
            'description': '30% after successful installation'
        })

    elif terms == '30 days credit':
        due_date = order_date + timedelta(days=30)
        schedule.append({
            'milestone': 'Net 30 Days',
            'percentage': 100.0,
            'amount': total,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'description': 'Full payment due within 30 days'
        })

    elif terms == '60 days credit':
        due_date = order_date + timedelta(days=60)
        schedule.append({
            'milestone': 'Net 60 Days',
            'percentage': 100.0,
            'amount': total,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'description': 'Full payment due within 60 days'
        })

    elif terms == '90 days credit':
        due_date = order_date + timedelta(days=90)
        schedule.append({
            'milestone': 'Net 90 Days',
            'percentage': 100.0,
            'amount': total,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'description': 'Full payment due within 90 days'
        })

    else:
        # Default: 100% advance
        schedule.append({
            'milestone': 'Order Confirmation',
            'percentage': 100.0,
            'amount': total,
            'due_date': order_date.strftime('%Y-%m-%d'),
            'description': 'Custom payment terms - contact sales'
        })

    return schedule


def calculate_custom_payment_schedule(
    total: float,
    milestones: List[Dict],
    currency: str = 'INR'
) -> List[Dict]:
    """
    Calculate custom payment schedule

    Args:
        total: Total amount
        milestones: List of milestone dicts with 'name', 'percentage', 'days_from_order'
        currency: Currency code

    Returns:
        List of payment milestone dictionaries
    """
    schedule = []
    order_date = datetime.now()
    currency_symbol = '₹' if currency == 'INR' else currency

    for milestone in milestones:
        due_date = order_date + timedelta(days=milestone.get('days_from_order', 0))
        percentage = milestone['percentage']
        amount = total * (percentage / 100)

        schedule.append({
            'milestone': milestone['name'],
            'percentage': percentage,
            'amount': amount,
            'due_date': due_date.strftime('%Y-%m-%d'),
            'description': milestone.get('description', f'{percentage}% payment')
        })

    return schedule


def calculate_late_payment_interest(
    amount: float,
    days_late: int,
    annual_rate: float = 18.0,
    currency: str = 'INR'
) -> Dict:
    """
    Calculate late payment interest

    Args:
        amount: Principal amount
        days_late: Number of days payment is overdue
        annual_rate: Annual interest rate percentage
        currency: Currency code

    Returns:
        Dictionary with interest calculation details
    """
    # Calculate daily interest rate
    daily_rate = annual_rate / 365 / 100

    # Calculate interest
    interest = amount * daily_rate * days_late

    # Calculate total amount due
    total_due = amount + interest

    currency_symbol = '₹' if currency == 'INR' else currency

    return {
        'principal': amount,
        'days_late': days_late,
        'annual_rate': annual_rate,
        'interest': interest,
        'total_due': total_due,
        'currency': currency,
        'currency_symbol': currency_symbol,
        'formatted': {
            'principal': f"{currency_symbol}{amount:,.2f}",
            'interest': f"{currency_symbol}{interest:,.2f}",
            'total_due': f"{currency_symbol}{total_due:,.2f}"
        }
    }


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> Dict:
    """
    Convert amount between currencies

    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code

    Returns:
        Dictionary with conversion details
    """
    if from_currency not in EXCHANGE_RATES:
        raise ValueError(f"Unsupported currency: {from_currency}")

    if to_currency not in EXCHANGE_RATES:
        raise ValueError(f"Unsupported currency: {to_currency}")

    # Convert to INR first, then to target currency
    amount_in_inr = amount / EXCHANGE_RATES[from_currency]
    converted_amount = amount_in_inr * EXCHANGE_RATES[to_currency]

    exchange_rate = EXCHANGE_RATES[to_currency] / EXCHANGE_RATES[from_currency]

    from_symbol = '₹' if from_currency == 'INR' else from_currency
    to_symbol = '₹' if to_currency == 'INR' else to_currency

    return {
        'original_amount': amount,
        'from_currency': from_currency,
        'to_currency': to_currency,
        'converted_amount': converted_amount,
        'exchange_rate': exchange_rate,
        'formatted': {
            'original': f"{from_symbol}{amount:,.2f}",
            'converted': f"{to_symbol}{converted_amount:,.2f}",
            'rate': f"1 {from_currency} = {exchange_rate:.6f} {to_currency}"
        }
    }


def calculate_installment_plan(
    total: float,
    num_installments: int,
    currency: str = 'INR',
    first_payment_date: Optional[datetime] = None,
    frequency: str = 'monthly'
) -> List[Dict]:
    """
    Calculate equal installment payment plan

    Args:
        total: Total amount
        num_installments: Number of installments
        currency: Currency code
        first_payment_date: Date of first payment
        frequency: Payment frequency ('weekly', 'monthly', 'quarterly')

    Returns:
        List of installment dictionaries
    """
    if first_payment_date is None:
        first_payment_date = datetime.now()

    installment_amount = total / num_installments
    currency_symbol = '₹' if currency == 'INR' else currency

    # Determine days between payments
    if frequency == 'weekly':
        days_between = 7
    elif frequency == 'monthly':
        days_between = 30
    elif frequency == 'quarterly':
        days_between = 90
    else:
        days_between = 30  # default to monthly

    installments = []
    for i in range(num_installments):
        payment_date = first_payment_date + timedelta(days=i * days_between)
        installments.append({
            'installment_number': i + 1,
            'amount': installment_amount,
            'due_date': payment_date.strftime('%Y-%m-%d'),
            'description': f'Installment {i + 1} of {num_installments}',
            'formatted_amount': f"{currency_symbol}{installment_amount:,.2f}"
        })

    return installments


def get_payment_term_options() -> List[Dict]:
    """
    Get standard payment term options

    Returns:
        List of payment term option dictionaries
    """
    return [
        {
            'value': '100% advance',
            'label': '100% Advance Payment',
            'description': 'Full payment required before order processing',
            'risk_level': 'low',
            'recommended_for': 'New customers, international orders'
        },
        {
            'value': '50% advance, 50% on delivery',
            'label': '50-50 Payment',
            'description': '50% advance, 50% before delivery',
            'risk_level': 'medium',
            'recommended_for': 'Established customers'
        },
        {
            'value': '30% advance, 40% on delivery, 30% after installation',
            'label': '30-40-30 Payment',
            'description': '30% advance, 40% on delivery, 30% after installation',
            'risk_level': 'medium',
            'recommended_for': 'Long-term customers, large orders'
        },
        {
            'value': '30 days credit',
            'label': 'Net 30 Days',
            'description': 'Full payment due within 30 days',
            'risk_level': 'high',
            'recommended_for': 'Trusted corporate customers'
        },
        {
            'value': '60 days credit',
            'label': 'Net 60 Days',
            'description': 'Full payment due within 60 days',
            'risk_level': 'high',
            'recommended_for': 'Premium corporate customers'
        },
        {
            'value': '90 days credit',
            'label': 'Net 90 Days',
            'description': 'Full payment due within 90 days',
            'risk_level': 'very high',
            'recommended_for': 'Strategic partners only'
        }
    ]


def calculate_discount_impact(
    subtotal: float,
    discount_percent: float,
    tax_rate: float = 18.0,
    currency: str = 'INR'
) -> Dict:
    """
    Calculate the impact of discount on final pricing

    Args:
        subtotal: Subtotal amount before discount
        discount_percent: Discount percentage
        tax_rate: Tax rate percentage
        currency: Currency code

    Returns:
        Dictionary with discount impact analysis
    """
    discount_amount = subtotal * (discount_percent / 100)
    taxable_amount = subtotal - discount_amount
    tax_amount = taxable_amount * (tax_rate / 100)

    total_without_discount = subtotal + (subtotal * tax_rate / 100)
    total_with_discount = taxable_amount + tax_amount

    savings = total_without_discount - total_with_discount

    currency_symbol = '₹' if currency == 'INR' else currency

    return {
        'subtotal': subtotal,
        'discount_percent': discount_percent,
        'discount_amount': discount_amount,
        'taxable_amount': taxable_amount,
        'tax_amount': tax_amount,
        'total_without_discount': total_without_discount,
        'total_with_discount': total_with_discount,
        'total_savings': savings,
        'savings_percent': (savings / total_without_discount * 100),
        'currency': currency,
        'formatted': {
            'subtotal': f"{currency_symbol}{subtotal:,.2f}",
            'discount': f"-{currency_symbol}{discount_amount:,.2f}",
            'tax': f"{currency_symbol}{tax_amount:,.2f}",
            'total_with_discount': f"{currency_symbol}{total_with_discount:,.2f}",
            'savings': f"{currency_symbol}{savings:,.2f}"
        }
    }


def get_bulk_discount_recommendation(quantity: int) -> Dict:
    """
    Get recommended bulk discount based on quantity

    Args:
        quantity: Total quantity of units

    Returns:
        Dictionary with discount recommendation
    """
    if quantity > 5:
        return {
            'recommended_discount': 10.0,
            'reason': 'Bulk order (>5 units)',
            'tier': 'Tier 3',
            'description': '10% discount for orders over 5 units'
        }
    elif quantity > 3:
        return {
            'recommended_discount': 5.0,
            'reason': 'Bulk order (>3 units)',
            'tier': 'Tier 2',
            'description': '5% discount for orders over 3 units'
        }
    elif quantity > 1:
        return {
            'recommended_discount': 2.0,
            'reason': 'Multi-unit order',
            'tier': 'Tier 1',
            'description': '2% discount for orders over 1 unit'
        }
    else:
        return {
            'recommended_discount': 0.0,
            'reason': 'Single unit order',
            'tier': 'Standard',
            'description': 'No bulk discount applicable'
        }
