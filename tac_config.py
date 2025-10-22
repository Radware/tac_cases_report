"""
Configuration constants for the TAC Executive Report Generator
"""

# Chart styling constants for Radware branding
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

# Color palette for charts (colorblind friendly)
CHART_COLORS = [
    '#003f7f', '#6cb2eb', '#ff6b35', '#28a745', '#ffc107',
    '#dc3545', '#17a2b8', '#6f42c1', '#e83e8c', '#fd7e14',
    '#20c997', '#6610f2', '#e91e63', '#795548', '#607d8b'
]

# Output format configuration
OUTPUT_FORMATS = ['html', 'pdf']  # Available options: 'html', 'pdf'. Use ['html'] for HTML only, ['pdf'] for PDF only, or ['html', 'pdf'] for both

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

/* Statistics Cards */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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