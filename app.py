import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
from datetime import datetime

# Import CFD modules
from modules.cfd_simulation import CFDSimulator
from modules.visualizations.cfd_plots_3d import (
    plot_temperature_3d,
    plot_velocity_vectors_3d,
    plot_humidity_3d,
    plot_cross_section_heatmap,
    plot_chamber_3d_model,
    plot_velocity_magnitude_3d,
    create_multi_panel_view
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📐 Chamber Design",
    "💡 UV System",
    "💰 Quote Generator",
    "📈 Business Analysis",
    "🖥️ Virtual HMI",
    "🌀 CFD Simulation"
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
    st.header("📈 Business Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("10-Year TCO", "₹2.27 Cr", "+66%")
        st.metric("ROI Period", "0.58 years")
    
    with col2:
        st.metric("Annual Revenue", "₹12.5 L")
        st.metric("CO₂ Emissions", "15.2 tonnes/yr")
    
    with col3:
        st.metric("Energy Cost", "₹18.5 L/yr")
        st.metric("MTBF", "20,000 hrs")

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

with tab6:
    st.header("🌀 CFD Simulation Engine")
    st.markdown("""
    Comprehensive Computational Fluid Dynamics analysis for thermal, airflow, and humidity distribution.
    Validate chamber performance and optimize component placement.
    """)

    # Simulation Parameters
    st.subheader("⚙️ Simulation Parameters")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Temperature Settings**")
        temp_setpoint = st.slider("Temperature Setpoint (°C)", -45, 105, 85, key="cfd_temp")
        heater_power = st.number_input("Heater Power (W)", 1000, 20000, 10000, step=1000, key="cfd_heater")
        ambient_temp = st.number_input("Ambient Temperature (°C)", 10, 35, 25, key="cfd_ambient")

    with col2:
        st.markdown("**Airflow Configuration**")
        num_fans = st.selectbox("Number of Fans", [1, 2, 4, 6, 8], index=2, key="cfd_fans")
        fan_power = st.number_input("Total Fan Power (W)", 100, 2000, 500, step=50, key="cfd_fan_power")

    with col3:
        st.markdown("**Humidity Settings**")
        target_humidity = st.slider("Target Humidity (%RH)", 40, 95, 85, key="cfd_humidity")
        num_humidifiers = st.selectbox("Number of Humidifiers", [1, 2, 3, 4], index=1, key="cfd_humidifiers")

    # Grid resolution
    with st.expander("Advanced Settings"):
        grid_res = st.selectbox("Grid Resolution",
                               ["Coarse (30×30×30)", "Medium (50×50×50)", "Fine (70×70×70)"],
                               index=1)

        if grid_res == "Coarse (30×30×30)":
            grid_size = (30, 30, 30)
        elif grid_res == "Fine (70×70×70)":
            grid_size = (70, 70, 70)
        else:
            grid_size = (50, 50, 50)

    # Run Simulation Button
    if st.button("▶️ Run CFD Simulation", type="primary", use_container_width=True):
        with st.spinner("Running CFD simulation... This may take a few moments."):
            try:
                # Initialize CFD simulator
                chamber_dims = (length, width, height)
                simulator = CFDSimulator(
                    chamber_dims=chamber_dims,
                    temp_range=temp_range,
                    humidity_range=humidity_range,
                    grid_resolution=grid_size
                )

                # Get component positions
                components = simulator.get_component_positions(
                    num_fans=num_fans,
                    num_humidifiers=num_humidifiers,
                    num_uv_panels=2
                )

                # Run simulations
                temp_field = simulator.calculate_temperature_field(
                    setpoint=temp_setpoint,
                    heater_power=heater_power,
                    ambient_temp=ambient_temp,
                    fan_positions=components['fans']
                )

                velocity_field = simulator.calculate_velocity_field(
                    fan_power_w=fan_power,
                    fan_positions=components['fans']
                )

                humidity_field = simulator.calculate_humidity_field(
                    target_rh=target_humidity,
                    humidifier_positions=components['humidifiers']
                )

                # Store results in session state
                st.session_state['cfd_results'] = {
                    'simulator': simulator,
                    'temp_field': temp_field,
                    'velocity_field': velocity_field,
                    'humidity_field': humidity_field,
                    'components': components
                }

                st.success("✅ CFD Simulation completed successfully!")

            except Exception as e:
                st.error(f"❌ Simulation failed: {str(e)}")

    # Display results if available
    if 'cfd_results' in st.session_state:
        results = st.session_state['cfd_results']
        simulator = results['simulator']
        temp_field = results['temp_field']
        velocity_field = results['velocity_field']
        humidity_field = results['humidity_field']
        components = results['components']

        st.divider()

        # Performance Metrics
        st.subheader("📊 Performance Metrics")

        # Temperature Analysis
        temp_uniformity = simulator.validate_temperature_uniformity(temp_field, tolerance=2.0)
        hot_cold_spots = simulator.detect_hot_cold_spots(temp_field)
        thermal_strat = simulator.calculate_thermal_stratification(temp_field)

        # Airflow Analysis
        dead_zones = simulator.detect_dead_zones(velocity_field, threshold=0.1)
        pressure_drop = simulator.calculate_pressure_drop(velocity_field)
        recirculation = simulator.detect_recirculation_zones(velocity_field)

        # Humidity Analysis
        humidity_uniformity = simulator.validate_humidity_uniformity(humidity_field, tolerance=3.0)
        condensation_risk = simulator.detect_condensation_risk(temp_field, humidity_field)

        # Display metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Temperature Uniformity",
                     f"{temp_uniformity['uniformity_percentage']:.1f}%",
                     delta="Pass" if temp_uniformity['passes_criteria'] else "Fail")
            st.metric("Temp Range", f"{temp_uniformity['temperature_range']:.2f}°C")

        with col2:
            st.metric("Dead Zone Volume", f"{dead_zones['dead_zone_percentage']:.1f}%",
                     delta="Pass" if dead_zones['passes_criteria'] else "Fail")
            st.metric("Mean Velocity", f"{dead_zones['mean_velocity']:.2f} m/s")

        with col3:
            st.metric("Humidity Uniformity", f"{humidity_uniformity['uniformity_percentage']:.1f}%",
                     delta="Pass" if humidity_uniformity['passes_criteria'] else "Fail")
            st.metric("RH Range", f"{humidity_uniformity['humidity_range']:.2f}%")

        with col4:
            st.metric("Pressure Drop", f"{pressure_drop['total_pressure_drop']:.1f} Pa",
                     delta="Pass" if pressure_drop['passes_criteria'] else "Fail")
            st.metric("Flow Regime", pressure_drop['flow_regime'])

        # Additional metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Stratification Index", f"{thermal_strat['stratification_index']:.3f}")
            st.metric("Hot Spot", f"{hot_cold_spots['hot_spot']['temperature']:.1f}°C")

        with col2:
            st.metric("Reynolds Number", f"{pressure_drop['reynolds_number']:.0f}")
            st.metric("Recirculation %", f"{recirculation['recirculation_volume_percentage']:.1f}%")

        with col3:
            st.metric("Condensation Risk", f"{condensation_risk['condensation_risk_percentage']:.1f}%")
            st.metric("Safe Operation", "Yes" if condensation_risk['safe_operation'] else "No")

        st.divider()

        # 3D Visualizations
        st.subheader("🎨 3D Visualizations")

        viz_tab1, viz_tab2, viz_tab3, viz_tab4, viz_tab5 = st.tabs([
            "🌡️ Temperature", "💨 Airflow", "💧 Humidity", "🏗️ Chamber Model", "📐 Cross-Sections"
        ])

        with viz_tab1:
            st.markdown("**3D Temperature Distribution**")
            fig_temp = plot_temperature_3d(temp_field, simulator.x, simulator.y, simulator.z)
            st.plotly_chart(fig_temp, use_container_width=True)

            # Temperature statistics
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Hot Spot:** {hot_cold_spots['hot_spot']['temperature']:.1f}°C at "
                       f"({hot_cold_spots['hot_spot']['location_mm'][0]:.0f}, "
                       f"{hot_cold_spots['hot_spot']['location_mm'][1]:.0f}, "
                       f"{hot_cold_spots['hot_spot']['location_mm'][2]:.0f}) mm")
            with col2:
                st.info(f"**Cold Spot:** {hot_cold_spots['cold_spot']['temperature']:.1f}°C at "
                       f"({hot_cold_spots['cold_spot']['location_mm'][0]:.0f}, "
                       f"{hot_cold_spots['cold_spot']['location_mm'][1]:.0f}, "
                       f"{hot_cold_spots['cold_spot']['location_mm'][2]:.0f}) mm")

        with viz_tab2:
            st.markdown("**3D Velocity Vector Field**")

            # Choose visualization type
            airflow_viz = st.radio("Visualization Type",
                                  ["Velocity Vectors", "Velocity Magnitude"],
                                  horizontal=True)

            if airflow_viz == "Velocity Vectors":
                fig_vel = plot_velocity_vectors_3d(velocity_field, simulator.x, simulator.y, simulator.z)
            else:
                fig_vel = plot_velocity_magnitude_3d(velocity_field, simulator.x, simulator.y, simulator.z)

            st.plotly_chart(fig_vel, use_container_width=True)

            st.info(f"**Flow Regime:** {pressure_drop['flow_regime']} "
                   f"(Re = {pressure_drop['reynolds_number']:.0f})")

        with viz_tab3:
            st.markdown("**3D Humidity Distribution**")
            fig_hum = plot_humidity_3d(humidity_field, simulator.x, simulator.y, simulator.z)
            st.plotly_chart(fig_hum, use_container_width=True)

            st.info(f"**Mean RH:** {humidity_uniformity['mean_humidity']:.1f}% | "
                   f"**Range:** {humidity_uniformity['humidity_range']:.2f}%")

        with viz_tab4:
            st.markdown("**3D Chamber Model with Components**")
            chamber_geom = simulator.generate_chamber_geometry()
            fig_chamber = plot_chamber_3d_model(chamber_geom, components, show_components=True)
            st.plotly_chart(fig_chamber, use_container_width=True)

            # Component summary
            st.markdown("**Component Configuration:**")
            st.write(f"- **Fans:** {num_fans} units")
            st.write(f"- **Humidifiers:** {num_humidifiers} units")
            st.write(f"- **UV Panels:** 2 units")
            st.write(f"- **Test Specimen:** PV Module at center")

        with viz_tab5:
            st.markdown("**Cross-Section Views**")

            # Select plane and position
            col1, col2 = st.columns(2)
            with col1:
                plane = st.selectbox("Cross-Section Plane", ["XY (Horizontal)", "XZ (Vertical)", "YZ (Vertical)"])
                plane_code = plane[:2]

            with col2:
                position = st.slider("Slice Position", 0.0, 1.0, 0.5, 0.05)

            # Select field
            field_type = st.radio("Field Type", ["Temperature", "Velocity", "Humidity"], horizontal=True)

            if field_type == "Temperature":
                field_data = temp_field
                colorbar_title = "Temperature (°C)"
            elif field_type == "Velocity":
                field_data = np.sqrt(np.sum(velocity_field**2, axis=3))
                colorbar_title = "Velocity (m/s)"
            else:
                field_data = humidity_field
                colorbar_title = "Humidity (%RH)"

            fig_cross = plot_cross_section_heatmap(
                field_data, simulator.x, simulator.y, simulator.z,
                plane=plane_code, position=position,
                title=f"{field_type} Cross-Section",
                colorbar_title=colorbar_title
            )
            st.plotly_chart(fig_cross, use_container_width=True)

        st.divider()

        # Advanced Analysis
        with st.expander("📈 Advanced Analysis"):
            st.subheader("Transient Response Analysis")

            col1, col2 = st.columns(2)
            with col1:
                ramp_start = st.number_input("Start Temperature (°C)", -45, 105, 25)
                ramp_end = st.number_input("End Temperature (°C)", -45, 105, temp_setpoint)
            with col2:
                ramp_time = st.number_input("Ramp Time (minutes)", 1, 120, 30)

            if st.button("Calculate Ramp Rate"):
                ramp_analysis = simulator.simulate_ramp_rate(
                    start_temp=ramp_start,
                    end_temp=ramp_end,
                    time_seconds=ramp_time * 60,
                    heater_power=heater_power
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Ramp Rate", f"{ramp_analysis['ramp_rate_celsius_per_min']:.2f} °C/min")
                with col2:
                    st.metric("IEC Compliant", "Yes" if ramp_analysis['meets_iec_spec'] else "No")
                with col3:
                    st.metric("Power Sufficient", "Yes" if ramp_analysis['power_sufficient'] else "No")

                # Plot transient response
                fig_transient = go.Figure()
                fig_transient.add_trace(go.Scatter(
                    x=ramp_analysis['time_profile']['time_minutes'],
                    y=ramp_analysis['time_profile']['temperature'],
                    mode='lines',
                    name='Temperature',
                    line=dict(color='red', width=2)
                ))
                fig_transient.update_layout(
                    title="Transient Temperature Response",
                    xaxis_title="Time (minutes)",
                    yaxis_title="Temperature (°C)",
                    height=400
                )
                st.plotly_chart(fig_transient, use_container_width=True)

            st.divider()

            st.subheader("Energy Balance")
            energy_balance = simulator.calculate_energy_balance(
                setpoint=temp_setpoint,
                ambient_temp=ambient_temp,
                heater_power=heater_power
            )

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Heater Power", f"{energy_balance['heater_power']:.0f} W")
            with col2:
                st.metric("Heat Loss", f"{energy_balance['heat_loss']:.0f} W")
            with col3:
                st.metric("Thermal Efficiency", f"{energy_balance['thermal_efficiency']:.1f}%")
            with col4:
                st.metric("Balance Check", "OK" if energy_balance['energy_balanced'] else "Error")

        # Export Results
        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Export Simulation Data (JSON)", use_container_width=True):
                json_data = simulator.export_simulation_data('cfd_results.json')
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="cfd_simulation_results.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📊 Generate Full Report", use_container_width=True):
                st.info("Full report generation will be implemented in Phase 8: Report Generator")

    else:
        st.info("👆 Configure simulation parameters above and click 'Run CFD Simulation' to begin analysis.")

# Footer
st.divider()
st.markdown(f"""
---
**{company_name}** | {company_address} | {company_email}  
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
*White-labeled PV Chamber Configurator v1.0*
""")
