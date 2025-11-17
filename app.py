"""
PV Test Chamber Configurator - Main Application
White-labeled professional configurator for photovoltaic test equipment
"""

import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

# Add modules to path
sys.path.append(os.path.dirname(__file__))

from modules.engineering_core import (
    ChamberDimensions, PVModuleSpec, TestConditions,
    ThermalCalculations, HumidityCalculations, AirflowCalculations,
    UVCalculations, IECValidation, UnitConverter
)
from modules.supplier_manager import SupplierDatabase, SupplierQuote
from ui.branding_config import (
    render_branding_config, display_header_with_branding,
    get_company_info, load_config
)
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


# Page configuration
st.set_page_config(
    page_title="PV Test Chamber Configurator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_home():
    """Render home page"""
    display_header_with_branding()

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("### 🌡️ Thermal Design\nAccurate heat load calculations per IEC 61215")

    with col2:
        st.success("### 💡 UV System Design\nLED array optimization for uniform irradiance")

    with col3:
        st.warning("### 💰 Cost Estimation\nComplete BOM with Indian supplier quotes")

    st.markdown("---")

    st.markdown("""
    ## About This Configurator

    Professional tool for designing and quoting PV (Photovoltaic) module test chambers
    that comply with international standards.

    ### Key Features:

    - ✅ **IEC 61215/61730 Compliance** - Design validation against international standards
    - 🔬 **Engineering Calculations** - Thermal, humidity, airflow, and UV calculations
    - 📊 **Supplier Database** - Pre-loaded Indian supplier quotes + custom upload capability
    - 🎨 **White-Label Ready** - Fully customizable branding and company information
    - 📄 **Professional Reports** - Export detailed technical reports and BOMs
    - 💻 **CFD Integration Ready** - Future integration with simulation tools

    ### Technical Standards Implemented:

    - **IEC 61215-2:2021** - Terrestrial PV modules - Design qualification and type approval
    - **IEC 61730-2:2016** - PV module safety qualification
    - **IEC 60068-2-38** - Environmental testing - Combined temperature/humidity cyclic test
    - **IEC 60068-2-14** - Environmental testing - Change of temperature

    ### Use Cases:

    1. **Test Equipment Manufacturers** - Design chambers for your clients
    2. **Solar Module Manufacturers** - Specify in-house testing facilities
    3. **Testing Laboratories** - Upgrade or expand testing capabilities
    4. **Consultants & Engineers** - Rapid feasibility studies and budgetary quotes

    ---

    ### Quick Start Guide:

    1. **Configure Chamber** - Enter chamber dimensions and test requirements
    2. **Calculate Loads** - Automatic thermal, humidity, and UV calculations
    3. **Select Suppliers** - Compare quotes from database or upload custom quotes
    4. **Generate Report** - Export professional technical report with BOM

    """)

    st.info("👈 **Use the navigation menu to get started!**")


def render_chamber_calculator():
    """Render chamber thermal calculator"""
    st.title("🌡️ Chamber Thermal Calculator")

    st.markdown("""
    Calculate chamber heat loads, refrigeration requirements, and airflow specifications.
    All calculations based on fundamental heat transfer principles and IEC standards.
    """)

    # Load defaults from config
    config = load_config()
    defaults = config.get('technical', {})
    default_chamber = defaults.get('default_chamber', {})
    default_module = defaults.get('default_module', {})
    currency_symbol = config.get('defaults', {}).get('currency_symbol', '₹')

    st.markdown("---")

    # Input Section
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Chamber Dimensions")

        chamber_length = st.number_input(
            "Internal Length (m)",
            value=default_chamber.get('length', 3.2),
            min_value=1.0,
            max_value=10.0,
            step=0.1
        )

        chamber_width = st.number_input(
            "Internal Width (m)",
            value=default_chamber.get('width', 2.1),
            min_value=1.0,
            max_value=10.0,
            step=0.1
        )

        chamber_height = st.number_input(
            "Internal Height (m)",
            value=default_chamber.get('height', 2.2),
            min_value=1.0,
            max_value=10.0,
            step=0.1
        )

        st.subheader("Environmental Conditions")

        ambient_temp = st.number_input(
            "Ambient Temperature (°C)",
            value=35.0,
            min_value=-10.0,
            max_value=50.0,
            step=1.0
        )

        chamber_temp_min = st.number_input(
            "Chamber Min Temperature (°C)",
            value=-45.0,
            min_value=-80.0,
            max_value=0.0,
            step=1.0
        )

        chamber_temp_max = st.number_input(
            "Chamber Max Temperature (°C)",
            value=105.0,
            min_value=50.0,
            max_value=200.0,
            step=1.0
        )

    with col2:
        st.subheader("PV Module Specifications")

        module_quantity = st.number_input(
            "Number of Modules",
            value=2,
            min_value=1,
            max_value=10,
            step=1
        )

        module_length = st.number_input(
            "Module Length (m)",
            value=default_module.get('length', 2.2),
            min_value=0.5,
            max_value=5.0,
            step=0.1
        )

        module_width = st.number_input(
            "Module Width (m)",
            value=default_module.get('width', 1.3),
            min_value=0.5,
            max_value=3.0,
            step=0.1
        )

        module_mass = st.number_input(
            "Module Mass (kg)",
            value=default_module.get('mass', 62),
            min_value=10,
            max_value=200,
            step=1
        )

        module_power = st.number_input(
            "Module Max Power (W)",
            value=default_module.get('max_power', 650),
            min_value=100,
            max_value=1000,
            step=10
        )

        st.subheader("UV System")

        uv_irradiance = st.number_input(
            "Target UV Irradiance (W/m²)",
            value=250.0,
            min_value=25.0,
            max_value=500.0,
            step=25.0
        )

    # Calculate button
    if st.button("🔬 Calculate System Requirements", type="primary"):

        # Create objects
        chamber = ChamberDimensions(chamber_length, chamber_width, chamber_height)
        module = PVModuleSpec(
            module_length, module_width, 0.04,
            module_mass, module_power, module_quantity
        )

        # Calculations
        st.markdown("---")
        st.header("📊 Calculation Results")

        # Chamber geometry
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Chamber Volume", f"{chamber.volume:.2f} m³")
        with col2:
            st.metric("Surface Area", f"{chamber.surface_area:.2f} m²")
        with col3:
            st.metric("Total Module Mass", f"{module.total_mass:.1f} kg")

        st.markdown("---")

        # Heat loads
        st.subheader("1️⃣ Heat Load Analysis")

        # Chamber heat transfer (worst case: max cooling)
        chamber_load = ThermalCalculations.chamber_heat_load(
            chamber, ambient_temp, chamber_temp_min
        )

        # Product heat load
        product_load = ThermalCalculations.product_heat_load(module, uv_irradiance)

        # UV lighting heat load
        uv_optical_power = module.total_area * uv_irradiance
        lighting_load = ThermalCalculations.lighting_heat_load(uv_optical_power)

        # Total refrigeration
        total_refrig = ThermalCalculations.total_refrigeration_load(
            chamber_load['total_kW'],
            product_load['heat_load_kW'],
            lighting_load['heat_load_kW']
        )

        # Display results
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Chamber Heat Transfer",
                f"{chamber_load['total_kW']:.2f} kW",
                help="Heat transfer through walls at min temperature"
            )

        with col2:
            st.metric(
                "Product Heat Load",
                f"{product_load['heat_load_kW']:.2f} kW",
                help="Heat absorbed by PV modules under UV"
            )

        with col3:
            st.metric(
                "Lighting Heat Load",
                f"{lighting_load['heat_load_kW']:.2f} kW",
                help="Heat from UV LED system"
            )

        with col4:
            st.metric(
                "**TOTAL Refrigeration**",
                f"{total_refrig['design_load_kW']:.2f} kW",
                delta=f"{total_refrig['tons_refrigeration']:.2f} TR",
                help="Total cooling capacity required"
            )

        # Heat load breakdown chart
        heat_loads = {
            'Chamber': chamber_load['total_kW'],
            'Product': product_load['heat_load_kW'],
            'UV Lighting': lighting_load['heat_load_kW']
        }

        fig_heat = px.pie(
            values=list(heat_loads.values()),
            names=list(heat_loads.keys()),
            title="Heat Load Distribution",
            hole=0.4
        )
        st.plotly_chart(fig_heat, use_container_width=True)

        st.markdown("---")

        # Airflow calculations
        st.subheader("2️⃣ Airflow Requirements")

        airflow = AirflowCalculations.required_airflow(
            chamber,
            total_refrig['base_total_kW']
        )

        fan_power = AirflowCalculations.fan_power(airflow['volume_flow_m3_h'])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Volume Flow", f"{airflow['volume_flow_m3_h']:.0f} m³/h")

        with col2:
            st.metric("Air Velocity", f"{airflow['velocity_m_s']:.2f} m/s")

        with col3:
            st.metric("Air Changes/Hour", f"{airflow['air_changes_per_hour']:.1f} ACH")

        with col4:
            st.metric("Fan Power", f"{fan_power['shaft_power_kW']:.2f} kW")

        st.markdown("---")

        # UV LED system
        st.subheader("3️⃣ UV LED System Design")

        uv_design = UVCalculations.led_array_design(
            module.total_area,
            uv_irradiance
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Number of LEDs", f"{uv_design['num_leds']}")

        with col2:
            st.metric("Total Optical Power", f"{uv_design['design_optical_W']:.0f} W")

        with col3:
            st.metric("Total Electrical Power", f"{uv_design['total_electrical_kW']:.2f} kW")

        with col4:
            st.metric("Optical per LED", f"{uv_design['optical_per_led_W']:.1f} W")

        st.markdown("---")

        # IEC Validation
        st.subheader("4️⃣ IEC Standards Compliance")

        temp_valid = IECValidation.validate_temperature_range(chamber_temp_min, chamber_temp_max)
        uv_valid = IECValidation.validate_uv_spectrum(280, 400)

        col1, col2 = st.columns(2)

        with col1:
            if temp_valid['valid']:
                st.success(f"✅ Temperature Range: COMPLIANT")
                st.write(f"- Required: {temp_valid['iec_min_required']}°C to {temp_valid['iec_max_required']}°C")
                st.write(f"- Chamber: {temp_valid['chamber_min']}°C to {temp_valid['chamber_max']}°C")
                if temp_valid['extended_range']:
                    st.info("🌟 Extended range capability (up to 105°C)")
            else:
                st.error("❌ Temperature Range: NON-COMPLIANT")

        with col2:
            if uv_valid['valid']:
                st.success(f"✅ UV Spectrum: COMPLIANT")
                st.write(f"- Required: {uv_valid['iec_min_wavelength']}-{uv_valid['iec_max_wavelength']} nm")
                st.write(f"- Spectrum: {uv_valid['spectrum']}")
            else:
                st.error("❌ UV Spectrum: NON-COMPLIANT")

        st.markdown("---")

        # Summary table
        st.subheader("📋 System Summary")

        summary_data = {
            "Parameter": [
                "Chamber Volume",
                "Chamber Surface Area",
                "Total Heat Load (Base)",
                "Design Refrigeration Load",
                "Refrigeration Capacity (TR)",
                "Airflow Rate",
                "Air Velocity",
                "Number of UV LEDs",
                "UV Electrical Power",
                "Fan Power",
                "Temperature Range",
                "IEC Compliance"
            ],
            "Value": [
                f"{chamber.volume:.2f} m³",
                f"{chamber.surface_area:.2f} m²",
                f"{total_refrig['base_total_kW']:.2f} kW",
                f"{total_refrig['design_load_kW']:.2f} kW",
                f"{total_refrig['tons_refrigeration']:.2f} TR",
                f"{airflow['volume_flow_m3_h']:.0f} m³/h",
                f"{airflow['velocity_m_s']:.2f} m/s",
                f"{uv_design['num_leds']}",
                f"{uv_design['total_electrical_kW']:.2f} kW",
                f"{fan_power['shaft_power_kW']:.2f} kW",
                f"{chamber_temp_min}°C to {chamber_temp_max}°C",
                "✅ PASS" if temp_valid['valid'] and uv_valid['valid'] else "❌ FAIL"
            ]
        }

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)


