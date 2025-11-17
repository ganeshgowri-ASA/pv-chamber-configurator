"""
Business Visualization Charts
Financial and business analysis visualizations using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List


def plot_tco_breakdown(tco_data: pd.DataFrame) -> go.Figure:
    """
    Create TCO breakdown visualization over time.

    Args:
        tco_data: DataFrame with year, capex, opex, cumulative_cost

    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Annual Costs', 'Cumulative TCO'),
        vertical_spacing=0.15,
        row_heights=[0.5, 0.5]
    )

    # Annual costs stacked bar
    fig.add_trace(
        go.Bar(
            x=tco_data['year'],
            y=tco_data['capex'],
            name='CAPEX',
            marker_color='#FF6B6B'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=tco_data['year'],
            y=tco_data['opex'],
            name='OPEX',
            marker_color='#4ECDC4'
        ),
        row=1, col=1
    )

    # Cumulative TCO line
    fig.add_trace(
        go.Scatter(
            x=tco_data['year'],
            y=tco_data['cumulative_cost'],
            name='Cumulative TCO',
            mode='lines+markers',
            line=dict(color='#95E1D3', width=3),
            marker=dict(size=8)
        ),
        row=2, col=1
    )

    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Cost (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Cumulative Cost (₹)", row=2, col=1)

    fig.update_layout(
        title='Total Cost of Ownership (10-Year)',
        height=700,
        barmode='stack',
        showlegend=True,
        template='plotly_white'
    )

    return fig


def plot_roi_timeline(annual_data: List[Dict]) -> go.Figure:
    """
    Create ROI timeline with cumulative cash flow.

    Args:
        annual_data: List of dicts with year, revenue, opex, net_cash_flow

    Returns:
        Plotly figure
    """
    df = pd.DataFrame(annual_data)

    # Calculate cumulative cash flow
    df['cumulative_cash_flow'] = df['net_cash_flow'].cumsum()

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Annual Cash Flows', 'Cumulative Cash Flow'),
        vertical_spacing=0.15
    )

    # Annual revenue and costs
    fig.add_trace(
        go.Bar(
            x=df['year'],
            y=df['revenue'],
            name='Revenue',
            marker_color='#2ECC71'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df['year'],
            y=-df['opex'],
            name='Operating Costs',
            marker_color='#E74C3C'
        ),
        row=1, col=1
    )

    # Cumulative cash flow with break-even line
    fig.add_trace(
        go.Scatter(
            x=df['year'],
            y=df['cumulative_cash_flow'],
            name='Cumulative Cash Flow',
            mode='lines+markers',
            line=dict(color='#3498DB', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.2)'
        ),
        row=2, col=1
    )

    # Zero line (break-even)
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        row=2, col=1
    )

    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Annual Cash Flow (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Cumulative Cash Flow (₹)", row=2, col=1)

    fig.update_layout(
        title='Return on Investment Timeline',
        height=700,
        barmode='relative',
        showlegend=True,
        template='plotly_white'
    )

    return fig


def plot_competitive_comparison(comparison_data: pd.DataFrame) -> go.Figure:
    """
    Create competitive comparison radar chart and bar charts.

    Args:
        comparison_data: DataFrame with supplier comparisons

    Returns:
        Plotly figure
    """
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Initial Cost Comparison', '10-Year TCO Comparison'),
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )

    # Initial cost comparison
    fig.add_trace(
        go.Bar(
            x=comparison_data['supplier'],
            y=comparison_data['initial_cost'],
            name='Initial Cost',
            marker_color=['#FF6B6B' if i == 0 else '#95E1D3'
                          for i in range(len(comparison_data))],
            text=comparison_data['initial_cost'],
            texttemplate='₹%{text:,.0f}',
            textposition='outside'
        ),
        row=1, col=1
    )

    # TCO comparison
    fig.add_trace(
        go.Bar(
            x=comparison_data['supplier'],
            y=comparison_data['tco_10_year'],
            name='10-Year TCO',
            marker_color=['#4ECDC4' if i == 0 else '#FFE66D'
                          for i in range(len(comparison_data))],
            text=comparison_data['tco_10_year'],
            texttemplate='₹%{text:,.0f}',
            textposition='outside'
        ),
        row=1, col=2
    )

    fig.update_xaxes(title_text="Supplier", row=1, col=1)
    fig.update_xaxes(title_text="Supplier", row=1, col=2)
    fig.update_yaxes(title_text="Cost (₹)", row=1, col=1)
    fig.update_yaxes(title_text="Cost (₹)", row=1, col=2)

    fig.update_layout(
        title='Competitive Comparison',
        height=500,
        showlegend=False,
        template='plotly_white'
    )

    return fig


