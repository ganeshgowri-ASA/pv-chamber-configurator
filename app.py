import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
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

# Import supplier database modules
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

# Initialize database (only runs once if empty)
@st.cache_resource
def get_database():
    """Initialize and return database manager."""
    return initialize_database()

db = get_database()

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
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📐 Chamber Design",
    "💡 UV System",
    "💰 Quote Generator",
    "📊 Supplier Database",
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
    st.header("📊 Supplier Database & Quote Comparison")

    # Subtabs for different sections
    subtab1, subtab2, subtab3, subtab4, subtab5 = st.tabs([
        "📤 Upload Quote",
        "🏢 Suppliers",
        "📦 Components",
        "💲 Price Comparison",
        "🎯 Procurement Recommendation"
    ])

    # Upload Quote Tab
    with subtab1:
        st.subheader("Upload & Parse Quote")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Supplier selection
            suppliers_df = db.get_suppliers()
            if not suppliers_df.empty:
                supplier_names = suppliers_df['name'].tolist()
                selected_supplier = st.selectbox("Select Supplier", supplier_names)
                supplier_id = suppliers_df[suppliers_df['name'] == selected_supplier]['id'].iloc[0]
            else:
                st.warning("No suppliers found. Please add suppliers first.")
                supplier_id = None

            # File upload
            uploaded_file = st.file_uploader(
                "Upload Quote (PDF, Excel, or CSV)",
                type=['pdf', 'xlsx', 'xls', 'csv'],
                help="Upload a quote file to automatically parse component prices"
            )

            if uploaded_file and supplier_id:
                # Save uploaded file temporarily
                temp_dir = "data/temp_quotes"
                os.makedirs(temp_dir, exist_ok=True)
                temp_path = os.path.join(temp_dir, uploaded_file.name)

                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                if st.button("Parse Quote", type="primary"):
                    with st.spinner("Parsing quote..."):
                        # Parse the quote
                        result = auto_detect_and_parse(temp_path)

                        if result.get('success'):
                            st.success("Quote parsed successfully!")

                            # Display metadata
                            if result.get('metadata'):
                                st.write("**Quote Metadata:**")
                                metadata_df = pd.DataFrame([result['metadata']])
                                st.dataframe(metadata_df, use_container_width=True)

                            # Display items
                            if result.get('items'):
                                st.write(f"**Found {len(result['items'])} items:**")
                                items_df = pd.DataFrame(result['items'])
                                st.dataframe(items_df, use_container_width=True)

                                # Option to save to database
                                if st.button("Save Quote to Database"):
                                    try:
                                        # Prepare quote data
                                        quote_data = {
                                            'supplier_id': supplier_id,
                                            'quote_date': result['metadata'].get('quote_date', datetime.now().strftime('%Y-%m-%d')),
                                            'quote_number': result['metadata'].get('quote_number', ''),
                                            'validity_days': result['metadata'].get('validity_days', 30),
                                            'total_cost': result['metadata'].get('total_cost', sum(item['total_price'] for item in result['items'])),
                                            'uploaded_file': uploaded_file.name,
                                            'parsed_data': json.dumps(result),
                                            'status': 'active'
                                        }

                                        # Add quote
                                        quote_id = db.add_quote(quote_data, result['items'])
                                        st.success(f"Quote saved successfully! Quote ID: {quote_id}")

                                    except Exception as e:
                                        st.error(f"Error saving quote: {str(e)}")
                            else:
                                st.warning("No items found in quote. You may need to enter data manually.")
                        else:
                            st.error(f"Failed to parse quote: {result.get('error', 'Unknown error')}")
                            if result.get('raw_text'):
                                with st.expander("View Raw Extracted Text"):
                                    st.text(result['raw_text'][:2000])  # Show first 2000 chars

        with col2:
            st.info("""
            **Supported Formats:**
            - PDF quotes
            - Excel files (.xlsx, .xls)
            - CSV files

            **Auto-parsing extracts:**
            - Component names
            - Quantities
            - Unit prices
            - Total prices
            - Lead times
            - Warranty terms
            """)

    # Suppliers Tab
    with subtab2:
        st.subheader("Supplier Management")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Display all suppliers
            suppliers_df = db.get_suppliers()
            if not suppliers_df.empty:
                st.dataframe(
                    suppliers_df[['name', 'location', 'rating', 'avg_delivery_days', 'payment_terms', 'contact', 'email']],
                    use_container_width=True
                )

                # Statistics
                st.write("**Supplier Statistics:**")
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    st.metric("Total Suppliers", len(suppliers_df))
                with stats_col2:
                    st.metric("Avg Rating", f"{suppliers_df['rating'].mean():.2f}/5.0")
                with stats_col3:
                    st.metric("Avg Delivery", f"{suppliers_df['avg_delivery_days'].mean():.0f} days")
            else:
                st.info("No suppliers found in database.")

        with col2:
            # Add new supplier form
            with st.expander("➕ Add New Supplier"):
                with st.form("add_supplier_form"):
                    new_name = st.text_input("Supplier Name*")
                    new_contact = st.text_input("Contact Number")
                    new_email = st.text_input("Email")
                    new_location = st.text_input("Location")
                    new_rating = st.slider("Rating", 0.0, 5.0, 3.5, 0.1)
                    new_delivery = st.number_input("Avg Delivery Days", 1, 180, 30)
                    new_payment = st.selectbox("Payment Terms", ["Net 15", "Net 30", "Net 45", "Net 60", "50% Advance"])

                    submitted = st.form_submit_button("Add Supplier")
                    if submitted and new_name:
                        try:
                            supplier_data = {
                                'name': new_name,
                                'contact': new_contact,
                                'email': new_email,
                                'location': new_location,
                                'rating': new_rating,
                                'avg_delivery_days': new_delivery,
                                'payment_terms': new_payment
                            }
                            supplier_id = db.add_supplier(supplier_data)
                            st.success(f"Supplier added successfully! ID: {supplier_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding supplier: {str(e)}")

    # Components Tab
    with subtab3:
        st.subheader("Component Catalog")

        # Category filter
        categories = db.get_categories()
        selected_category = st.selectbox("Filter by Category", ["All"] + categories)

        # Get components
        if selected_category == "All":
            components_df = db.get_components()
        else:
            components_df = db.get_components(category=selected_category)

        if not components_df.empty:
            # Display components
            st.dataframe(
                components_df[['category', 'name', 'specification', 'supplier_name', 'price',
                             'lead_time_days', 'warranty_months', 'moq']],
                use_container_width=True
            )

            # Statistics
            st.write("**Component Statistics:**")
            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
            with stats_col1:
                st.metric("Total Components", len(components_df))
            with stats_col2:
                st.metric("Avg Price", f"₹{components_df['price'].mean():,.0f}")
            with stats_col3:
                st.metric("Avg Lead Time", f"{components_df['lead_time_days'].mean():.0f} days")
            with stats_col4:
                st.metric("Avg Warranty", f"{components_df['warranty_months'].mean():.0f} months")

            # Export option
            if st.button("Export to Excel"):
                export_path = db.export_comparison_report(components_df, format='excel',
                                                         output_path='data/components_export')
                st.success(f"Components exported to: {export_path}")
        else:
            st.info("No components found.")

    # Price Comparison Tab
    with subtab4:
        st.subheader("Price Comparison & Best Value Analysis")

        # Select category for comparison
        categories = db.get_categories()
        if categories:
            compare_category = st.selectbox("Select Category to Compare", categories)

            if compare_category:
                # Get best value analysis
                comparison_df = db.get_best_value_supplier(compare_category)

                if not comparison_df.empty:
                    # Display results with scores
                    st.write(f"**Price Comparison for {compare_category}:**")

                    display_cols = ['name', 'supplier_name', 'price', 'lead_time_days',
                                  'warranty_months', 'rating', 'total_score']

                    # Highlight best value (highest score)
                    st.dataframe(
                        comparison_df[display_cols].style.background_gradient(
                            subset=['total_score'], cmap='RdYlGn'
                        ),
                        use_container_width=True
                    )

                    # Show recommendation
                    best_supplier = comparison_df.iloc[0]
                    st.success(f"""
                    **Recommended Supplier:** {best_supplier['supplier_name']}
                    - Price: ₹{best_supplier['price']:,.2f}
                    - Lead Time: {best_supplier['lead_time_days']} days
                    - Warranty: {best_supplier['warranty_months']} months
                    - Supplier Rating: {best_supplier['rating']}/5.0
                    - Overall Score: {best_supplier['total_score']:.1f}/100
                    """)

                    # Visualization
                    fig = go.Figure()

                    # Add bars for total score
                    fig.add_trace(go.Bar(
                        x=comparison_df['supplier_name'],
                        y=comparison_df['total_score'],
                        text=comparison_df['total_score'].round(1),
                        textposition='auto',
                        marker_color=comparison_df['total_score'],
                        marker_colorscale='RdYlGn',
                        name='Total Score'
                    ))

                    fig.update_layout(
                        title=f"Supplier Comparison Score - {compare_category}",
                        xaxis_title="Supplier",
                        yaxis_title="Total Score (out of 100)",
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Detailed score breakdown
                    with st.expander("View Detailed Score Breakdown"):
                        score_cols = ['supplier_name', 'price_score', 'lead_time_score',
                                    'rating_score', 'warranty_score', 'payment_score', 'total_score']
                        st.dataframe(comparison_df[score_cols], use_container_width=True)
                else:
                    st.warning(f"No components found in category: {compare_category}")
        else:
            st.info("No categories available for comparison.")

    # Procurement Recommendation Tab
    with subtab5:
        st.subheader("Procurement Recommendation Engine")

        st.write("Define your component requirements to get optimal supplier recommendations:")

        # Component requirements input
        num_requirements = st.number_input("Number of Components Required", 1, 20, 5)

        requirements = []
        for i in range(num_requirements):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                categories = db.get_categories()
                category = st.selectbox(f"Category {i+1}", [""] + categories, key=f"cat_{i}")
            with col2:
                quantity = st.number_input(f"Qty {i+1}", 1, 100, 1, key=f"qty_{i}")
            with col3:
                st.write("")  # Spacing

            if category:
                requirements.append({
                    'category': category,
                    'quantity': quantity
                })

        if requirements and st.button("Generate Recommendation", type="primary"):
            with st.spinner("Analyzing procurement options..."):
                # Generate recommendation
                recommendation = db.generate_procurement_recommendation(requirements)

                # Display summary
                st.write("**Procurement Summary:**")
                sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)

                with sum_col1:
                    st.metric("Total Cost", f"₹{recommendation['total_cost']:,.2f}")
                with sum_col2:
                    st.metric("Max Lead Time", f"{recommendation['max_lead_time_days']} days")
                with sum_col3:
                    st.metric("Suppliers", recommendation['num_suppliers'])
                with sum_col4:
                    risk_color = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
                    st.metric("Risk Level", f"{risk_color.get(recommendation['risk_level'], '⚪')} {recommendation['risk_level']}")

                # Display recommendations
                st.write("**Recommended Components & Suppliers:**")
                rec_df = pd.DataFrame(recommendation['recommendations'])
                st.dataframe(rec_df, use_container_width=True)

                # Supplier distribution
                st.write("**Supplier Distribution:**")
                supplier_dist = pd.DataFrame(
                    list(recommendation['supplier_distribution'].items()),
                    columns=['Supplier', 'Number of Components']
                )

                fig = go.Figure(data=[go.Pie(
                    labels=supplier_dist['Supplier'],
                    values=supplier_dist['Number of Components'],
                    hole=0.3
                )])
                fig.update_layout(title="Component Distribution by Supplier")
                st.plotly_chart(fig, use_container_width=True)

                # Risk assessment
                st.write("**Risk Assessment:**")
                if recommendation['risk_level'] == "High":
                    st.warning("""
                    ⚠️ **High Risk**: Only 1 supplier selected. Consider diversifying suppliers to reduce dependency.
                    """)
                elif recommendation['risk_level'] == "Medium":
                    st.info("""
                    ℹ️ **Medium Risk**: 2 suppliers selected. Acceptable risk level, but consider adding one more supplier for critical components.
                    """)
                else:
                    st.success("""
                    ✅ **Low Risk**: Multiple suppliers selected. Good diversification reduces supply chain risk.
                    """)

                # Export option
                if st.button("Export Recommendation"):
                    export_path = db.export_comparison_report(rec_df, format='excel',
                                                             output_path='data/procurement_recommendation')
                    st.success(f"Recommendation exported to: {export_path}")

with tab5:
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

with tab6:
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

with tab7:
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
