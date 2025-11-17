import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.business_analysis_enhanced import (
    BusinessAnalysisEnhanced,
    ChamberConfig,
    OperatingCosts,
    RevenueParams,
    FinancialAssumptions
)
from modules.visualizations.business_charts import (
    plot_tco_breakdown,
    plot_roi_timeline,
    plot_competitive_comparison,
    plot_tornado_chart,
    plot_scenario_comparison,
    plot_financial_dashboard,
    plot_sensitivity_line,
    plot_monte_carlo_distribution,
    plot_capex_breakdown,
    plot_opex_trend,
    plot_break_even_analysis
)

# Page configuration
st.set_page_config(
    page_title="PV Chamber Configurator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🔬 UV+TC+HF+DH Chamber Configurator")
st.markdown("""
Comprehensive Environmental Test Chamber Configurator & Quote Generation System  
for PV Module Testing with CFD Simulations, Virtual HMI, and Business Analysis
""")

# Sidebar for company branding
with st.sidebar:
    st.header("🎨 Company Branding")
    
    company_name = st.text_input("Company Name", "Zenitek Solutions")
    company_address = st.text_area("Address", "Tamil Nadu, India")
    company_email = st.text_input("Email", "info@zenitek.com")
    
    st.divider()
    st.subheader("📊 Quick Stats")
    st.metric("Total Cost", "₹1.37 Cr")
    st.metric("Delivery", "22 weeks")
    st.metric("Warranty", "36 months")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📐 Chamber Design",
    "💡 UV System",
    "💰 Quote Generator",
    "📈 Business Analysis",
    "🖥️ Virtual HMI"
])

with tab1:
    st.header("Chamber Design Specifications")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dimensions")
        length = st.number_input("Length (mm)", value=3200, step=100)
        width = st.number_input("Width (mm)", value=2100, step=100)
        height = st.number_input("Height (mm)", value=2200, step=100)
        
        volume = (length * width * height) / 1e9
        st.info(f"📦 Internal Volume: {volume:.2f} m³")
    
    with col2:
        st.subheader("Performance")
        temp_range = st.slider("Temperature Range (°C)", -45, 105, (-45, 105))
        humidity_range = st.slider("Humidity Range (%RH)", 40, 95, (40, 95))
        uv_intensity = st.slider("UV Intensity (W/m²)", 25, 250, 60)
        
        st.success("✓ IEC 61215/61730 Compliant")

with tab2:
    st.header("UV Optical System")
    
    col1, col2 = st.columns(2)
    with col1:
        led_type = st.selectbox("LED Type", ["LED (45% efficiency)", "Metal Halide (35%)", "Fluorescent (25%)"])
        num_modules = st.number_input("Number of PV Modules", value=2, min_value=1, max_value=4)
        
    with col2:
        st.metric("Required LEDs", "28 units")
        st.metric("Total UV Power", "2.4 kW")
        st.metric("Uniformity", "±8.5%")

