"""
HMI Visualization Components for Streamlit
Reusable widgets for Virtual HMI interface
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List, Optional


def render_gauge(value: float, max_value: float, label: str, units: str = "",
                 thresholds: Dict[str, float] = None, height: int = 200) -> go.Figure:
    """
    Render an animated gauge chart

    Args:
        value: Current value
        max_value: Maximum value for gauge scale
        label: Label for the gauge
        units: Units of measurement
        thresholds: Dict with 'warning' and 'critical' threshold values
        height: Height of gauge in pixels

    Returns:
        Plotly figure object
    """
    if thresholds is None:
        thresholds = {'warning': max_value * 0.8, 'critical': max_value * 0.95}

    # Determine color based on value
    if value >= thresholds.get('critical', max_value):
        color = 'red'
    elif value >= thresholds.get('warning', max_value * 0.8):
        color = 'orange'
    else:
        color = 'green'

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{label}", 'font': {'size': 16}},
        number={'suffix': f" {units}", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, thresholds.get('warning', max_value * 0.8)], 'color': 'lightgray'},
                {'range': [thresholds.get('warning', max_value * 0.8), thresholds.get('critical', max_value)],
                 'color': 'lightyellow'},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': thresholds.get('critical', max_value)
            }
        }
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    return fig


def render_status_indicator(status: str, size: str = "large") -> str:
    """
    Render a color-coded status indicator

    Args:
        status: Status text ('Running', 'Idle', 'Alarm', 'Error', etc.)
        size: 'small', 'medium', or 'large'

    Returns:
        HTML string for status indicator
    """
    # Color mapping
    color_map = {
        'Running': 'green',
        'Idle': 'gray',
        'Paused': 'orange',
        'Alarm': 'red',
        'Error': 'darkred',
        'Homing': 'blue',
        'Moving': 'lightblue',
        'Measuring': 'purple'
    }

    color = color_map.get(status, 'gray')

    # Size mapping
    size_map = {
        'small': '10px',
        'medium': '15px',
        'large': '20px'
    }

    dot_size = size_map.get(size, '15px')

    html = f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <div style="
            width: {dot_size};
            height: {dot_size};
            border-radius: 50%;
            background-color: {color};
            box-shadow: 0 0 10px {color};
            animation: pulse 2s infinite;
        "></div>
        <span style="font-weight: bold; font-size: 18px;">{status}</span>
    </div>
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
    </style>
    """

    return html


