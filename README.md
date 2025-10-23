# TAC Executive Report Generator

A professional tool for generating executive-level reports from Technical Assistance Center (TAC) case data. Creates comprehensive HTML and PDF reports with interactive visualizations and business insights.

## 🎯 Features

- **Executive-Level Insights**: Monthly trends, severity analysis, product impact, and team performance metrics
- **Flexible Input Support**: Processes both CSV and Excel files with intelligent column mapping
- **Interactive Visualizations**: Professional charts with Plotly for executive presentations
- **Multiple Output Formats**: HTML reports with embedded charts and optional PDF generation
- **Bug Analysis**: Identifies bug-related cases and analyzes impact on support operations
- **Customer Analytics**: Engineer workload distribution and case assignment patterns
- **Professional Styling**: Radware-branded reports suitable for executive presentations

## 📊 Report Sections

### Key Performance Metrics
- Total cases, monthly velocity, bug percentage, response times

### Monthly Volume Trends
- Case creation patterns with trend analysis
- Seasonal workload identification

### Severity Distribution
- Critical, High, Medium, Low case breakdown
- Priority-based resource allocation insights

### Product Analysis
- Cases by product hierarchy
- Version-specific issue tracking

### Bug Impact Analysis
- Bug vs non-bug case ratios
- Bug type categorization (AL-, CYCON-, etc.)
- Severity distribution of bug-related cases

### Team Performance
- Engineer case distribution
- Queue workload analysis
- Internal vs external case ratios

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

For PDF generation (optional):
```bash
# For Playwright (recommended)
pip install playwright
playwright install chromium

# OR for WeasyPrint (alternative)
pip install weasyprint
```

## 🎯 Quick Start

### 1. Prepare Input Data
Place your TAC case files in the `input_data/` directory:
- **CSV files**: `.csv` extension
- **Excel files**: `.xlsx` or `.xls` extension

### 2. Run Analysis

**Basic usage** (processes all files in input_data/):
```bash
python tac_analyzer.py
```

**Advanced usage**:
```bash
# Specify custom directories
python tac_analyzer.py --input-dir /path/to/files --output-dir /path/to/reports

# Generate only HTML reports
python tac_analyzer.py --format html

# Generate only PDF reports  
python tac_analyzer.py --format pdf

# Enable verbose logging
python tac_analyzer.py --verbose

# Help
python tac_analyzer.py --help
```

### 3. View Results

Reports are generated in the `reports/` directory:
- `{filename}_executive_report.html` - Interactive HTML report
- `{filename}_executive_report.pdf` - PDF version for sharing
- `tac_batch_summary_{timestamp}.html` - Summary when processing multiple files

## 📁 Project Structure

```
TAC_Executive_Report/
├── tac_analyzer.py           # Main orchestrator script
├── tac_data_processor.py     # CSV/Excel parsing and analytics
├── tac_report_generator.py   # HTML/PDF generation
├── tac_visualizations.py     # Chart creation logic
├── tac_utils.py             # Helper functions
├── tac_config.py            # Configuration constants
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── input_data/             # Input directory (place files here)
└── reports/                # Output directory
```

## 📋 Expected Data Format

The tool expects TAC case data with the following columns (flexible naming):

### Required Columns
- **Reference/Case #**: Unique case identifier
- **Status**: Case status (Open, Closed, etc.)
- **Date Created**: Case creation timestamp

### Optional Columns (Enhanced Analytics)
- **Subject**: Case description
- **Severity/Priority**: Case priority level
- **Product Hierarchy**: Product line information
- **Product Version**: Specific product version
- **Experienced Bug**: Bug identification field
- **Internal Case**: Internal vs external flag
- **End Customer**: Customer organization
- **Full Name**: Engineer/contact name
- **Assigned Account**: Assigned engineer
- **Queue**: Support queue/team
- **Date Last Responded**: Response timestamp

### Column Name Flexibility
The tool automatically maps common column name variations:
- `Reference #` → `Reference`, `Case #`, `Case Number`, `Ticket #`
- `Date Created` → `Created Date`, `Created`, `Open Date`
- `Product Hierarchy` → `Product`, `Product Line`
- And many more...

## 🔧 Configuration

### Output Formats
Edit `OUTPUT_FORMATS` in `tac_config.py`:
```python
OUTPUT_FORMATS = ['html']        # HTML only
OUTPUT_FORMATS = ['pdf']         # PDF only  
OUTPUT_FORMATS = ['html', 'pdf'] # Both formats
```

### Chart Styling
Customize colors and branding in `tac_config.py`:
```python
RADWARE_COLORS = {
    'primary': '#003f7f',    # Radware blue
    'secondary': '#6cb2eb',  # Light blue
    # ... more colors
}
```

## 🐛 Troubleshooting

### Common Issues

**"No TAC case files found"**
- Ensure files are in the correct input directory
- Check file extensions (.csv, .xlsx, .xls)
- Verify files are not empty

**"Missing essential columns"**
- Check that your data includes at minimum: Reference, Status, Date Created
- The tool will attempt to find alternative column names automatically

**"PDF generation failed"**
- Install Playwright or WeasyPrint (see Installation section)
- HTML reports will still be generated successfully

**Memory issues with large files**
- The tool processes data in chunks to handle large files
- Consider splitting very large files (>100MB) for better performance

### Getting Help
1. Check the log file `tac_report.log` for detailed error messages
2. Run with `--verbose` flag for more detailed output
3. Ensure all dependencies are installed correctly

## 📈 Sample Output

The generated reports include:
- **Executive Summary**: High-level findings and recommendations
- **Key Metrics Dashboard**: Visual KPI cards
- **Monthly Trends**: Time-series analysis with trend lines
- **Severity Analysis**: Priority distribution with color coding
- **Product Impact**: Product hierarchy breakdown
- **Bug Analysis**: Bug identification and categorization
- **Team Performance**: Engineer workload and queue distribution
- **Customer Analytics**: Internal vs external case analysis

## Version control

V0.2.0 
    Added 2 new charts - by status and by owner
    Cosmetic improvements
V0.1.2 
    Added support for MIS generated csv reports
    Added chart style control functionality to user, added to tac_config.py
    Enhance visualization of pie charts/donuts types of charts
    Removed Report Details section
V0.1.1 Bugfixes adjustments
V0.1.0 First push


## 🔄 Updates and Maintenance

To update the tool:
1. Pull latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Test with sample data

## 📄 License

This tool is designed for internal use with TAC case data analysis and executive reporting.