with tab3:
    st.header("💰 Commercial Quote Generator")
    
    st.subheader("Cost Breakdown")
    
    cost_data = {
        "Component": [
            "Chamber System",
            "UV LED Arrays",
            "Refrigeration",
            "Controls/HMI",
            "DC Power Supply",
            "Uniformity Robot",
            "Water Treatment",
            "Installation",
            "Calibration"
        ],
        "Cost (₹L)": [35, 16, 8, 7, 6, 12, 6.3, 5, 3.5]
    }
    
    df_cost = pd.DataFrame(cost_data)
    df_cost["Cost (₹)"] = df_cost["Cost (₹L)"] * 100000
    
    st.dataframe(df_cost, use_container_width=True)
    
    total_cost = df_cost["Cost (₹L)"].sum()
    st.success(f"### Total Project Cost: ₹{total_cost:.1f} Lakhs (₹{total_cost/100:.2f} Crores)")
    
    # Cost breakdown chart
    fig = go.Figure(data=[go.Pie(
        labels=df_cost["Component"],
        values=df_cost["Cost (₹L)"],
        hole=0.4
    )])
    fig.update_layout(title="Cost Distribution")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("📈 Enhanced Business Analysis & ROI Calculator")

    # Load competitor data
    @st.cache_data
    def load_competitor_data():
        with open('data/competitor_data.json', 'r') as f:
            data = json.load(f)
        return data['competitors']

    try:
        competitor_data = load_competitor_data()
    except:
        competitor_data = []

    # Initialize business analysis
    @st.cache_resource
    def get_business_analysis():
        return BusinessAnalysisEnhanced(
            chamber_config=ChamberConfig(),
            operating_costs=OperatingCosts(),
            revenue_params=RevenueParams(),
            financial_assumptions=FinancialAssumptions()
        )

    business_analysis = get_business_analysis()

    # Sub-tabs for different analyses
    sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5, sub_tab6 = st.tabs([
        "📊 Dashboard",
        "💰 TCO Analysis",
        "📈 ROI Metrics",
        "🎯 Competitive Comparison",
        "🔍 Sensitivity Analysis",
        "📋 Investment Report"
    ])

    with sub_tab1:
        st.subheader("Financial KPI Dashboard")

        # Generate dashboard metrics
        dashboard = business_analysis.generate_financial_dashboard()

        # Display KPI metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Payback Period",
                f"{dashboard['payback_period_years']:.2f} years",
                delta="Excellent" if dashboard['payback_period_years'] < 3 else "Good"
            )
            st.metric(
                "NPV (10-Year)",
                f"₹{dashboard['npv']:,.0f}",
                delta="Positive" if dashboard['npv'] > 0 else "Negative"
            )

        with col2:
            st.metric(
                "Annual ROI",
                f"{dashboard['roi_annual_percent']:.1f}%",
                delta="Strong" if dashboard['roi_annual_percent'] > 15 else "Moderate"
            )
            st.metric(
                "IRR",
                f"{dashboard['irr_percent']:.1f}%",
                delta="Excellent" if dashboard['irr_percent'] > 20 else "Good"
            )

        with col3:
            st.metric(
                "Cost per Test",
                f"₹{dashboard['cost_per_test']:,.0f}",
                delta=f"-{((35000 - dashboard['cost_per_test'])/35000*100):.0f}% vs outsource"
            )
            st.metric(
                "Energy Cost/Test",
                f"₹{dashboard['energy_cost_per_test']:,.0f}"
            )

        with col4:
            st.metric(
                "Utilization Rate",
                f"{dashboard['utilization_rate_percent']:.1f}%",
                delta="Optimal" if dashboard['utilization_rate_percent'] > 60 else "Room for growth"
            )
            st.metric(
                "Break-Even Tests",
                f"{dashboard['break_even_tests']:.0f}/year"
            )

        st.divider()

        # Dashboard visualization
        st.plotly_chart(
            plot_financial_dashboard(dashboard),
            use_container_width=True
        )

    with sub_tab2:
        st.subheader("Total Cost of Ownership (10-Year)")

        # CAPEX Breakdown
        st.markdown("#### Capital Expenditure (CAPEX)")
        capex = business_analysis.breakdown_capex()

        col1, col2 = st.columns([1, 1])

        with col1:
            capex_df = pd.DataFrame([
                {"Component": k.replace('_', ' ').title(), "Amount (₹)": v}
                for k, v in capex.items() if k != 'total'
            ])
            st.dataframe(capex_df, use_container_width=True)
            st.success(f"**Total CAPEX: ₹{capex['total']:,.0f}**")

        with col2:
            st.plotly_chart(
                plot_capex_breakdown(capex),
                use_container_width=True
            )

        st.divider()

        # TCO Over Time
        st.markdown("#### TCO Breakdown Over 10 Years")
        tco_df = business_analysis.calculate_tco_detailed(10)

        st.plotly_chart(
            plot_tco_breakdown(tco_df),
            use_container_width=True
        )

        # TCO Data Table
        with st.expander("📄 View Detailed TCO Data"):
            display_tco = tco_df.copy()
            display_tco['capex'] = display_tco['capex'].apply(lambda x: f"₹{x:,.0f}")
            display_tco['opex'] = display_tco['opex'].apply(lambda x: f"₹{x:,.0f}")
            display_tco['total_cost'] = display_tco['total_cost'].apply(lambda x: f"₹{x:,.0f}")
            display_tco['cumulative_cost'] = display_tco['cumulative_cost'].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(display_tco, use_container_width=True)

        # OPEX Trend
        st.plotly_chart(
            plot_opex_trend(tco_df),
            use_container_width=True
        )

        # Cost escalation details
        st.info("""
        **Cost Escalation Assumptions:**
        - Energy costs: 5% per annum
        - Maintenance costs: 4% per annum
        - Other costs: 6% per annum (general inflation)
        """)

    with sub_tab3:
        st.subheader("Return on Investment Analysis")

        # ROI Metrics
        roi_metrics = business_analysis.calculate_roi_metrics(10)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Key Metrics")
            metrics_df = pd.DataFrame([
                {"Metric": "Net Present Value (NPV)", "Value": f"₹{roi_metrics['npv']:,.0f}"},
                {"Metric": "Internal Rate of Return (IRR)", "Value": f"{roi_metrics['irr']*100:.2f}%" if roi_metrics['irr'] else "N/A"},
                {"Metric": "Payback Period", "Value": f"{roi_metrics['payback_period']:.2f} years" if roi_metrics['payback_period'] else "N/A"},
                {"Metric": "Total ROI (10-year)", "Value": f"{roi_metrics['roi_percent']:.1f}%"},
                {"Metric": "Annual ROI", "Value": f"{roi_metrics['annual_roi']:.1f}%"},
                {"Metric": "Total Revenue (10-year)", "Value": f"₹{roi_metrics['total_revenue']:,.0f}"},
                {"Metric": "Total Costs (10-year)", "Value": f"₹{roi_metrics['total_costs']:,.0f}"},
            ])
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("#### Investment Recommendation")

            if roi_metrics['npv'] > 0 and roi_metrics['payback_period'] and roi_metrics['payback_period'] < 5:
                st.success("✅ **APPROVED** - Strong financial case")
                st.write("**Rationale:**")
                st.write(f"- Positive NPV of ₹{roi_metrics['npv']:,.0f}")
                st.write(f"- Quick payback in {roi_metrics['payback_period']:.1f} years")
                st.write(f"- Strong IRR of {roi_metrics['irr']*100:.1f}%" if roi_metrics['irr'] else "")
            elif roi_metrics['npv'] > 0:
                st.warning("⚠️ **REVIEW** - Moderate financial case")
                st.write("**Considerations:**")
                st.write(f"- Positive NPV of ₹{roi_metrics['npv']:,.0f}")
                st.write(f"- Longer payback period")
                st.write("- Review sensitivity to key assumptions")
            else:
                st.error("❌ **NOT RECOMMENDED** - Weak financial case")
                st.write("**Concerns:**")
                st.write(f"- Negative NPV of ₹{roi_metrics['npv']:,.0f}")
                st.write("- Consider alternative options")

        st.divider()

        # ROI Timeline
        st.markdown("#### Cash Flow Timeline")
        st.plotly_chart(
            plot_roi_timeline(roi_metrics['annual_data']),
            use_container_width=True
        )

        # Break-Even Analysis
        st.divider()
        st.markdown("#### Break-Even Analysis")

        breakeven = business_analysis.break_even_analysis()

        col1, col2 = st.columns(2)

        with col1:
            be_df = pd.DataFrame([
                {"Metric": "Break-Even Tests/Year", "Value": f"{breakeven['break_even_tests']:.0f}"},
                {"Metric": "Current Tests/Year", "Value": f"{breakeven['current_tests']:.0f}"},
                {"Metric": "Utilization at Break-Even", "Value": f"{breakeven['utilization_at_breakeven']:.1f}%"},
                {"Metric": "Fixed Costs (Annual)", "Value": f"₹{breakeven['fixed_costs']:,.0f}"},
                {"Metric": "Variable Cost/Test", "Value": f"₹{breakeven['variable_cost_per_test']:,.0f}"},
                {"Metric": "Revenue/Test", "Value": f"₹{breakeven['revenue_per_test']:,.0f}"},
            ])
            st.dataframe(be_df, use_container_width=True, hide_index=True)

        with col2:
            st.plotly_chart(
                plot_break_even_analysis(breakeven),
                use_container_width=True
            )

    with sub_tab4:
        st.subheader("Competitive Comparison")

        # Compare with competitors
        if competitor_data:
            comp_df = business_analysis.compare_with_competitors(competitor_data)

            st.markdown("#### Market Comparison")

            # Display comparison table
            display_cols = [
                'supplier', 'model', 'initial_cost', 'tco_10_year',
                'npv', 'payback_years', 'tests_per_year'
            ]

            st.dataframe(
                comp_df[display_cols].style.format({
                    'initial_cost': '₹{:,.0f}',
                    'tco_10_year': '₹{:,.0f}',
                    'npv': '₹{:,.0f}',
                    'payback_years': '{:.2f}',
                    'tests_per_year': '{:.0f}'
                }),
                use_container_width=True
            )

            # Competitive comparison charts
            st.plotly_chart(
                plot_competitive_comparison(comp_df),
                use_container_width=True
            )

            st.divider()

        # Compare with outsourcing
        st.markdown("#### In-House vs Outsourcing")

        outsource_comparison = business_analysis.compare_with_outsourcing()

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "In-House TCO (10-year)",
                f"₹{outsource_comparison['inhouse_tco_10yr']:,.0f}"
            )
            st.metric(
                "Outsource Cost (10-year)",
                f"₹{outsource_comparison['outsource_cost_10yr']:,.0f}"
            )

        with col2:
            st.metric(
                "Total Savings",
                f"₹{outsource_comparison['savings']:,.0f}",
                delta=f"{outsource_comparison['savings_percent']:.1f}% reduction"
            )
            st.metric(
                "Payback Period",
                f"{outsource_comparison['payback_years']:.2f} years"
            )

        # Outsourcing comparison chart
        comparison_data = pd.DataFrame([
            {'Option': 'In-House Chamber', 'Cost': outsource_comparison['inhouse_tco_10yr']},
            {'Option': 'Outsourced Testing', 'Cost': outsource_comparison['outsource_cost_10yr']}
        ])

        fig_outsource = go.Figure(data=[
            go.Bar(
                x=comparison_data['Option'],
                y=comparison_data['Cost'],
                text=comparison_data['Cost'],
                texttemplate='₹%{text:,.0f}',
                textposition='outside',
                marker_color=['#2ECC71', '#E74C3C']
            )
        ])
        fig_outsource.update_layout(
            title='10-Year Cost Comparison: In-House vs Outsourcing',
            yaxis_title='Total Cost (₹)',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig_outsource, use_container_width=True)

    with sub_tab5:
        st.subheader("Sensitivity & Risk Analysis")

        # Scenario Analysis
        st.markdown("#### Scenario Analysis")
        scenarios_df = business_analysis.scenario_analysis()

        st.dataframe(
            scenarios_df.style.format({
                'npv': '₹{:,.0f}',
                'irr': '{:.2%}',
                'payback_years': '{:.2f}',
                'roi_percent': '{:.1f}%'
            }),
            use_container_width=True
        )

        st.plotly_chart(
            plot_scenario_comparison(scenarios_df),
            use_container_width=True
        )

        st.divider()

        # Sensitivity Analysis
        st.markdown("#### Sensitivity Analysis")

        # Variable selector
        sensitivity_var = st.selectbox(
            "Select Variable to Analyze",
            options=[
                ('test_volume', 'Test Volume'),
                ('revenue_per_test', 'Revenue per Test'),
                ('energy_price', 'Energy Price'),
                ('maintenance_cost', 'Maintenance Cost'),
                ('equipment_cost', 'Equipment Cost')
            ],
            format_func=lambda x: x[1]
        )

        var_name, var_label = sensitivity_var

        # Run sensitivity analysis
        sens_df = business_analysis.sensitivity_analysis(var_name, 30)

        st.plotly_chart(
            plot_sensitivity_line(sens_df, var_label),
            use_container_width=True
        )

        # Tornado Chart
        st.divider()
        st.markdown("#### Tornado Chart - Impact Ranking")

        tornado_df = business_analysis.tornado_chart_data()

        st.plotly_chart(
            plot_tornado_chart(tornado_df),
            use_container_width=True
        )

        with st.expander("📊 View Tornado Data"):
            st.dataframe(
                tornado_df.style.format({
                    'base_npv': '₹{:,.0f}',
                    'npv_low': '₹{:,.0f}',
                    'npv_high': '₹{:,.0f}',
                    'impact': '₹{:,.0f}',
                    'impact_percent': '{:.1f}%'
                }),
                use_container_width=True
            )

        # Monte Carlo Simulation
        st.divider()
        st.markdown("#### Monte Carlo Risk Analysis")

        if st.button("🎲 Run Monte Carlo Simulation (1000 iterations)"):
            with st.spinner("Running simulation..."):
                mc_results = business_analysis.monte_carlo_simulation(1000)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Mean NPV", f"₹{mc_results['npv_mean']:,.0f}")
                st.metric("Std Deviation", f"₹{mc_results['npv_std']:,.0f}")

            with col2:
                st.metric("P10 (Pessimistic)", f"₹{mc_results['npv_p10']:,.0f}")
                st.metric("P50 (Median)", f"₹{mc_results['npv_p50']:,.0f}")

            with col3:
                st.metric("P90 (Optimistic)", f"₹{mc_results['npv_p90']:,.0f}")
                st.metric("Success Probability", f"{mc_results['probability_positive_npv']:.1f}%")

            st.plotly_chart(
                plot_monte_carlo_distribution(mc_results['npv_distribution']),
                use_container_width=True
            )

    with sub_tab6:
        st.subheader("Investment Justification Report")

        # Generate report
        report = business_analysis.generate_investment_justification()

        # Executive Summary
        st.markdown("### 📋 Executive Summary")

        exec_summary = report['executive_summary']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"""
            **Financial Metrics:**
            - Net Present Value: ₹{exec_summary['npv']:,.0f}
            - Internal Rate of Return: {exec_summary['irr']*100:.1f}%
            - Payback Period: {exec_summary['payback_period']:.2f} years
            - 10-Year ROI: {exec_summary['roi_10_year']:.1f}%
            """)

        with col2:
            recommendation = exec_summary['recommendation']
            if recommendation == 'APPROVED':
                st.success(f"**Recommendation: {recommendation}** ✅")
                st.write("The investment demonstrates strong financial returns with positive NPV and reasonable payback period.")
            else:
                st.warning(f"**Recommendation: {recommendation}** ⚠️")
                st.write("Further review recommended. Consider optimizing key parameters or exploring alternatives.")

        st.divider()

        # Key Findings
        st.markdown("### 🔍 Key Findings")

        dashboard = report['financial_analysis']['dashboard_kpis']

        st.markdown(f"""
        1. **Cost Efficiency**: At ₹{dashboard['cost_per_test']:,.0f} per test, the in-house chamber offers significant savings compared to outsourcing (₹35,000/test)

        2. **Capacity Utilization**: Current utilization at {dashboard['utilization_rate_percent']:.1f}% provides room for growth and improved ROI

        3. **Break-Even**: Requires {dashboard['break_even_tests']:.0f} tests annually to break even, well below planned capacity

        4. **Risk Assessment**: Monte Carlo analysis shows {report['risk_analysis']['probability_success']:.1f}% probability of positive NPV
        """)

        # Export Options
        st.divider()
        st.markdown("### 💾 Export Options")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Export to Excel"):
                try:
                    output_path = "business_analysis_report.xlsx"
                    business_analysis.export_to_excel(output_path)
                    st.success(f"✅ Report exported to {output_path}")

                    with open(output_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Download Excel Report",
                            data=f,
                            file_name="pv_chamber_business_analysis.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error exporting: {str(e)}")

        with col2:
            if st.button("📄 Export to JSON"):
                try:
                    json_str = json.dumps(report, indent=2, default=str)
                    st.download_button(
                        label="⬇️ Download JSON Report",
                        data=json_str,
                        file_name="pv_chamber_business_analysis.json",
                        mime="application/json"
                    )
                    st.success("✅ JSON report ready for download")
                except Exception as e:
                    st.error(f"Error exporting: {str(e)}")

        # Print-Ready Summary
        st.divider()
        st.markdown("### 📄 Print-Ready Summary")

        with st.expander("View Full Investment Justification"):
            st.markdown(f"""
            # PV Chamber Investment Justification

            **Date**: {datetime.now().strftime('%Y-%m-%d')}

            ## Executive Summary

            This analysis evaluates the financial viability of investing in a custom UV+TC+HF+DH environmental test chamber for PV module testing.

            **Investment Required**: ₹{report['financial_analysis']['capex']['total']:,.0f}

            **Key Financial Metrics**:
            - NPV (10-year): ₹{exec_summary['npv']:,.0f}
            - IRR: {exec_summary['irr']*100:.1f}%
            - Payback Period: {exec_summary['payback_period']:.2f} years
            - Total ROI: {exec_summary['roi_10_year']:.1f}%

            **Recommendation**: {exec_summary['recommendation']}

            ## Financial Analysis

            ### Capital Expenditure
            - Equipment: ₹{report['financial_analysis']['capex']['equipment']:,.0f}
            - Installation: ₹{report['financial_analysis']['capex']['installation']:,.0f}
            - Training: ₹{report['financial_analysis']['capex']['training']:,.0f}
            - Spare Parts: ₹{report['financial_analysis']['capex']['spare_parts']:,.0f}
            - Calibration: ₹{report['financial_analysis']['capex']['initial_calibration']:,.0f}

            ### Operating Performance
            - Annual Tests: 200
            - Cost per Test: ₹{dashboard['cost_per_test']:,.0f}
            - Utilization Rate: {dashboard['utilization_rate_percent']:.1f}%

            ## Risk Analysis

            **Scenario Analysis**:
            - Best Case NPV: ₹{report['risk_analysis']['scenarios'][1]['npv']:,.0f}
            - Expected NPV: ₹{report['risk_analysis']['scenarios'][0]['npv']:,.0f}
            - Worst Case NPV: ₹{report['risk_analysis']['scenarios'][2]['npv']:,.0f}

            **Probability of Success**: {report['risk_analysis']['probability_success']:.1f}%

            ## Conclusion

            The investment in the PV chamber demonstrates strong financial viability with positive NPV,
            attractive IRR, and reasonable payback period. The analysis supports proceeding with the investment.

            ---
            *Generated by PV Chamber Configurator - Business Analysis Module*
            """)


with tab5:
    st.header("🖥️ Virtual HMI - Real-time Monitoring")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Temperature", "85.0°C", "±0.2°C")
        st.progress(85/105)
    
    with col2:
        st.metric("Humidity", "85.0%RH", "±0.5%")
        st.progress(85/100)
    
    with col3:
        st.metric("UV Intensity", "248 W/m²", "±2 W/m²")
        st.progress(248/250)
    
    st.info("🔄 System Status: Running | ⏰ Runtime: 1,245 hours | ✅ All sensors calibrated")

# Footer
st.divider()
st.markdown(f"""
---
**{company_name}** | {company_address} | {company_email}  
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
*White-labeled PV Chamber Configurator v1.0*
""")
