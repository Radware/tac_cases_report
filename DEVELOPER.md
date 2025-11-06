# TAC Executive Report Generator - Developer Documentation

## 📚 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Execution Flow](#execution-flow)
3. [Module Breakdown](#module-breakdown)
4. [Configuration System](#configuration-system)
5. [Adding New Charts - Step-by-Step Guide](#adding-new-charts---step-by-step-guide)
6. [Data Processing Pipeline](#data-processing-pipeline)
7. [Extending the System](#extending-the-system)
8. [Troubleshooting Guide](#troubleshooting-guide)

---

## Architecture Overview

### System Design Philosophy
The TAC Executive Report Generator follows a **modular pipeline architecture** with clear separation of concerns:

```
Input (CSV/Excel) → Data Processing → Analytics → Visualization → Report Generation → Output (HTML/PDF)
```

### Core Modules

```
tac_analyzer.py (Orchestrator)
    ↓
    ├─→ tac_data_processor.py (Data Processing & Analytics)
    │       ↓
    │       └─→ tac_utils.py (Helper Functions)
    │
    ├─→ tac_visualizations.py (Chart Generation)
    │       ↓
    │       └─→ tac_config.py (Configuration)
    │
    └─→ tac_report_generator.py (Report Assembly)
            ↓
            └─→ tac_config.py (Styling & Layout)
```

### Key Design Patterns
- **Pipeline Pattern**: Data flows through sequential stages
- **Strategy Pattern**: Configurable chart types and color palettes
- **Template Pattern**: Consistent chart creation methods
- **Facade Pattern**: Simple external API hiding complex internals

---

## Execution Flow

### High-Level Process Flow

```
1. START: tac_analyzer.py main()
   ↓
2. Parse CLI arguments (input/output directories, formats, verbose)
   ↓
3. Initialize TACAnalyzer
   ├─ Create output directories
   ├─ Setup logging
   └─ Initialize TACReportGenerator
   ↓
4. Discover input files (.csv, .xlsx, .xls)
   ↓
5. FOR EACH input file:
   │
   ├─→ 5.1: Validate file (exists, readable, non-zero size)
   │
   ├─→ 5.2: Initialize TACDataProcessor
   │     ├─ Detect file type (CSV vs Excel)
   │     ├─ Load file with encoding detection
   │     ├─ Map columns to expected schema
   │     └─ Validate essential columns exist
   │
   ├─→ 5.3: Process Analytics
   │     ├─ Summary metrics (total cases, date range, velocity)
   │     ├─ Monthly trends analysis
   │     ├─ Severity distribution
   │     ├─ Product hierarchy breakdown
   │     ├─ Bug analysis (identification & categorization)
   │     ├─ Engineer/Owner assignments
   │     ├─ Status distribution
   │     ├─ Internal vs External analysis
   │     ├─ Queue distribution
   │     ├─ Escalation analysis
   │     ├─ Category analysis
   │     └─ Resolution analysis
   │
   ├─→ 5.4: Generate Visualizations
   │     ├─ Initialize TACVisualizer
   │     ├─ Load color palette from config
   │     ├─ Create charts (Plotly figures)
   │     └─ Convert to HTML strings
   │
   ├─→ 5.5: Generate Reports
   │     ├─ Create executive summary
   │     ├─ Build table of contents
   │     ├─ Assemble HTML report
   │     └─ [Optional] Convert to PDF via Playwright
   │
   └─→ 5.6: Record results
   ↓
6. Generate batch summary report (if multiple files)
   ↓
7. Display results and exit
```

### Detailed Stage Breakdown

#### Stage 1: File Discovery & Validation
**Location**: `tac_analyzer.py` → `discover_input_files()`, `validate_input_file()`

```python
# Discovery Process
1. Scan input_dir for files matching: *.csv, *.xlsx, *.xls
2. Remove duplicates and sort alphabetically
3. For each file:
   - Check existence
   - Verify it's a file (not directory)
   - Check size (warn if > 100MB, error if 0)
4. Return list of valid file paths
```

#### Stage 2: Data Loading
**Location**: `tac_data_processor.py` → `load_and_analyze()`

```python
# CSV Loading (_load_csv_file)
1. Detect encoding using chardet library
   - Read first 50KB sample
   - Test detected encoding
   - Fallback to utf-8, cp1252, iso-8859-1 if needed
2. Check for title row (common in exports)
   - First line might be "Open Cases All" instead of headers
   - Skip title row if detected
3. Load with pandas.read_csv()
4. Remove footer rows (like "Record Count: 18")
5. Return DataFrame

# Excel Loading (_load_excel_file)
1. Read first 3 rows to detect structure
2. Check if first row is title (Unnamed columns)
3. Skip title row if detected
4. Load with pandas.read_excel()
5. Remove footer rows
6. Return DataFrame
```

#### Stage 3: Column Mapping
**Location**: `tac_data_processor.py` → `_create_column_mapping()`

```python
# Intelligent Column Mapping
1. Define expected columns and their variants:
   Expected: 'reference'
   Variants: ['Reference #', 'Reference', 'Case #', 'Case Number', 'Ticket #']

2. For each expected column:
   - Try exact match with variants (case-insensitive)
   - If found, map: column_mapping['reference'] = 'Reference #'
   - If not found, try alternative matching:
     * For 'reference': look for words like 'case', 'ticket', 'ref', '#'
     * For 'status': look for 'status', 'state'
     * For 'date_created': look for 'date', 'created', 'open'

3. Store mapping for use in analytics
   Example: {'reference': 'Reference #', 'status': 'Status', ...}
```

#### Stage 4: Data Cleaning
**Location**: `tac_data_processor.py` → `_clean_data()`

```python
# Cleaning Operations
1. Clean text columns:
   - Convert to string
   - Strip whitespace
   - Replace 'nan', 'None', 'null' with 'N/A'

2. Standardize severity values:
   - Map variations to standard format
   - '1' or 'critical' → '1 - Critical'
   - '2' or 'high' → '2 - High'
   - etc.

3. Parse and validate dates
```

#### Stage 5: Analytics Processing
**Location**: `tac_data_processor.py` → `process_executive_analytics()`

Each analytics method follows this pattern:
```python
def _get_<metric>_analysis(self) -> Dict[str, Any]:
    # 1. Check if required columns exist
    if 'required_column' not in self.column_mapping:
        return {'available': False, 'reason': 'Missing column'}
    
    # 2. Extract data
    column = self.column_mapping['required_column']
    data = self.data[column]
    
    # 3. Process and aggregate
    counts = data.value_counts().to_dict()
    
    # 4. Calculate additional metrics
    percentages = calculate_percentages(counts)
    
    # 5. Return structured result
    return {
        'available': True,
        'counts': counts,
        'percentages': percentages
    }
```

#### Stage 6: Visualization
**Location**: `tac_visualizations.py` → `create_*_chart()` methods

```python
# Chart Creation Pipeline
1. Check data availability
   if not data.get('available'):
       return error_message

2. Load configuration
   - Chart type (pie, bar, line, etc.) from CHART_TYPES
   - Color palette from CHART_COLOR_ASSIGNMENTS
   - Styling options from CHART_STYLES

3. Prepare data
   - Extract labels and values
   - Sort as needed
   - Apply color mapping

4. Create Plotly figure
   - Use configured chart type
   - Apply styling
   - Add interactivity

5. Return HTML string
   - Convert figure.to_html()
   - Include Plotly.js (CDN or inline)
```

#### Stage 7: Report Assembly
**Location**: `tac_report_generator.py` → `_generate_html_report()`

```python
# HTML Report Construction
1. Generate all charts
   - Call visualizer for each metric
   - Store HTML strings in dictionary

2. Create executive summary
   - Extract key findings
   - Format as HTML section

3. Build table of contents
   - List all available sections
   - Create navigation links

4. Assemble HTML document
   - Add CSS from REPORT_CSS
   - Insert header with title
   - Add TOC
   - Add executive summary
   - Add metrics cards
   - Add all chart sections
   - Add footer

5. Write to file
```

#### Stage 8: PDF Generation (Optional)
**Location**: `tac_report_generator.py` → `_generate_pdf_report()`

```python
# PDF Generation via Playwright
1. Generate PDF-optimized HTML
   - Use smaller chart dimensions
   - Adjust margins for print
   - Compact layouts (e.g., side-by-side bug charts)

2. Launch Playwright browser
   - Use Chromium engine
   - Load HTML file

3. Wait for rendering
   - Wait for network idle (charts loaded)
   - Additional 3s for Plotly rendering

4. Generate PDF
   - A4 format
   - 1" margins
   - Print background graphics

5. Clean up temporary HTML
```

---

## Module Breakdown

### 1. tac_analyzer.py (Main Orchestrator)

**Purpose**: CLI interface and workflow coordination

**Key Classes**:
- `TACAnalyzer`: Main orchestrator class

**Key Methods**:
```python
def __init__(input_dir, output_dir, verbose):
    """Initialize directories and components"""

def discover_input_files() -> List[Path]:
    """Find all CSV/Excel files in input directory"""

def validate_input_file(file_path) -> bool:
    """Check file is accessible and valid"""

def process_single_file(file_path, formats) -> Dict:
    """Process one file through entire pipeline"""

def process_all_files(formats) -> Dict:
    """Batch process all discovered files"""

def generate_batch_summary_report(batch_results) -> Path:
    """Create summary HTML for batch processing"""
```

**CLI Arguments**:
- `--input-dir`: Input directory (default: `input_data`)
- `--output-dir`: Output directory (default: `reports`)
- `--format`: Output format(s) - html, pdf, or both
- `--verbose`: Enable debug logging

### 2. tac_data_processor.py (Data Processing)

**Purpose**: Load, clean, and analyze TAC case data

**Key Classes**:
- `TACDataProcessor`: Handles all data operations

**Key Methods**:
```python
def load_and_analyze() -> Dict:
    """Load file and create column mapping"""
    - Calls _load_csv_file() or _load_excel_file()
    - Calls _create_column_mapping()
    - Calls _validate_columns()
    - Calls _clean_data()

def process_executive_analytics() -> Dict:
    """Generate all analytics metrics"""
    Returns: {
        'summary': {...},
        'monthly_trends': {...},
        'severity_analysis': {...},
        'product_analysis': {...},
        'bug_analysis': {...},
        'engineer_assignment': {...},
        'case_owner_assignment': {...},
        'status_analysis': {...},
        'internal_vs_external': {...},
        'queue_analysis': {...},
        'escalation': {...},
        'category_analysis': {...},
        'resolution_analysis': {...}
    }

def _get_<metric>_analysis() -> Dict:
    """Individual analysis methods"""
    - Check column availability
    - Extract and process data
    - Return structured results
```

**Column Mapping Schema**:
```python
expected_columns = {
    'reference': ['Reference #', 'Reference', 'Case #', ...],
    'subject': ['Subject', 'Title', 'Summary', ...],
    'status': ['Status', 'Case Status', 'State'],
    'date_created': ['Date Created', 'Created Date', ...],
    'severity': ['Severity', 'Priority', 'Urgency'],
    'product_hierarchy': ['Product Hierarchy', 'Product', ...],
    'experienced_bug': ['Experienced Bug', 'Known Bug', ...],
    'assigned_account': ['Assigned Account', 'Assigned Engineer', ...],
    'full_name': ['Full Name', 'Name', 'Engineer Name'],
    'queue': ['Queue', 'Team', 'Group'],
    'internal_case': ['Internal Case', 'Internal', ...],
    'jira_case': ['Jira Case', 'Jira', 'Jira Ticket'],
    'category': ['Category', 'Case Category', ...],
    'resolution_code_1': ['Resolution Code 1', ...]
}
```

### 3. tac_visualizations.py (Chart Generation)

**Purpose**: Create interactive Plotly charts

**Key Classes**:
- `TACVisualizer`: Chart factory class

**Key Methods**:
```python
def __init__(output_format='html'):
    """Initialize with format-specific settings"""
    - Load color palette from config
    - Load PDF dimensions if needed

def create_<chart_name>_chart(data) -> str:
    """Chart creation methods"""
    Available charts:
    - create_monthly_cases_chart()
    - create_severity_distribution_chart()
    - create_status_distribution_chart()
    - create_product_hierarchy_chart()
    - create_bug_analysis_chart()
    - create_engineer_assignment_chart()
    - create_case_owner_assignment_chart()
    - create_internal_external_chart()
    - create_queue_distribution_chart()
    - create_escalation_chart()
    - create_category_chart()
    - create_resolution_chart()
    - create_summary_statistics_cards()

def _create_distribution_chart(labels, values, colors, chart_type, title, div_id):
    """Generic distribution chart creator"""
    - Supports: pie, donut, bar, horizontal_bar
    - Applies styling from config
    - Returns Plotly figure

def _create_assignment_chart(labels, values, colors, chart_type, title, div_id):
    """Generic assignment/ranking chart creator"""
    - Supports: bar, horizontal_bar
    - Auto-sorts by value
    - Returns Plotly figure
```

**Chart Type Configuration**:
Charts read their type from `tac_config.py`:
```python
CHART_TYPES = {
    'monthly_trends': 'bar',  # or 'line', 'area'
    'severity_distribution': 'pie',  # or 'donut', 'bar', 'horizontal_bar'
    'product_hierarchy': 'pie',
    'bug_analysis': 'pie',
    # ... etc
}
```

### 4. tac_report_generator.py (Report Assembly)

**Purpose**: Generate HTML and PDF reports

**Key Classes**:
- `TACReportGenerator`: Report assembly coordinator

**Key Methods**:
```python
def generate_reports(input_filename, analytics, file_analysis, formats) -> Dict[str, Path]:
    """Main report generation method"""
    - Generates HTML report
    - Optionally generates PDF
    - Returns paths to generated files

def _generate_html_report(base_name, analytics, file_analysis, output_format) -> Path:
    """Create HTML report"""
    - Generate all charts
    - Create executive summary
    - Build table of contents
    - Assemble HTML
    - Write file

def _generate_all_charts(analytics, visualizer) -> Dict[str, str]:
    """Generate all chart HTML strings"""

def _create_executive_summary(analytics) -> str:
    """Generate executive summary section"""

def _create_table_of_contents(analytics) -> str:
    """Build interactive TOC with navigation"""

def _create_bug_cases_table(analytics) -> str:
    """Create detailed bug cases table"""

def _create_html_content(...) -> str:
    """Assemble complete HTML document"""

def _generate_pdf_report(html_path, base_name) -> Path:
    """Convert HTML to PDF using Playwright"""
```

### 5. tac_config.py (Configuration)

**Purpose**: Centralized configuration for colors, styling, and chart types

**Key Sections**:

```python
# Output Formats
OUTPUT_FORMATS = ['html']  # or ['pdf'] or ['html', 'pdf']

# Color Palettes
COLOR_PALETTES = {
    'radware_corporate': ['#003f7f', '#6cb2eb', ...],
    'professional_blue': ['#1f4e79', '#2e75b6', ...],
    'modern_minimal': [...],
    'vibrant_corporate': [...],
    'high_contrast': [...],
    'colorblind_friendly': [...]
}
ACTIVE_COLOR_PALETTE = 'professional_blue'

# Chart-Specific Colors (Optional Overrides)
CHART_COLOR_ASSIGNMENTS = {
    'severity_colors': {
        'Critical': '#dc3545',
        'High': '#ff6b35',
        ...
    },
    'bug_colors': {...},
    'status_colors': {...},
    # ... etc
}

# Chart Types
CHART_TYPES = {
    'monthly_trends': 'bar',
    'severity_distribution': 'pie',
    ...
}

# Chart Styling
CHART_STYLES = {
    'monthly_trends': {
        'bar': {'show_values': True, 'bar_width': 0.6},
        'line': {'line_width': 3, 'marker_size': 8},
        ...
    },
    'distribution_charts': {...},
    'assignment_charts': {...}
}

# PDF Configuration
PDF_CHART_DIMENSIONS = {
    'standard_chart': {'width': 550, 'height': 400},
    'bug_analysis_chart': {'width': 500, 'height': 450},
    ...
}

# Report CSS
REPORT_CSS = """<style>...</style>"""
```

### 6. tac_utils.py (Utilities)

**Purpose**: Helper functions for common operations

**Key Functions**:
```python
def detect_file_encoding(file_path) -> str:
    """Detect CSV/Excel encoding using chardet"""

def parse_date_flexible(date_str) -> Optional[datetime]:
    """Parse dates with multiple format attempts"""

def format_number(number) -> str:
    """Format numbers with commas (1000 → 1,000)"""

def clean_text(text) -> str:
    """Clean and normalize text (handle nulls, whitespace)"""

def normalize_severity(severity) -> str:
    """Standardize severity values ('1' → '1 - Critical')"""

def setup_logging(verbose) -> None:
    """Configure logging system"""

def format_duration(seconds) -> str:
    """Human-readable duration (3661.5 → '1.0 hours')"""

def clean_filename(filename) -> str:
    """Remove invalid characters for file creation"""
```

---

## Configuration System

### How Configuration Works

1. **Centralized in tac_config.py**: All user-customizable settings
2. **Imported by modules**: Each module imports what it needs
3. **Runtime evaluation**: Configuration read at runtime, no hardcoding

### Configuration Hierarchy

```
User edits tac_config.py
    ↓
Modules import config values at startup
    ↓
Visualizer applies colors/styles when creating charts
    ↓
Report generator uses layout settings for HTML/PDF
```

### Color Assignment Priority

When assigning colors to chart elements:

```
1. Explicit color assignment (highest priority)
   CHART_COLOR_ASSIGNMENTS = {
       'severity_colors': {'Critical': '#dc3545'}
   }

2. Alternative palette for specific chart
   CHART_COLOR_ASSIGNMENTS = {
       'status_color_palette': 'vibrant_corporate'
   }

3. Active color palette (default)
   ACTIVE_COLOR_PALETTE = 'professional_blue'
   
4. Fallback to radware_corporate
```

### Example: Adding a New Color Palette

```python
# In tac_config.py

# 1. Add to COLOR_PALETTES dictionary
COLOR_PALETTES = {
    'my_custom_palette': [
        '#ff0000',  # Red
        '#00ff00',  # Green
        '#0000ff',  # Blue
        '#ffff00',  # Yellow
        '#ff00ff',  # Magenta
        '#00ffff'   # Cyan
    ]
}

# 2. Activate it
ACTIVE_COLOR_PALETTE = 'my_custom_palette'

# 3. [Optional] Override specific charts
CHART_COLOR_ASSIGNMENTS = {
    'severity_color_palette': 'my_custom_palette',
    # Or explicit colors:
    'severity_colors': {
        'Critical': '#ff0000',
        'High': '#ff6600',
        'Medium': '#ffcc00',
        'Low': '#00ff00'
    }
}
```

---

## Adding New Charts - Step-by-Step Guide

### Scenario: Adding a "Response Time Distribution" Chart

This guide walks through creating a completely new chart from scratch.

### Step 1: Add Analytics Method (tac_data_processor.py)

**Location**: Add new method in `TACDataProcessor` class

```python
def _get_response_time_distribution_analysis(self) -> Dict[str, Any]:
    """
    Analyze response time distribution in buckets.
    
    Returns:
        Dictionary with response time distribution data
    """
    # Check if required columns exist
    if 'date_created' not in self.column_mapping or 'date_responded' not in self.column_mapping:
        return {
            'available': False,
            'reason': 'Missing date columns for response time analysis'
        }
    
    created_col = self.column_mapping['date_created']
    responded_col = self.column_mapping['date_responded']
    
    # Define response time buckets (in hours)
    buckets = {
        '< 1 hour': 0,
        '1-4 hours': 0,
        '4-24 hours': 0,
        '1-3 days': 0,
        '3-7 days': 0,
        '> 7 days': 0
    }
    
    # Calculate response times
    for _, row in self.data.iterrows():
        created_str = str(row.get(created_col, ''))
        responded_str = str(row.get(responded_col, ''))
        
        if created_str and responded_str and created_str != 'nan' and responded_str != 'nan':
            created_date = parse_date_flexible(created_str)
            responded_date = parse_date_flexible(responded_str)
            
            if created_date and responded_date and responded_date > created_date:
                response_time_hours = (responded_date - created_date).total_seconds() / 3600
                
                # Categorize into buckets
                if response_time_hours < 1:
                    buckets['< 1 hour'] += 1
                elif response_time_hours < 4:
                    buckets['1-4 hours'] += 1
                elif response_time_hours < 24:
                    buckets['4-24 hours'] += 1
                elif response_time_hours < 72:
                    buckets['1-3 days'] += 1
                elif response_time_hours < 168:
                    buckets['3-7 days'] += 1
                else:
                    buckets['> 7 days'] += 1
    
    # Check if we have any data
    total_responses = sum(buckets.values())
    if total_responses == 0:
        return {
            'available': False,
            'reason': 'No valid response time data found'
        }
    
    return {
        'available': True,
        'distribution': buckets,
        'total_responses': total_responses
    }
```

**Add to Analytics Pipeline**:
```python
def process_executive_analytics(self) -> Dict[str, Any]:
    """Process data for executive-level analytics."""
    analytics = {
        'summary': self._get_summary_metrics(),
        'monthly_trends': self._get_monthly_trends(),
        # ... existing analytics ...
        'response_time_distribution': self._get_response_time_distribution_analysis(),  # ADD THIS LINE
    }
    return analytics
```

### Step 2: Add Chart Configuration (tac_config.py)

```python
# Add to CHART_TYPES dictionary
CHART_TYPES = {
    'monthly_trends': 'bar',
    'severity_distribution': 'pie',
    # ... existing charts ...
    'response_time_distribution': 'bar',  # ADD THIS LINE - choose chart type
}

# [Optional] Add custom colors
CHART_COLOR_ASSIGNMENTS = {
    # ... existing assignments ...
    'response_time_colors': {  # ADD THIS BLOCK
        '< 1 hour': '#28a745',      # Green (fast)
        '1-4 hours': '#9fc5e8',     # Light blue
        '4-24 hours': '#ffc107',    # Yellow
        '1-3 days': '#ff6b35',      # Orange
        '3-7 days': '#dc3545',      # Red
        '> 7 days': '#8b0000'       # Dark red (slow)
    }
}
```

### Step 3: Add Visualization Method (tac_visualizations.py)

**Location**: Add new method in `TACVisualizer` class

```python
def create_response_time_distribution_chart(self, response_time_data: Dict[str, Any]) -> str:
    """
    Create response time distribution chart.
    
    Args:
        response_time_data: Response time distribution analysis data
        
    Returns:
        HTML string with chart
    """
    # Check availability
    if not response_time_data.get('available') or not response_time_data.get('distribution'):
        return self._create_not_available_message(
            "Response Time Distribution",
            response_time_data.get('reason', 'No data available')
        )
    
    try:
        from tac_config import CHART_TYPES
        
        distribution = response_time_data['distribution']
        chart_type = CHART_TYPES.get('response_time_distribution', 'bar')
        
        # Prepare data (maintain order of buckets)
        bucket_order = ['< 1 hour', '1-4 hours', '4-24 hours', '1-3 days', '3-7 days', '> 7 days']
        labels = []
        values = []
        
        for bucket in bucket_order:
            if bucket in distribution and distribution[bucket] > 0:
                labels.append(bucket)
                values.append(distribution[bucket])
        
        # Get colors
        colors = self._get_response_time_colors(labels)
        
        # Create chart using generic method
        fig = self._create_distribution_chart(
            labels=labels,
            values=values,
            colors=colors,
            chart_type=chart_type,
            title='Response Time Distribution',
            div_id='response_time_distribution_chart'
        )
        
        return fig.to_html(
            include_plotlyjs=CHART_PLOTLYJS_MODE,
            div_id="response_time_distribution_chart",
            config=CHART_CONFIG
        )
        
    except Exception as e:
        logger.error(f"Failed to create response time distribution chart: {e}")
        return self._create_error_message("Response Time Distribution Chart")

def _get_response_time_colors(self, buckets: List[str]) -> List[str]:
    """
    Get colors for response time buckets.
    
    Args:
        buckets: List of response time bucket labels
        
    Returns:
        List of color codes
    """
    # Get custom colors if defined
    rt_colors = self.color_assignments.get('response_time_colors', {})
    
    colors = []
    for i, bucket in enumerate(buckets):
        # Use custom color if defined, otherwise cycle through palette
        if bucket in rt_colors:
            colors.append(rt_colors[bucket])
        else:
            colors.append(self.chart_colors[i % len(self.chart_colors)])
    
    return colors
```

### Step 4: Add to Report Generator (tac_report_generator.py)

**Add to chart generation**:
```python
def _generate_all_charts(self, analytics: Dict[str, Any], visualizer: TACVisualizer = None) -> Dict[str, str]:
    """Generate all charts for the report."""
    viz = visualizer or self.visualizer
    charts = {}
    
    # ... existing chart generation ...
    
    # Response Time Distribution
    charts['response_time_distribution'] = viz.create_response_time_distribution_chart(
        analytics.get('response_time_distribution', {})
    )
    
    return charts
```

**Add to HTML report**:
```python
def _create_html_content(self, ...) -> str:
    """Create the complete HTML content for the report."""
    
    html_content = f"""
    ... existing HTML ...
    
    <!-- Response Time Distribution -->
    <div class="section" id="response-time-distribution">
        <h2>Response Time Distribution</h2>
        <div class="chart-container">
            {charts['response_time_distribution']}
        </div>
        <p class="chart-description">
            This chart shows the distribution of response times, helping identify
            how quickly the team responds to cases and where improvements may be needed.
        </p>
    </div>
    
    ... rest of HTML ...
    """
    
    return html_content
```

**Add to table of contents**:
```python
def _create_table_of_contents(self, analytics: Dict[str, Any]) -> str:
    """Create a table of contents for the report."""
    sections = []
    
    # ... existing sections ...
    
    # Response Time Distribution
    response_time_data = analytics.get('response_time_distribution', {})
    if response_time_data.get('available'):
        sections.append(("response-time-distribution", "Response Time Distribution"))
    
    # ... build TOC HTML ...
```

### Step 5: Test Your New Chart

**Create test script** (`test_response_time_chart.py`):
```python
"""Test response time distribution chart."""
from pathlib import Path
from tac_data_processor import TACDataProcessor
from tac_visualizations import TACVisualizer

# Load test data
test_file = Path('input_data/test_cases.csv')
processor = TACDataProcessor(test_file)

# Process data
processor.load_and_analyze()
analytics = processor.process_executive_analytics()

# Check if analysis worked
rt_data = analytics.get('response_time_distribution', {})
print(f"Response Time Analysis Available: {rt_data.get('available')}")
print(f"Distribution: {rt_data.get('distribution')}")

# Create chart
visualizer = TACVisualizer()
chart_html = visualizer.create_response_time_distribution_chart(rt_data)

# Save to test file
with open('test_response_time_chart.html', 'w') as f:
    f.write(f"""
    <!DOCTYPE html>
    <html>
    <head><title>Test Chart</title></head>
    <body>
        <h1>Response Time Distribution Test</h1>
        {chart_html}
    </body>
    </html>
    """)

print("Test chart saved to test_response_time_chart.html")
```

**Run test**:
```bash
python test_response_time_chart.py
```

### Step 6: Integration Checklist

- [ ] Analytics method added to `tac_data_processor.py`
- [ ] Analytics method added to `process_executive_analytics()`
- [ ] Chart type configured in `tac_config.py` → `CHART_TYPES`
- [ ] [Optional] Custom colors configured in `CHART_COLOR_ASSIGNMENTS`
- [ ] Visualization method added to `tac_visualizations.py`
- [ ] Color getter method added (if using custom colors)
- [ ] Chart added to `_generate_all_charts()` in `tac_report_generator.py`
- [ ] Chart section added to HTML template in `_create_html_content()`
- [ ] Chart added to table of contents in `_create_table_of_contents()`
- [ ] Test script created and passes
- [ ] Full integration test with real data
- [ ] Documentation updated (if needed)

### Common Pitfalls to Avoid

1. **Forgetting to check data availability**: Always return `{'available': False, 'reason': '...'}` if data missing
2. **Hardcoding colors**: Use configuration system for all colors
3. **Not handling empty data**: Check if aggregated data has entries before creating chart
4. **Missing error handling**: Wrap chart creation in try-except
5. **Forgetting TOC update**: New charts should be in table of contents
6. **Inconsistent naming**: Use same key name across all modules (e.g., 'response_time_distribution')
7. **Not testing with missing columns**: Test with data that lacks the required columns

---

## Data Processing Pipeline

### Data Flow Diagram

```
Raw CSV/Excel File
    ↓
[1. File Loading]
    ├─ Encoding Detection
    ├─ Title Row Detection
    ├─ pandas DataFrame
    └─ Footer Removal
    ↓
[2. Column Mapping]
    ├─ Identify columns by variants
    ├─ Create mapping dictionary
    └─ Validate essentials exist
    ↓
[3. Data Cleaning]
    ├─ Text normalization
    ├─ Null handling
    ├─ Severity standardization
    └─ Date parsing
    ↓
[4. Analytics Processing]
    ├─ For each metric:
    │   ├─ Check column availability
    │   ├─ Extract relevant data
    │   ├─ Aggregate/calculate
    │   └─ Return structured dict
    └─ Combine all metrics
    ↓
[5. Return Analytics Dictionary]
```

### Analytics Data Structure

The complete analytics dictionary structure:

```python
{
    'summary': {
        'total_cases': int,
        'date_range': {
            'start': datetime,
            'end': datetime,
            'days': int
        },
        'status_breakdown': {status: count, ...},
        'cases_per_month': float,
        'avg_cases_per_day': float,
        'average_ttr': str  # "12d:03h:45m"
    },
    
    'monthly_trends': {
        'available': bool,
        'monthly_counts': {'2025-01': 45, '2025-02': 52, ...},
        'monthly_status': {
            '2025-01': {'Open': 10, 'Closed': 35},
            ...
        },
        'monthly_severity': {
            '2025-01': {'Critical': 5, 'High': 15, ...},
            ...
        }
    },
    
    'severity_analysis': {
        'available': bool,
        'counts': {'1 - Critical': 10, '2 - High': 25, ...},
        'percentages': {'1 - Critical': 10.5, ...},
        'total': int
    },
    
    'product_analysis': {
        'available': bool,
        'product_counts': {'Alteon': 45, 'DefensePro': 32, ...},
        'version_analysis': {
            'Alteon': {'33.5.1.0': 20, '33.0.5.0': 15, ...},
            ...
        }
    },
    
    'bug_analysis': {
        'available': bool,
        'bug_vs_non_bug': {'Bug Cases': 15, 'Non-Bug Cases': 85},
        'bug_types': {'Alteon': 8, 'DefensePro': 5, ...},
        'bug_severity': {'1 - Critical': 3, '2 - High': 7, ...},
        'bug_cases_details': [
            {
                'case_number': 'CS0123456',
                'subject': 'SSL handshake failure',
                'status': 'Closed',
                'product': 'Alteon',
                'product_version': '33.5.1.0',
                'bug_id': 'AL-12345'
            },
            ...
        ],
        'bug_percentage': float
    },
    
    'engineer_assignment': {
        'available': bool,
        'case_counts': {'John Doe': 25, 'Jane Smith': 20, ...},
        'status_breakdown': {
            'John Doe': {'Open': 5, 'Closed': 20},
            ...
        }
    },
    
    'case_owner_assignment': {
        'available': bool,
        'case_counts': {'Owner 1': 15, 'Owner 2': 12, ...},
        'status_breakdown': {...}
    },
    
    'status_analysis': {
        'available': bool,
        'counts': {'Open': 25, 'Closed': 60, 'Pending': 15}
    },
    
    'internal_vs_external': {
        'available': bool,
        'breakdown': {'Internal': 20, 'External': 80}
    },
    
    'queue_analysis': {
        'available': bool,
        'queue_counts': {'TAC Queue': 50, 'Tier 4': 30, ...}
    },
    
    'escalation': {
        'available': bool,
        'counts': {
            'Not Escalated': 75,
            'Escalated': 20,
            'Escalated TopN': 5
        }
    },
    
    'category_analysis': {
        'available': bool,
        'counts': {
            'Layer 3 (IPv4)': 15,
            'Upgrade/Downgrade/Install': 25,
            ...
        }
    },
    
    'resolution_analysis': {
        'available': bool,
        'counts': {
            'Explanations Provided': 30,
            'Workaround Provided': 20,
            ...
        }
    }
}
```

### Error Handling Strategy

Each analytics method follows this error handling pattern:

```python
def _get_<metric>_analysis(self) -> Dict[str, Any]:
    # Graceful degradation
    if <required_data_missing>:
        return {
            'available': False,
            'reason': '<human-readable explanation>'
        }
    
    try:
        # Processing logic
        result = process_data()
        
        # Additional validation
        if not result or len(result) == 0:
            return {
                'available': False,
                'reason': 'No valid data found'
            }
        
        return {
            'available': True,
            <metric_data>
        }
        
    except Exception as e:
        logger.error(f"Error in <metric> analysis: {e}")
        return {
            'available': False,
            'reason': f'Processing error: {str(e)}'
        }
```

This ensures:
- Reports can be generated even if some metrics fail
- Users get clear explanations for missing charts
- Logging captures detailed errors for debugging
- No complete failure from one bad metric

---

## Extending the System

### Adding New Data Sources

To support additional file formats (e.g., JSON, database):

1. **Add loader method** in `tac_data_processor.py`:
```python
def _load_json_file(self):
    """Load JSON file format."""
    with open(self.file_path, 'r') as f:
        json_data = json.load(f)
    
    # Convert to DataFrame
    self.data = pd.DataFrame(json_data)
```

2. **Update file discovery** in `tac_analyzer.py`:
```python
def discover_input_files(self) -> List[Path]:
    supported_extensions = ['.csv', '.xlsx', '.xls', '.json']  # Add .json
    # ... rest of method
```

3. **Add to load logic** in `tac_data_processor.py`:
```python
def load_and_analyze(self) -> Dict[str, Any]:
    # Determine file type
    if self.file_path.suffix.lower() == '.json':
        self._load_json_file()
    elif self.file_path.suffix.lower() in ['.xlsx', '.xls']:
        self._load_excel_file()
    else:
        self._load_csv_file()
    # ... rest of method
```

### Adding New Output Formats

To support additional output formats (e.g., PowerPoint, Word):

1. **Add format option** in `tac_config.py`:
```python
OUTPUT_FORMATS = ['html', 'pdf', 'pptx']
```

2. **Add generation method** in `tac_report_generator.py`:
```python
def _generate_pptx_report(self, analytics, file_analysis) -> Path:
    """Generate PowerPoint presentation."""
    from pptx import Presentation
    
    prs = Presentation()
    # Add slides with charts...
    
    output_path = self.output_dir / f"{base_name}_report.pptx"
    prs.save(str(output_path))
    return output_path
```

3. **Update generate_reports**:
```python
def generate_reports(self, ..., formats=['html', 'pdf']) -> Dict[str, Path]:
    # ... existing HTML/PDF generation ...
    
    if 'pptx' in formats:
        pptx_path = self._generate_pptx_report(analytics, file_analysis)
        generated_files['pptx'] = pptx_path
    
    return generated_files
```

### Adding Custom Analytics

Example: Track cases by day of week

1. **Add analysis method**:
```python
def _get_day_of_week_analysis(self) -> Dict[str, Any]:
    """Analyze case distribution by day of week."""
    if 'date_created' not in self.column_mapping:
        return {'available': False, 'reason': 'No date column'}
    
    date_col = self.column_mapping['date_created']
    day_counts = {
        'Monday': 0, 'Tuesday': 0, 'Wednesday': 0,
        'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0
    }
    
    for _, row in self.data.iterrows():
        date_str = str(row.get(date_col, ''))
        parsed_date = parse_date_flexible(date_str)
        
        if parsed_date:
            day_name = parsed_date.strftime('%A')
            day_counts[day_name] += 1
    
    return {
        'available': True,
        'day_counts': day_counts
    }
```

2. **Add to analytics pipeline**:
```python
def process_executive_analytics(self) -> Dict[str, Any]:
    analytics = {
        # ... existing metrics ...
        'day_of_week': self._get_day_of_week_analysis()
    }
    return analytics
```

3. Follow chart creation steps from "Adding New Charts" section

### Customizing Report Layout

To change report structure:

1. **Modify HTML template** in `tac_report_generator.py` → `_create_html_content()`:
```python
html_content = f"""
<!DOCTYPE html>
<html>
<head>...</head>
<body>
    <!-- Your custom layout -->
    <div class="container">
        <div class="left-column">
            <!-- Executive summary -->
        </div>
        <div class="right-column">
            <!-- Key metrics -->
        </div>
    </div>
    <!-- Charts below -->
</body>
</html>
"""
```

2. **Update CSS** in `tac_config.py` → `REPORT_CSS`:
```python
REPORT_CSS = """
<style>
.container {
    display: grid;
    grid-template-columns: 60% 40%;
    gap: 20px;
}
.left-column { ... }
.right-column { ... }
</style>
"""
```

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "No TAC case files found"

**Symptoms**: Script runs but reports 0 files processed

**Causes**:
1. Files in wrong directory
2. Unsupported file extension
3. Empty input directory

**Solutions**:
```bash
# Check input directory
ls input_data/

# Verify file extensions
# Supported: .csv, .xlsx, .xls

# Try with explicit path
python tac_analyzer.py --input-dir /full/path/to/files --verbose
```

#### Issue: "Missing essential columns"

**Symptoms**: Chart shows "Data not available"

**Causes**:
1. CSV has different column names than expected
2. First row is a title, not headers
3. File exported with unusual column names

**Solutions**:
1. Check actual column names:
```python
import pandas as pd
df = pd.read_csv('input_data/your_file.csv')
print(df.columns.tolist())
```

2. Add column name variants to `tac_data_processor.py`:
```python
self.expected_columns = {
    'reference': [
        'Reference #', 'Reference', 'Case #',
        'YOUR_CUSTOM_NAME_HERE'  # Add your variation
    ],
    # ...
}
```

3. Enable verbose logging:
```bash
python tac_analyzer.py --verbose
# Check tac_report.log for column mapping details
```

#### Issue: PDF generation fails

**Symptoms**: HTML generates but PDF fails or creates instructions file

**Causes**:
1. Playwright not installed
2. Chromium browser not installed
3. JavaScript charts not loading

**Solutions**:
```bash
# Install Playwright
pip install playwright

# Install browser
playwright install chromium

# Test Playwright
python -c "from playwright.sync_api import sync_playwright; print('OK')"

# If still failing, check firewall/proxy settings
```

#### Issue: Charts not displaying in HTML

**Symptoms**: HTML file shows boxes but no charts

**Causes**:
1. Plotly.js not loading (CDN blocked)
2. Browser JavaScript disabled
3. Invalid chart data

**Solutions**:
1. Change Plotly mode to 'inline' in `tac_config.py`:
```python
CHART_PLOTLYJS_MODE = 'inline'  # Embeds Plotly.js in HTML
```

2. Check browser console for errors:
   - Open HTML in browser
   - Press F12
   - Check Console tab for error messages

3. Verify chart data:
```bash
python tac_analyzer.py --verbose
# Check log for "Failed to create <chart> chart" messages
```

#### Issue: Memory errors with large files

**Symptoms**: Script crashes or becomes very slow

**Causes**:
1. File > 100MB
2. Too many rows
3. Memory leak in processing

**Solutions**:
1. Process files separately:
```bash
# Instead of processing all at once
python tac_analyzer.py

# Process one at a time by placing in input_data folder alone
```

2. Increase chunk size for pandas:
```python
# In tac_data_processor.py, modify loading:
self.data = pd.read_csv(
    self.file_path,
    encoding=self.encoding,
    low_memory=True,  # Changed from False
    chunksize=10000  # Process in chunks
)
```

#### Issue: Incorrect date parsing

**Symptoms**: Date-based charts empty or wrong

**Causes**:
1. Unusual date format
2. Dates in non-US format (DD/MM/YYYY vs MM/DD/YYYY)
3. Timezone issues

**Solutions**:
1. Add date format to `tac_utils.py`:
```python
def parse_date_flexible(date_str, date_format=None):
    common_formats = [
        '%m/%d/%Y %I:%M %p',
        '%d/%m/%Y %H:%M:%S',  # European format
        '%Y.%m.%d %H:%M:%S',  # Your format here
        # ...
    ]
```

2. Enable date parsing debug:
```python
# In tac_utils.py, temporarily add:
logger.debug(f"Parsing date: {date_str}")
logger.debug(f"Parsed result: {parsed_date}")
```

3. Check date range in report:
   - Look at Executive Summary
   - Verify start/end dates make sense

#### Issue: Colors not applying

**Symptoms**: Charts use wrong colors or default colors

**Causes**:
1. Typo in configuration
2. Invalid hex codes
3. Configuration not reloaded

**Solutions**:
1. Verify configuration syntax:
```python
# In tac_config.py
CHART_COLOR_ASSIGNMENTS = {
    'severity_colors': {
        'Critical': '#dc3545',  # Correct hex code
        'High': 'ff6b35',       # WRONG - missing #
    }
}
```

2. Reload configuration:
```bash
# Python caches imports, restart completely
# Kill any running processes
# Run fresh:
python tac_analyzer.py
```

3. Check effective colors in code:
```python
# In tac_visualizations.py, add debug:
logger.info(f"Using colors: {colors}")
```

### Debug Mode

Enable maximum debugging:

```bash
# Run with verbose flag
python tac_analyzer.py --verbose

# Check log file
cat tac_report.log

# Or on Windows
type tac_report.log
```

### Getting Support

1. **Check log file**: `tac_report.log` has detailed trace
2. **Run verbose**: Use `--verbose` flag
3. **Test with sample data**: Try with known-good CSV
4. **Check dependencies**: `pip list | grep plotly`
5. **Review recent changes**: What changed since last working version?

---

## Version Control and Maintenance

### Version History Tracking

Version numbers in `README.md` follow format: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

### Making Changes Safely

1. **Test with sample data first**
2. **Keep backup of working version**
3. **Update version number in README.md**
4. **Document changes in version notes**
5. **Test all output formats (HTML and PDF)**

### Code Review Checklist

Before committing changes:

- [ ] Code follows existing style and patterns
- [ ] New functionality has error handling
- [ ] Configuration options documented
- [ ] Test with multiple data files
- [ ] No hardcoded values
- [ ] Logging messages added for debugging
- [ ] DEVELOPER.md updated if architecture changed
- [ ] README.md updated if user-facing changes

---

## Performance Optimization Tips

### Large File Handling

```python
# Use chunking for files > 50MB
def _load_csv_file_chunked(self):
    chunks = []
    for chunk in pd.read_csv(self.file_path, chunksize=10000):
        # Process each chunk
        chunks.append(chunk)
    self.data = pd.concat(chunks, ignore_index=True)
```

### Chart Generation

```python
# Limit data points in charts
def create_product_hierarchy_chart(self, product_data):
    # Take only top 15 products
    product_counts = product_data['product_counts']
    sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:15]
```

### Memory Management

```python
# Clear unused data after processing
def process_executive_analytics(self):
    analytics = {...}
    
    # Clear large DataFrame to free memory
    del self.data
    
    return analytics
```

---

## Summary

This TAC Executive Report Generator is a modular, configurable system for processing TAC case data and generating executive reports. The architecture emphasizes:

1. **Separation of Concerns**: Each module has a single responsibility
2. **Configuration over Code**: User customization through config files
3. **Graceful Degradation**: Missing data doesn't break entire report
4. **Extensibility**: Easy to add new charts, metrics, and formats
5. **Error Handling**: Comprehensive logging and fallbacks

By following this documentation, you can:
- Understand how data flows through the system
- Add new charts and analytics metrics
- Customize appearance and behavior
- Troubleshoot issues effectively
- Extend the system for new requirements

For questions or issues not covered here, check:
1. Source code comments
2. Log files (`tac_report.log`)
3. README.md for user-facing documentation
4. Git history for recent changes

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-29  
**Maintainer**: Egor Egorov (@egori4)
