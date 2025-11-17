import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

from modules.virtual_hmi import VirtualHMI
from modules.robot_controller import UniformityRobot
from modules.visualizations import hmi_components

# Page configuration
st.set_page_config(
    page_title="PV Chamber Configurator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'hmi' not in st.session_state:
    st.session_state.hmi = VirtualHMI()

if 'robot' not in st.session_state:
    st.session_state.robot = UniformityRobot()

if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False

if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Load recipes
try:
    with open('data/sample_recipes.json', 'r') as f:
        recipes = json.load(f)
except:
    recipes = {}

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

    # Get current status
    hmi_status = st.session_state.hmi.get_current_status()

    st.metric("Chamber Status", hmi_status['status'])
    st.metric("Uptime", f"{hmi_status['uptime']/3600:.1f} hrs")
    st.metric("Active Alarms", hmi_status['active_alarms'])
    st.metric("Power", f"{hmi_status['power_consumption']:.1f} kW")

    st.divider()

    # Auto-refresh control
    auto_refresh = st.checkbox("Auto-refresh (1s)", value=False)
    if auto_refresh:
        st.session_state.hmi.update_simulation(dt=1.0)
        st.rerun()

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📐 Chamber Design",
    "💡 UV System",
    "💰 Quote Generator",
    "📈 Business Analysis",
    "🖥️ Virtual HMI",
    "🤖 Robot Control",
    "📊 Data Logs",
    "📋 Test Recipes",
    "⚙️ Settings"
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
    st.header("🖥️ Virtual HMI - Real-time Monitoring & Control")

    # System overview
    hmi_components.render_system_overview(hmi_status)

    st.divider()

    # Sub-tabs for HMI sections
    hmi_tab1, hmi_tab2, hmi_tab3 = st.tabs([
        "📊 Dashboard",
        "🎛️ Control Panel",
        "⚠️ Alarms"
    ])

    with hmi_tab1:
        st.subheader("Real-time Parameters")

        # Temperature, Humidity, UV metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            hmi_components.render_parameter_card(
                "Temperature",
                hmi_status['temperature']['current'],
                hmi_status['temperature']['setpoint'],
                "°C",
                deviation_threshold=3.0
            )

            # Temperature gauge
            temp_gauge = hmi_components.render_gauge(
                hmi_status['temperature']['current'],
                105,
                "Temperature",
                "°C",
                thresholds={'warning': 100, 'critical': 105}
            )
            st.plotly_chart(temp_gauge, use_container_width=True)

        with col2:
            hmi_components.render_parameter_card(
                "Humidity",
                hmi_status['humidity']['current'],
                hmi_status['humidity']['setpoint'],
                "%RH",
                deviation_threshold=5.0
            )

            # Humidity gauge
            humidity_gauge = hmi_components.render_gauge(
                hmi_status['humidity']['current'],
                100,
                "Humidity",
                "%RH",
                thresholds={'warning': 95, 'critical': 98}
            )
            st.plotly_chart(humidity_gauge, use_container_width=True)

        with col3:
            hmi_components.render_parameter_card(
                "UV Intensity",
                hmi_status['uv_intensity']['current'],
                hmi_status['uv_intensity']['setpoint'],
                "W/m²",
                deviation_threshold=10.0
            )

            # UV gauge
            uv_gauge = hmi_components.render_gauge(
                hmi_status['uv_intensity']['current'],
                250,
                "UV Intensity",
                "W/m²",
                thresholds={'warning': 240, 'critical': 250}
            )
            st.plotly_chart(uv_gauge, use_container_width=True)

        st.divider()

        # Trend charts
        st.subheader("📈 Historical Trends (Last 24 Hours)")

        trend_col1, trend_col2 = st.columns(2)

        with trend_col1:
            # Temperature trend
            temp_data = st.session_state.hmi.generate_trend_chart('temperature', hours=24)
            temp_chart = hmi_components.render_trend_chart(temp_data, 'temperature', 'Temperature Trend')
            st.plotly_chart(temp_chart, use_container_width=True)

            # UV trend
            uv_data = st.session_state.hmi.generate_trend_chart('uv_intensity', hours=24)
            uv_chart = hmi_components.render_trend_chart(uv_data, 'uv_intensity', 'UV Intensity Trend')
            st.plotly_chart(uv_chart, use_container_width=True)

        with trend_col2:
            # Humidity trend
            humidity_data = st.session_state.hmi.generate_trend_chart('humidity', hours=24)
            humidity_chart = hmi_components.render_trend_chart(humidity_data, 'humidity', 'Humidity Trend')
            st.plotly_chart(humidity_chart, use_container_width=True)

            # Power consumption trend
            power_data = st.session_state.hmi.generate_trend_chart('power_consumption', hours=24)
            power_chart = hmi_components.render_trend_chart(power_data, 'power_consumption', 'Power Consumption', show_setpoint=False)
            st.plotly_chart(power_chart, use_container_width=True)

        # 9-point grid heatmaps
        st.divider()
        st.subheader("🔥 Uniformity Heatmaps (9-Point Grid)")

        grid_col1, grid_col2, grid_col3 = st.columns(3)

        live_data = st.session_state.hmi.get_live_data()

        with grid_col1:
            temp_heatmap = hmi_components.render_measurement_heatmap(
                np.array(live_data['temperature_grid']),
                "Temperature",
                "°C"
            )
            st.plotly_chart(temp_heatmap, use_container_width=True)

        with grid_col2:
            humidity_heatmap = hmi_components.render_measurement_heatmap(
                np.array(live_data['humidity_grid']),
                "Humidity",
                "%RH"
            )
            st.plotly_chart(humidity_heatmap, use_container_width=True)

        with grid_col3:
            uv_heatmap = hmi_components.render_measurement_heatmap(
                np.array(live_data['uv_grid']),
                "UV Intensity",
                "W/m²"
            )
            st.plotly_chart(uv_heatmap, use_container_width=True)

    with hmi_tab2:
        st.subheader("🎛️ Chamber Control Panel")

        # Status indicator
        st.markdown(hmi_components.render_status_indicator(hmi_status['status'], 'large'), unsafe_allow_html=True)

        st.divider()

        # Setpoint controls
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Setpoint Adjustments")

            # Temperature setpoint
            new_temp = st.slider(
                "Temperature Setpoint (°C)",
                -45.0, 105.0,
                st.session_state.hmi.setpoints['temperature'],
                step=0.5
            )
            if st.button("Set Temperature"):
                success, msg = st.session_state.hmi.set_temperature_setpoint(new_temp)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

            # Humidity setpoint
            new_humidity = st.slider(
                "Humidity Setpoint (%RH)",
                40.0, 95.0,
                st.session_state.hmi.setpoints['humidity'],
                step=1.0
            )
            if st.button("Set Humidity"):
                success, msg = st.session_state.hmi.set_humidity_setpoint(new_humidity)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

            # UV intensity setpoint
            new_uv = st.slider(
                "UV Intensity (W/m²)",
                0.0, 250.0,
                st.session_state.hmi.setpoints['uv_intensity'],
                step=5.0
            )
            if st.button("Set UV Intensity"):
                success, msg = st.session_state.hmi.set_uv_intensity(new_uv)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

            # Ramp rate
            new_ramp = st.slider(
                "Ramp Rate (°C/min)",
                0.5, 5.0,
                st.session_state.hmi.setpoints['ramp_rate'],
                step=0.1
            )
            if st.button("Set Ramp Rate"):
                success, msg = st.session_state.hmi.set_ramp_rate(new_ramp)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

        with col2:
            st.subheader("Chamber Operations")

            # Mode selection
            mode = st.selectbox("Operation Mode", ["Manual", "Auto", "Recipe"])
            st.session_state.hmi.chamber_state['mode'] = mode

            st.divider()

            # Start/Stop/Pause buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)

            with btn_col1:
                if st.button("▶️ START", type="primary", use_container_width=True):
                    success, msg = st.session_state.hmi.start_chamber()
                    if success:
                        st.success(msg)
                    else:
                        st.warning(msg)

            with btn_col2:
                if st.button("⏸️ PAUSE", use_container_width=True):
                    success, msg = st.session_state.hmi.pause_chamber()
                    if success:
                        st.info(msg)
                    else:
                        st.warning(msg)

            with btn_col3:
                if st.button("⏹️ STOP", use_container_width=True):
                    success, msg = st.session_state.hmi.stop_chamber()
                    if success:
                        st.info(msg)
                    else:
                        st.warning(msg)

            st.divider()

            # Emergency stop
            st.error("**EMERGENCY CONTROLS**")
            if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
                success, msg = st.session_state.hmi.emergency_stop()
                st.error(msg)

            st.caption("Emergency stop will halt all chamber operations immediately")

    with hmi_tab3:
        st.subheader("⚠️ Alarm Management")

        # Active alarms
        active_alarms = st.session_state.hmi.active_alarms

        if active_alarms:
            alarm_id = hmi_components.render_alarm_panel(active_alarms)

            if alarm_id:
                if st.session_state.hmi.acknowledge_alarm(alarm_id):
                    st.success(f"Alarm {alarm_id} acknowledged")
                    st.rerun()
        else:
            st.success("✅ No Active Alarms")

        st.divider()

        # Alarm history
        st.subheader("📜 Alarm History")

        alarm_history = st.session_state.hmi.get_alarm_history(limit=50)

        if alarm_history:
            # Convert to DataFrame
            alarm_df = pd.DataFrame(alarm_history)
            alarm_df = alarm_df[['timestamp', 'level', 'message', 'acknowledged']]
            alarm_df['acknowledged'] = alarm_df['acknowledged'].map({True: '✓', False: '✗'})

            st.dataframe(alarm_df, use_container_width=True, height=400)
        else:
            st.info("No alarm history available")

