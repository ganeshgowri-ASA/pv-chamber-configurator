"""
UV Irradiance Heatmap Visualizations

Comprehensive Plotly-based 3D and 2D visualizations for UV uniformity analysis.
Creates interactive heatmaps, 3D surface plots, and zone compliance maps.

Author: PV Chamber Configurator System
Version: 2.0
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.interpolate import griddata
from typing import List, Tuple, Optional, Dict, Any


class UVHeatmapVisualizer:
    """
    Create interactive UV irradiance heatmap visualizations.

    Provides 2D top-view heatmaps, 3D surface plots, and uniformity zone maps.
    """

    def __init__(
        self,
        chamber_length: float,
        chamber_width: float,
        grid_points: List[Tuple[float, float, float]],
        irradiance_values: np.ndarray
    ):
        """
        Initialize heatmap visualizer.

        Args:
            chamber_length: Chamber length (mm)
            chamber_width: Chamber width (mm)
            grid_points: List of (x, y, z) measurement points
            irradiance_values: Irradiance at each point (W/m²)
        """
        self.chamber_length = chamber_length
        self.chamber_width = chamber_width
        self.grid_points = grid_points
        self.irradiance_values = irradiance_values

        # Extract x, y coordinates and irradiance
        self.x_coords = np.array([p[0] for p in grid_points])
        self.y_coords = np.array([p[1] for p in grid_points])

    def create_2d_heatmap(
        self,
        title: str = "UV Irradiance Uniformity Map (Top View)",
        show_annotations: bool = True,
        show_contours: bool = True
    ) -> go.Figure:
        """
        Create 2D top-view heatmap with contour lines.

        Args:
            title: Plot title
            show_annotations: Show irradiance values at points
            show_contours: Show contour lines

        Returns:
            Plotly Figure object
        """
        # Create high-resolution interpolation grid
        grid_x, grid_y = np.meshgrid(
            np.linspace(0, self.chamber_length, 100),
            np.linspace(0, self.chamber_width, 100)
        )

        # Interpolate irradiance values
        grid_irradiance = griddata(
            points=(self.x_coords, self.y_coords),
            values=self.irradiance_values,
            xi=(grid_x, grid_y),
            method='cubic'
        )

        # Create heatmap
        fig = go.Figure()

        # Add heatmap
        fig.add_trace(go.Heatmap(
            x=np.linspace(0, self.chamber_length, 100),
            y=np.linspace(0, self.chamber_width, 100),
            z=grid_irradiance,
            colorscale='Viridis',
            colorbar=dict(
                title="Irradiance<br>(W/m²)",
                titleside="right",
                tickmode="linear",
                tick0=0,
                dtick=10
            ),
            hovertemplate='X: %{x:.0f} mm<br>Y: %{y:.0f} mm<br>Irradiance: %{z:.1f} W/m²<extra></extra>'
        ))

        # Add contour lines if requested
        if show_contours:
            fig.add_trace(go.Contour(
                x=np.linspace(0, self.chamber_length, 100),
                y=np.linspace(0, self.chamber_width, 100),
                z=grid_irradiance,
                showscale=False,
                contours=dict(
                    start=np.min(grid_irradiance),
                    end=np.max(grid_irradiance),
                    size=10,
                    showlabels=True,
                    labelfont=dict(size=10, color='white')
                ),
                line=dict(color='white', width=1),
                hoverinfo='skip'
            ))

        # Add measurement point markers
        fig.add_trace(go.Scatter(
            x=self.x_coords,
            y=self.y_coords,
            mode='markers+text' if show_annotations else 'markers',
            marker=dict(
                size=12,
                color='white',
                symbol='circle',
                line=dict(color='black', width=2)
            ),
            text=[f'{val:.1f}' for val in self.irradiance_values] if show_annotations else None,
            textposition='top center',
            textfont=dict(size=10, color='white', family='Arial Black'),
            name='Measurement Points',
            hovertemplate='Point: %{pointNumber}<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<br>Irradiance: %{text} W/m²<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='Chamber Length (mm)',
                range=[0, self.chamber_length],
                constrain='domain'
            ),
            yaxis=dict(
                title='Chamber Width (mm)',
                range=[0, self.chamber_width],
                scaleanchor='x',
                scaleratio=1,
                constrain='domain'
            ),
            width=800,
            height=600,
            showlegend=False,
            hovermode='closest'
        )

        return fig

    def create_3d_surface(
        self,
        title: str = "UV Irradiance 3D Surface Plot"
    ) -> go.Figure:
        """
        Create 3D surface plot of irradiance distribution.

        Args:
            title: Plot title

        Returns:
            Plotly Figure object
        """
        # Create high-resolution interpolation grid
        grid_x, grid_y = np.meshgrid(
            np.linspace(0, self.chamber_length, 50),
            np.linspace(0, self.chamber_width, 50)
        )

        # Interpolate irradiance values
        grid_irradiance = griddata(
            points=(self.x_coords, self.y_coords),
            values=self.irradiance_values,
            xi=(grid_x, grid_y),
            method='cubic'
        )

        # Create 3D surface
        fig = go.Figure()

        fig.add_trace(go.Surface(
            x=np.linspace(0, self.chamber_length, 50),
            y=np.linspace(0, self.chamber_width, 50),
            z=grid_irradiance,
            colorscale='Viridis',
            colorbar=dict(
                title="Irradiance<br>(W/m²)",
                titleside="right"
            ),
            hovertemplate='X: %{x:.0f} mm<br>Y: %{y:.0f} mm<br>Irradiance: %{z:.1f} W/m²<extra></extra>',
            contours=dict(
                z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="limegreen",
                    project=dict(z=True)
                )
            )
        ))

        # Add measurement point markers
        fig.add_trace(go.Scatter3d(
            x=self.x_coords,
            y=self.y_coords,
            z=self.irradiance_values,
            mode='markers+text',
            marker=dict(
                size=8,
                color='red',
                symbol='circle',
                line=dict(color='darkred', width=2)
            ),
            text=[f'{val:.1f}' for val in self.irradiance_values],
            textposition='top center',
            textfont=dict(size=9, color='black'),
            name='Measurement Points',
            hovertemplate='Point: %{pointNumber}<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<br>Irradiance: %{z:.1f} W/m²<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=16, color='#2c3e50')
            ),
            scene=dict(
                xaxis=dict(
                    title='Length (mm)',
                    backgroundcolor="rgb(230, 230,230)",
                    gridcolor="white",
                    showbackground=True
                ),
                yaxis=dict(
                    title='Width (mm)',
                    backgroundcolor="rgb(230, 230,230)",
                    gridcolor="white",
                    showbackground=True
                ),
                zaxis=dict(
                    title='Irradiance (W/m²)',
                    backgroundcolor="rgb(230, 230,230)",
                    gridcolor="white",
                    showbackground=True
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            width=900,
            height=700,
            showlegend=False
        )

        return fig

    def create_uniformity_zone_map(
        self,
        avg_irradiance: float,
        title: str = "Uniformity Zone Compliance Map"
    ) -> go.Figure:
        """
        Create zone map showing uniformity compliance.

        Zones:
        - Green: ±5% (excellent)
        - Yellow: ±5-10% (acceptable)
        - Red: >±10% (non-compliant)

        Args:
            avg_irradiance: Average irradiance value (W/m²)
            title: Plot title

        Returns:
            Plotly Figure object
        """
        # Create high-resolution interpolation grid
        grid_x, grid_y = np.meshgrid(
            np.linspace(0, self.chamber_length, 100),
            np.linspace(0, self.chamber_width, 100)
        )

        # Interpolate irradiance values
        grid_irradiance = griddata(
            points=(self.x_coords, self.y_coords),
            values=self.irradiance_values,
            xi=(grid_x, grid_y),
            method='cubic'
        )

        # Calculate deviation percentage
        deviation_pct = np.abs((grid_irradiance - avg_irradiance) / avg_irradiance) * 100.0

        # Create zone classification
        zones = np.zeros_like(deviation_pct)
        zones[deviation_pct <= 5.0] = 1  # Excellent (green)
        zones[(deviation_pct > 5.0) & (deviation_pct <= 10.0)] = 2  # Acceptable (yellow)
        zones[deviation_pct > 10.0] = 3  # Non-compliant (red)

        # Create custom colorscale
        colorscale = [
            [0, 'rgb(46, 204, 113)'],  # Green
            [0.33, 'rgb(46, 204, 113)'],
            [0.33, 'rgb(241, 196, 15)'],  # Yellow
            [0.67, 'rgb(241, 196, 15)'],
            [0.67, 'rgb(231, 76, 60)'],  # Red
            [1, 'rgb(231, 76, 60)']
        ]

        fig = go.Figure()

        # Add zone heatmap
        fig.add_trace(go.Heatmap(
            x=np.linspace(0, self.chamber_length, 100),
            y=np.linspace(0, self.chamber_width, 100),
            z=zones,
            colorscale=colorscale,
            showscale=False,
            hovertemplate='X: %{x:.0f} mm<br>Y: %{y:.0f} mm<br>Zone: %{text}<extra></extra>',
            text=np.where(zones == 1, 'Excellent (±5%)',
                          np.where(zones == 2, 'Acceptable (±5-10%)',
                                   'Non-compliant (>±10%)'))
        ))

        # Add measurement points
        point_deviations = np.abs((self.irradiance_values - avg_irradiance) / avg_irradiance) * 100.0
        point_colors = ['green' if d <= 5 else 'orange' if d <= 10 else 'red'
                        for d in point_deviations]

        fig.add_trace(go.Scatter(
            x=self.x_coords,
            y=self.y_coords,
            mode='markers+text',
            marker=dict(
                size=14,
                color=point_colors,
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            text=[f'{dev:.1f}%' for dev in point_deviations],
            textposition='top center',
            textfont=dict(size=9, color='white', family='Arial Black'),
            name='Deviation %',
            hovertemplate='Point: %{pointNumber}<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<br>Deviation: %{text}<extra></extra>'
        ))

        # Add legend manually
        for zone_val, zone_name, zone_color in [
            (1, 'Excellent (±5%)', 'rgb(46, 204, 113)'),
            (2, 'Acceptable (±5-10%)', 'rgb(241, 196, 15)'),
            (3, 'Non-compliant (>±10%)', 'rgb(231, 76, 60)')
        ]:
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color=zone_color, symbol='square'),
                name=zone_name,
                showlegend=True
            ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='Chamber Length (mm)',
                range=[0, self.chamber_length],
                constrain='domain'
            ),
            yaxis=dict(
                title='Chamber Width (mm)',
                range=[0, self.chamber_width],
                scaleanchor='x',
                scaleratio=1,
                constrain='domain'
            ),
            width=800,
            height=600,
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#2c3e50',
                borderwidth=1
            ),
            hovermode='closest'
        )

        return fig

    def create_led_position_map(
        self,
        led_positions: List[Tuple[float, float, float]],
        title: str = "UV LED Array Layout (Top View)"
    ) -> go.Figure:
        """
        Visualize LED positions over test plane.

        Args:
            led_positions: List of LED (x, y, z) positions
            title: Plot title

        Returns:
            Plotly Figure object
        """
        led_x = [pos[0] for pos in led_positions]
        led_y = [pos[1] for pos in led_positions]

        fig = go.Figure()

        # Add chamber outline
        fig.add_trace(go.Scatter(
            x=[0, self.chamber_length, self.chamber_length, 0, 0],
            y=[0, 0, self.chamber_width, self.chamber_width, 0],
            mode='lines',
            line=dict(color='black', width=2, dash='dash'),
            name='Chamber Outline',
            hoverinfo='skip'
        ))

        # Add measurement grid points
        fig.add_trace(go.Scatter(
            x=self.x_coords,
            y=self.y_coords,
            mode='markers',
            marker=dict(
                size=10,
                color='blue',
                symbol='x',
                line=dict(color='darkblue', width=1)
            ),
            name='Measurement Points',
            hovertemplate='Measurement Point<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<extra></extra>'
        ))

        # Add LED positions
        fig.add_trace(go.Scatter(
            x=led_x,
            y=led_y,
            mode='markers',
            marker=dict(
                size=15,
                color='yellow',
                symbol='star',
                line=dict(color='orange', width=2)
            ),
            name='UV LEDs',
            hovertemplate='LED Position<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='Chamber Length (mm)',
                range=[-100, self.chamber_length + 100],
                constrain='domain'
            ),
            yaxis=dict(
                title='Chamber Width (mm)',
                range=[-100, self.chamber_width + 100],
                scaleanchor='x',
                scaleratio=1,
                constrain='domain'
            ),
            width=800,
            height=600,
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#2c3e50',
                borderwidth=1
            ),
            hovermode='closest',
            plot_bgcolor='rgba(240, 240, 240, 0.5)'
        )

        return fig

    def create_spectrum_plot(
        self,
        spectrum_df: pd.DataFrame,
        title: str = "UV LED Spectral Power Distribution"
    ) -> go.Figure:
        """
        Create UV spectrum visualization.

        Args:
            spectrum_df: DataFrame with 'Wavelength (nm)' and 'Relative Intensity (%)'
            title: Plot title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Add spectrum line
        fig.add_trace(go.Scatter(
            x=spectrum_df['Wavelength (nm)'],
            y=spectrum_df['Relative Intensity (%)'],
            mode='lines',
            line=dict(color='purple', width=3),
            fill='tozeroy',
            fillcolor='rgba(147, 51, 234, 0.3)',
            name='SPD',
            hovertemplate='Wavelength: %{x:.1f} nm<br>Intensity: %{y:.1f}%<extra></extra>'
        ))

        # Add UVA/UVB region markers
        fig.add_vrect(
            x0=280, x1=315,
            fillcolor="rgba(231, 76, 60, 0.2)",
            layer="below",
            line_width=0,
            annotation_text="UVB",
            annotation_position="top left"
        )

        fig.add_vrect(
            x0=315, x1=400,
            fillcolor="rgba(52, 152, 219, 0.2)",
            layer="below",
            line_width=0,
            annotation_text="UVA",
            annotation_position="top right"
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='Wavelength (nm)',
                range=[270, 410],
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='Relative Intensity (%)',
                range=[0, 105],
                gridcolor='lightgray'
            ),
            width=800,
            height=500,
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='white'
        )

        return fig

    def create_aging_curve_plot(
        self,
        aging_df: pd.DataFrame,
        current_hours: float = 0.0,
        title: str = "LED Degradation Curve (L80 Model)"
    ) -> go.Figure:
        """
        Create LED aging/degradation curve visualization.

        Args:
            aging_df: DataFrame with 'Operating Hours' and 'Output (%)'
            current_hours: Current operating hours (for marker)
            title: Plot title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Add degradation curve
        fig.add_trace(go.Scatter(
            x=aging_df['Operating Hours'],
            y=aging_df['Output (%)'],
            mode='lines',
            line=dict(color='#e74c3c', width=3),
            name='LED Output',
            hovertemplate='Hours: %{x:,.0f}<br>Output: %{y:.1f}%<extra></extra>'
        ))

        # Add L80 threshold line
        fig.add_hline(
            y=80,
            line_dash="dash",
            line_color="orange",
            annotation_text="L80 Threshold (80%)",
            annotation_position="right"
        )

        # Add current position marker if provided
        if current_hours > 0:
            current_output = aging_df.loc[
                (aging_df['Operating Hours'] - current_hours).abs().idxmin(),
                'Output (%)'
            ]
            fig.add_trace(go.Scatter(
                x=[current_hours],
                y=[current_output],
                mode='markers',
                marker=dict(size=15, color='green', symbol='diamond'),
                name='Current Status',
                hovertemplate=f'Current: {current_hours:,.0f} hrs<br>Output: {current_output:.1f}%<extra></extra>'
            ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='Operating Hours',
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='LED Output (%)',
                range=[70, 105],
                gridcolor='lightgray'
            ),
            width=800,
            height=500,
            showlegend=True,
            legend=dict(
                x=0.7,
                y=0.95,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#2c3e50',
                borderwidth=1
            ),
            hovermode='x unified',
            plot_bgcolor='white'
        )

        return fig

    def create_robot_path_visualization(
        self,
        path_df: pd.DataFrame,
        title: str = "Robot Measurement Path (Optimized)"
    ) -> go.Figure:
        """
        Visualize robot measurement path.

        Args:
            path_df: DataFrame with 'Sequence', 'X (mm)', 'Y (mm)'
            title: Plot title

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Add chamber outline
        fig.add_trace(go.Scatter(
            x=[0, self.chamber_length, self.chamber_length, 0, 0],
            y=[0, 0, self.chamber_width, self.chamber_width, 0],
            mode='lines',
            line=dict(color='black', width=2, dash='dash'),
            name='Chamber Outline',
            hoverinfo='skip'
        ))

        # Add path lines
        fig.add_trace(go.Scatter(
            x=path_df['X (mm)'],
            y=path_df['Y (mm)'],
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=10, color='lightblue', line=dict(color='blue', width=1)),
            name='Travel Path',
            hovertemplate='Sequence: %{text}<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<extra></extra>',
            text=path_df['Sequence']
        ))

        # Add sequence numbers
        fig.add_trace(go.Scatter(
            x=path_df['X (mm)'],
            y=path_df['Y (mm)'],
            mode='text',
            text=path_df['Sequence'],
            textposition='middle center',
            textfont=dict(size=10, color='darkblue', family='Arial Black'),
            name='Sequence',
            hoverinfo='skip'
        ))

        # Highlight start and end points
        fig.add_trace(go.Scatter(
            x=[path_df.iloc[0]['X (mm)']],
            y=[path_df.iloc[0]['Y (mm)']],
            mode='markers',
            marker=dict(size=20, color='green', symbol='star'),
            name='Start',
            hovertemplate='START<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<extra></extra>'
        ))

        fig.add_trace(go.Scatter(
            x=[path_df.iloc[-1]['X (mm)']],
            y=[path_df.iloc[-1]['Y (mm)']],
            mode='markers',
            marker=dict(size=20, color='red', symbol='square'),
            name='End',
            hovertemplate='END<br>X: %{x:.0f} mm<br>Y: %{y:.0f} mm<extra></extra>'
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                xanchor='center',
                font=dict(size=16, color='#2c3e50')
            ),
            xaxis=dict(
                title='Chamber Length (mm)',
                range=[-100, self.chamber_length + 100],
                constrain='domain'
            ),
            yaxis=dict(
                title='Chamber Width (mm)',
                range=[-100, self.chamber_width + 100],
                scaleanchor='x',
                scaleratio=1,
                constrain='domain'
            ),
            width=800,
            height=600,
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#2c3e50',
                borderwidth=1
            ),
            hovermode='closest',
            plot_bgcolor='rgba(240, 240, 240, 0.5)'
        )

        return fig


def create_comprehensive_report_figure(
    heatmap_fig: go.Figure,
    surface_fig: go.Figure,
    zone_fig: go.Figure,
    spectrum_fig: go.Figure
) -> go.Figure:
    """
    Create comprehensive multi-panel report figure.

    Args:
        heatmap_fig: 2D heatmap figure
        surface_fig: 3D surface figure
        zone_fig: Zone compliance figure
        spectrum_fig: Spectrum figure

    Returns:
        Combined Plotly Figure with subplots
    """
    # Note: This is a simplified version. Full subplot integration
    # with 3D plots requires careful layout management.

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            '2D Irradiance Heatmap',
            'Uniformity Zone Map',
            'UV Spectrum',
            'LED Layout'
        ),
        specs=[
            [{'type': 'heatmap'}, {'type': 'heatmap'}],
            [{'type': 'scatter'}, {'type': 'scatter'}]
        ]
    )

    # Note: Adding traces from existing figures to subplots
    # requires trace extraction and repositioning.
    # This is a template for custom implementation.

    fig.update_layout(
        title_text="UV Optical System Comprehensive Report",
        height=1000,
        showlegend=False
    )

    return fig
