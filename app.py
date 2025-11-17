import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# Import UV optical system modules
from modules.uv_optical_system import (
    create_default_uv_system,
    ChamberDimensions,
    LEDSpecification,
    UVLEDLayoutCalculator,
    UniformityGridMapper,
    SpectrumAnalyzer,
    LEDAgingModel,
    PowerRequirementCalculator,
    UniformityRobotPathPlanner
)
from modules.visualizations.uv_heatmap_3d import UVHeatmapVisualizer

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
    st.header("💡 UV Optical System Design & Analysis")

    # Create tabs within UV System
    uv_sub_tabs = st.tabs([
        "🔧 LED Configuration",
        "📊 Uniformity Analysis",
        "🌈 Spectrum Analysis",
        "⏳ LED Aging & Maintenance",
        "⚡ Power Requirements",
        "🤖 Robot Path Planning"
    ])

    # Initialize UV system with current chamber dimensions
    if 'uv_system' not in st.session_state or st.session_state.get('chamber_changed', False):
        with st.spinner('Calculating UV optical system...'):
            st.session_state.uv_system = create_default_uv_system(
                chamber_length=length,
                chamber_width=width,
                chamber_height=height,
                target_irradiance=uv_intensity
            )
            st.session_state.chamber_changed = False

    uv_sys = st.session_state.uv_system

    # Tab 1: LED Configuration
    with uv_sub_tabs[0]:
        st.subheader("LED Array Configuration")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total LEDs Required",
                f"{uv_sys['layout']['num_leds']} units",
                help="Calculated for uniform coverage"
            )
            st.metric(
                "Array Layout",
                f"{uv_sys['layout']['rows']}×{uv_sys['layout']['cols']}",
                help="Rows × Columns"
            )

        with col2:
            st.metric(
                "LED Spacing (X)",
                f"{uv_sys['layout']['spacing_x']:.0f} mm",
                help="Horizontal spacing between LEDs"
            )
            st.metric(
                "LED Spacing (Y)",
                f"{uv_sys['layout']['spacing_y']:.0f} mm",
                help="Vertical spacing between LEDs"
            )

        with col3:
            st.metric(
                "Total UV Power",
                f"{uv_sys['layout']['total_uv_power']/1000:.2f} kW",
                help="Total UV output power"
            )
            st.metric(
                "Predicted Irradiance",
                f"{uv_sys['layout']['predicted_avg_irradiance']:.1f} W/m²",
                help="Average irradiance on test plane"
            )

        # LED Specifications
        st.divider()
        st.subheader("LED Specifications")

        col1, col2 = st.columns(2)

        with col1:
            spec_data = {
                "Parameter": [
                    "Peak Wavelength",
                    "Wavelength Range",
                    "Power per LED",
                    "Beam Angle",
                    "Efficiency",
                    "Lifespan (L80)"
                ],
                "Value": [
                    f"{uv_sys['led_spec'].wavelength_peak} nm",
                    f"{uv_sys['led_spec'].wavelength_range[0]}-{uv_sys['led_spec'].wavelength_range[1]} nm",
                    f"{uv_sys['led_spec'].power_per_led} W",
                    f"{uv_sys['led_spec'].beam_angle}°",
                    f"{uv_sys['led_spec'].efficiency * 100}%",
                    f"{uv_sys['led_spec'].lifespan_l80:,.0f} hours"
                ]
            }
            st.dataframe(pd.DataFrame(spec_data), hide_index=True, use_container_width=True)

        with col2:
            # LED position visualization
            visualizer = UVHeatmapVisualizer(
                chamber_length=length,
                chamber_width=width,
                grid_points=uv_sys['uniformity_mapper'].grid_points,
                irradiance_values=uv_sys['uniformity_analysis']['irradiance_array'].flatten()
            )

            led_map = visualizer.create_led_position_map(
                uv_sys['led_calculator'].led_positions,
                title="LED Array Layout (Top View)"
            )
            st.plotly_chart(led_map, use_container_width=True)

    # Tab 2: Uniformity Analysis
    with uv_sub_tabs[1]:
        st.subheader("IEC 60904-9 Uniformity Analysis")

        analysis = uv_sys['uniformity_analysis']

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Average Irradiance",
                f"{analysis['avg_irradiance']:.1f} W/m²",
                help="Average across 9-point grid"
            )

        with col2:
            st.metric(
                "Non-uniformity",
                f"{analysis['non_uniformity_pct']:.2f}%",
                delta=f"Target: ±10%",
                delta_color="inverse"
            )

        with col3:
            compliance_status = "✅ PASS" if analysis['passes_10pct'] else "❌ FAIL"
            st.metric(
                "IEC 60904-9",
                compliance_status,
                help="±10% uniformity requirement"
            )

        with col4:
            quality = "Excellent" if analysis['passes_5pct'] else "Good" if analysis['passes_10pct'] else "Poor"
            st.metric(
                "Uniformity Grade",
                quality,
                help="Excellent: ±5%, Good: ±10%"
            )

        # Grid data table
        st.divider()
        st.subheader("9-Point Measurement Grid Data")
        st.dataframe(
            analysis['grid_data'].style.applymap(
                lambda x: 'background-color: #d4edda' if x == 'Excellent'
                else ('background-color: #fff3cd' if x == 'Acceptable'
                else ('background-color: #f8d7da' if x == 'Non-compliant' else '')),
                subset=['Status']
            ),
            hide_index=True,
            use_container_width=True
        )

        # Visualizations
        st.divider()
        st.subheader("Uniformity Visualizations")

        viz_col1, viz_col2 = st.columns(2)

        visualizer = UVHeatmapVisualizer(
            chamber_length=length,
            chamber_width=width,
            grid_points=uv_sys['uniformity_mapper'].grid_points,
            irradiance_values=analysis['irradiance_array'].flatten()
        )

        with viz_col1:
            heatmap_2d = visualizer.create_2d_heatmap(
                title="UV Irradiance Map (2D Top View)",
                show_annotations=True,
                show_contours=True
            )
            st.plotly_chart(heatmap_2d, use_container_width=True)

        with viz_col2:
            zone_map = visualizer.create_uniformity_zone_map(
                avg_irradiance=analysis['avg_irradiance'],
                title="Uniformity Zone Compliance Map"
            )
            st.plotly_chart(zone_map, use_container_width=True)

        # 3D Surface Plot
        st.subheader("3D Irradiance Distribution")
        surface_3d = visualizer.create_3d_surface(
            title="UV Irradiance 3D Surface Plot"
        )
        st.plotly_chart(surface_3d, use_container_width=True)

        # Recommendations
        st.divider()
        st.subheader("System Recommendations")
        recommendations = uv_sys['uniformity_mapper'].get_recommendations()
        for rec in recommendations:
            if "✓" in rec:
                st.success(rec)
            elif "⚠️" in rec or "→" in rec:
                st.warning(rec)
            else:
                st.info(rec)

    # Tab 3: Spectrum Analysis
    with uv_sub_tabs[2]:
        st.subheader("UV Spectral Analysis")

        spectrum_data = uv_sys['spectrum_analyzer'].calculate_uva_uvb_ratio()

        # UVA/UVB metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Peak Wavelength",
                f"{spectrum_data['peak_wavelength']} nm",
                help="LED peak emission wavelength"
            )

        with col2:
            uva_status = "✅" if 90 <= spectrum_data['UVA_pct'] <= 97 else "⚠️"
            st.metric(
                "UVA Content",
                f"{spectrum_data['UVA_pct']:.1f}% {uva_status}",
                help="Target: 90-97% (315-400nm)"
            )

        with col3:
            uvb_status = "✅" if 3 <= spectrum_data['UVB_pct'] <= 10 else "⚠️"
            st.metric(
                "UVB Content",
                f"{spectrum_data['UVB_pct']:.1f}% {uvb_status}",
                help="Target: 3-10% (280-315nm)"
            )

        with col4:
            st.metric(
                "UVA/UVB Ratio",
                f"{spectrum_data['UVA_UVB_ratio']:.1f}",
                help="Ratio of UVA to UVB content"
            )

        # Spectral distribution plot
        st.divider()
        st.subheader("Spectral Power Distribution (SPD)")

        spd_df = uv_sys['spectrum_analyzer'].generate_spectral_distribution(resolution=1.0)

        spectrum_plot = visualizer.create_spectrum_plot(
            spectrum_df=spd_df,
            title="UV LED Spectral Power Distribution"
        )
        st.plotly_chart(spectrum_plot, use_container_width=True)

        # Export spectrum data
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("📥 Download spectral data for further analysis")
        with col2:
            csv_data = spd_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="uv_spectrum_data.csv",
                mime="text/csv"
            )

    # Tab 4: LED Aging & Maintenance
    with uv_sub_tabs[3]:
        st.subheader("LED Aging Model & Maintenance Planning")

        # Operating hours input
        col1, col2 = st.columns([2, 1])
        with col1:
            operating_hours = st.number_input(
                "Current Operating Hours",
                min_value=0,
                max_value=100000,
                value=0,
                step=1000,
                help="Enter total operating hours for aging analysis"
            )

        with col2:
            annual_hours = st.number_input(
                "Annual Usage (hrs/year)",
                min_value=500,
                max_value=8760,
                value=2000,
                step=100
            )

        # Update aging model
        aging_model = LEDAgingModel(
            led_spec=uv_sys['led_spec'],
            num_leds=uv_sys['layout']['num_leds'],
            operating_hours=operating_hours
        )

        current_output = aging_model.calculate_current_output()
        remaining_hours = aging_model.calculate_remaining_lifetime()

        # Current status
        st.divider()
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Current Output",
                f"{current_output:.1f}%",
                delta=f"{current_output - 100:.1f}%",
                help="Current LED output vs. new"
            )

        with col2:
            degradation = 100 - current_output
            st.metric(
                "Degradation",
                f"{degradation:.1f}%",
                delta_color="inverse",
                help="Total degradation from new"
            )

        with col3:
            st.metric(
                "Remaining Life (L80)",
                f"{remaining_hours:,.0f} hrs",
                help="Hours until 80% output threshold"
            )

        with col4:
            remaining_years = remaining_hours / annual_hours
            st.metric(
                "Years Remaining",
                f"{remaining_years:.1f} years",
                help=f"Based on {annual_hours} hrs/year usage"
            )

        # Aging curve
        st.divider()
        st.subheader("LED Degradation Curve")

        aging_df = aging_model.predict_degradation_curve(time_points=100)

        aging_plot = visualizer.create_aging_curve_plot(
            aging_df=aging_df,
            current_hours=operating_hours,
            title="LED Output Degradation Over Time (L80 Model)"
        )
        st.plotly_chart(aging_plot, use_container_width=True)

        # Maintenance cost projection
        st.divider()
        st.subheader("Maintenance Cost Projection")

        projection_years = st.slider("Projection Period (years)", 1, 20, 10)

        maintenance_cost = aging_model.calculate_maintenance_cost(
            years=projection_years,
            annual_usage_hours=annual_hours
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Replacement Cycles",
                f"{maintenance_cost['replacement_cycles']}",
                help=f"Over {projection_years} years"
            )

        with col2:
            st.metric(
                "Cost per Replacement",
                f"₹{maintenance_cost['cost_per_replacement']:,.0f}",
                help="Material + labor costs"
            )

        with col3:
            st.metric(
                "Total Maintenance Cost",
                f"₹{maintenance_cost['total_maintenance_cost']:,.0f}",
                help=f"{projection_years}-year total"
            )

        st.info(f"📅 Next replacement due in {maintenance_cost['next_replacement_hours']:,.0f} operating hours")

    # Tab 5: Power Requirements
    with uv_sub_tabs[4]:
        st.subheader("Power Requirements & Energy Cost Analysis")

        power_calc = uv_sys['power_calculator']
        power_req = power_calc.calculate_power_requirements()

        # Power requirements
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "LED Power",
                f"{power_req['led_power_kw']:.2f} kW",
                help="Total LED consumption"
            )

        with col2:
            st.metric(
                "Driver Losses",
                f"{power_req['driver_losses_kw']:.2f} kW",
                help="Power lost in LED drivers"
            )

        with col3:
            st.metric(
                "Total Input Power",
                f"{power_req['total_input_power_kw']:.2f} kW",
                help="Total electrical input"
            )

        with col4:
            st.metric(
                "Apparent Power",
                f"{power_req['apparent_power_kva']:.2f} kVA",
                help="Including power factor"
            )

        # Energy cost analysis
        st.divider()
        st.subheader("Energy Cost Analysis")

        col1, col2 = st.columns([2, 1])
        with col1:
            electricity_rate = st.number_input(
                "Electricity Rate (₹/kWh)",
                min_value=1.0,
                max_value=20.0,
                value=8.0,
                step=0.5,
                help="Enter your electricity tariff"
            )

        with col2:
            usage_hours = st.number_input(
                "Annual Usage (hrs/year)",
                min_value=500,
                max_value=8760,
                value=2000,
                step=100
            )

        energy_cost = power_calc.calculate_energy_cost(
            annual_usage_hours=usage_hours,
            electricity_rate=electricity_rate
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Annual Energy",
                f"{energy_cost['annual_energy_kwh']:,.0f} kWh",
                help="Total annual consumption"
            )

        with col2:
            st.metric(
                "Annual Cost",
                f"₹{energy_cost['annual_cost_inr']:,.0f}",
                help="Total annual energy cost"
            )

        with col3:
            st.metric(
                "Daily Cost",
                f"₹{energy_cost['daily_cost_inr']:.2f}",
                help="Average daily energy cost"
            )

        with col4:
            st.metric(
                "Cost per Hour",
                f"₹{energy_cost['cost_per_hour']:.2f}",
                help="Operating cost per hour"
            )

        # Power summary table
        st.divider()
        st.subheader("Detailed Power Breakdown")

        power_summary = {
            "Parameter": [
                "Number of LEDs",
                "Power per LED",
                "Total LED Power",
                "Driver Efficiency",
                "Driver Losses",
                "Power Factor",
                "Total Input Power",
                "Apparent Power"
            ],
            "Value": [
                f"{uv_sys['layout']['num_leds']} units",
                f"{uv_sys['led_spec'].power_per_led} W",
                f"{power_req['led_power_kw']:.2f} kW",
                f"{power_req['driver_efficiency'] * 100:.0f}%",
                f"{power_req['driver_losses_kw']:.2f} kW",
                f"{power_req['power_factor']}",
                f"{power_req['total_input_power_kw']:.2f} kW",
                f"{power_req['apparent_power_kva']:.2f} kVA"
            ]
        }
        st.dataframe(pd.DataFrame(power_summary), hide_index=True, use_container_width=True)

    # Tab 6: Robot Path Planning
    with uv_sub_tabs[5]:
        st.subheader("Uniformity Measurement Robot Path Planning")

        robot_planner = uv_sys['robot_planner']
        robot_planner.optimize_path()

        timing = robot_planner.calculate_cycle_time()

        # Cycle time metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Measurement Points",
                f"{timing['num_points']}",
                help="9-point uniformity grid"
            )

        with col2:
            st.metric(
                "Total Travel Distance",
                f"{timing['total_travel_distance_mm']:.0f} mm",
                help="Optimized path length"
            )

        with col3:
            st.metric(
                "Measurement Time",
                f"{timing['measurement_time_sec']:.0f} sec",
                help="Total dwell time"
            )

        with col4:
            st.metric(
                "Total Cycle Time",
                f"{timing['total_cycle_time_min']:.2f} min",
                help="Complete measurement cycle"
            )

        # Path visualization
        st.divider()
        st.subheader("Optimized Measurement Path")

        path_df = robot_planner.get_path_dataframe()

        col1, col2 = st.columns([2, 1])

        with col1:
            path_plot = visualizer.create_robot_path_visualization(
                path_df=path_df,
                title="Robot Measurement Path (Optimized)"
            )
            st.plotly_chart(path_plot, use_container_width=True)

        with col2:
            st.subheader("Path Sequence")
            st.dataframe(
                path_df[['Sequence', 'X (mm)', 'Y (mm)']],
                hide_index=True,
                height=400
            )

        # G-code export
        st.divider()
        st.subheader("Export G-Code for Robot Controller")

        col1, col2 = st.columns([3, 1])

        with col1:
            feedrate = st.number_input(
                "Feed Rate (mm/min)",
                min_value=1000,
                max_value=10000,
                value=6000,
                step=500,
                help="Robot travel speed"
            )
            st.info("📥 Download G-code program for 3-axis gantry robot")

        with col2:
            gcode = robot_planner.generate_gcode(feedrate=feedrate)
            st.download_button(
                label="Download G-Code",
                data=gcode,
                file_name="uv_uniformity_measurement.gcode",
                mime="text/plain"
            )

        # Show G-code preview
        with st.expander("Preview G-Code"):
            st.code(gcode, language="gcode")

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

# Footer
st.divider()
st.markdown(f"""
---
**{company_name}** | {company_address} | {company_email}  
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
*White-labeled PV Chamber Configurator v1.0*
""")