def render_trend_chart(data: pd.DataFrame, parameter: str, title: str = None,
                        show_setpoint: bool = True, height: int = 400) -> go.Figure:
    """
    Render a trend chart with historical data

    Args:
        data: DataFrame with 'timestamp' and parameter columns
        parameter: Parameter name to plot
        title: Chart title
        show_setpoint: Whether to show setpoint line
        height: Chart height in pixels

    Returns:
        Plotly figure object
    """
    if title is None:
        title = f"{parameter.replace('_', ' ').title()} Trend"

    fig = go.Figure()

    # Add process value line
    if parameter in data.columns:
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data[parameter],
            mode='lines',
            name='Process Value',
            line=dict(color='blue', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 100, 255, 0.1)'
        ))

    # Add setpoint line if available
    setpoint_col = f'{parameter}_setpoint'
    if show_setpoint and setpoint_col in data.columns:
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data[setpoint_col],
            mode='lines',
            name='Setpoint',
            line=dict(color='red', width=2, dash='dash')
        ))

    fig.update_layout(
        title=title,
        xaxis_title='Time',
        yaxis_title=parameter.replace('_', ' ').title(),
        hovermode='x unified',
        height=height,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def render_alarm_panel(alarms: List[Dict], max_display: int = 10) -> None:
    """
    Render alarm panel with color-coded alarms

    Args:
        alarms: List of alarm dictionaries
        max_display: Maximum number of alarms to display
    """
    if not alarms:
        st.success("✅ No Active Alarms")
        return

    # Color mapping for alarm levels
    level_colors = {
        'CRITICAL': '🔴',
        'WARNING': '🟡',
        'INFO': '🔵'
    }

    st.subheader(f"⚠️ Active Alarms ({len(alarms)})")

    # Display alarms
    for alarm in alarms[:max_display]:
        level_icon = level_colors.get(alarm['level'], '⚪')
        timestamp = alarm.get('timestamp', 'Unknown')

        # Parse timestamp for display
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime('%H:%M:%S')
        except:
            time_str = timestamp

        # Create alarm card
        with st.container():
            col1, col2, col3 = st.columns([1, 6, 2])

            with col1:
                st.markdown(f"### {level_icon}")

            with col2:
                st.markdown(f"**{alarm['message']}**")
                st.caption(f"Time: {time_str} | ID: {alarm['id']}")

            with col3:
                if st.button(f"Acknowledge", key=f"ack_{alarm['id']}"):
                    return alarm['id']  # Return alarm ID to acknowledge

            st.divider()

    if len(alarms) > max_display:
        st.info(f"Showing {max_display} of {len(alarms)} alarms. See alarm history for more.")


def render_measurement_heatmap(grid_data: np.ndarray, parameter: str = "Temperature",
                                 units: str = "°C", grid_size: int = 3) -> go.Figure:
    """
    Render 9-point measurement grid as heatmap

    Args:
        grid_data: 1D array of 9 measurements (3x3 grid)
        parameter: Parameter name
        units: Units of measurement
        grid_size: Grid size (default 3 for 3x3)

    Returns:
        Plotly figure object
    """
    # Reshape to 2D grid
    grid_2d = grid_data.reshape(grid_size, grid_size)

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=grid_2d,
        text=grid_2d,
        texttemplate='%{text:.1f}' + units,
        textfont={"size": 14},
        colorscale='RdYlGn_r',
        colorbar=dict(title=units),
        hoverongaps=False
    ))

    # Calculate uniformity
    mean_val = np.mean(grid_data)
    max_dev = np.max(np.abs(grid_data - mean_val))
    uniformity_pct = (max_dev / mean_val * 100) if mean_val != 0 else 0

    fig.update_layout(
        title=f"{parameter} Distribution (Uniformity: ±{uniformity_pct:.1f}%)",
        xaxis=dict(title="X Position", showgrid=False, zeroline=False),
        yaxis=dict(title="Y Position", showgrid=False, zeroline=False),
        height=400
    )

    return fig


def render_robot_3d_view(position: Dict[str, float], workspace: Dict[str, float],
                          measurement_points: List[Dict] = None) -> go.Figure:
    """
    Render 3D visualization of robot workspace and position

    Args:
        position: Current robot position {'x', 'y', 'z'} in mm
        workspace: Workspace dimensions {'x', 'y', 'z'} in mm
        measurement_points: List of measurement point positions

    Returns:
        Plotly 3D figure
    """
    fig = go.Figure()

    # Draw workspace boundary (as wireframe box)
    x = [0, workspace['x'], workspace['x'], 0, 0,
         0, workspace['x'], workspace['x'], 0, 0,
         0, 0, workspace['x'], workspace['x'], workspace['x'], workspace['x']]
    y = [0, 0, workspace['y'], workspace['y'], 0,
         0, 0, workspace['y'], workspace['y'], 0,
         0, workspace['y'], workspace['y'], 0, 0, workspace['y']]
    z = [0, 0, 0, 0, 0,
         workspace['z'], workspace['z'], workspace['z'], workspace['z'], workspace['z'],
         0, 0, 0, 0, workspace['z'], workspace['z']]

    fig.add_trace(go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines',
        line=dict(color='gray', width=2),
        name='Workspace',
        showlegend=True
    ))

    # Draw current robot position
    fig.add_trace(go.Scatter3d(
        x=[position['x']],
        y=[position['y']],
        z=[position['z']],
        mode='markers',
        marker=dict(size=15, color='red', symbol='diamond'),
        name='Robot Position',
        text=[f"X: {position['x']:.0f}mm<br>Y: {position['y']:.0f}mm<br>Z: {position['z']:.0f}mm"],
        hoverinfo='text'
    ))

    # Draw measurement points if provided
    if measurement_points:
        meas_x = [p['x'] for p in measurement_points]
        meas_y = [p['y'] for p in measurement_points]
        meas_z = [p['z'] for p in measurement_points]

        fig.add_trace(go.Scatter3d(
            x=meas_x, y=meas_y, z=meas_z,
            mode='markers',
            marker=dict(size=8, color='green', symbol='circle'),
            name='Measurement Points',
            showlegend=True
        ))

    # Update layout
    fig.update_layout(
        title="Robot 3D Workspace",
        scene=dict(
            xaxis=dict(title='X (mm)', range=[0, workspace['x']]),
            yaxis=dict(title='Y (mm)', range=[0, workspace['y']]),
            zaxis=dict(title='Z (mm)', range=[0, workspace['z']]),
            aspectmode='data'
        ),
        height=500,
        showlegend=True
    )

    return fig


