"""
Configuration constants for the TAC Executive Report Generator

This file contains all user-configurable options for the TAC Executive Report Generator.
Users can modify these settings to customize report appearance and chart types without 
modifying the core code.
"""

# Chart styling constants for Radware branding
# this is needed for UI elements, specifically the header and footer
RADWARE_COLORS = {
    'primary': '#003f7f',      # Radware blue
    'secondary': '#6cb2eb',    # Light blue
    'accent': '#ff6b35',       # Orange accent
    'success': '#28a745',      # Green
    'warning': '#ffc107',      # Yellow
    'danger': '#dc3545',       # Red
    'dark': '#343a40',         # Dark gray
    'light': '#f8f9fa',        # Light gray
    'background': '#ffffff',    # White background
}

# ============================================================================
# COLOR CONFIGURATION - USER CUSTOMIZABLE
# ============================================================================
# Users can easily customize chart colors by changing the color palettes below.
# Colors can be specified as hex codes (#RRGGBB), RGB values, or named colors.

# Color palette options - choose one by setting ACTIVE_COLOR_PALETTE
COLOR_PALETTES = {
    # Radware Corporate (default)
    'radware_corporate': [
        '#003f7f', '#6cb2eb', '#ff6b35', '#28a745', '#ffc107',
        '#dc3545', '#17a2b8', '#6f42c1', '#e83e8c', '#fd7e14',
        '#20c997', '#6610f2', '#e91e63', '#795548', '#607d8b'
    ],
    
    # Professional Blue Theme
    'professional_blue': [
        '#1f4e79',  # Dark blue
        '#2e75b6',  # Medium blue
        '#5b9bd5',  # Standard blue
        '#9fc5e8',  # Light blue
        '#cfe2f3',  # Very light blue
        '#003f7f',  # Radware blue (deep blue)
        '#34495e',  # Slate blue/gray
        '#6cb2eb',  # Soft blue
        '#3a6ea5',  # Steel blue
        '#b4c6e7'   # Pale blue
    ],

    # Modern Minimal
    'modern_minimal': [
        '#2c3e50', '#34495e', '#95a5a6', '#bdc3c7', '#ecf0f1',
        '#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#3498db'
    ],
    
    # Vibrant Corporate
    'vibrant_corporate': [
        '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
        '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#f1c40f'
    ],
    
    # High Contrast (accessibility friendly)
    'high_contrast': [
        '#000000', '#ffffff', '#ff0000', '#00ff00', '#0000ff',
        '#ffff00', '#ff00ff', '#00ffff', '#800000', '#008000'
    ],
    
    # Colorblind Friendly (deuteranopia/protanopia safe)
    'colorblind_friendly': [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
}

# Set the active color palette (change this to switch color schemes)
ACTIVE_COLOR_PALETTE = 'professional_blue'  # Options: 'radware_corporate', 'professional_blue', 'modern_minimal', 'vibrant_corporate', 'high_contrast', 'colorblind_friendly'

# Specific color assignments for chart elements (optional, if need to override automatic colors)
CHART_COLOR_ASSIGNMENTS = {

    # Monthly trends line/area chart colors

    # Option 1: Radware blue theme
    # 'trends_colors': {
    #     'primary': '#003f7f',        # Main trend line color
    #     'area_fill': 'rgba(0, 63, 127, 0.3)'  # Semi-transparent fill
    # },

    # Option 2: Custom green theme

    # 'trends_colors': {
    #     'primary': "#08532D",        # Custom main trend line color
    #     'area_fill': 'rgba(0, 63, 127, 0.3)'  # Semi-transparent fill
    # },

    
    # Severity colors (override automatic colors for severity levels)

    # Severity colors option - Original vibrant colors

    # 'severity_colors': {
    #     '1 - Critical': '#dc3545',    # Red
    #     '2 - High': '#ff6b35',        # Orange
    #     '3 - Medium': '#ffc107',      # Yellow
    #     '4 - Low': '#28a745',         # Green
    # },

    # Severity colors option - all Dark Blue

    # 'severity_colors': {
    #     '1 - Critical': '#003f7f',    # Dark Blue
    #     '2 - High': '#003f7f',        # Dark Blue
    #     '3 - Medium': '#003f7f',      # Dark Blue
    #     '4 - Low': '#003f7f',         # Dark Blue
    # },
    
    # Bug analysis specific colors
    # 'bug_colors': {
    #     'Bug Cases': '#dc3545',      # Red for bugs
    #     'Non-Bug Cases': '#003f7f'   # Dark Blue for non-bugs
    # },

    # # Engineer assignment colors
    # 'engineer_assignment_colors': {
    #     'primary': '#003f7f'   # Dark Blue for engineer assignment bars
    # },

    # # Case owner assignment colors
    # 'case_owner_assignment_colors': {
    #     'primary': '#003f7f'   # Dark Blue for case owner assignment bars
    # },

    # Status distribution colors (optional: override automatic colors for specific status values)
    # Option 1: Use a different color palette for all status values
    # Specify a palette name from COLOR_PALETTES to use different colors than the default
    
    # 'status_color_palette': 'vibrant_corporate',  # Use this palette instead of ACTIVE_COLOR_PALETTE
    
    # Option 2: Override specific status colors (takes priority over palette)
    # Only define colors here for statuses that need specific colors (e.g., Open=red, Closed=green)
    # All other statuses will use the palette specified above
    # 'status_colors': {
    #     'Pending Customer': '#dc3545',           # Red for open cases (high priority)
    #     'Closed': '#28a745',         # Green for closed cases (resolved)
    #     # 'Pending R&D': '#ffc107',  # Yellow - uncomment if you want to override
    #     # All other statuses will use colors from 'status_color_palette' automatically
    # },


    
    # Internal/External colors
    # 'internal_external_colors': {
    #     'Internal': '#003f7f',       # Radware blue for internal
    #     'External': '#6cb2eb'        # Light blue for external
    # },
    

}

# Output format configuration
OUTPUT_FORMATS = ['html']  # Available options: 'html', 'pdf'. Use ['html'] for HTML only, ['pdf'] for PDF only, or ['html', 'pdf'] for both

# ============================================================================
# CHART TYPE CONFIGURATION - USER CUSTOMIZABLE
# ============================================================================
# Users can easily change chart types here to customize report visualizations
# without modifying any code. Simply change the values below to your preferred
# chart type for each visualization.

CHART_TYPES = {
    # Monthly trends chart
    # Options: 'line', 'bar', 'area'
    # - 'line': Traditional line chart with trend line (good for time series)
    # - 'bar': Bar chart showing discrete monthly values (easier to read exact values)
    # - 'area': Area chart with filled region under line (emphasizes volume)
    'monthly_trends': 'bar',
    
    # Distribution charts (for categorical data)
    # Options: 'pie', 'donut', 'bar', 'horizontal_bar'
    # - 'pie': Traditional pie chart (good for showing proportions)
    # - 'donut': Pie chart with center hole (modern look, easier to read labels)
    # - 'bar': Vertical bar chart (easier to compare exact values)
    # - 'horizontal_bar': Horizontal bar chart (better for long category names)
    'severity_distribution': 'pie',
    'product_hierarchy': 'pie',
    'bug_analysis': 'pie',
    'internal_external': 'pie',
    'queue_distribution': 'pie',
    'status_distribution': 'pie',

    # Assignment charts (for ranking/comparison data)
    # Options: 'bar', 'horizontal_bar'
    # - 'bar': Vertical bars (good for rankings)
    # - 'horizontal_bar': Horizontal bars (better for names/labels)
    'engineer_assignment': 'horizontal_bar',
    'case_owner_assignment': 'horizontal_bar',
}

# Advanced chart styling options
# Users can modify these to fine-tune chart appearance
CHART_STYLES = {
    'monthly_trends': {
        'line': {
            'mode': 'lines+markers',
            'line_width': 3,
            'marker_size': 8,
            'show_trend': True  # Show trend line for line charts
        },
        'bar': {
            'show_values': True,  # Show values on bars
            'show_trend': False,  # No trend line for bar charts
            'bar_width': 0.6
        },
        'area': {
            'fill': 'tonexty',
            'line_width': 2,
            'show_trend': True
        }
    },
    'distribution_charts': {
        'pie': {
            'hole': 0,  # 0 for full pie (no hole), 0.3+ for donut
            'textinfo': 'label+value',  # Show labels and values
            'textposition': 'outside'
        },
        'donut': {
            'hole': 0.5,  # Larger hole for donut
            'textinfo': 'label+value',
            'textposition': 'outside'
        },
        'bar': {
            'orientation': 'vertical',
            'show_values': True
        },
        'horizontal_bar': {
            'orientation': 'horizontal', 
            'show_values': True
        }
    },
    'assignment_charts': {
        'bar': {
            'orientation': 'vertical',
            'show_values': True,
            'sort_values': 'descending'  # 'ascending', 'descending', 'none'
        },
        'horizontal_bar': {
            'orientation': 'horizontal',
            'show_values': True,
            'sort_values': 'descending'
        }
    }
}

# Chart configuration
CHART_CONFIG = {
    'displayModeBar': True,
    'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'autoScale2d'],
    'displaylogo': False,
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'chart',
        'height': 600,
        'width': 800,
        'scale': 2
    }
}