with tab6:
    st.header("🤖 Uniformity Robot Control")

    # Robot status
    robot_status = st.session_state.robot.get_robot_status()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Robot Status", robot_status['status'])
    with col2:
        st.metric("Homed", "Yes" if robot_status['is_homed'] else "No")
    with col3:
        st.metric("Total Measurements", robot_status['total_measurements'])
    with col4:
        st.metric("Emergency Stop", "ACTIVE" if robot_status['emergency_stop'] else "Clear")

    st.divider()

    # Sub-tabs for robot sections
    robot_tab1, robot_tab2, robot_tab3 = st.tabs([
        "🎮 Manual Control",
        "📐 Auto Measurement",
        "📊 Results"
    ])

    with robot_tab1:
        st.subheader("Manual Jog Controls")

        col1, col2 = st.columns([2, 1])

        with col1:
            # 3D visualization
            measurement_points = st.session_state.robot.generate_grid_path()
            robot_3d = hmi_components.render_robot_3d_view(
                robot_status['position'],
                robot_status['workspace'],
                measurement_points
            )
            st.plotly_chart(robot_3d, use_container_width=True)

        with col2:
            st.markdown("**Current Position**")
            st.text(f"X: {robot_status['position']['x']:.1f} mm")
            st.text(f"Y: {robot_status['position']['y']:.1f} mm")
            st.text(f"Z: {robot_status['position']['z']:.1f} mm")

            st.divider()

            # Home button
            if st.button("🏠 Home All Axes", use_container_width=True):
                if st.session_state.robot.home_axes():
                    st.success("Robot homed successfully")
                else:
                    st.error("Homing failed")

            st.divider()

            # Jog distance
            jog_distance = st.number_input("Jog Distance (mm)", value=100.0, min_value=1.0, max_value=500.0)

            # X axis jog
            st.markdown("**X Axis**")
            jog_x_col1, jog_x_col2 = st.columns(2)
            with jog_x_col1:
                if st.button("⬅️ X-", use_container_width=True):
                    st.session_state.robot.jog('x', -jog_distance)
            with jog_x_col2:
                if st.button("➡️ X+", use_container_width=True):
                    st.session_state.robot.jog('x', jog_distance)

            # Y axis jog
            st.markdown("**Y Axis**")
            jog_y_col1, jog_y_col2 = st.columns(2)
            with jog_y_col1:
                if st.button("⬇️ Y-", use_container_width=True):
                    st.session_state.robot.jog('y', -jog_distance)
            with jog_y_col2:
                if st.button("⬆️ Y+", use_container_width=True):
                    st.session_state.robot.jog('y', jog_distance)

            # Z axis jog
            st.markdown("**Z Axis**")
            jog_z_col1, jog_z_col2 = st.columns(2)
            with jog_z_col1:
                if st.button("🔽 Z-", use_container_width=True):
                    st.session_state.robot.jog('z', -jog_distance)
            with jog_z_col2:
                if st.button("🔼 Z+", use_container_width=True):
                    st.session_state.robot.jog('z', jog_distance)

            st.divider()

            # Emergency stop
            if st.button("🛑 Robot E-Stop", type="primary", use_container_width=True):
                st.session_state.robot.emergency_stop()
                st.error("Robot emergency stop activated!")

    with robot_tab2:
        st.subheader("Automated 9-Point Measurement")

        col1, col2 = st.columns([1, 1])

        with col1:
            # Measurement configuration
            z_height = st.number_input("Measurement Height (Z mm)", value=750.0, min_value=0.0, max_value=1500.0)

            # Generate path
            waypoints = st.session_state.robot.generate_grid_path(grid_size=3, z_height=z_height)

            # Estimate time
            estimated_time = st.session_state.robot.estimate_completion_time(waypoints)
            st.info(f"⏱️ Estimated completion time: {estimated_time:.1f} seconds ({estimated_time/60:.1f} minutes)")

            # Start measurement
            if st.button("▶️ Start 9-Point Measurement", type="primary", use_container_width=True):
                if not st.session_state.robot.is_homed:
                    st.error("Please home the robot first!")
                else:
                    with st.spinner("Executing measurement sequence..."):
                        result = st.session_state.robot.measure_9_point_grid(z_height=z_height)

                        if 'error' in result:
                            st.error(result['error'])
                        else:
                            st.success(f"✅ Measurement complete in {result['duration']:.1f}s")
                            st.session_state.last_measurement = result
                            st.rerun()

        with col2:
            # Display measurement grid
            st.markdown("**Measurement Grid Pattern**")

            # Create grid visualization
            grid_fig = go.Figure()

            for i, wp in enumerate(waypoints):
                grid_fig.add_trace(go.Scatter(
                    x=[wp['x']],
                    y=[wp['y']],
                    mode='markers+text',
                    marker=dict(size=15, color='blue'),
                    text=[str(i+1)],
                    textposition='top center',
                    name=f'Point {i+1}'
                ))

            # Add path lines
            x_coords = [wp['x'] for wp in waypoints]
            y_coords = [wp['y'] for wp in waypoints]
            grid_fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines',
                line=dict(color='gray', dash='dash'),
                name='Path',
                showlegend=False
            ))

            grid_fig.update_layout(
                title="9-Point Grid Path",
                xaxis_title="X (mm)",
                yaxis_title="Y (mm)",
                showlegend=False,
                height=400
            )

            st.plotly_chart(grid_fig, use_container_width=True)

        # G-code upload
        st.divider()
        st.subheader("📄 G-Code Custom Path")

        gcode_file = st.file_uploader("Upload G-Code File", type=['gcode', 'nc', 'txt'])

        if gcode_file:
            # Save uploaded file
            gcode_path = f"logs/{gcode_file.name}"
            with open(gcode_path, 'wb') as f:
                f.write(gcode_file.getbuffer())

            # Parse G-code
            commands = st.session_state.robot.parse_gcode(gcode_path)

            st.info(f"Parsed {len(commands)} G-code commands")

            with st.expander("View Commands"):
                st.json(commands)

            if st.button("Execute G-Code", type="primary"):
                with st.spinner("Executing G-code..."):
                    if st.session_state.robot.execute_gcode(commands):
                        st.success("G-code executed successfully")
                    else:
                        st.error("G-code execution failed")

    with robot_tab3:
        st.subheader("📊 Measurement Results")

        if hasattr(st.session_state, 'last_measurement') and st.session_state.last_measurement:
            result = st.session_state.last_measurement

            # Summary metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Measurement Duration", f"{result['duration']:.1f} s")
                st.metric("Grid Size", f"{result['grid_size']}x{result['grid_size']}")

            with col2:
                temp_uniformity = result['uniformity']['temperature']['uniformity_percent']
                st.metric("Temp Uniformity", f"±{temp_uniformity:.2f}%")
                st.metric("Avg Temperature", f"{result['uniformity']['temperature']['mean']:.1f}°C")

            with col3:
                uv_uniformity = result['uniformity']['uv_intensity']['uniformity_percent']
                st.metric("UV Uniformity", f"±{uv_uniformity:.2f}%")
                st.metric("Avg UV Intensity", f"{result['uniformity']['uv_intensity']['mean']:.1f} W/m²")

            st.divider()

            # Heatmaps
            st.subheader("Measurement Heatmaps")

            heat_col1, heat_col2, heat_col3 = st.columns(3)

            # Extract grid data
            measurements = result['measurements']
            temp_grid = np.array([m['temperature'] for m in measurements])
            humidity_grid = np.array([m['humidity'] for m in measurements])
            uv_grid = np.array([m['uv_intensity'] for m in measurements])

            with heat_col1:
                temp_heat = hmi_components.render_measurement_heatmap(temp_grid, "Temperature", "°C")
                st.plotly_chart(temp_heat, use_container_width=True)

            with heat_col2:
                humidity_heat = hmi_components.render_measurement_heatmap(humidity_grid, "Humidity", "%RH")
                st.plotly_chart(humidity_heat, use_container_width=True)

            with heat_col3:
                uv_heat = hmi_components.render_measurement_heatmap(uv_grid, "UV Intensity", "W/m²")
                st.plotly_chart(uv_heat, use_container_width=True)

            st.divider()

            # Detailed results table
            st.subheader("Detailed Measurements")

            meas_df = pd.DataFrame(measurements)
            meas_df = meas_df[['x', 'y', 'z', 'temperature', 'humidity', 'uv_intensity']]
            meas_df = meas_df.round(2)

            st.dataframe(meas_df, use_container_width=True)

            # Export results
            if st.button("💾 Export Results to CSV"):
                csv_file = f"logs/robot_measurement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                meas_df.to_csv(csv_file, index=False)
                st.success(f"Results exported to {csv_file}")

        else:
            st.info("No measurement results available. Run a 9-point measurement first.")

