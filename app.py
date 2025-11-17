import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))

# Import core calculations module
from modules.core_calculations import (
    ChamberDimensions, PerformanceSpec, ComponentCosts,
    ChamberVolumeCalculator, HeatLoadCalculator,
    AirflowCalculator, PowerConsumptionCalculator,
    validate_chamber_configuration
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

    # Calculate quick stats from default configuration
    default_costs = ComponentCosts()
    st.metric("Base Cost", f"₹{default_costs.get_total_crores():.2f} Cr")
    st.metric("Delivery", "22 weeks")
    st.metric("Warranty", "36 months")
    st.metric("IEC Compliance", "61215/61730")

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
        length = st.number_input("Length (mm)", value=3200, step=100, min_value=1000, max_value=10000)
        width = st.number_input("Width (mm)", value=2100, step=100, min_value=1000, max_value=10000)
        height = st.number_input("Height (mm)", value=2200, step=100, min_value=1000, max_value=10000)
        num_modules = st.number_input("Number of PV Modules", value=2, min_value=1, max_value=4, step=1)

    with col2:
        st.subheader("Performance")
        temp_min = st.number_input("Min Temperature (°C)", value=-45, min_value=-70, max_value=0)
        temp_max = st.number_input("Max Temperature (°C)", value=105, min_value=50, max_value=150)
        humidity_min = st.number_input("Min Humidity (%RH)", value=40, min_value=10, max_value=90)
        humidity_max = st.number_input("Max Humidity (%RH)", value=95, min_value=50, max_value=98)
        uv_intensity_max = st.slider("Max UV Intensity (W/m²)", 25, 250, 250)

    # Create configuration objects
    try:
        dims = ChamberDimensions(length_mm=length, width_mm=width, height_mm=height)
        spec = PerformanceSpec(
            temp_min_c=temp_min,
            temp_max_c=temp_max,
            humidity_min_rh=humidity_min,
            humidity_max_rh=humidity_max,
            uv_intensity_max=uv_intensity_max
        )

        # Calculate volumes
        internal_volume = ChamberVolumeCalculator.calculate_internal_volume(dims)
        surface_areas = ChamberVolumeCalculator.calculate_surface_area(dims)
        working_volume = ChamberVolumeCalculator.calculate_working_volume(dims)

        # Display volume metrics
        st.divider()
        st.subheader("📐 Volume & Area Calculations")
        vol_col1, vol_col2, vol_col3 = st.columns(3)
        with vol_col1:
            st.metric("Internal Volume", f"{internal_volume} m³")
        with vol_col2:
            st.metric("Working Volume", f"{working_volume} m³")
        with vol_col3:
            st.metric("Surface Area", f"{surface_areas['total']} m²")

        # Heat load calculations
        st.divider()
        st.subheader("❄️ Heat Load Analysis")

        cooling_load = HeatLoadCalculator.calculate_total_cooling_load(
            dims, temp_max, num_modules, uv_power_w=uv_intensity_max * surface_areas['floor']
        )
        heating_load = HeatLoadCalculator.calculate_total_heating_load(dims, temp_min, num_modules)

        heat_col1, heat_col2 = st.columns(2)
        with heat_col1:
            st.info("**Cooling Requirements**")
            st.write(f"- Total Load: **{cooling_load['total_kw']} kW** ({cooling_load['total_tons']:.1f} tons)")
            st.write(f"- Transmission: {cooling_load['transmission_w']:.0f} W")
            st.write(f"- Air Infiltration: {cooling_load['air_infiltration_w']:.0f} W")
            st.write(f"- Equipment: {cooling_load['equipment_w']:.0f} W")
            st.write(f"- Product Load: {cooling_load['product_w']:.0f} W")

        with heat_col2:
            st.warning("**Heating Requirements**")
            st.write(f"- Total Load: **{heating_load['total_kw']} kW**")
            st.write(f"- Transmission: {heating_load['transmission_w']:.0f} W")
            st.write(f"- Air Infiltration: {heating_load['air_infiltration_w']:.0f} W")
            st.write(f"- Product Load: {heating_load['product_w']:.0f} W")

        # Airflow calculations
        st.divider()
        st.subheader("💨 Airflow & Circulation")

        airflow = AirflowCalculator.calculate_required_airflow_for_uniformity(dims, target_velocity_ms=0.78)
        fan_power = AirflowCalculator.calculate_fan_power(airflow['flow_rate_m3h'])
        air_changes = AirflowCalculator.calculate_air_changes_per_hour(dims, airflow['flow_rate_m3h'])

        air_col1, air_col2, air_col3, air_col4 = st.columns(4)
        with air_col1:
            st.metric("Airflow Rate", f"{airflow['flow_rate_cfm']:.0f} CFM")
        with air_col2:
            st.metric("Air Velocity", f"{airflow['velocity_ms']} m/s")
        with air_col3:
            st.metric("Fan Power", f"{fan_power['power_kw']} kW")
        with air_col4:
            st.metric("Air Changes/Hr", f"{air_changes}")

        # Power consumption
        st.divider()
        st.subheader("⚡ Power Consumption")

        refrig_power = PowerConsumptionCalculator.calculate_refrigeration_power(cooling_load['total_w'])
        heat_power = PowerConsumptionCalculator.calculate_heating_power(heating_load['total_w'])

        total_power = PowerConsumptionCalculator.calculate_total_power_consumption(
            refrig_power['compressor_power_kw'],
            heat_power['heater_power_kw'],
            uv_power_kw=uv_intensity_max * surface_areas['floor'] / 1000,
            fan_power_kw=fan_power['power_kw']
        )

        energy_cost = PowerConsumptionCalculator.calculate_energy_cost(
            total_power['max_demand_kw'] * 0.6  # Assume 60% average load
        )

        pwr_col1, pwr_col2, pwr_col3, pwr_col4 = st.columns(4)
        with pwr_col1:
            st.metric("Connected Load", f"{total_power['connected_load_kw']} kW")
        with pwr_col2:
            st.metric("Max Demand", f"{total_power['max_demand_kw']} kW")
        with pwr_col3:
            st.metric("Breaker Rating", f"{total_power['recommended_breaker_a']} A")
        with pwr_col4:
            st.metric("Annual Energy Cost", f"₹{energy_cost['annual_cost_lakhs']} L")

        # Configuration validation
        st.divider()
        validation = validate_chamber_configuration(dims, spec, num_modules)

        if validation['is_valid']:
            st.success("✅ **Configuration Valid** - IEC 61215/61730 Compliant")

        if validation['warnings']:
            with st.expander("⚠️ Warnings & Recommendations", expanded=True):
                for warning in validation['warnings']:
                    st.warning(warning)
                for rec in validation['recommendations']:
                    st.info(rec)

    except ValueError as e:
        st.error(f"❌ Configuration Error: {str(e)}")
        st.info("Please adjust the parameters to valid ranges.")

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

    # Initialize component costs
    costs = ComponentCosts()

    # Allow customization of costs
    with st.expander("🔧 Customize Component Costs (₹ Lakhs)", expanded=False):
        cost_col1, cost_col2 = st.columns(2)
        with cost_col1:
            chamber_body = st.number_input("Chamber Body", value=35.0, step=0.5)
            uv_led_arrays = st.number_input("UV LED Arrays", value=16.0, step=0.5)
            refrigeration = st.number_input("Refrigeration", value=8.0, step=0.5)
            controls_hmi = st.number_input("Controls/HMI", value=7.0, step=0.5)
            dc_power = st.number_input("DC Power Supply", value=6.0, step=0.5)
        with cost_col2:
            uniformity_robot = st.number_input("Uniformity Robot", value=12.0, step=0.5)
            water_treatment = st.number_input("Water Treatment", value=6.3, step=0.1)
            installation = st.number_input("Installation", value=5.0, step=0.5)
            calibration = st.number_input("Calibration", value=3.5, step=0.5)

        # Update costs object
        costs = ComponentCosts(
            chamber_body=chamber_body,
            uv_led_arrays=uv_led_arrays,
            refrigeration=refrigeration,
            controls_hmi=controls_hmi,
            dc_power_supply=dc_power,
            uniformity_robot=uniformity_robot,
            water_treatment=water_treatment,
            installation=installation,
            calibration=calibration
        )

    st.subheader("Cost Breakdown")

    # Prepare cost data for display
    cost_breakdown = costs.get_breakdown_dict()
    cost_data = {
        "Component": list(cost_breakdown.keys()),
        "Cost (₹L)": list(cost_breakdown.values())
    }

    df_cost = pd.DataFrame(cost_data)
    df_cost["Cost (₹)"] = df_cost["Cost (₹L)"] * 100000
    df_cost["Percentage"] = (df_cost["Cost (₹L)"] / costs.get_total_lakhs() * 100).round(1)

    # Display cost table
    st.dataframe(
        df_cost[["Component", "Cost (₹L)", "Percentage"]].style.format({
            "Cost (₹L)": "₹{:.2f}L",
            "Percentage": "{:.1f}%"
        }),
        use_container_width=True
    )

    # Total cost metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total (Lakhs)", f"₹{costs.get_total_lakhs():.2f}L")
    with col2:
        st.metric("Total (Crores)", f"₹{costs.get_total_crores():.2f}Cr")
    with col3:
        discount = st.selectbox("Quantity Discount", ["None", ">2 units: 8% off"])
        if "8%" in discount:
            discounted = costs.get_total_crores() * 0.92
            st.metric("After Discount", f"₹{discounted:.2f}Cr")

    # Cost breakdown chart
    fig = go.Figure(data=[go.Pie(
        labels=df_cost["Component"],
        values=df_cost["Cost (₹L)"],
        hole=0.4,
        textinfo='label+percent',
        textposition='outside'
    )])
    fig.update_layout(
        title="Cost Distribution by Component",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    # Payment terms
    st.divider()
    st.subheader("💳 Payment Terms Calculator")
    payment_col1, payment_col2 = st.columns(2)

    with payment_col1:
        advance_pct = st.slider("Advance Payment (%)", 0, 100, 30)
        milestone1_pct = st.slider("First Milestone (%)", 0, 100, 30)
        milestone2_pct = st.slider("Second Milestone (%)", 0, 100, 30)
        final_pct = 100 - advance_pct - milestone1_pct - milestone2_pct

    with payment_col2:
        total_inr = costs.get_total_lakhs() * 100000
        st.write("**Payment Schedule:**")
        st.write(f"- Advance ({advance_pct}%): ₹{(total_inr * advance_pct / 100):,.0f}")
        st.write(f"- Milestone 1 ({milestone1_pct}%): ₹{(total_inr * milestone1_pct / 100):,.0f}")
        st.write(f"- Milestone 2 ({milestone2_pct}%): ₹{(total_inr * milestone2_pct / 100):,.0f}")
        st.write(f"- Final ({final_pct}%): ₹{(total_inr * final_pct / 100):,.0f}")

    # Quote generation button
    st.divider()
    if st.button("📄 Generate PDF Quote", type="primary"):
        st.info("PDF quote generation will be available in Phase 8 (Report Generator module)")
        st.success(f"Quote prepared for **{company_name}**")

with tab4:
    st.header("📈 Business Analysis & TCO Calculator")

    # TCO Input Parameters
    st.subheader("🔧 Operating Parameters")
    tco_col1, tco_col2, tco_col3 = st.columns(3)

    with tco_col1:
        operating_hours_day = st.number_input("Operating Hours/Day", value=16, min_value=1, max_value=24)
        operating_days_year = st.number_input("Operating Days/Year", value=250, min_value=1, max_value=365)
        electricity_rate = st.number_input("Electricity Rate (₹/kWh)", value=8.0, min_value=1.0, max_value=20.0, step=0.5)

    with tco_col2:
        annual_maintenance = st.number_input("Annual Maintenance (₹L)", value=2.0, min_value=0.0, step=0.5)
        annual_calibration = st.number_input("Annual Calibration (₹L)", value=1.5, min_value=0.0, step=0.5)
        operator_cost_annual = st.number_input("Operator Cost/Year (₹L)", value=6.0, min_value=0.0, step=0.5)

    with tco_col3:
        analysis_years = st.slider("Analysis Period (years)", 1, 15, 10)

    # Calculate TCO
    st.divider()
    st.subheader("💰 Total Cost of Ownership Analysis")

    # Assume average power consumption is 60% of max demand
    # Using default chamber for TCO - in real app would use configured chamber
    default_dims = ChamberDimensions(3200, 2100, 2200)
    default_cooling = HeatLoadCalculator.calculate_total_cooling_load(default_dims, 105, 2)
    default_heating = HeatLoadCalculator.calculate_total_heating_load(default_dims, -45, 2)
    default_refrig = PowerConsumptionCalculator.calculate_refrigeration_power(default_cooling['total_w'])
    default_heat = PowerConsumptionCalculator.calculate_heating_power(default_heating['total_w'])
    default_power = PowerConsumptionCalculator.calculate_total_power_consumption(
        default_refrig['compressor_power_kw'],
        default_heat['heater_power_kw']
    )

    avg_power_kw = default_power['max_demand_kw'] * 0.6  # 60% average load

    energy_costs = PowerConsumptionCalculator.calculate_energy_cost(
        avg_power_kw,
        operating_hours_day,
        operating_days_year,
        electricity_rate
    )

    # Calculate multi-year TCO
    initial_investment = costs.get_total_lakhs()
    annual_energy_cost = energy_costs['annual_cost_lakhs']
    annual_recurring = annual_maintenance + annual_calibration + operator_cost_annual

    total_recurring_costs = []
    cumulative_tco = []

    for year in range(1, analysis_years + 1):
        yearly_recurring = annual_energy_cost + annual_recurring
        total_recurring_costs.append(yearly_recurring)
        cumulative = initial_investment + sum(total_recurring_costs)
        cumulative_tco.append(cumulative)

    final_tco = cumulative_tco[-1]

    # Display TCO Summary
    tco_summary_col1, tco_summary_col2, tco_summary_col3, tco_summary_col4 = st.columns(4)

    with tco_summary_col1:
        st.metric("Initial Investment", f"₹{initial_investment:.1f}L")
    with tco_summary_col2:
        st.metric(f"{analysis_years}-Year TCO", f"₹{final_tco:.1f}L", f"₹{final_tco/100:.2f}Cr")
    with tco_summary_col3:
        st.metric("Annual Energy Cost", f"₹{annual_energy_cost:.2f}L")
    with tco_summary_col4:
        st.metric("Annual Recurring", f"₹{(annual_recurring + annual_energy_cost):.2f}L")

    # TCO Breakdown
    st.divider()
    tco_breakdown_col1, tco_breakdown_col2 = st.columns(2)

    with tco_breakdown_col1:
        st.subheader("📊 Cost Breakdown Over " + str(analysis_years) + " Years")
        total_energy = annual_energy_cost * analysis_years
        total_maintenance = annual_maintenance * analysis_years
        total_calibration = annual_calibration * analysis_years
        total_operator = operator_cost_annual * analysis_years

        tco_pie_data = {
            "Category": ["Initial Investment", "Energy", "Maintenance", "Calibration", "Labor"],
            "Cost (₹L)": [initial_investment, total_energy, total_maintenance, total_calibration, total_operator]
        }

        fig_tco = go.Figure(data=[go.Pie(
            labels=tco_pie_data["Category"],
            values=tco_pie_data["Cost (₹L)"],
            hole=0.4
        )])
        fig_tco.update_layout(title=f"{analysis_years}-Year TCO Distribution", height=400)
        st.plotly_chart(fig_tco, use_container_width=True)

    with tco_breakdown_col2:
        st.subheader("📈 Cumulative TCO Over Time")
        years_list = list(range(1, analysis_years + 1))

        fig_cumulative = go.Figure()
        fig_cumulative.add_trace(go.Scatter(
            x=years_list,
            y=cumulative_tco,
            mode='lines+markers',
            name='Cumulative TCO',
            line=dict(color='red', width=3),
            fill='tozeroy'
        ))
        fig_cumulative.update_layout(
            xaxis_title="Year",
            yaxis_title="Total Cost (₹ Lakhs)",
            height=400
        )
        st.plotly_chart(fig_cumulative, use_container_width=True)

    # ROI Calculator
    st.divider()
    st.subheader("💹 ROI & Payback Analysis")

    roi_col1, roi_col2 = st.columns(2)

    with roi_col1:
        st.write("**Revenue Assumptions**")
        modules_per_year = st.number_input("Modules Tested/Year", value=500, min_value=1, step=50)
        revenue_per_module = st.number_input("Revenue/Module (₹)", value=2500, min_value=100, step=100)
        annual_revenue = modules_per_year * revenue_per_module / 100000  # Convert to lakhs

        st.metric("Annual Revenue", f"₹{annual_revenue:.2f}L")

    with roi_col2:
        st.write("**Payback Analysis**")
        annual_net_profit = annual_revenue - (annual_energy_cost + annual_recurring)
        if annual_net_profit > 0:
            payback_years = initial_investment / annual_net_profit
            roi_percentage = (annual_net_profit / initial_investment) * 100
            st.metric("Payback Period", f"{payback_years:.2f} years")
            st.metric("Annual ROI", f"{roi_percentage:.1f}%")
        else:
            st.error("⚠️ Negative cash flow - adjust revenue assumptions")

    # Additional metrics
    st.divider()
    st.subheader("⚙️ Operational Metrics")

    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

    with metrics_col1:
        st.metric("Annual kWh", f"{energy_costs['annual_kwh']:,.0f}")
    with metrics_col2:
        co2_emissions = energy_costs['annual_kwh'] * 0.82 / 1000  # 0.82 kg CO2/kWh for India
        st.metric("CO₂ Emissions", f"{co2_emissions:.1f} tonnes/yr")
    with metrics_col3:
        st.metric("MTBF", "20,000 hrs")
    with metrics_col4:
        capacity_utilization = (operating_hours_day / 24) * (operating_days_year / 365) * 100
        st.metric("Capacity Util.", f"{capacity_utilization:.0f}%")

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
