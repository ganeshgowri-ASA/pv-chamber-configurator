import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import json
from datetime import datetime
import sys
import os
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# Import core calculations module
from modules.core_calculations import (
    ChamberDimensions as CoreChamberDimensions,
    PerformanceSpec, ComponentCosts,
    ChamberVolumeCalculator, HeatLoadCalculator,
    AirflowCalculator, PowerConsumptionCalculator,
    validate_chamber_configuration
)

# Import UV optical system modules
from modules.uv_optical_system import (
    create_default_uv_system,
    ChamberDimensions as UVChamberDimensions,
    LEDSpecification,
    UVLEDLayoutCalculator,
    UniformityGridMapper,
    SpectrumAnalyzer,
    LEDAgingModel,
    PowerRequirementCalculator,
    UniformityRobotPathPlanner
)
from modules.visualizations.uv_heatmap_3d import UVHeatmapVisualizer

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

# Import Supplier Database modules
from modules.supplier_database import SupplierDatabaseManager
from modules.quote_parser import auto_detect_and_parse
from modules.init_database import initialize_database

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