def plot_tornado_chart(sensitivity_data: pd.DataFrame) -> go.Figure:
    """
    Create tornado chart for sensitivity analysis.

    Args:
        sensitivity_data: DataFrame with variable, npv_low, npv_high, impact

    Returns:
        Plotly figure
    """
    # Sort by impact
    data = sensitivity_data.sort_values('impact', ascending=True)

    # Calculate deviations from base
    base_npv = data.iloc[0]['base_npv']
    low_deviation = data['npv_low'] - base_npv
    high_deviation = data['npv_high'] - base_npv

    fig = go.Figure()

    # Low impact (negative deviation)
    fig.add_trace(go.Bar(
        y=data['variable'],
        x=low_deviation,
        name='Downside',
        orientation='h',
        marker_color='#E74C3C'
    ))

    # High impact (positive deviation)
    fig.add_trace(go.Bar(
        y=data['variable'],
        x=high_deviation,
        name='Upside',
        orientation='h',
        marker_color='#2ECC71'
    ))

    # Add center line
    fig.add_vline(x=0, line_dash="dash", line_color="gray")

    fig.update_layout(
        title='Tornado Chart - NPV Sensitivity Analysis',
        xaxis_title='NPV Impact (₹)',
        yaxis_title='Variable',
        barmode='overlay',
        height=400,
        template='plotly_white'
    )

    return fig


def plot_scenario_comparison(scenarios: pd.DataFrame) -> go.Figure:
    """
    Create scenario comparison visualization.

    Args:
        scenarios: DataFrame with scenario, npv, irr, payback_years, roi_percent

    Returns:
        Plotly figure
    """
    metrics = ['npv', 'roi_percent', 'payback_years']
    metric_names = ['NPV (₹)', 'ROI (%)', 'Payback (Years)']

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=metric_names,
        specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
    )

    colors = {'Best Case': '#2ECC71', 'Expected': '#3498DB', 'Worst Case': '#E74C3C'}

    for i, (metric, name) in enumerate(zip(metrics, metric_names)):
        fig.add_trace(
            go.Bar(
                x=scenarios['scenario'],
                y=scenarios[metric],
                name=name,
                marker_color=[colors.get(s, '#95E1D3') for s in scenarios['scenario']],
                text=scenarios[metric],
                texttemplate='%{text:.2f}',
                textposition='outside'
            ),
            row=1, col=i+1
        )

    fig.update_layout(
        title='Scenario Analysis: Best / Expected / Worst',
        height=400,
        showlegend=False,
        template='plotly_white'
    )

    return fig


