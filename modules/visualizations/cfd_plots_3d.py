"""
3D Visualization Functions for CFD Simulation Results
Provides interactive Plotly visualizations for temperature, velocity, humidity fields
and 3D chamber model rendering.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional


def plot_temperature_3d(temp_field: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                       title: str = "3D Temperature Distribution") -> go.Figure:
    """
    Create 3D scatter plot of temperature field.

    Args:
        temp_field: 3D temperature array (nx, ny, nz)
        x, y, z: Coordinate arrays
        title: Plot title

    Returns:
        Plotly Figure object
    """
    # Subsample for visualization (every 5th point)
    step = 5
    X, Y, Z = np.meshgrid(x[::step], y[::step], z[::step], indexing='ij')
    temp_sub = temp_field[::step, ::step, ::step]

    # Flatten arrays
    x_flat = X.flatten()
    y_flat = Y.flatten()
    z_flat = Z.flatten()
    temp_flat = temp_sub.flatten()

    fig = go.Figure(data=[go.Scatter3d(
        x=x_flat * 1000,  # Convert to mm
        y=y_flat * 1000,
        z=z_flat * 1000,
        mode='markers',
        marker=dict(
            size=3,
            color=temp_flat,
            colorscale='RdBu_r',
            showscale=True,
            colorbar=dict(title="Temperature (°C)", x=1.1),
            cmin=np.min(temp_field),
            cmax=np.max(temp_field)
        ),
        text=[f"T: {t:.1f}°C" for t in temp_flat],
        hovertemplate="X: %{x:.0f}mm<br>Y: %{y:.0f}mm<br>Z: %{z:.0f}mm<br>%{text}<extra></extra>"
    )])

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Length (mm)",
            yaxis_title="Width (mm)",
            zaxis_title="Height (mm)",
            aspectmode='data'
        ),
        width=900,
        height=700
    )

    return fig


def plot_velocity_vectors_3d(velocity_field: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                             title: str = "3D Velocity Vector Field") -> go.Figure:
    """
    Create 3D quiver plot of velocity vectors.

    Args:
        velocity_field: 4D velocity array (nx, ny, nz, 3) with [vx, vy, vz]
        x, y, z: Coordinate arrays
        title: Plot title

    Returns:
        Plotly Figure object
    """
    # Subsample for visualization (every 8th point for clarity)
    step = 8
    X, Y, Z = np.meshgrid(x[::step], y[::step], z[::step], indexing='ij')

    vx = velocity_field[::step, ::step, ::step, 0]
    vy = velocity_field[::step, ::step, ::step, 1]
    vz = velocity_field[::step, ::step, ::step, 2]

    # Flatten arrays
    x_flat = X.flatten() * 1000  # mm
    y_flat = Y.flatten() * 1000
    z_flat = Z.flatten() * 1000
    vx_flat = vx.flatten()
    vy_flat = vy.flatten()
    vz_flat = vz.flatten()

    # Calculate velocity magnitude
    vel_mag = np.sqrt(vx_flat**2 + vy_flat**2 + vz_flat**2)

    # Create cone plot for velocity vectors
    fig = go.Figure(data=go.Cone(
        x=x_flat,
        y=y_flat,
        z=z_flat,
        u=vx_flat,
        v=vy_flat,
        w=vz_flat,
        colorscale='Viridis',
        sizemode="absolute",
        sizeref=0.5,
        showscale=True,
        colorbar=dict(title="Velocity (m/s)", x=1.1),
        hovertemplate="Velocity: %{marker.color:.2f} m/s<extra></extra>"
    ))

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Length (mm)",
            yaxis_title="Width (mm)",
            zaxis_title="Height (mm)",
            aspectmode='data'
        ),
        width=900,
        height=700
    )

    return fig


def plot_humidity_3d(humidity_field: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                    title: str = "3D Humidity Distribution") -> go.Figure:
    """
    Create 3D scatter plot of humidity field.

    Args:
        humidity_field: 3D humidity array (nx, ny, nz)
        x, y, z: Coordinate arrays
        title: Plot title

    Returns:
        Plotly Figure object
    """
    # Subsample for visualization
    step = 5
    X, Y, Z = np.meshgrid(x[::step], y[::step], z[::step], indexing='ij')
    humidity_sub = humidity_field[::step, ::step, ::step]

    # Flatten arrays
    x_flat = X.flatten() * 1000
    y_flat = Y.flatten() * 1000
    z_flat = Z.flatten() * 1000
    humidity_flat = humidity_sub.flatten()

    fig = go.Figure(data=[go.Scatter3d(
        x=x_flat,
        y=y_flat,
        z=z_flat,
        mode='markers',
        marker=dict(
            size=3,
            color=humidity_flat,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Humidity (%RH)", x=1.1),
            cmin=np.min(humidity_field),
            cmax=np.max(humidity_field)
        ),
        text=[f"RH: {h:.1f}%" for h in humidity_flat],
        hovertemplate="X: %{x:.0f}mm<br>Y: %{y:.0f}mm<br>Z: %{z:.0f}mm<br>%{text}<extra></extra>"
    )])

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Length (mm)",
            yaxis_title="Width (mm)",
            zaxis_title="Height (mm)",
            aspectmode='data'
        ),
        width=900,
        height=700
    )

    return fig


def plot_cross_section_heatmap(field_data: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                               plane: str = 'XY', position: float = 0.5,
                               title: str = "Cross-Section Heatmap",
                               colorbar_title: str = "Value") -> go.Figure:
    """
    Create 2D heatmap of field cross-section.

    Args:
        field_data: 3D field array
        x, y, z: Coordinate arrays
        plane: 'XY', 'XZ', or 'YZ'
        position: Normalized position along the perpendicular axis (0-1)
        title: Plot title
        colorbar_title: Colorbar label

    Returns:
        Plotly Figure object
    """
    if plane == 'XY':
        # Horizontal slice at height z
        z_idx = int(position * (len(z) - 1))
        data_slice = field_data[:, :, z_idx]
        x_coords = x * 1000
        y_coords = y * 1000
        x_label = "Length (mm)"
        y_label = "Width (mm)"
        slice_info = f"at Z = {z[z_idx]*1000:.0f} mm"

    elif plane == 'XZ':
        # Vertical slice along length at width y
        y_idx = int(position * (len(y) - 1))
        data_slice = field_data[:, y_idx, :].T
        x_coords = x * 1000
        y_coords = z * 1000
        x_label = "Length (mm)"
        y_label = "Height (mm)"
        slice_info = f"at Y = {y[y_idx]*1000:.0f} mm"

    elif plane == 'YZ':
        # Vertical slice along width at length x
        x_idx = int(position * (len(x) - 1))
        data_slice = field_data[x_idx, :, :].T
        x_coords = y * 1000
        y_coords = z * 1000
        x_label = "Width (mm)"
        y_label = "Height (mm)"
        slice_info = f"at X = {x[x_idx]*1000:.0f} mm"

    else:
        raise ValueError(f"Invalid plane: {plane}. Must be 'XY', 'XZ', or 'YZ'")

    fig = go.Figure(data=go.Heatmap(
        x=x_coords,
        y=y_coords,
        z=data_slice,
        colorscale='RdBu_r',
        colorbar=dict(title=colorbar_title),
        hovertemplate="%{x:.0f}, %{y:.0f}<br>Value: %{z:.2f}<extra></extra>"
    ))

    fig.update_layout(
        title=f"{title} - {plane} Plane {slice_info}",
        xaxis_title=x_label,
        yaxis_title=y_label,
        width=800,
        height=600
    )

    return fig


def plot_chamber_3d_model(chamber_geometry: Dict, components: Optional[Dict] = None,
                         show_components: bool = True) -> go.Figure:
    """
    Create 3D chamber model with component placement.

    Args:
        chamber_geometry: Dictionary with vertices, edges, faces
        components: Dictionary with component positions
        show_components: Whether to show components

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Extract geometry
    vertices = np.array(chamber_geometry['vertices']) * 1000  # Convert to mm
    edges = chamber_geometry['edges']

    # Draw chamber edges (wireframe)
    for edge in edges:
        v1, v2 = vertices[edge[0]], vertices[edge[1]]
        fig.add_trace(go.Scatter3d(
            x=[v1[0], v2[0]],
            y=[v1[1], v2[1]],
            z=[v1[2], v2[2]],
            mode='lines',
            line=dict(color='black', width=4),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Draw chamber faces (semi-transparent)
    faces = chamber_geometry['faces']
    for i, face in enumerate(faces):
        face_vertices = vertices[face]

        # Create mesh for face
        if i < 2:  # Bottom and top - full opacity
            opacity = 0.1
            color = 'lightgray'
        else:  # Sides - more transparent
            opacity = 0.05
            color = 'lightblue'

        # Triangulate quad face
        triangles = [[face[0], face[1], face[2]], [face[0], face[2], face[3]]]

        for tri in triangles:
            tri_vertices = vertices[tri]
            fig.add_trace(go.Mesh3d(
                x=tri_vertices[:, 0],
                y=tri_vertices[:, 1],
                z=tri_vertices[:, 2],
                color=color,
                opacity=opacity,
                showlegend=False,
                hoverinfo='skip'
            ))

    # Add components if provided
    if show_components and components:
        # Add fans
        if 'fans' in components:
            fan_positions = np.array(components['fans']) * 1000
            fig.add_trace(go.Scatter3d(
                x=fan_positions[:, 0],
                y=fan_positions[:, 1],
                z=fan_positions[:, 2],
                mode='markers',
                marker=dict(size=12, color='blue', symbol='diamond'),
                name='Fans',
                text=[f"Fan {i+1}" for i in range(len(fan_positions))],
                hovertemplate="%{text}<br>X: %{x:.0f}mm<br>Y: %{y:.0f}mm<br>Z: %{z:.0f}mm<extra></extra>"
            ))

        # Add humidifiers
        if 'humidifiers' in components:
            hum_positions = np.array(components['humidifiers']) * 1000
            fig.add_trace(go.Scatter3d(
                x=hum_positions[:, 0],
                y=hum_positions[:, 1],
                z=hum_positions[:, 2],
                mode='markers',
                marker=dict(size=12, color='cyan', symbol='square'),
                name='Humidifiers',
                text=[f"Humidifier {i+1}" for i in range(len(hum_positions))],
                hovertemplate="%{text}<br>X: %{x:.0f}mm<br>Y: %{y:.0f}mm<br>Z: %{z:.0f}mm<extra></extra>"
            ))

        # Add UV panels
        if 'uv_panels' in components:
            uv_positions = np.array(components['uv_panels']) * 1000
            fig.add_trace(go.Scatter3d(
                x=uv_positions[:, 0],
                y=uv_positions[:, 1],
                z=uv_positions[:, 2],
                mode='markers',
                marker=dict(size=15, color='purple', symbol='square'),
                name='UV Panels',
                text=[f"UV Panel {i+1}" for i in range(len(uv_positions))],
                hovertemplate="%{text}<br>X: %{x:.0f}mm<br>Y: %{y:.0f}mm<br>Z: %{z:.0f}mm<extra></extra>"
            ))

        # Add test specimen
        if 'test_specimen' in components:
            spec_pos = np.array(components['test_specimen']) * 1000
            fig.add_trace(go.Scatter3d(
                x=[spec_pos[0]],
                y=[spec_pos[1]],
                z=[spec_pos[2]],
                mode='markers',
                marker=dict(size=20, color='red', symbol='square'),
                name='Test Specimen',
                text=["PV Module Test Specimen"],
                hovertemplate="%{text}<br>X: %{x:.0f}mm<br>Y: %{y:.0f}mm<br>Z: %{z:.0f}mm<extra></extra>"
            ))

    # Add dimension annotations
    dims = chamber_geometry['dimensions']
    annotations_text = (
        f"Chamber Dimensions:<br>"
        f"L: {dims['length_mm']:.0f} mm<br>"
        f"W: {dims['width_mm']:.0f} mm<br>"
        f"H: {dims['height_mm']:.0f} mm<br>"
        f"Volume: {dims['length']*dims['width']*dims['height']:.2f} m³"
    )

    fig.update_layout(
        title="3D Chamber Model with Component Placement",
        scene=dict(
            xaxis_title="Length (mm)",
            yaxis_title="Width (mm)",
            zaxis_title="Height (mm)",
            aspectmode='data',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        width=1000,
        height=800,
        annotations=[
            dict(
                text=annotations_text,
                xref="paper",
                yref="paper",
                x=0.02,
                y=0.98,
                showarrow=False,
                bgcolor="white",
                bordercolor="black",
                borderwidth=1,
                align="left"
            )
        ]
    )

    return fig


def plot_iso_surface(field_data: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                    iso_value: float, title: str = "Iso-Surface Plot",
                    colorscale: str = 'Viridis') -> go.Figure:
    """
    Create 3D iso-surface plot at specified field value.

    Args:
        field_data: 3D field array
        x, y, z: Coordinate arrays
        iso_value: Value for iso-surface
        title: Plot title
        colorscale: Plotly colorscale name

    Returns:
        Plotly Figure object
    """
    # Create mesh grid
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Convert to mm
    X_mm = X * 1000
    Y_mm = Y * 1000
    Z_mm = Z * 1000

    fig = go.Figure(data=go.Isosurface(
        x=X_mm.flatten(),
        y=Y_mm.flatten(),
        z=Z_mm.flatten(),
        value=field_data.flatten(),
        isomin=iso_value - 0.5,
        isomax=iso_value + 0.5,
        surface_count=3,
        colorscale=colorscale,
        caps=dict(x_show=True, y_show=True, z_show=True),
        showscale=True,
        colorbar=dict(title="Value", x=1.1)
    ))

    fig.update_layout(
        title=f"{title} - Iso-Value: {iso_value:.1f}",
        scene=dict(
            xaxis_title="Length (mm)",
            yaxis_title="Width (mm)",
            zaxis_title="Height (mm)",
            aspectmode='data'
        ),
        width=900,
        height=700
    )

    return fig


def plot_velocity_magnitude_3d(velocity_field: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                               title: str = "Velocity Magnitude Distribution") -> go.Figure:
    """
    Create 3D scatter plot of velocity magnitude.

    Args:
        velocity_field: 4D velocity array (nx, ny, nz, 3)
        x, y, z: Coordinate arrays
        title: Plot title

    Returns:
        Plotly Figure object
    """
    # Calculate velocity magnitude
    vel_magnitude = np.sqrt(np.sum(velocity_field**2, axis=3))

    # Subsample
    step = 5
    X, Y, Z = np.meshgrid(x[::step], y[::step], z[::step], indexing='ij')
    vel_sub = vel_magnitude[::step, ::step, ::step]

    # Flatten
    x_flat = X.flatten() * 1000
    y_flat = Y.flatten() * 1000
    z_flat = Z.flatten() * 1000
    vel_flat = vel_sub.flatten()

    fig = go.Figure(data=[go.Scatter3d(
        x=x_flat,
        y=y_flat,
        z=z_flat,
        mode='markers',
        marker=dict(
            size=3,
            color=vel_flat,
            colorscale='Jet',
            showscale=True,
            colorbar=dict(title="Velocity (m/s)", x=1.1),
            cmin=0,
            cmax=np.max(vel_magnitude)
        ),
        text=[f"V: {v:.2f} m/s" for v in vel_flat],
        hovertemplate="X: %{x:.0f}mm<br>Y: %{y:.0f}mm<br>Z: %{z:.0f}mm<br>%{text}<extra></extra>"
    )])

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Length (mm)",
            yaxis_title="Width (mm)",
            zaxis_title="Height (mm)",
            aspectmode='data'
        ),
        width=900,
        height=700
    )

    return fig


def export_interactive_html(figure: go.Figure, filename: str) -> str:
    """
    Export Plotly figure to interactive HTML file.

    Args:
        figure: Plotly Figure object
        filename: Output HTML filename

    Returns:
        Filename of exported HTML
    """
    figure.write_html(filename)
    return filename


def create_multi_panel_view(temp_field: np.ndarray, velocity_field: np.ndarray,
                           humidity_field: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> go.Figure:
    """
    Create multi-panel view with cross-sections of all fields.

    Args:
        temp_field: Temperature field array
        velocity_field: Velocity field array
        humidity_field: Humidity field array
        x, y, z: Coordinate arrays

    Returns:
        Plotly Figure with subplots
    """
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Temperature (XY)", "Velocity Magnitude (XY)",
                       "Humidity (XY)", "Temperature (XZ)"),
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}],
               [{"type": "heatmap"}, {"type": "heatmap"}]]
    )

    # Middle slice indices
    z_mid = len(z) // 2
    y_mid = len(y) // 2

    # Temperature XY
    fig.add_trace(
        go.Heatmap(z=temp_field[:, :, z_mid].T, x=x*1000, y=y*1000,
                  colorscale='RdBu_r', showscale=False),
        row=1, col=1
    )

    # Velocity magnitude XY
    vel_mag = np.sqrt(np.sum(velocity_field**2, axis=3))
    fig.add_trace(
        go.Heatmap(z=vel_mag[:, :, z_mid].T, x=x*1000, y=y*1000,
                  colorscale='Jet', showscale=False),
        row=1, col=2
    )

    # Humidity XY
    fig.add_trace(
        go.Heatmap(z=humidity_field[:, :, z_mid].T, x=x*1000, y=y*1000,
                  colorscale='Blues', showscale=False),
        row=2, col=1
    )

    # Temperature XZ
    fig.add_trace(
        go.Heatmap(z=temp_field[:, y_mid, :].T, x=x*1000, y=z*1000,
                  colorscale='RdBu_r', showscale=False),
        row=2, col=2
    )

    fig.update_layout(
        title="CFD Simulation Results - Multi-Panel View",
        width=1200,
        height=900
    )

    return fig
