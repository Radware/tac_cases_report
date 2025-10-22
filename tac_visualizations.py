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
    RADWARE_COLORS, CHART_COLORS, CHART_CONFIG, CHART_LAYOUT,
    CHART_PLOTLYJS_MODE
)
from tac_utils import format_number, calculate_percentage

logger = logging.getLogger(__name__)


class TACVisualizer:
    """
    Creates interactive visualizations for TAC case analysis.
    """
    
    def __init__(self):
        """Initialize the visualizer with Radware styling."""
        self.colors = RADWARE_COLORS
        self.chart_colors = CHART_COLORS
        
        # Common layout settings
        self.common_layout = {
            'font': {'family': 'Arial, sans-serif', 'size': 12},
            'paper_bgcolor': 'white',
            'plot_bgcolor': 'white',
            'margin': {'l': 50, 'r': 50, 't': 80, 'b': 50}
        }
        
        logger.info("Initialized TAC Visualizer")
    
    def create_monthly_cases_chart(self, monthly_data: Dict[str, Any]) -> str:
        """
        Create monthly case volume trend chart.
        
        Args:
            monthly_data: Monthly trends data
            
        Returns:
            HTML string with chart
        """
        if not monthly_data.get('available') or not monthly_data.get('monthly_counts'):
            return self._create_not_available_message("Monthly Trends", 
                monthly_data.get('reason', 'No data available'))
        
        try:
            monthly_counts = monthly_data['monthly_counts']
            
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
            
            # Add line chart
            fig.add_trace(go.Scatter(
                x=month_labels,
                y=values,
                mode='lines+markers',
                name='Cases Created',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8, color=self.colors['primary']),
                hovertemplate='<b>%{x}</b><br>Cases: %{y}<extra></extra>'
            ))
            
            # Add trend line if more than 2 data points
            if len(values) > 2:
                # Simple linear trend
                x_numeric = list(range(len(values)))
                z = self._calculate_trend(x_numeric, values)
                trend_y = [z[0] + z[1] * x for x in x_numeric]
                
                fig.add_trace(go.Scatter(
                    x=month_labels,
                    y=trend_y,
                    mode='lines',
                    name='Trend',
                    line=dict(color=self.colors['accent'], width=2, dash='dash'),
                    hovertemplate='Trend: %{y:.1f}<extra></extra>'
                ))
            
            fig.update_layout(
                title='TAC Cases Created by Month',
                xaxis_title='Month',
                yaxis_title='Number of Cases',
                yaxis=dict(rangemode='tozero'),  # Start y-axis from 0
                **self.common_layout
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="monthly_cases_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create monthly cases chart: {e}")
            return self._create_error_message("Monthly Cases Chart")
    
    def create_severity_distribution_chart(self, severity_data: Dict[str, Any]) -> str:
        """
        Create severity distribution pie chart.
        
        Args:
            severity_data: Severity analysis data
            
        Returns:
            HTML string with chart
        """
        if not severity_data.get('available') or not severity_data.get('counts'):
            return self._create_not_available_message("Severity Distribution", 
                severity_data.get('reason', 'No data available'))
        
        try:
            counts = severity_data['counts']
            
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
            
            # Color mapping for severities
            severity_colors = {
                '1 - Critical': self.colors['danger'],
                '2 - High': self.colors['warning'],
                '3 - Medium': self.colors['secondary'],
                '4 - Low': self.colors['success']
            }
            
            colors = [severity_colors.get(sev, self.chart_colors[i % len(self.chart_colors)]) 
                     for i, sev in enumerate(sorted_severities)]
            
            fig = go.Figure(data=[go.Pie(
                labels=sorted_severities,
                values=sorted_values,
                hole=0.3,
                marker_colors=colors,
                textinfo='label+value',  # Show label and count instead of percentage
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>Cases: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Case Distribution by Severity',
                **self.common_layout
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="severity_distribution_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create severity distribution chart: {e}")
            return self._create_error_message("Severity Distribution Chart")
    
    def create_product_hierarchy_chart(self, product_data: Dict[str, Any]) -> str:
        """
        Create product hierarchy distribution chart.
        
        Args:
            product_data: Product analysis data
            
        Returns:
            HTML string with chart
        """
        if not product_data.get('available') or not product_data.get('product_counts'):
            return self._create_not_available_message("Product Distribution", 
                product_data.get('reason', 'No data available'))
        
        try:
            product_counts = product_data['product_counts']
            
            # Sort by count (descending)
            sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)
            products = [item[0] for item in sorted_products]
            values = [item[1] for item in sorted_products]
            
            # Take top 10 products if more than 10
            if len(products) > 10:
                products = products[:10]
                values = values[:10]
            
            fig = go.Figure(data=[go.Bar(
                x=values,
                y=products,
                orientation='h',
                marker_color=self.colors['primary'],
                hovertemplate='<b>%{y}</b><br>Cases: %{x}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Cases by Product Hierarchy',
                xaxis_title='Number of Cases',
                yaxis_title='Product',
                **self.common_layout
            )
            
            # Reverse y-axis to show highest at top
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
        Create bug vs non-bug analysis chart.
        
        Args:
            bug_data: Bug analysis data
            
        Returns:
            HTML string with chart
        """
        if not bug_data.get('available') or not bug_data.get('bug_vs_non_bug'):
            return self._create_not_available_message("Bug Analysis", 
                bug_data.get('reason', 'No data available'))
        
        try:
            bug_vs_non_bug = bug_data['bug_vs_non_bug']
            
            # Create subplot with pie chart and bug types
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Bug vs Non-Bug Cases', 'Bug Types Distribution'),
                specs=[[{'type': 'pie'}, {'type': 'pie'}]]
            )
            
            # Bug vs Non-Bug pie chart
            fig.add_trace(
                go.Pie(
                    labels=list(bug_vs_non_bug.keys()),
                    values=list(bug_vs_non_bug.values()),
                    hole=0.3,
                    marker_colors=[self.colors['danger'], self.colors['success']],
                    textinfo='label+value',  # Show label and count instead of percentage
                    hovertemplate='<b>%{label}</b><br>Cases: %{value}<br>Percentage: %{percent}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Bug types distribution
            if bug_data.get('bug_types'):
                bug_types = bug_data['bug_types']
                fig.add_trace(
                    go.Pie(
                        labels=list(bug_types.keys()),
                        values=list(bug_types.values()),
                        hole=0.3,
                        marker_colors=self.chart_colors[:len(bug_types)],
                        textinfo='label+value',  # Show label and count instead of percentage
                        hovertemplate='<b>%{label}</b><br>Cases: %{value}<br>Percentage: %{percent}<extra></extra>'
                    ),
                    row=1, col=2
                )
            
            fig.update_layout(
                title='Bug Analysis Overview',
                **self.common_layout
            )
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="bug_analysis_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create bug analysis chart: {e}")
            return self._create_error_message("Bug Analysis Chart")
    
    def create_engineer_performance_chart(self, engineer_data: Dict[str, Any]) -> str:
        """
        Create engineer performance chart.
        
        Args:
            engineer_data: Engineer performance data
            
        Returns:
            HTML string with chart
        """
        if not engineer_data.get('available') or not engineer_data.get('case_counts'):
            return self._create_not_available_message("Engineer Performance", 
                engineer_data.get('reason', 'No data available'))
        
        try:
            case_counts = engineer_data['case_counts']
            
            # Sort by case count (descending) and take top 15
            sorted_engineers = sorted(case_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            engineers = [item[0] for item in sorted_engineers]
            values = [item[1] for item in sorted_engineers]
            
            fig = go.Figure(data=[go.Bar(
                x=values,
                y=engineers,
                orientation='h',
                marker_color=self.colors['secondary'],
                hovertemplate='<b>%{y}</b><br>Cases: %{x}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Cases by Assigned Engineer (Top 15)',
                xaxis_title='Number of Cases',
                yaxis_title='Engineer',
                **self.common_layout
            )
            
            # Reverse y-axis to show highest at top
            fig.update_yaxes(autorange="reversed")
            
            return fig.to_html(
                include_plotlyjs=CHART_PLOTLYJS_MODE,
                div_id="engineer_performance_chart",
                config=CHART_CONFIG
            )
            
        except Exception as e:
            logger.error(f"Failed to create engineer performance chart: {e}")
            return self._create_error_message("Engineer Performance Chart")
    
    def create_internal_external_chart(self, internal_data: Dict[str, Any]) -> str:
        """
        Create internal vs external cases chart.
        
        Args:
            internal_data: Internal vs external analysis data
            
        Returns:
            HTML string with chart
        """
        if not internal_data.get('available') or not internal_data.get('breakdown'):
            return self._create_not_available_message("Internal vs External Cases", 
                internal_data.get('reason', 'No data available'))
        
        try:
            breakdown = internal_data['breakdown']
            
            # Normalize the labels
            normalized_breakdown = {}
            for key, value in breakdown.items():
                if str(key).lower() in ['yes', 'true', '1', 'internal']:
                    normalized_breakdown['Internal'] = value
                else:
                    normalized_breakdown['External'] = value
            
            fig = go.Figure(data=[go.Pie(
                labels=list(normalized_breakdown.keys()),
                values=list(normalized_breakdown.values()),
                hole=0.3,
                marker_colors=[self.colors['warning'], self.colors['primary']],
                textinfo='label+value',  # Show label and count instead of percentage
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>Cases: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Internal vs External Cases',
                **self.common_layout
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
        Create queue distribution chart.
        
        Args:
            queue_data: Queue analysis data
            
        Returns:
            HTML string with chart
        """
        if not queue_data.get('available') or not queue_data.get('queue_counts'):
            return self._create_not_available_message("Queue Distribution", 
                queue_data.get('reason', 'No data available'))
        
        try:
            queue_counts = queue_data['queue_counts']
            
            fig = go.Figure(data=[go.Pie(
                labels=list(queue_counts.keys()),
                values=list(queue_counts.values()),
                hole=0.3,
                marker_colors=self.chart_colors[:len(queue_counts)],
                textinfo='label+value',  # Show label and count instead of percentage
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>Cases: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Cases by Queue',
                **self.common_layout
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