def plot_financial_dashboard(metrics: Dict) -> go.Figure:
    """
    Create financial KPI dashboard with gauges.

    Args:
        metrics: Dictionary with dashboard KPIs

    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=(
            'Payback Period',
            'Annual ROI',
            'NPV',
            'IRR',
            'Cost per Test',
            'Utilization Rate'
        ),
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]
        ]
    )

    # Payback Period
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=metrics['payback_period_years'],
            title={'text': "Years"},
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': "#4ECDC4"},
                'steps': [
                    {'range': [0, 2], 'color': "#2ECC71"},
                    {'range': [2, 5], 'color': "#F39C12"},
                    {'range': [5, 10], 'color': "#E74C3C"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 5
                }
            }
        ),
        row=1, col=1
    )

    # Annual ROI
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=metrics['roi_annual_percent'],
            title={'text': "%"},
            gauge={
                'axis': {'range': [0, 50]},
                'bar': {'color': "#3498DB"},
                'steps': [
                    {'range': [0, 10], 'color': "#E74C3C"},
                    {'range': [10, 20], 'color': "#F39C12"},
                    {'range': [20, 50], 'color': "#2ECC71"}
                ]
            }
        ),
        row=1, col=2
    )

    # NPV
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=metrics['npv'],
            title={'text': "NPV (₹)"},
            number={'prefix': "₹", 'valueformat': ",.0f"},
            delta={'reference': 0, 'relative': False}
        ),
        row=1, col=3
    )

    # IRR
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=metrics['irr_percent'],
            title={'text': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#9B59B6"},
                'steps': [
                    {'range': [0, 10], 'color': "#E74C3C"},
                    {'range': [10, 30], 'color': "#F39C12"},
                    {'range': [30, 100], 'color': "#2ECC71"}
                ]
            }
        ),
        row=2, col=1
    )

    # Cost per Test
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=metrics['cost_per_test'],
            title={'text': "Cost/Test (₹)"},
            number={'prefix': "₹", 'valueformat': ",.0f"}
        ),
        row=2, col=2
    )

    # Utilization Rate
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=metrics['utilization_rate_percent'],
            title={'text': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1ABC9C"},
                'steps': [
                    {'range': [0, 40], 'color': "#E74C3C"},
                    {'range': [40, 70], 'color': "#F39C12"},
                    {'range': [70, 100], 'color': "#2ECC71"}
                ]
            }
        ),
        row=2, col=3
    )

    fig.update_layout(
        title='Financial KPI Dashboard',
        height=600,
        template='plotly_white'
    )

    return fig


def plot_sensitivity_line(sensitivity_data: pd.DataFrame, variable_name: str) -> go.Figure:
    """
    Create line chart for single variable sensitivity analysis.

    Args:
        sensitivity_data: DataFrame with variation_percent, npv, irr, roi_percent
        variable_name: Name of the variable being analyzed

    Returns:
        Plotly figure
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('NPV Sensitivity', 'ROI Sensitivity'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )

    # NPV sensitivity
    fig.add_trace(
        go.Scatter(
            x=sensitivity_data['variation_percent'],
            y=sensitivity_data['npv'],
            mode='lines+markers',
            name='NPV',
            line=dict(color='#3498DB', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)

    # ROI sensitivity
    fig.add_trace(
        go.Scatter(
            x=sensitivity_data['variation_percent'],
            y=sensitivity_data['roi_percent'],
            mode='lines+markers',
            name='ROI %',
            line=dict(color='#2ECC71', width=3),
            marker=dict(size=8)
        ),
        row=1, col=2
    )

    fig.update_xaxes(title_text=f"{variable_name} Variation (%)", row=1, col=1)
    fig.update_xaxes(title_text=f"{variable_name} Variation (%)", row=1, col=2)
    fig.update_yaxes(title_text="NPV (₹)", row=1, col=1)
    fig.update_yaxes(title_text="ROI (%)", row=1, col=2)

    fig.update_layout(
        title=f'Sensitivity Analysis: {variable_name}',
        height=400,
        template='plotly_white',
        showlegend=False
    )

    return fig


def plot_monte_carlo_distribution(npv_distribution: List[float]) -> go.Figure:
    """
    Create histogram of Monte Carlo NPV distribution.

    Args:
        npv_distribution: List of NPV values from simulation

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=npv_distribution,
        nbinsx=50,
        name='NPV Distribution',
        marker_color='#3498DB',
        opacity=0.75
    ))

    # Add mean line
    mean_npv = np.mean(npv_distribution)
    fig.add_vline(
        x=mean_npv,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Mean: ₹{mean_npv:,.0f}"
    )

    # Add zero line
    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="red",
        annotation_text="Break-even"
    )

    # Add percentiles
    p10 = np.percentile(npv_distribution, 10)
    p90 = np.percentile(npv_distribution, 90)

    fig.add_vline(x=p10, line_dash="dot", line_color="orange",
                  annotation_text=f"P10: ₹{p10:,.0f}")
    fig.add_vline(x=p90, line_dash="dot", line_color="orange",
                  annotation_text=f"P90: ₹{p90:,.0f}")

    fig.update_layout(
        title='Monte Carlo Simulation - NPV Distribution (1000 iterations)',
        xaxis_title='NPV (₹)',
        yaxis_title='Frequency',
        height=500,
        template='plotly_white',
        showlegend=False
    )

    return fig


def plot_capex_breakdown(capex_data: Dict) -> go.Figure:
    """
    Create CAPEX breakdown pie chart.

    Args:
        capex_data: Dictionary with CAPEX components

    Returns:
        Plotly figure
    """
    # Remove 'total' from data
    data = {k: v for k, v in capex_data.items() if k != 'total'}

    labels = list(data.keys())
    values = list(data.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=px.colors.qualitative.Set3),
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        title=f'CAPEX Breakdown (Total: ₹{capex_data.get("total", 0):,.0f})',
        height=500,
        template='plotly_white'
    )

    return fig


def plot_opex_trend(tco_data: pd.DataFrame) -> go.Figure:
    """
    Create OPEX trend over time showing escalation.

    Args:
        tco_data: DataFrame with year, opex

    Returns:
        Plotly figure
    """
    # Filter out year 0 (CAPEX year)
    data = tco_data[tco_data['year'] > 0].copy()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data['year'],
        y=data['opex'],
        mode='lines+markers',
        name='Annual OPEX',
        line=dict(color='#E67E22', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(230, 126, 34, 0.2)'
    ))

    # Add trend line
    z = np.polyfit(data['year'], data['opex'], 1)
    p = np.poly1d(z)
    fig.add_trace(go.Scatter(
        x=data['year'],
        y=p(data['year']),
        mode='lines',
        name='Trend',
        line=dict(color='red', width=2, dash='dash')
    ))

    fig.update_layout(
        title='Annual Operating Expenses (with Escalation)',
        xaxis_title='Year',
        yaxis_title='OPEX (₹)',
        height=400,
        template='plotly_white'
    )

    return fig


def plot_break_even_analysis(breakeven_data: Dict, scenarios: List[int] = None) -> go.Figure:
    """
    Create break-even analysis chart.

    Args:
        breakeven_data: Dictionary with break-even metrics
        scenarios: List of test volumes to plot

    Returns:
        Plotly figure
    """
    if scenarios is None:
        scenarios = list(range(50, 401, 50))

    fixed_costs = breakeven_data['fixed_costs']
    variable_cost = breakeven_data['variable_cost_per_test']
    revenue_per_test = breakeven_data['revenue_per_test']

    # Calculate total costs and revenue for each scenario
    total_costs = [fixed_costs + (variable_cost * units) for units in scenarios]
    total_revenue = [revenue_per_test * units for units in scenarios]
    profit = [rev - cost for rev, cost in zip(total_revenue, total_costs)]

    fig = go.Figure()

    # Total costs
    fig.add_trace(go.Scatter(
        x=scenarios,
        y=total_costs,
        mode='lines',
        name='Total Costs',
        line=dict(color='#E74C3C', width=3)
    ))

    # Total revenue
    fig.add_trace(go.Scatter(
        x=scenarios,
        y=total_revenue,
        mode='lines',
        name='Total Revenue',
        line=dict(color='#2ECC71', width=3)
    ))

    # Break-even point
    be_units = breakeven_data['break_even_tests']
    be_revenue = revenue_per_test * be_units

    fig.add_trace(go.Scatter(
        x=[be_units],
        y=[be_revenue],
        mode='markers',
        name=f'Break-Even ({be_units:.0f} tests)',
        marker=dict(size=15, color='#F39C12', symbol='star')
    ))

    # Current volume
    current = breakeven_data['current_tests']
    current_revenue = revenue_per_test * current

    fig.add_trace(go.Scatter(
        x=[current],
        y=[current_revenue],
        mode='markers',
        name=f'Current Volume ({current} tests)',
        marker=dict(size=12, color='#3498DB', symbol='diamond')
    ))

    fig.update_layout(
        title='Break-Even Analysis',
        xaxis_title='Number of Tests per Year',
        yaxis_title='Amount (₹)',
        height=500,
        template='plotly_white'
    )

    return fig