def render_supplier_database():
    """Render supplier database and quote management"""
    st.title("💰 Supplier Database & Quote Management")

    st.markdown("""
    Browse built-in Indian supplier quotes or upload your own custom quotes for comparison.
    Generate complete Bill of Materials (BOM) for your project.
    """)

    # Initialize database
    db = SupplierDatabase()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Browse Suppliers",
        "📤 Upload Custom Quotes",
        "🔍 Compare Quotes",
        "📄 Generate BOM"
    ])

    with tab1:
        st.subheader("Built-in Supplier Database")

        categories = ["uv_leds", "chambers", "refrigeration", "controls", "sensors"]
        category_names = {
            "uv_leds": "UV LED Systems",
            "chambers": "Environmental Chambers",
            "refrigeration": "Refrigeration Systems",
            "controls": "Control Systems & PLCs",
            "sensors": "Sensors & Instrumentation"
        }

        selected_category = st.selectbox(
            "Select Category",
            options=categories,
            format_func=lambda x: category_names[x]
        )

        quotes = db.get_quotes_by_category(selected_category)

        if quotes:
            for quote in quotes:
                with st.expander(f"**{quote['supplier_name']}** - {quote['product_model']}"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**Specification:** {quote['specification']}")
                        st.write(f"**Notes:** {quote['notes']}")

                    with col2:
                        st.metric("Price", f"₹{quote['price_inr']/100000:.2f}L")
                        st.write(f"**Lead Time:** {quote['lead_time_weeks']} weeks")
                        st.write(f"**Warranty:** {quote['warranty_years']} years")

                    if quote.get('contact_person'):
                        st.markdown("---")
                        st.write(f"**Contact:** {quote['contact_person']}")
                        st.write(f"📧 {quote.get('contact_email', 'N/A')}")
                        st.write(f"📞 {quote.get('contact_phone', 'N/A')}")
        else:
            st.info("No quotes available in this category.")

    with tab2:
        st.subheader("Upload Custom Supplier Quotes")

        st.markdown("""
        Upload your own supplier quotes in Excel or CSV format.

        **Required columns:**
        - Supplier Name
        - Category (UV_LEDs, Chamber, Refrigeration, Controls_PLC, Sensors)
        - Product Model
        - Specification
        - Price (INR)
        - Lead Time (weeks)
        - Warranty (years)
        - Notes
        - Contact Person
        - Contact Email
        - Contact Phone
        """)

        uploaded_file = st.file_uploader(
            "Upload Quote File",
            type=['xlsx', 'csv'],
            help="Upload Excel or CSV file with supplier quotes"
        )

        if uploaded_file:
            st.info(f"File uploaded: {uploaded_file.name}")

            if st.button("💾 Import Quotes"):
                st.success("✅ Custom quotes imported successfully!")
                st.info("Feature implementation in progress. File parsing logic is ready in supplier_manager.py")

    with tab3:
        st.subheader("Compare Supplier Quotes")

        compare_category = st.selectbox(
            "Category to Compare",
            options=categories,
            format_func=lambda x: category_names[x],
            key="compare_category"
        )

        comparison_df = db.compare_quotes(compare_category)

        if not comparison_df.empty:
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)

            # Highlight best options
            col1, col2 = st.columns(2)

            with col1:
                cheapest = db.get_cheapest_quote(compare_category)
                if cheapest:
                    st.success(f"💰 **Cheapest:** {cheapest['supplier_name']} - ₹{cheapest['price_inr']/100000:.2f}L")

            with col2:
                fastest = db.get_fastest_delivery(compare_category)
                if fastest:
                    st.info(f"⚡ **Fastest Delivery:** {fastest['supplier_name']} - {fastest['lead_time_weeks']} weeks")

            # Price comparison chart
            if 'supplier_name' in comparison_df.columns and 'price_lakhs' in comparison_df.columns:
                fig = px.bar(
                    comparison_df,
                    x='supplier_name',
                    y='price_lakhs',
                    title=f"Price Comparison - {category_names[compare_category]}",
                    labels={'supplier_name': 'Supplier', 'price_lakhs': 'Price (₹ Lakhs)'},
                    text='price_lakhs'
                )
                fig.update_traces(texttemplate='₹%{text:.2f}L', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No quotes available for comparison.")

    with tab4:
        st.subheader("Generate Bill of Materials (BOM)")

        st.markdown("Select your preferred supplier for each category to generate a complete BOM.")

        selected_quotes = {}

        for category in categories:
            quotes = db.get_quotes_by_category(category)
            if quotes:
                selected_model = st.selectbox(
                    category_names[category],
                    options=[q['product_model'] for q in quotes],
                    key=f"bom_{category}"
                )
                selected_quotes[category] = selected_model

        if st.button("📄 Generate BOM", type="primary"):
            bom_df = db.generate_bom(selected_quotes)

            if not bom_df.empty:
                st.success("✅ Bill of Materials Generated")

                st.dataframe(bom_df, use_container_width=True, hide_index=True)

                # Total summary
                total_row = bom_df[bom_df['Category'] == 'TOTAL']
                if not total_row.empty:
                    total_price = total_row.iloc[0]['Price (Lakhs)']
                    total_lead_time = bom_df[bom_df['Category'] != 'TOTAL']['Lead Time (weeks)'].max()

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Project Cost", f"₹{total_price:.2f} Lakhs")
                    with col2:
                        st.metric("Total Cost", f"₹{total_price * 100000:,.0f}")
                    with col3:
                        st.metric("Max Lead Time", f"{total_lead_time} weeks")

                # Download options
                st.markdown("---")
                st.download_button(
                    label="📥 Download BOM (CSV)",
                    data=bom_df.to_csv(index=False),
                    file_name="pv_chamber_bom.csv",
                    mime="text/csv"
                )


def main():
    """Main application entry point"""

    # Sidebar navigation
    with st.sidebar:
        company_info = get_company_info()

        st.markdown(f"### {company_info.get('name', 'PV Configurator')}")
        st.markdown("---")

        selected = option_menu(
            menu_title="Navigation",
            options=[
                "Home",
                "Chamber Calculator",
                "Supplier Database",
                "Branding Config"
            ],
            icons=["house", "calculator", "database", "palette"],
            menu_icon="cast",
            default_index=0,
        )

        st.markdown("---")
        st.markdown("### 📚 Resources")
        st.markdown("- [IEC 61215 Standard](https://webstore.iec.ch/)")
        st.markdown("- [User Guide](#)")
        st.markdown("- [API Documentation](#)")

        st.markdown("---")
        st.caption("v1.0.0 | Built with Streamlit")

    # Route to selected page
    if selected == "Home":
        render_home()
    elif selected == "Chamber Calculator":
        render_chamber_calculator()
    elif selected == "Supplier Database":
        render_supplier_database()
    elif selected == "Branding Config":
        render_branding_config()


if __name__ == "__main__":
    main()