with tab7:
    st.header("📊 Data Logs & Export")

    # Statistics
    st.subheader("📈 Log Statistics (Last 7 Days)")

    stats = st.session_state.hmi.get_log_statistics(days=7)

    if stats:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Records", stats.get('total_records', 0))
        with col2:
            st.metric("Avg Temperature", f"{stats.get('avg_temperature', 0):.1f}°C")
        with col3:
            st.metric("Avg Humidity", f"{stats.get('avg_humidity', 0):.1f}%RH")
        with col4:
            st.metric("Avg Power", f"{stats.get('avg_power_consumption', 0):.1f} kW")

    st.divider()

    # Export panel
    hmi_components.render_data_export_panel(st.session_state.hmi)

with tab8:
    st.header("📋 Test Recipe Management")

    # Recipe tabs
    recipe_tab1, recipe_tab2 = st.tabs(["📖 Recipe Library", "➕ Create Recipe"])

    with recipe_tab1:
        st.subheader("Available Test Recipes")

        # Recipe selector
        selected_recipe = hmi_components.render_recipe_selector(recipes)

        if selected_recipe:
            recipe = recipes[selected_recipe]

            st.divider()

            # Recipe details
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**Description:** {recipe['description']}")
                st.markdown(f"**Standard:** {recipe['standard']}")
                st.markdown(f"**Test Code:** {recipe['test_code']}")
                st.markdown(f"**Duration:** {recipe['duration_hours']} hours ({recipe['duration_hours']/24:.1f} days)")
                st.markdown(f"**Cycles:** {recipe['cycles']}")

            with col2:
                # Execute recipe
                if st.button("▶️ Execute Recipe", type="primary", use_container_width=True):
                    st.session_state.hmi.active_recipe = recipe
                    st.session_state.hmi.recipe_start_time = datetime.now()
                    st.success(f"Recipe '{selected_recipe}' started!")

            st.divider()

            # Recipe steps
            st.subheader("Test Steps")

            steps_df = pd.DataFrame(recipe['steps'])
            st.dataframe(steps_df, use_container_width=True)

    with recipe_tab2:
        st.subheader("Create Custom Recipe")

        recipe_name = st.text_input("Recipe Name")
        recipe_desc = st.text_area("Description")

        st.markdown("**Recipe Steps**")
        st.info("Custom recipe creation coming soon...")

