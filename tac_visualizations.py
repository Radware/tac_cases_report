"""
TAC Executive Report Visualizations Module

Creates professional, interactive charts and graphs for TAC case analysis
with executive-level insights and styling.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from collections import Counter

from tac_config import (
    COLOR_PALETTES, ACTIVE_COLOR_PALETTE, CHART_COLOR_ASSIGNMENTS,
    CHART_CONFIG, CHART_LAYOUT, CHART_PLOTLYJS_MODE
)
from tac_utils import format_number, calculate_percentage

logger = logging.getLogger(__name__)


class TACVisualizer:
    """
    Creates interactive visualizations for TAC case analysis.
    """
    
    def __init__(self, output_format: str = 'html'):
        """Initialize the visualizer with configurable colors and output format.
        
        Args:
            output_format: Target output format ('html' or 'pdf')
        """
        # Get active color palette
        self.chart_colors = COLOR_PALETTES.get(ACTIVE_COLOR_PALETTE, COLOR_PALETTES['radware_corporate'])
        self.color_assignments = CHART_COLOR_ASSIGNMENTS
        self.output_format = output_format
        
        # Load PDF-specific settings if generating for PDF
        if output_format == 'pdf':
            from tac_config import PDF_CHART_DIMENSIONS, PDF_LAYOUT_SETTINGS
            self.pdf_dimensions = PDF_CHART_DIMENSIONS
            self.pdf_layout = PDF_LAYOUT_SETTINGS
        else:
            self.pdf_dimensions = None
            self.pdf_layout = None
        
        # Common layout settings
        self.common_layout = {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'paper_bgcolor': 'white',
            'plot_bgcolor': 'white',
            'margin': {'l': 50, 'r': 50, 't': 80, 'b': 50}
        }
        
        logger.info("Initialized TAC Visualizer")
    
    def _get_chart_width(self, chart_type: str = 'standard') -> int:
        """Get appropriate chart width based on output format."""
        if self.output_format == 'pdf' and self.pdf_dimensions:
            chart_key = f'{chart_type}_chart'
            return self.pdf_dimensions.get(chart_key, {}).get('width', 650)
        return 900  # Default HTML width
    
    def _get_chart_height(self, chart_type: str = 'standard') -> int:
        """Get appropriate chart height based on output format."""
        if self.output_format == 'pdf' and self.pdf_dimensions:
            chart_key = f'{chart_type}_chart'
            return self.pdf_dimensions.get(chart_key, {}).get('height', 400)
        return 600  # Default HTML height
    
    def _get_chart_margins(self) -> dict:
        """Get appropriate chart margins based on output format."""
        if self.output_format == 'pdf' and self.pdf_layout:
            return self.pdf_layout.get('chart_margins', {'l': 30, 'r': 30, 't': 80, 'b': 60})
        return {'l': 40, 'r': 40, 't': 100, 'b': 80}  # Default margins
    
    def create_monthly_cases_chart(self, monthly_data: Dict[str, Any]) -> str:
        """
        Create monthly case volume trend chart with configurable chart type.
        
        Args:
            monthly_data: Monthly trends data
            
        Returns:
            HTML string with chart
        """
        if not monthly_data.get('available') or not monthly_data.get('monthly_counts'):
            return self._create_not_available_message("Monthly Trends", 
                monthly_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES, CHART_STYLES
            
            monthly_counts = monthly_data['monthly_counts']
            chart_type = CHART_TYPES.get('monthly_trends', 'line')
            
            # Sort by date
            sorted_months = sorted(monthly_counts.keys())
            values = [monthly_counts[month] for month in sorted_months]
            
            # Format month labels
            month_labels = []
            for month in sorted_months:
                try:
                    date_obj = datetime.strptime(month, '%Y-%m')
                    month_labels.append(date_obj.strftime('%b %Y'))
                except:
                    month_labels.append(month)
            
            fig = go.Figure()
            
            # Create chart based on configured type
            if chart_type == 'bar':
                style = CHART_STYLES.get('monthly_trends', {}).get('bar', {})
                bar_width = style.get('bar_width', 0.6)
                show_values = style.get('show_values', True)
                
                # Use configurable trend colors
                trend_colors = self.color_assignments.get('trends_colors', {})
                bar_color = trend_colors.get('primary', self.chart_colors[0])
                
                fig.add_trace(go.Bar(
                    x=month_labels,
                    y=values,
                    name='Cases Created',
                    marker=dict(color=bar_color),
                    width=bar_width,
                    text=values if show_values else None,
                    textposition='outside' if show_values else None,
                    hovertemplate='<b>%{x}</b><br>Cases: %{y}<extra></extra>'
                ))
                
            elif chart_type == 'area':
                style = CHART_STYLES.get('monthly_trends', {}).get('area', {})
                line_width = style.get('line_width', 2)
                show_trend = style.get('show_trend', True)
                
                # Use configurable trend colors
                trend_colors = self.color_assignments.get('trends_colors', {})
                line_color = trend_colors.get('primary', self.chart_colors[0])
                fill_color = trend_colors.get('area_fill', f'rgba({int(line_color[1:3], 16)}, {int(line_color[3:5], 16)}, {int(line_color[5:7], 16)}, 0.3)')
                
                fig.add_trace(go.Scatter(
                    x=month_labels,
                    y=values,
                    mode='lines+markers',
                    name='Cases Created',
                    line=dict(color=line_color, width=line_width),
                    marker=dict(size=6, color=line_color),
                    fill='tozeroy',
                    fillcolor=fill_color,
                    hovertemplate='<b>%{x}</b><br>Cases: %{y}<extra></extra>'
                ))
                
                # Add trend line if enabled and more than 2 data points
                if show_trend and len(values) > 2:
                    x_numeric = list(range(len(values)))
                    z = self._calculate_trend(x_numeric, values)
                    trend_y = [z[0] + z[1] * x for x in x_numeric]
                    
                    fig.add_trace(go.Scatter(
                        x=month_labels,
                        y=trend_y,
                        mode='lines',
                        name='Trend',
                        line=dict(color=self.chart_colors[2], width=2, dash='dash'),  # Use 3rd color from palette for accent
                        hovertemplate='Trend: %{y:.1f}<extra></extra>'
                    ))
                    
            else:  # Default to line chart
                style = CHART_STYLES.get('monthly_trends', {}).get('line', {})
                line_width = style.get('line_width', 3)
                marker_size = style.get('marker_size', 8)
                show_trend = style.get('show_trend', True)
                
                # Use configurable trend colors
                trend_colors = self.color_assignments.get('trends_colors', {})
                line_color = trend_colors.get('primary', self.chart_colors[0])
                
                fig.add_trace(go.Scatter(
                    x=month_labels,
                    y=values,
                    mode='lines+markers',
                    name='Cases Created',
                    line=dict(color=line_color, width=line_width),
                    marker=dict(size=marker_size, color=line_color),
                    hovertemplate='<b>%{x}</b><br>Cases: %{y}<extra></extra>'
                ))
                
                # Add trend line if enabled and more than 2 data points
                if show_trend and len(values) > 2:
                    x_numeric = list(range(len(values)))
                    z = self._calculate_trend(x_numeric, values)
                    trend_y = [z[0] + z[1] * x for x in x_numeric]
                    
                    fig.add_trace(go.Scatter(
                        x=month_labels,
                        y=trend_y,
                        mode='lines',
                        name='Trend',
                        line=dict(color=self.chart_colors[2], width=2, dash='dash'),  # Use 3rd color from palette for accent
                        hovertemplate='Trend: %{y:.1f}<extra></extra>'
                    ))
            
            # Create base layout without margin conflicts
            base_layout = {k: v for k, v in self.common_layout.items() if k != 'margin'}
            
            fig.update_layout(
                title='TAC Cases Created by Month',
                xaxis_title='Month',
                yaxis_title='Number of Cases',
                yaxis=dict(rangemode='tozero'),  # Start y-axis from 0
                width=self._get_chart_width('standard'),
                height=self._get_chart_height('standard'),
                margin=self._get_chart_margins(),
                **base_layout
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="monthly_cases_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create monthly cases chart: {e}")
            return self._create_error_message("Monthly Cases Chart")
    
    def _create_distribution_chart(self, labels: list, values: list, colors: list, 
                                  chart_type: str, title: str, div_id: str) -> go.Figure:
        """
        Create a distribution chart with configurable type.
        
        Args:
            labels: Data labels
            values: Data values  
            colors: Color list for data points
            chart_type: Type of chart ('pie', 'donut', 'bar', 'horizontal_bar')
            title: Chart title
            div_id: HTML div ID for the chart
            
        Returns:
            Plotly Figure object
        """
        from tac_config import CHART_STYLES
        
        fig = go.Figure()
        
        if chart_type in ['pie', 'donut']:
            style = CHART_STYLES.get('distribution_charts', {}).get(chart_type, {})
            hole_size = style.get('hole', 0.3 if chart_type == 'pie' else 0.5)
            textinfo = style.get('textinfo', 'label+value')
            textposition = style.get('textposition', 'outside')
            
            # Create pie/donut with enhanced styling
            fig.add_trace(go.Pie(
                labels=labels,
                values=values,
                hole=hole_size,
                marker=dict(
                    colors=colors,
                    line=dict(
                        color='white',  # White borders between slices
                        width=3         # Thick borders for clean separation
                    )
                ),
                textinfo=textinfo,
                textposition=textposition,
                textfont=dict(
                    size=14,
                    family='Arial, sans-serif',
                    color='#2c3e50'  # Dark color for better readability
                ),
                insidetextfont=dict(
                    size=16,
                    family='Arial, sans-serif', 
                    color='white'  # White text inside slices
                ),
                outsidetextfont=dict(
                    size=14,
                    family='Arial, sans-serif',
                    color='#2c3e50'  # Dark text outside
                ),
                pull=[0.01] * len(labels),  # Slightly separate all slices for 3D effect
                domain=dict(x=[0.0, 0.65], y=[0.1, 0.9]),  # Fixed pie chart position - consistent for all pies
                hovertemplate='<b>%{label}</b><br>' +
                             'Cases: <b>%{value}</b><br>' +
                             'Percentage: <b>%{percent}</b><br>' +
                             '<extra></extra>',
                hoverlabel=dict(
                    bgcolor='rgba(255,255,255,0.95)',
                    bordercolor='#2c3e50',
                    font=dict(
                        color='#2c3e50',
                        size=13,
                        family='Arial, sans-serif'
                    )
                )
            ))
            
        elif chart_type == 'bar':
            style = CHART_STYLES.get('distribution_charts', {}).get('bar', {})
            show_values = style.get('show_values', True)
            
            fig.add_trace(go.Bar(
                x=labels,
                y=values,
                marker_color=colors,
                text=values if show_values else None,
                textposition='outside' if show_values else None,
                hovertemplate='<b>%{x}</b><br>Cases: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                xaxis_title='Category',
                yaxis_title='Number of Cases',
                yaxis=dict(rangemode='tozero')
            )
            
        elif chart_type == 'horizontal_bar':
            style = CHART_STYLES.get('distribution_charts', {}).get('horizontal_bar', {})
            show_values = style.get('show_values', True)
            
            fig.add_trace(go.Bar(
                x=values,
                y=labels,
                orientation='h',
                marker_color=colors,
                text=values if show_values else None,
                textposition='outside' if show_values else None,
                hovertemplate='<b>%{y}</b><br>Cases: %{x}<extra></extra>'
            ))
            
            fig.update_layout(
                xaxis_title='Number of Cases',
                yaxis_title='Category',
                xaxis=dict(rangemode='tozero')
            )
        
        # Enhanced layout configuration
        if chart_type in ['pie', 'donut']:
            # Special layout for pie/donut charts
            enhanced_layout = {
                'title': dict(
                    text=title,
                    font=dict(
                        size=20,
                        family='Arial Black, sans-serif',
                        color='#2c3e50'
                    ),
                    x=0.5,  # Center the title
                    y=0.95
                ),
                'width': self._get_chart_width('standard'),
                'height': self._get_chart_height('standard'),
                'showlegend': True,
                'legend': dict(
                    orientation='v',  # Vertical legend for pie charts
                    yanchor='top',
                    y=0.9,
                    xanchor='left',
                    x=0.67,  # Fixed legend position - consistent for all pies
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='#e1e8ed',
                    borderwidth=1,
                    font=dict(
                        size=11,
                        family='Arial, sans-serif',
                        color='#2c3e50'
                    )
                ),
                'plot_bgcolor': 'white',
                'paper_bgcolor': 'white',
                'margin': self._get_chart_margins(),  # Use format-appropriate margins
                'annotations': [
                    dict(
                        text=f'Total Cases: {sum(values)}',
                        x=0.5, y=-0.15,  # Moved annotation much lower to avoid overlap with pie labels
                        xref='paper', yref='paper',
                        showarrow=False,
                        font=dict(
                            size=14,
                            family='Arial, sans-serif',
                            color='#7f8c8d'
                        )
                    )
                ]
            }
            fig.update_layout(**enhanced_layout)
        else:
            # Regular layout for other chart types
            fig.update_layout(
                title=title,
                **self.common_layout
            )
        
        return fig

    def create_severity_distribution_chart(self, severity_data: Dict[str, Any]) -> str:
        """
        Create severity distribution chart with configurable chart type.
        
        Args:
            severity_data: Severity analysis data
            
        Returns:
            HTML string with chart
        """
        if not severity_data.get('available') or not severity_data.get('counts'):
            return self._create_not_available_message("Severity Distribution", 
                severity_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES
            
            counts = severity_data['counts']
            chart_type = CHART_TYPES.get('severity_distribution', 'pie')
            
            # Sort by severity order (Critical, High, Medium, Low)
            severity_order = ['1 - Critical', '2 - High', '3 - Medium', '4 - Low']
            sorted_severities = []
            sorted_values = []
            
            for severity in severity_order:
                if severity in counts:
                    sorted_severities.append(severity)
                    sorted_values.append(counts[severity])
            
            # Add any remaining severities not in standard order
            for severity, count in counts.items():
                if severity not in severity_order:
                    sorted_severities.append(severity)
                    sorted_values.append(count)
            
            # Color mapping for severities (use configurable colors)
            severity_colors = self.color_assignments.get('severity_colors', {})
            
            colors = [severity_colors.get(sev, self.chart_colors[i % len(self.chart_colors)]) 
                     for i, sev in enumerate(sorted_severities)]
            
            fig = self._create_distribution_chart(
                labels=sorted_severities,
                values=sorted_values,
                colors=colors,
                chart_type=chart_type,
                title='Case Distribution by Severity',
                div_id='severity_distribution_chart'
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="severity_distribution_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create severity distribution chart: {e}")
            return self._create_error_message("Severity Distribution Chart")
    
    def create_status_distribution_chart(self, status_data: Dict[str, Any]) -> str:
        """
        Create status distribution chart with configurable chart type.
        
        Args:
            status_data: Status analysis data
            
        Returns:
            HTML string with chart
        """
        if not status_data.get('available') or not status_data.get('counts'):
            return self._create_not_available_message("Status Distribution", 
                status_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES
            
            counts = status_data['counts']
            chart_type = CHART_TYPES.get('status_distribution', 'pie')
            
            # Sort by count (descending)
            sorted_statuses = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            statuses = [item[0] for item in sorted_statuses]
            values = [item[1] for item in sorted_statuses]
            
            # Get colors for statuses
            colors = self._get_status_colors(statuses)
            
            fig = self._create_distribution_chart(
                labels=statuses,
                values=values,
                colors=colors,
                chart_type=chart_type,
                title='Case Distribution by Status',
                div_id='status_distribution_chart'
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="status_distribution_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create status distribution chart: {e}")
            return self._create_error_message("Status Distribution Chart")

    def create_product_hierarchy_chart(self, product_data: Dict[str, Any]) -> str:
        """
        Create product hierarchy distribution chart with configurable chart type.
        
        Args:
            product_data: Product analysis data
            
        Returns:
            HTML string with chart
        """
        if not product_data.get('available') or not product_data.get('product_counts'):
            return self._create_not_available_message("Product Distribution", 
                product_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES
            
            product_counts = product_data['product_counts']
            chart_type = CHART_TYPES.get('product_hierarchy', 'pie')
            
            # Sort by count (descending)
            sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
            products = [item[0] for item in sorted_products]
            values = [item[1] for item in sorted_products]
            
            # Take top 10 products if more than 10
            if len(products) > 10:
                products = products[:10]
                values = values[:10]
            
            # Generate colors
            colors = [self.chart_colors[i % len(self.chart_colors)] for i in range(len(products))]
            
            fig = self._create_distribution_chart(
                labels=products,
                values=values,
                colors=colors,
                chart_type=chart_type,
                title='Cases by Product Hierarchy',
                div_id='product_hierarchy_chart'
            )
            
            # For horizontal bar charts, reverse y-axis to show highest at top
            if chart_type == 'horizontal_bar':
                fig.update_yaxes(autorange="reversed")
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="product_hierarchy_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create product hierarchy chart: {e}")
            return self._create_error_message("Product Hierarchy Chart")
    
    def create_bug_analysis_chart(self, bug_data: Dict[str, Any]) -> str:
        """
        Create bug vs non-bug analysis chart with configurable chart type.
        Shows both the bug vs non-bug breakdown and detailed bug types.
        
        Args:
            bug_data: Bug analysis data
            
        Returns:
            HTML string with chart(s)
        """
        if not bug_data.get('available') or not bug_data.get('bug_vs_non_bug'):
            return self._create_not_available_message("Bug Analysis", 
                bug_data.get('reason', 'No data available'))

        try:
            from tac_config import CHART_TYPES
            
            bug_vs_non_bug = bug_data['bug_vs_non_bug']
            bug_types = bug_data.get('bug_types', {})
            chart_type = CHART_TYPES.get('bug_analysis', 'pie')
            
            # Check if we should use compact layout for PDF
            use_compact = (self.output_format == 'pdf' and 
                          self.pdf_layout and 
                          self.pdf_layout.get('use_compact_bug_analysis', False) and
                          bug_types and len(bug_types) > 0)
            
            if use_compact:
                # Create side-by-side layout for PDF
                return self._create_compact_bug_analysis(bug_vs_non_bug, bug_types, chart_type)
            else:
                # Create standard vertical layout
                return self._create_standard_bug_analysis(bug_vs_non_bug, bug_types, chart_type)
            
        except Exception as e:
            logger.error(f"Failed to create bug analysis chart: {e}")
            return self._create_error_message("Bug Analysis Chart")
    
    def _create_standard_bug_analysis(self, bug_vs_non_bug: dict, bug_types: dict, chart_type: str) -> str:
        """Create standard vertical layout for bug analysis."""
        charts_html = ""
        
        # Chart 1: Bug vs Non-Bug Analysis
        labels = list(bug_vs_non_bug.keys())
        values = list(bug_vs_non_bug.values())
        
        # Use configurable bug colors
        bug_colors = self.color_assignments.get('bug_colors', {})
        colors = [bug_colors.get(label, self.chart_colors[i % len(self.chart_colors)]) 
                 for i, label in enumerate(labels)]
        
        fig1 = self._create_distribution_chart(
            labels=labels,
            values=values,
            colors=colors,
            chart_type=chart_type,
            title='Bug vs Non-Bug Cases',
            div_id='bug_analysis_main_chart'
        )
        
        charts_html += fig1.to_html(
            include_plotlyjs=CHART_PLOTLYJS_MODE,
            div_id="bug_analysis_main_chart",
            config=CHART_CONFIG
        )
        
        # Chart 2: Bug Types Breakdown (if there are bugs)
        if bug_types and len(bug_types) > 0:
            bug_labels = list(bug_types.keys())
            bug_values = list(bug_types.values())
            bug_colors_list = self.chart_colors[:len(bug_labels)]
            
            fig2 = self._create_distribution_chart(
                labels=bug_labels,
                values=bug_values,
                colors=bug_colors_list,
                chart_type=chart_type,
                title='Bug Types Breakdown',
                div_id='bug_types_chart'
            )
            
            charts_html += "<br><br>" + fig2.to_html(
                include_plotlyjs=False,  # Don't include plotly.js again
                div_id="bug_types_chart",
                config=CHART_CONFIG
            )
        
        return charts_html
    
    def _create_compact_bug_analysis(self, bug_vs_non_bug: dict, bug_types: dict, chart_type: str) -> str:
        """Create compact side-by-side layout for PDF."""
        from plotly.subplots import make_subplots
        from tac_config import CHART_STYLES
        
        # Get pie chart styling from config
        style = CHART_STYLES.get('distribution_charts', {}).get(chart_type, {})
        hole_size = style.get('hole', 0.3 if chart_type == 'pie' else 0.5)
        textinfo = style.get('textinfo', 'label+value')
        textposition = style.get('textposition', 'outside')
        
        # Create subplot with 1 row, 2 columns
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'domain'}, {'type': 'domain'}]],
            subplot_titles=('Bug vs Non-Bug Cases', 'Bug Types Breakdown'),
            horizontal_spacing=0.05
        )
        
        # Chart 1: Bug vs Non-Bug Analysis
        labels1 = list(bug_vs_non_bug.keys())
        values1 = list(bug_vs_non_bug.values())
        bug_colors = self.color_assignments.get('bug_colors', {})
        colors1 = [bug_colors.get(label, self.chart_colors[i % len(self.chart_colors)]) 
                  for i, label in enumerate(labels1)]
        
        fig.add_trace(go.Pie(
            labels=labels1,
            values=values1,
            hole=hole_size,
            marker=dict(
                colors=colors1,
                line=dict(
                    color='white',  # White borders between slices
                    width=3         # Thick borders for clean separation
                )
            ),
            textinfo=textinfo,
            textposition=textposition,
            textfont=dict(
                size=14,
                family='Arial, sans-serif',
                color='#2c3e50'  # Dark color for better readability
            ),
            insidetextfont=dict(
                size=16,
                family='Arial, sans-serif', 
                color='white'  # White text inside slices
            ),
            outsidetextfont=dict(
                size=14,
                family='Arial, sans-serif',
                color='#2c3e50'  # Dark text outside
            ),
            pull=[0.01] * len(labels1),  # Slightly separate all slices for 3D effect
            domain=dict(x=[0.0, 0.45], y=[0.0, 1.0]),
            hovertemplate='<b>%{label}</b><br>' +
                         'Cases: <b>%{value}</b><br>' +
                         'Percentage: <b>%{percent}</b><br>' +
                         '<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='#2c3e50',
                font=dict(
                    color='#2c3e50',
                    size=13,
                    family='Arial, sans-serif'
                )
            )
        ), row=1, col=1)
        
        # Chart 2: Bug Types Breakdown
        if bug_types and len(bug_types) > 0:
            labels2 = list(bug_types.keys())
            values2 = list(bug_types.values())
            colors2 = self.chart_colors[:len(labels2)]
            
            fig.add_trace(go.Pie(
                labels=labels2,
                values=values2,
                hole=hole_size,
                marker=dict(
                    colors=colors2,
                    line=dict(
                        color='white',  # White borders between slices
                        width=3         # Thick borders for clean separation
                    )
                ),
                textinfo=textinfo,
                textposition=textposition,
                textfont=dict(
                    size=14,
                    family='Arial, sans-serif',
                    color='#2c3e50'  # Dark color for better readability
                ),
                insidetextfont=dict(
                    size=16,
                    family='Arial, sans-serif', 
                    color='white'  # White text inside slices
                ),
                outsidetextfont=dict(
                    size=14,
                    family='Arial, sans-serif',
                    color='#2c3e50'  # Dark text outside
                ),
                pull=[0.01] * len(labels2),  # Slightly separate all slices for 3D effect
                domain=dict(x=[0.55, 1.0], y=[0.0, 1.0]),
                hovertemplate='<b>%{label}</b><br>' +
                             'Cases: <b>%{value}</b><br>' +
                             'Percentage: <b>%{percent}</b><br>' +
                             '<extra></extra>',
                hoverlabel=dict(
                    bgcolor='rgba(255,255,255,0.95)',
                    bordercolor='#2c3e50',
                    font=dict(
                        color='#2c3e50',
                        size=13,
                        family='Arial, sans-serif'
                    )
                )
            ), row=1, col=2)
        
        # Update layout for compact format
        fig.update_layout(
            title="Bug-Related Case Analysis",
            width=self._get_chart_width('bug_analysis'),
            height=self._get_chart_height('bug_analysis'),
            margin=self._get_chart_margins(),
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5
            )
        )
        
        return fig.to_html(
            include_plotlyjs=CHART_PLOTLYJS_MODE,
            div_id="bug_analysis_compact_chart",
            config=CHART_CONFIG
        )
    
    def _create_assignment_chart(self, labels: list, values: list, colors: list,
                                chart_type: str, title: str, div_id: str) -> go.Figure:
        """
        Create an assignment chart with configurable type.
        
        Args:
            labels: Data labels (e.g., engineer names)
            values: Data values (e.g., case counts)
            colors: Color list for data points
            chart_type: Type of chart ('bar', 'horizontal_bar')
            title: Chart title
            div_id: HTML div ID for the chart
            
        Returns:
            Plotly Figure object
        """
        from tac_config import CHART_STYLES
        
        fig = go.Figure()
        
        if chart_type == 'horizontal_bar':
            style = CHART_STYLES.get('assignment_charts', {}).get('horizontal_bar', {})
            show_values = style.get('show_values', True)
            
            fig.add_trace(go.Bar(
                x=values,
                y=labels,
                orientation='h',
                marker_color=colors,
                text=values if show_values else None,
                textposition='outside' if show_values else None,
                hovertemplate='<b>%{y}</b><br>Cases: %{x}<extra></extra>'
            ))
            
            fig.update_layout(
                xaxis_title='Number of Cases',
                yaxis_title='Engineer',
                xaxis=dict(rangemode='tozero')
            )
            
            # Reverse y-axis to show highest at top
            fig.update_yaxes(autorange="reversed")
            
        else:  # Default to vertical bar
            style = CHART_STYLES.get('assignment_charts', {}).get('bar', {})
            show_values = style.get('show_values', True)
            
            fig.add_trace(go.Bar(
                x=labels,
                y=values,
                marker_color=colors,
                text=values if show_values else None,
                textposition='outside' if show_values else None,
                hovertemplate='<b>%{x}</b><br>Cases: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                xaxis_title='Engineer',
                yaxis_title='Number of Cases',
                yaxis=dict(rangemode='tozero')
            )
        
        # Create base layout without margin conflicts
        base_layout = {k: v for k, v in self.common_layout.items() if k != 'margin'}
        
        fig.update_layout(
            title=title,
            width=self._get_chart_width('bar'),
            height=self._get_chart_height('bar'),
            margin=self._get_chart_margins(),
            **base_layout
        )
        
        return fig

    def create_engineer_assignment_chart(self, engineer_data: Dict[str, Any]) -> str:
        """
        Create engineer case assignment chart with configurable chart type.
        
        Args:
            engineer_data: Engineer assignment data
            
        Returns:
            HTML string with chart
        """
        if not engineer_data.get('available') or not engineer_data.get('case_counts'):
            return self._create_not_available_message("Engineer Case Assignment", 
                engineer_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES
            
            case_counts = engineer_data['case_counts']
            chart_type = CHART_TYPES.get('engineer_assignment', 'horizontal_bar')
            
            # Sort by case count (descending) and take top 15
            sorted_engineers = sorted(case_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            engineers = [item[0] for item in sorted_engineers]
            values = [item[1] for item in sorted_engineers]
            
            # Use configurable engineer assignment colors
            assignment_colors = self.color_assignments.get('engineer_assignment_colors', {})
            bar_color = assignment_colors.get('primary', self.chart_colors[0])  # Use first color from active palette as fallback
            colors = [bar_color] * len(engineers)
            
            fig = self._create_assignment_chart(
                labels=engineers,
                values=values,
                colors=colors,
                chart_type=chart_type,
                title='Cases by Assigned Engineer (Top 15)',
                div_id='engineer_assignment_chart'
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="engineer_assignment_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create engineer assignment chart: {e}")
            return self._create_error_message("Engineer Assignment Chart")
    
    def create_case_owner_assignment_chart(self, owner_data: Dict[str, Any]) -> str:
        """
        Create case owner assignment chart with configurable chart type.
        
        Args:
            owner_data: Case owner assignment data
            
        Returns:
            HTML string with chart
        """
        if not owner_data.get('available') or not owner_data.get('case_counts'):
            return self._create_not_available_message("Case Owner Assignment", 
                owner_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES
            
            case_counts = owner_data['case_counts']
            chart_type = CHART_TYPES.get('case_owner_assignment', 'horizontal_bar')
            
            # Sort by case count and get top 15
            sorted_owners = sorted(case_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            owners = [item[0] for item in sorted_owners]
            values = [item[1] for item in sorted_owners]
            
            # Color assignment for case owners
            owner_colors = self.color_assignments.get('case_owner_assignment_colors', {})
            if owner_colors.get('primary'):
                colors = [owner_colors['primary']] * len(owners)
            else:
                colors = [self.chart_colors[0]] * len(owners)
            
            fig = self._create_assignment_chart(
                labels=owners,
                values=values,
                colors=colors,
                chart_type=chart_type,
                title='Cases by Case Owner (Top 15)',
                div_id='case_owner_assignment_chart'
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="case_owner_assignment_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create case owner assignment chart: {e}")
            return self._create_error_message("Case Owner Assignment Chart")

    def create_internal_external_chart(self, internal_data: Dict[str, Any]) -> str:
        """
        Create internal vs external cases chart with configurable chart type.
        
        Args:
            internal_data: Internal vs external analysis data
            
        Returns:
            HTML string with chart
        """
        if not internal_data.get('available') or not internal_data.get('breakdown'):
            return self._create_not_available_message("Internal vs External Cases", 
                internal_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES
            
            breakdown = internal_data['breakdown']
            chart_type = CHART_TYPES.get('internal_external', 'pie')
            
            # Normalize the labels
            normalized_breakdown = {}
            for key, value in breakdown.items():
                if str(key).lower() in ['yes', 'true', '1', 'internal']:
                    normalized_breakdown['Internal'] = value
                else:
                    normalized_breakdown['External'] = value
            
            labels = list(normalized_breakdown.keys())
            values = list(normalized_breakdown.values())
            
            # Use configurable internal/external colors
            ie_colors = self.color_assignments.get('internal_external_colors', {})
            colors = [ie_colors.get(label, self.chart_colors[i % len(self.chart_colors)]) 
                     for i, label in enumerate(labels)]
            
            fig = self._create_distribution_chart(
                labels=labels,
                values=values,
                colors=colors,
                chart_type=chart_type,
                title='Internal vs External Cases',
                div_id='internal_external_chart'
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="internal_external_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create internal vs external chart: {e}")
            return self._create_error_message("Internal vs External Chart")
    
    def create_queue_distribution_chart(self, queue_data: Dict[str, Any]) -> str:
        """
        Create queue distribution chart with configurable chart type.
        
        Args:
            queue_data: Queue analysis data
            
        Returns:
            HTML string with chart
        """
        if not queue_data.get('available') or not queue_data.get('queue_counts'):
            return self._create_not_available_message("Queue Distribution", 
                queue_data.get('reason', 'No data available'))
        
        try:
            from tac_config import CHART_TYPES
            
            queue_counts = queue_data['queue_counts']
            chart_type = CHART_TYPES.get('queue_distribution', 'pie')
            
            labels = list(queue_counts.keys())
            values = list(queue_counts.values())
            colors = self.chart_colors[:len(queue_counts)]
            
            fig = self._create_distribution_chart(
                labels=labels,
                values=values,
                colors=colors,
                chart_type=chart_type,
                title='Cases by Queue',
                div_id='queue_distribution_chart'
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="queue_distribution_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create queue distribution chart: {e}")
            return self._create_error_message("Queue Distribution Chart")
    
    def create_summary_statistics_cards(self, analytics: Dict[str, Any]) -> str:
        """
        Create summary statistics cards.
        
        Args:
            analytics: Complete analytics data
            
        Returns:
            HTML string with statistics cards
        """
        try:
            summary = analytics.get('summary', {})
            
            total_cases = summary.get('total_cases', 0)
            cases_per_month = summary.get('cases_per_month', 0)
            
            # Bug analysis - get total count instead of percentage
            bug_data = analytics.get('bug_analysis', {})
            bug_total = 0
            if bug_data.get('available') and bug_data.get('bug_vs_non_bug'):
                bug_total = bug_data['bug_vs_non_bug'].get('Bug Cases', 0)
            
            cards_html = f"""
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{format_number(total_cases)}</div>
                    <div class="stat-label">Total Cases</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{cases_per_month:.1f}</div>
                    <div class="stat-label">Cases per Month</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{bug_total}</div>
                    <div class="stat-label">Bug-Related Cases</div>
                </div>
            </div>
            """
            
            return cards_html
            
        except Exception as e:
            logger.error(f"Failed to create summary statistics cards: {e}")
            return "<div class='error'>Error creating summary statistics</div>"
    
    def _calculate_trend(self, x: List[float], y: List[float]) -> Tuple[float, float]:
        """Calculate linear trend coefficients."""
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        return intercept, slope
    
    def _get_status_colors(self, statuses: List[str]) -> List[str]:
        """
        Get colors for status values using palette override or explicit colors.
        
        Args:
            statuses: List of status values
            
        Returns:
            List of color codes for each status
        """
        from tac_config import COLOR_PALETTES
        
        # Get status-specific color configurations
        status_colors = self.color_assignments.get('status_colors', {})
        status_palette_name = self.color_assignments.get('status_color_palette')
        
        # Use status-specific palette if specified, otherwise use default
        if status_palette_name and status_palette_name in COLOR_PALETTES:
            status_palette = COLOR_PALETTES[status_palette_name]
        else:
            status_palette = self.chart_colors
        
        colors = []
        for i, status in enumerate(statuses):
            # First check if there's an explicit color defined for this status
            if status in status_colors:
                colors.append(status_colors[status])
            else:
                # Use color from the status palette (cycling through if needed)
                colors.append(status_palette[i % len(status_palette)])
        
        return colors
    
    def _create_not_available_message(self, chart_name: str, reason: str = "Data not available") -> str:
        """Create a not available message for charts."""
        return f"""
        <div class="chart-not-available">
            <h3>{chart_name}</h3>
            <p class="not-available-message">{reason}</p>
        </div>
        """
    
    def _create_error_message(self, chart_name: str) -> str:
        """Create an error message for charts."""
        return f"""
        <div class="chart-error">
            <h3>{chart_name}</h3>
            <p class="error-message">Error generating chart</p>
        </div>
        """