CHART_LAYOUT = {
    'font': {'family': 'Arial, sans-serif', 'size': 12},
    'paper_bgcolor': 'white',
    'plot_bgcolor': 'white'
}

CHART_PLOTLYJS_MODE = 'cdn'  # Options: 'cdn', 'inline', 'directory'

# Report CSS styling
REPORT_CSS = """
<style>
/* TAC Executive Report Styling */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
    min-height: 100vh;
}

.header {
    background: linear-gradient(135deg, #003f7f 0%, #6cb2eb 100%);
    color: white;
    padding: 40px;
    text-align: center;
}

.header h1 {
    margin: 0 0 10px 0;
    font-size: 2.5em;
    font-weight: 300;
}

.subtitle {
    font-size: 1.2em;
    margin: 10px 0;
    opacity: 0.9;
}

.generation-info {
    font-size: 0.9em;
    opacity: 0.8;
    margin: 10px 0 0 0;
}

.content {
    padding: 40px;
}

.section {
    margin-bottom: 50px;
    background: white;
    border-radius: 8px;
    overflow: hidden;
}

.section h2 {
    color: #003f7f;
    border-bottom: 3px solid #003f7f;
    padding-bottom: 10px;
    margin-bottom: 25px;
    font-size: 1.8em;
    font-weight: 400;
}

.section h3 {
    color: #003f7f;
    margin-top: 30px;
    margin-bottom: 15px;
    font-size: 1.3em;
}

.executive-summary {
    background: #f8f9fa;
    padding: 30px;
    border-left: 5px solid #003f7f;
    margin: 20px 0;
    border-radius: 0 8px 8px 0;
}

.executive-summary h3 {
    color: #003f7f;
    margin-top: 20px;
}

.executive-summary ul {
    list-style-type: none;
    padding-left: 0;
}

.executive-summary li {
    padding: 8px 0;
    border-bottom: 1px solid #e9ecef;
}

.executive-summary li:last-child {
    border-bottom: none;
}

# Statistics Cards */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
    margin: 30px 0;
}

.stat-card {
    background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0,63,127,0.1);
    border: 1px solid #e9ecef;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,63,127,0.15);
}

.stat-number {
    font-size: 2.8em;
    font-weight: 700;
    color: #003f7f;
    margin-bottom: 10px;
    line-height: 1;
}

.stat-label {
    color: #666;
    font-size: 1em;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Chart containers */
.chart-container {
    margin: 30px 0;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid #e9ecef;
}

.chart-description {
    margin-top: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 6px;
    font-style: italic;
    color: #666;
    border-left: 4px solid #6cb2eb;
}

/* Chart not available styling */
.chart-not-available, .chart-error {
    text-align: center;
    padding: 40px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 2px dashed #dee2e6;
    margin: 20px 0;
}

.chart-not-available h3, .chart-error h3 {
    color: #6c757d;
    margin-bottom: 10px;
}

.not-available-message, .error-message {
    color: #6c757d;
    font-style: italic;
}

/* Data summary table */
.data-summary {
    margin: 20px 0;
}

.summary-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.summary-table td {
    padding: 15px;
    border-bottom: 1px solid #e9ecef;
}

.summary-table td:first-child {
    background: #f8f9fa;
    font-weight: 600;
    color: #003f7f;
    width: 30%;
}

.summary-table tr:last-child td {
    border-bottom: none;
}

/* Footer */
.footer {
    background: #003f7f;
    color: white;
    text-align: center;
    padding: 30px;
    margin-top: 50px;
}

.footer p {
    margin: 5px 0;
    opacity: 0.9;
}

/* Warning and error messages */
.warning {
    background: #fff3cd;
    color: #856404;
    padding: 15px;
    border-radius: 6px;
    border: 1px solid #ffeaa7;
    margin: 20px 0;
}

.error {
    background: #f8d7da;
    color: #721c24;
    padding: 15px;
    border-radius: 6px;
    border: 1px solid #f5c6cb;
    margin: 20px 0;
}

/* Responsive design */
@media (max-width: 768px) {
    .container {
        margin: 0;
        box-shadow: none;
    }
    
    .header {
        padding: 20px;
    }
    
    .header h1 {
        font-size: 2em;
    }
    
    .content {
        padding: 20px;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }
    
    .stat-card {
        padding: 20px;
    }
    
    .stat-number {
        font-size: 2.2em;
    }
}

/* Print styles */
@media print {
    .container {
        box-shadow: none;
        max-width: none;
    }
    
    .header {
        background: #003f7f !important;
        -webkit-print-color-adjust: exact;
        color-adjust: exact;
    }
    
    .section {
        page-break-inside: avoid;
    }
    
    .chart-container {
        page-break-inside: avoid;
    }
}
</style>
"""