with tab9:
    st.header("⚙️ System Settings")

    settings_tab1, settings_tab2 = st.tabs(["🔧 General", "⚠️ Alarm Configuration"])

    with settings_tab1:
        st.subheader("Data Logging Settings")

        logging_interval = st.number_input(
            "Logging Interval (seconds)",
            min_value=10,
            max_value=3600,
            value=st.session_state.hmi.logging_interval
        )

        if st.button("Update Logging Interval"):
            st.session_state.hmi.logging_interval = logging_interval
            st.success(f"Logging interval updated to {logging_interval} seconds")

        st.divider()

        st.subheader("Robot Settings")

        max_speed = st.slider("Max Robot Speed (mm/s)", 100, 500, st.session_state.robot.max_speed)

        if st.button("Update Robot Speed"):
            st.session_state.robot.max_speed = max_speed
            st.success(f"Robot max speed updated to {max_speed} mm/s")

    with settings_tab2:
        st.subheader("Alarm Rules")

        st.info("View and edit alarm configuration")

        try:
            with open('data/alarm_rules.json', 'r') as f:
                alarm_config = json.load(f)

            st.json(alarm_config)
        except:
            st.warning("Alarm configuration file not found")

# Footer
st.divider()
st.markdown(f"""
---
**{company_name}** | {company_address} | {company_email}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*White-labeled PV Chamber Configurator v2.0 - Phase 5: Virtual HMI + Robot Integration*
""")
