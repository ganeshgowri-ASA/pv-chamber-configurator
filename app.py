import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime

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
    "📄 Reports"
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
    st.header("📄 Comprehensive Report Generator")

    st.markdown("""
    Generate professional PDF and Excel reports aggregating data from all modules.
    Reports include branding, charts, tables, and compliance documentation.
    """)

    # Report configuration
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Report Configuration")

        # Report type selector
        report_type = st.selectbox(
            "Report Type",
            [
                "Technical Specification",
                "Test Execution",
                "Compliance & Calibration",
                "Commercial Proposal",
                "Business Analysis"
            ]
        )

        # Report format
        report_format = st.selectbox(
            "Output Format",
            ["PDF", "Excel (XLSX)", "Both PDF and Excel"]
        )

        # Template selector
        template_options = ["Default Template", "Custom Template"]
        selected_template = st.selectbox("Template", template_options)

        # Report status
        report_status = st.selectbox(
            "Report Status",
            ["Final", "Draft", "Confidential"]
        )

    with col2:
        st.subheader("Report Details")

        # Report ID (auto-generated)
        report_date = datetime.now().strftime('%Y%m%d')
        report_id = st.text_input("Report ID", f"RPT-{report_date}-001")

        # Chamber ID
        chamber_id = st.text_input("Chamber ID", "PV-CHAMBER-001")

        # Generated by
        generated_by = st.text_input("Generated By", "Test Engineer")

        # Include watermark
        include_watermark = st.checkbox("Include Watermark (Draft/Confidential)")

    st.divider()

    # Report preview section
    st.subheader("📋 Report Preview")

    # Show report sections based on type
    report_sections = {
        "Technical Specification": [
            "Executive Summary",
            "Chamber Specifications",
            "Performance Characteristics",
            "CFD Simulation Results",
            "UV System Analysis",
            "Component List",
            "Appendices"
        ],
        "Test Execution": [
            "Test Parameters",
            "Data Logs Summary",
            "Uniformity Measurements",
            "Alarm History",
            "Operator Notes",
            "Pass/Fail Status"
        ],
        "Compliance & Calibration": [
            "IEC 61215/61730 Compliance",
            "ISO 17025 Calibration",
            "Uncertainty Budgets",
            "Traceability Chain",
            "Next Calibration Due"
        ],
        "Commercial Proposal": [
            "Executive Summary",
            "Technical Specifications",
            "Quote and Pricing",
            "ROI Analysis",
            "Payment Terms",
            "Delivery Timeline"
        ],
        "Business Analysis": [
            "TCO Breakdown (10-year)",
            "ROI Metrics (NPV, IRR)",
            "Competitive Comparison",
            "Sensitivity Analysis",
            "Investment Justification"
        ]
    }

    sections = report_sections.get(report_type, [])
    st.info(f"**Sections to be included:** {', '.join(sections)}")

    st.divider()

    # Generate report button
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("🎯 Generate Report", type="primary", use_container_width=True):
            with st.spinner("Generating report..."):
                try:
                    import os
                    from modules.report_generator import ReportGenerator

                    # Prepare white-label config
                    white_label_config = {
                        'company_name': company_name,
                        'company_address': company_address,
                        'company_email': company_email,
                        'user_name': generated_by
                    }

                    # Prepare data sources
                    data_sources = {
                        'chamber_specs': {
                            'dimensions': f'{length} x {width} x {height} mm',
                            'volume': f'{volume:.2f} m³',
                            'temp_range': f'{temp_range[0]}°C to {temp_range[1]}°C',
                            'humidity_range': f'{humidity_range[0]}% to {humidity_range[1]}% RH',
                            'uv_intensity': f'{uv_intensity} W/m²'
                        },
                        'uv_system': {
                            'led_type': led_type,
                            'num_leds': '28 units',
                            'total_power': '2.4 kW'
                        },
                        'test_id': report_id,
                        'chamber_id': chamber_id
                    }

                    # Create report generator
                    generator = ReportGenerator(white_label_config, data_sources)

                    # Create output directory
                    os.makedirs('generated_reports', exist_ok=True)

                    # Map report type to internal format
                    report_type_map = {
                        "Technical Specification": "technical_specification",
                        "Test Execution": "test_execution",
                        "Compliance & Calibration": "compliance",
                        "Commercial Proposal": "commercial_proposal",
                        "Business Analysis": "business_analysis"
                    }

                    internal_type = report_type_map[report_type]
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                    generated_files = []

                    # Generate PDF
                    if report_format in ["PDF", "Both PDF and Excel"]:
                        pdf_path = f'generated_reports/{internal_type}_{timestamp}.pdf'
                        generator.generate_pdf_report(internal_type, pdf_path)
                        generated_files.append(pdf_path)

                    # Generate Excel
                    if report_format in ["Excel (XLSX)", "Both PDF and Excel"]:
                        excel_path = f'generated_reports/{internal_type}_{timestamp}.xlsx'
                        generator.generate_excel_report(internal_type, excel_path)
                        generated_files.append(excel_path)

                    st.success(f"✅ Report(s) generated successfully!")

                    # Show download buttons
                    for file_path in generated_files:
                        file_name = os.path.basename(file_path)
                        with open(file_path, 'rb') as f:
                            st.download_button(
                                label=f"📥 Download {file_name}",
                                data=f.read(),
                                file_name=file_name,
                                mime='application/pdf' if file_name.endswith('.pdf') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                            )

                except Exception as e:
                    st.error(f"❌ Error generating report: {str(e)}")
                    st.exception(e)

    with col2:
        st.button("👁️ Preview", use_container_width=True, disabled=True)

    with col3:
        st.button("📧 Email", use_container_width=True, disabled=True)

    st.divider()

    # Report history
    st.subheader("📚 Recent Reports")

    # Sample report history
    report_history_data = {
        "Report ID": ["RPT-20250120-001", "RPT-20250119-003", "RPT-20250118-002"],
        "Type": ["Technical Spec", "Test Execution", "Commercial Proposal"],
        "Format": ["PDF", "Excel", "Both"],
        "Generated": ["2025-01-20 14:30", "2025-01-19 11:15", "2025-01-18 16:45"],
        "Status": ["✅ Success", "✅ Success", "✅ Success"]
    }

    df_history = pd.DataFrame(report_history_data)
    st.dataframe(df_history, use_container_width=True, hide_index=True)

    # Report statistics
    st.subheader("📊 Report Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Reports", "127")
    with col2:
        st.metric("This Month", "15", "+3")
    with col3:
        st.metric("PDF Reports", "89")
    with col4:
        st.metric("Excel Reports", "38")

# Footer
st.divider()
st.markdown(f"""
---
**{company_name}** | {company_address} | {company_email}  
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
*White-labeled PV Chamber Configurator v1.0*
""")
