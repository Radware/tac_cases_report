# TAC Executive Report Generator

This tool generates TAC cases interactive report with charts and insights from csv or excel report exported from Rightnow .

## 🎯 Features

- **Insights**: Monthly trends, severity analysis, case status, product and otehr metrics
- **Flexible Input Support**: Processes both CSV and Excel files with intelligent column mapping
- **Interactive Visualizations**: Charts with Plotly
- **Multiple Output Formats**: HTML reports with embedded charts and optional PDF generation
- **Bug Analysis**: Identifies cases that ended up as a bug and breakdown by product
- **Customer Analytics**: TAC Engineer assignment patterns

## 📊 Report Sections

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

For PDF generation:
```bash
# Playwright is required for JavaScript chart rendering
pip install playwright
playwright install chromium
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
# Choose from available color palettes
ACTIVE_COLOR_PALETTE = 'professional_blue'  # Options: 'radware_corporate', 'professional_blue', etc.

# Available palettes
COLOR_PALETTES = {
    'radware_corporate': [
        '#003f7f', '#6cb2eb', '#ff6b35', '#28a745', '#ffc107',
        # ... more colors
    ],
    'professional_blue': [
        '#1f4e79', '#2e75b6', '#5b9bd5', '#9fc5e8',
        # ... more colors  
    ]
    # ... more palettes
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
- Install Playwright (see Installation section) - this is required for JavaScript chart rendering
- HTML reports will still be generated successfully

**Memory issues with large files**
- The tool processes data in chunks to handle large files

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

V0.2.6 
    Cosmetics - cleaned Case distibution by Severity chart - renamed categories instead of 1- Critical, 2- High to Critical, High etc.
V0.2.5 
    Added Case Escalation Distribution chart
    Added TopN and TTR as Key Performance Metrics
    Added cases by Category chart
    Added cases by Resolution chart
V0.2.4 
    Removed WeasyPrint support (incompatible with JS charts), cleaned up PDF generation to use Playwright only
    Added detailed bug cases table under Bug Analysis chart with case details (Case Number, Subject, Status, Product, Product Version, Bug ID)
    Added interactive table of contents with clickable navigation links in both HTML and PDF reports
V0.2.3 Improved coloring scheme, improved Bugs chart layout for PDF
V0.2.2 Fixed PDF export to properly export charts and fit them to PDF page
V0.2.1 Updated README.md
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

## 📞 Support & Maintenance
Project Maintainer: Egor Egorov (@egori4 | @rdwr-egore)
Email: egore@radware.com

## 🔄 Updates and Maintenance

To update the tool:
1. Pull latest changes
2. Update dependencies: `pip install -r requirements.txt --upgrade`
3. Test with sample data

## 📄 License

This tool is designed for internal use with TAC case data analysis and executive reporting.