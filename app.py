import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime
import sys
import os

# Add modules directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

# Import compliance and calibration modules
try:
    from modules.iec_compliance import IECComplianceChecker, ChamberSpecifications
    from modules.iso17025_calibration import (
        ISO17025Calibration, LabAccreditation, AccreditationBody,
        InstrumentData, InstrumentType, CalibrationResults,
        EnvironmentalConditions, CalibrationPoint
    )
    from modules.uncertainty_calculator import UncertaintyCalculator
    from modules.compliance_checklist import ComplianceChecklist
    COMPLIANCE_MODULES_AVAILABLE = True
except ImportError:
    COMPLIANCE_MODULES_AVAILABLE = False

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
    "✅ Compliance & Calibration"
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
    st.header("✅ Compliance & Calibration System")

    if not COMPLIANCE_MODULES_AVAILABLE:
        st.error("Compliance modules not available. Please check installation.")
    else:
        # Sub-tabs for different functions
        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "IEC Compliance Checker",
            "ISO 17025 Calibration",
            "Uncertainty Calculator",
            "Compliance Checklists"
        ])

        with subtab1:
            st.subheader("IEC 61215/61730/60068 Compliance Validation")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Chamber Specifications**")
                temp_min = st.number_input("Min Temperature (°C)", value=-45.0, step=1.0)
                temp_max = st.number_input("Max Temperature (°C)", value=105.0, step=1.0)
                hum_min = st.number_input("Min Humidity (%RH)", value=40.0, step=5.0)
                hum_max = st.number_input("Max Humidity (%RH)", value=95.0, step=5.0)
                temp_uniformity = st.number_input("Temp Uniformity (±°C)", value=2.0, step=0.1)
                air_velocity = st.number_input("Air Velocity (m/s)", value=1.5, step=0.1)
                ramp_rate = st.number_input("Ramp Rate (°C/min)", value=2.0, step=0.1)

            with col2:
                st.markdown("**UV System (if applicable)**")
                has_uv = st.checkbox("UV System Installed", value=True)
                uv_intensity_max = st.number_input("Max UV Intensity (W/m²)", value=250.0, step=10.0) if has_uv else 0.0
                uv_wl_min = st.number_input("UV Wavelength Min (nm)", value=280.0) if has_uv else 280.0
                uv_wl_max = st.number_input("UV Wavelength Max (nm)", value=400.0) if has_uv else 400.0
                uv_uniformity = st.number_input("UV Uniformity (±%)", value=8.5) if has_uv else 0.0

            if st.button("Run Compliance Check", type="primary"):
                # Create chamber specifications
                chamber_specs = ChamberSpecifications(
                    temp_min=temp_min,
                    temp_max=temp_max,
                    humidity_min=hum_min,
                    humidity_max=hum_max,
                    temp_uniformity=temp_uniformity,
                    air_velocity=air_velocity,
                    ramp_rate=ramp_rate,
                    recovery_time=25.0,
                    volume=14.78,
                    has_uv_system=has_uv,
                    uv_intensity_max=uv_intensity_max,
                    uv_wavelength_range=(uv_wl_min, uv_wl_max),
                    uv_uniformity=uv_uniformity
                )

                # Run compliance checks
                checker = IECComplianceChecker(chamber_specs)

                with st.spinner("Validating IEC compliance..."):
                    # IEC 61215 tests
                    iec_61215_results = checker.validate_iec_61215_capability()

                    # IEC 61730 tests
                    iec_61730_results = checker.validate_iec_61730_capability()

                    # IEC 60068 tests
                    uniformity_result = checker.validate_chamber_uniformity()
                    velocity_result = checker.check_air_velocity()
                    recovery_result = checker.validate_recovery_time()

                    # Generate summary
                    summary = checker.generate_compliance_summary()

                # Display results
                st.success("Compliance check completed!")

                # Overall compliance
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Tests", summary['overall_compliance']['total_tests'])
                with col2:
                    st.metric("Compliant", summary['overall_compliance']['compliant_tests'],
                             delta=f"{summary['overall_compliance']['compliance_rate']}")
                with col3:
                    st.metric("Non-Compliant", summary['overall_compliance']['non_compliant_tests'],
                             delta_color="inverse")

                # Detailed results
                st.markdown("### Detailed Test Results")

                for result_dict in summary['test_results']:
                    with st.expander(f"{result_dict['test_id']}: {result_dict['test_name']} - {result_dict['status']}"):
                        if result_dict['status'] == "FAIL":
                            st.error("**Issues Found:**")
                            for issue in result_dict['issues']:
                                st.write(f"- {issue}")

                            if result_dict['recommendations']:
                                st.info("**Recommendations:**")
                                for rec in result_dict['recommendations']:
                                    st.write(f"- {rec}")
                        else:
                            st.success("Test requirements met")

                # Gaps analysis
                gaps = checker.identify_gaps()
                if gaps:
                    st.markdown("### ⚠️ Compliance Gaps")
                    for gap in gaps:
                        st.warning(f"**{gap['test_name']}** ({gap['priority']} priority)")
                        for rec in gap['recommendations']:
                            st.write(f"→ {rec}")

                # Download report
                report = checker.generate_iec_61215_report()
                st.download_button(
                    label="Download IEC 61215 Compliance Report",
                    data=report,
                    file_name="iec_61215_compliance_report.txt",
                    mime="text/plain"
                )

        with subtab2:
            st.subheader("ISO/IEC 17025:2017 Calibration Certificate Generator")

            # Lab information
            st.markdown("**Laboratory Accreditation**")
            col1, col2 = st.columns(2)
            with col1:
                lab_name = st.text_input("Laboratory Name", "PV Testing Laboratory")
                lab_cert = st.text_input("Accreditation Certificate No.", "TC-1234")
                lab_body = st.selectbox("Accreditation Body", ["NABL", "A2LA", "ILAC", "UKAS"])
            with col2:
                lab_address = st.text_area("Laboratory Address", "Tamil Nadu, India")
                lab_contact = st.text_input("Contact", "+91-XXX-XXX-XXXX")
                lab_email = st.text_input("Email", "lab@pvtesting.com")

            st.divider()

            # Instrument information
            st.markdown("**Instrument Under Calibration**")
            col1, col2 = st.columns(2)
            with col1:
                inst_type = st.selectbox("Instrument Type", [
                    "RTD Temperature Sensor",
                    "Thermocouple",
                    "Humidity Sensor",
                    "UV Radiometer"
                ])
                inst_make = st.text_input("Make", "Manufacturer")
                inst_model = st.text_input("Model", "MODEL-123")
            with col2:
                inst_serial = st.text_input("Serial Number", "SN-001")
                inst_id = st.text_input("ID Number", "INST-001")
                inst_owner = st.text_input("Owner", "Customer Name")

            st.divider()

            # Calibration data
            st.markdown("**Calibration Data Entry**")

            # Select parameter
            param_map = {
                "RTD Temperature Sensor": "Temperature",
                "Thermocouple": "Temperature",
                "Humidity Sensor": "Relative Humidity",
                "UV Radiometer": "UV Irradiance"
            }
            parameter = param_map.get(inst_type, "Temperature")

            # Number of calibration points
            num_points = st.number_input("Number of Calibration Points", min_value=3, max_value=10, value=5)

            # Generate example calibration data
            if st.button("Generate Example Certificate"):
                # Create lab accreditation
                lab_acc = LabAccreditation(
                    lab_name=lab_name,
                    accreditation_body=AccreditationBody[lab_body],
                    certificate_number=lab_cert,
                    scope="Temperature, Humidity, UV Calibration",
                    address=lab_address,
                    contact=lab_contact,
                    email=lab_email
                )

                # Create calibration system
                cal_system = ISO17025Calibration(lab_acc)

                # Create instrument data
                inst_type_enum = {
                    "RTD Temperature Sensor": InstrumentType.TEMPERATURE_RTD,
                    "Thermocouple": InstrumentType.TEMPERATURE_TC,
                    "Humidity Sensor": InstrumentType.HUMIDITY,
                    "UV Radiometer": InstrumentType.UV_RADIOMETER
                }[inst_type]

                instrument = InstrumentData(
                    id=inst_id,
                    instrument_type=inst_type_enum,
                    make=inst_make,
                    model=inst_model,
                    serial_number=inst_serial,
                    identification_number=inst_id,
                    owner=inst_owner,
                    location="PV Test Chamber"
                )

                # Create example calibration results
                if parameter == "Temperature":
                    cal_points = [
                        CalibrationPoint(-40.0, -40.1, -40.05, -39.95, -40.03, -0.03, 0.15),
                        CalibrationPoint(0.0, 0.05, 0.02, 0.03, 0.03, 0.03, 0.15),
                        CalibrationPoint(25.0, 25.08, 25.06, 25.05, 25.06, 0.06, 0.15),
                        CalibrationPoint(60.0, 60.12, 60.10, 60.08, 60.10, 0.10, 0.15),
                        CalibrationPoint(85.0, 85.15, 85.12, 85.10, 85.12, 0.12, 0.15)
                    ]
                    unit = "°C"
                elif parameter == "Relative Humidity":
                    cal_points = [
                        CalibrationPoint(40.0, 40.5, 40.3, 40.4, 40.4, 0.4, 2.0),
                        CalibrationPoint(60.0, 60.6, 60.4, 60.5, 60.5, 0.5, 2.0),
                        CalibrationPoint(85.0, 85.8, 85.6, 85.7, 85.7, 0.7, 2.0)
                    ]
                    unit = "%RH"
                else:  # UV Irradiance
                    cal_points = [
                        CalibrationPoint(60.0, 61.5, 61.2, 61.3, 61.3, 1.3, 3.0),
                        CalibrationPoint(150.0, 152.0, 151.5, 151.8, 151.8, 1.8, 7.5),
                        CalibrationPoint(250.0, 253.0, 252.5, 252.8, 252.8, 2.8, 12.5)
                    ]
                    unit = "W/m²"

                env_conditions = EnvironmentalConditions(
                    temperature=23.0,
                    temperature_uncertainty=0.5,
                    humidity=50.0,
                    humidity_uncertainty=5.0,
                    pressure=101.3,
                    pressure_uncertainty=0.5
                )

                cal_results = CalibrationResults(
                    calibration_points=cal_points[:num_points],
                    parameter=parameter,
                    unit=unit,
                    procedure_reference="CAL-TEMP-001",
                    environmental_conditions=env_conditions
                )

                # Generate certificate
                certificate = cal_system.generate_calibration_certificate(
                    instrument_data=instrument,
                    reference_standard_id="RTD-REF-001",
                    calibration_results=cal_results,
                    calibrated_by="John Technician",
                    reviewed_by="Jane Supervisor",
                    approved_by="Dr. Lab Director",
                    remarks="Certificate generated for demonstration purposes"
                )

                st.success(f"Certificate Generated: {certificate.certificate_number}")

                # Display certificate details
                st.markdown("### Certificate Preview")
                st.markdown(f"**Certificate Number:** {certificate.certificate_number}")
                st.markdown(f"**Calibration Date:** {certificate.calibration_date}")
                st.markdown(f"**Next Calibration Due:** {certificate.next_calibration_date}")

                # Calibration results table
                st.markdown("### Calibration Results")
                results_data = []
                for pt in cal_results.calibration_points:
                    results_data.append({
                        f"Reference ({unit})": f"{pt.reference_value:.2f}",
                        f"Reading 1 ({unit})": f"{pt.reading_1:.2f}",
                        f"Reading 2 ({unit})": f"{pt.reading_2:.2f}",
                        f"Reading 3 ({unit})": f"{pt.reading_3:.2f}",
                        f"Mean ({unit})": f"{pt.mean_reading:.2f}",
                        f"Error ({unit})": f"{pt.error:.2f}",
                        f"Uncertainty (k=2) ({unit})": f"±{pt.uncertainty:.2f}"
                    })
                st.dataframe(pd.DataFrame(results_data), use_container_width=True)

                # Generate HTML certificate
                cert_html = cal_system.create_certificate_html(certificate)
                st.download_button(
                    label="Download Certificate (HTML)",
                    data=cert_html,
                    file_name=f"{certificate.certificate_number}.html",
                    mime="text/html"
                )

        with subtab3:
            st.subheader("Measurement Uncertainty Budget Calculator")

            st.markdown("""
            Calculate measurement uncertainty per GUM (Guide to the Expression of Uncertainty in Measurement)
            and ISO/IEC 17025:2017 requirements.
            """)

            # Select parameter type
            param_type = st.selectbox(
                "Select Parameter Type",
                ["Temperature Sensor", "Humidity Sensor", "UV Intensity Measurement"]
            )

            measured_value = st.number_input("Measured Value", value=85.0, step=0.1)

            if param_type == "Temperature Sensor":
                st.markdown("**Uncertainty Sources**")
                col1, col2 = st.columns(2)
                with col1:
                    ref_unc = st.number_input("Reference Standard Uncertainty (°C)", value=0.05, step=0.01)
                    resolution = st.number_input("Instrument Resolution (°C)", value=0.1, step=0.01)
                with col2:
                    repeatability = st.number_input("Repeatability Std Dev (°C)", value=0.08, step=0.01)
                    drift = st.number_input("Estimated Drift (°C)", value=0.03, step=0.01)

                num_readings = st.number_input("Number of Readings", value=10, min_value=2)

                if st.button("Calculate Uncertainty Budget"):
                    budget = UncertaintyCalculator.create_temperature_sensor_budget(
                        measured_temp=measured_value,
                        reference_uncertainty=ref_unc,
                        resolution=resolution,
                        repeatability_stdev=repeatability,
                        drift=drift,
                        num_readings=int(num_readings)
                    )

                    st.success("Uncertainty Budget Calculated!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Combined Uncertainty (uc)", f"{budget.combined_standard_uncertainty:.4f} °C")
                    with col2:
                        st.metric("Expanded Uncertainty (U)", f"{budget.expanded_uncertainty:.4f} °C")
                    with col3:
                        st.metric("Coverage Factor", f"k = {budget.coverage_factor}")

                    st.info(f"**Result:** {budget.measured_value} ± {budget.expanded_uncertainty:.2f} °C (k={budget.coverage_factor}, ~95% confidence)")

                    # Uncertainty budget table
                    budget_table = UncertaintyCalculator.generate_budget_table(budget)
                    st.text(budget_table)

            elif param_type == "Humidity Sensor":
                st.markdown("**Uncertainty Sources**")
                col1, col2 = st.columns(2)
                with col1:
                    ref_unc = st.number_input("Reference Standard Uncertainty (%RH)", value=1.0, step=0.1)
                    resolution = st.number_input("Instrument Resolution (%RH)", value=0.1, step=0.01)
                with col2:
                    repeatability = st.number_input("Repeatability Std Dev (%RH)", value=0.5, step=0.1)

                num_readings = st.number_input("Number of Readings", value=10, min_value=2)

                if st.button("Calculate Uncertainty Budget"):
                    budget = UncertaintyCalculator.create_humidity_sensor_budget(
                        measured_rh=measured_value,
                        reference_uncertainty=ref_unc,
                        resolution=resolution,
                        repeatability_stdev=repeatability,
                        num_readings=int(num_readings)
                    )

                    st.success("Uncertainty Budget Calculated!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Combined Uncertainty (uc)", f"{budget.combined_standard_uncertainty:.4f} %RH")
                    with col2:
                        st.metric("Expanded Uncertainty (U)", f"{budget.expanded_uncertainty:.4f} %RH")
                    with col3:
                        st.metric("Coverage Factor", f"k = {budget.coverage_factor}")

                    st.info(f"**Result:** {budget.measured_value} ± {budget.expanded_uncertainty:.2f} %RH (k={budget.coverage_factor})")

                    budget_table = UncertaintyCalculator.generate_budget_table(budget)
                    st.text(budget_table)

            else:  # UV Intensity
                st.markdown("**Uncertainty Sources**")
                col1, col2 = st.columns(2)
                with col1:
                    ref_unc = st.number_input("Reference Standard Uncertainty (W/m²)", value=2.0, step=0.1)
                    resolution = st.number_input("Instrument Resolution (W/m²)", value=1.0, step=0.1)
                with col2:
                    repeatability = st.number_input("Repeatability Std Dev (W/m²)", value=1.5, step=0.1)
                    uniformity = st.number_input("Spatial Uniformity (W/m²)", value=5.0, step=0.5)

                num_readings = st.number_input("Number of Readings", value=10, min_value=2)

                if st.button("Calculate Uncertainty Budget"):
                    budget = UncertaintyCalculator.create_uv_intensity_budget(
                        measured_intensity=measured_value,
                        reference_uncertainty=ref_unc,
                        resolution=resolution,
                        repeatability_stdev=repeatability,
                        uniformity=uniformity,
                        num_readings=int(num_readings)
                    )

                    st.success("Uncertainty Budget Calculated!")

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Combined Uncertainty (uc)", f"{budget.combined_standard_uncertainty:.4f} W/m²")
                    with col2:
                        st.metric("Expanded Uncertainty (U)", f"{budget.expanded_uncertainty:.4f} W/m²")
                    with col3:
                        st.metric("Coverage Factor", f"k = {budget.coverage_factor}")

                    st.info(f"**Result:** {budget.measured_value} ± {budget.expanded_uncertainty:.1f} W/m² (k={budget.coverage_factor})")

                    budget_table = UncertaintyCalculator.generate_budget_table(budget)
                    st.text(budget_table)

        with subtab4:
            st.subheader("IEC Compliance Checklists")

            st.markdown("""
            Generate and track compliance checklists for IEC 61215/61730 test procedures.
            """)

            # Initialize checklist system
            if 'checklist_system' not in st.session_state:
                st.session_state.checklist_system = ComplianceChecklist()

            checklist_sys = st.session_state.checklist_system

            # Select test
            test_options = {
                "MST 11 - UV Preconditioning": "MST_11_UV",
                "MST 12 - Thermal Cycling": "MST_12_Thermal_Cycling",
                "MST 13 - Humidity-Freeze": "MST_13_Humidity_Freeze",
                "MST 14 - Damp Heat": "MST_14_Damp_Heat",
                "Generic Pre-Test Checklist": "PRE_TEST",
                "Generic During-Test Checklist": "DURING_TEST",
                "Generic Post-Test Checklist": "POST_TEST"
            }

            selected_test = st.selectbox("Select Test", list(test_options.keys()))
            test_id = test_options[selected_test]

            if st.button("Generate Checklist"):
                if test_id == "PRE_TEST":
                    checklist = checklist_sys.generate_pre_test_checklist()
                elif test_id == "DURING_TEST":
                    checklist = checklist_sys.generate_during_test_checklist()
                elif test_id == "POST_TEST":
                    checklist = checklist_sys.generate_post_test_checklist()
                else:
                    checklist = checklist_sys.generate_iec_61215_checklist(test_id)

                st.success(f"Checklist generated with {len(checklist)} items")

                # Display checklist
                st.markdown(f"### {selected_test} Checklist")

                # Group by category
                categories = {}
                for item in checklist:
                    cat = item.category.value
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(item)

                for category, items in categories.items():
                    st.markdown(f"**{category.upper().replace('_', ' ')}**")
                    for item in items:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"☐ **{item.id}**: {item.description}")
                            if item.verification_method:
                                st.caption(f"   Verification: {item.verification_method}")
                        with col2:
                            if item.required:
                                st.badge("Required", type="warning")
                    st.divider()

                # Export checklist
                report = checklist_sys.export_checklist_report(test_id)
                st.download_button(
                    label="Download Checklist Report",
                    data=report,
                    file_name=f"checklist_{test_id}.txt",
                    mime="text/plain"
                )

# Footer
st.divider()
st.markdown(f"""
---
**{company_name}** | {company_address} | {company_email}  
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
*White-labeled PV Chamber Configurator v1.0*
""")