def render_parameter_card(title: str, current: float, setpoint: float, units: str,
                           deviation_threshold: float = 5.0) -> None:
    """
    Render a parameter display card with current value, setpoint, and deviation

    Args:
        title: Parameter title
        current: Current value
        setpoint: Setpoint value
        units: Units of measurement
        deviation_threshold: Threshold for warning color
    """
    deviation = current - setpoint

    # Determine status color
    if abs(deviation) > deviation_threshold:
        delta_color = "off"
        status = "⚠️"
    elif abs(deviation) > deviation_threshold / 2:
        delta_color = "normal"
        status = "⚡"
    else:
        delta_color = "normal"
        status = "✅"

    # Display metric
    st.metric(
        label=f"{status} {title}",
        value=f"{current:.1f} {units}",
        delta=f"{deviation:+.1f} {units} from SP",
        delta_color=delta_color
    )

    # Show setpoint
    st.caption(f"Setpoint: {setpoint:.1f} {units}")


def render_progress_bar(current: float, total: float, label: str = "Progress") -> None:
    """
    Render a progress bar with percentage

    Args:
        current: Current value
        total: Total value
        label: Label for progress bar
    """
    if total == 0:
        progress = 0
    else:
        progress = min(current / total, 1.0)

    st.progress(progress)
    st.caption(f"{label}: {progress*100:.1f}% ({current:.0f}/{total:.0f})")


def render_data_export_panel(hmi_controller) -> None:
    """
    Render data export control panel

    Args:
        hmi_controller: VirtualHMI instance
    """
    st.subheader("📊 Data Export")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

    with col2:
        export_format = st.selectbox("Export Format", ["CSV", "Excel", "JSON"])

        if st.button("Export Data", type="primary"):
            from datetime import datetime
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())

            try:
                filepath = hmi_controller.export_logs(
                    start_dt, end_dt,
                    format=export_format.lower()
                )
                st.success(f"✅ Data exported to: {filepath}")

                # Offer download
                with open(filepath, 'rb') as f:
                    st.download_button(
                        label="Download File",
                        data=f,
                        file_name=filepath.split('/')[-1],
                        mime='application/octet-stream'
                    )
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")


def render_recipe_selector(recipes: Dict[str, Dict]) -> Optional[str]:
    """
    Render recipe selection dropdown

    Args:
        recipes: Dictionary of available recipes

    Returns:
        Selected recipe name or None
    """
    if not recipes:
        st.warning("No recipes available")
        return None

    recipe_names = list(recipes.keys())
    selected = st.selectbox("Select Recipe", ["None"] + recipe_names)

    if selected != "None":
        recipe = recipes[selected]

        # Show recipe details
        with st.expander("Recipe Details"):
            st.json(recipe)

        return selected

    return None


def render_system_overview(status: Dict) -> None:
    """
    Render system overview panel

    Args:
        status: System status dictionary from HMI controller
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("System Status", status.get('status', 'Unknown'))

    with col2:
        st.metric("Mode", status.get('mode', 'Manual'))

    with col3:
        uptime_hours = status.get('uptime', 0) / 3600
        st.metric("Uptime", f"{uptime_hours:.1f} hrs")

    with col4:
        power = status.get('power_consumption', 0)
        st.metric("Power", f"{power:.1f} kW")


if __name__ == "__main__":
    # Test components
    print("HMI Components Test")
    print("Run with Streamlit to see visualizations")
