"""
TAC Executive Report Generator

Generates professional HTML and PDF reports from TAC case analysis data
with executive-level insights and visualizations.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import tempfile
import asyncio

from tac_config import REPORT_CSS
from tac_visualizations import TACVisualizer
from tac_utils import format_number, clean_filename

logger = logging.getLogger(__name__)


class TACReportGenerator:
    """
    Generates professional HTML and PDF reports for TAC case analysis.
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.visualizer = TACVisualizer()
        
        logger.info(f"Initialized TACReportGenerator with output directory: {output_dir}")
    
    def generate_reports(
        self,
        input_filename: str,
        analytics: Dict[str, Any],
        file_analysis: Dict[str, Any],
        formats: list = ['html', 'pdf']
    ) -> Dict[str, Path]:
        """
        Generate both HTML and PDF reports.
        
        Args:
            input_filename: Original input filename
            analytics: Complete analytics data
            file_analysis: File analysis information
            formats: List of formats to generate ('html', 'pdf', or both)
            
        Returns:
            Dictionary mapping format to generated file path
        """
        logger.info(f"Generating TAC executive reports for {input_filename}")
        
        # Clean filename for output
        base_name = clean_filename(Path(input_filename).stem)
        
        generated_files = {}
        
        try:
            # Generate HTML report
            if 'html' in formats:
                html_path = self._generate_html_report(base_name, analytics, file_analysis)
                generated_files['html'] = html_path
                logger.info(f"Generated HTML report: {html_path}")
            
            # Generate PDF report
            if 'pdf' in formats:
                if 'html' in generated_files:
                    # Use the HTML file we just generated
                    html_path = generated_files['html']
                else:
                    # Generate HTML first for PDF conversion
                    html_path = self._generate_html_report(base_name, analytics, file_analysis)
                
                pdf_path = self._generate_pdf_report(html_path, base_name)
                generated_files['pdf'] = pdf_path
                logger.info(f"Generated PDF report: {pdf_path}")
                
                # Clean up temporary HTML if we only wanted PDF
                if 'html' not in formats:
                    html_path.unlink()
            
            return generated_files
            
        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")
            raise
    
    def _generate_html_report(
        self,
        base_name: str,
        analytics: Dict[str, Any],
        file_analysis: Dict[str, Any]
    ) -> Path:
        """
        Generate HTML report with embedded visualizations.
        
        Args:
            base_name: Base filename for the report
            analytics: Complete analytics data
            file_analysis: File analysis information
            
        Returns:
            Path to generated HTML file
        """
        output_path = self.output_dir / f"{base_name}_executive_report.html"
        
        try:
            # Generate all visualizations
            charts = self._generate_all_charts(analytics)
            
            # Create executive summary
            executive_summary = self._create_executive_summary(analytics)
            
            # Generate the HTML content
            html_content = self._create_html_content(
                base_name, analytics, file_analysis, charts, executive_summary
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            raise
    
    def _generate_all_charts(self, analytics: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all charts for the report.
        
        Args:
            analytics: Complete analytics data
            
        Returns:
            Dictionary of chart HTML strings
        """
        try:
            charts = {}
            
            # Summary statistics cards
            charts['summary_stats'] = self.visualizer.create_summary_statistics_cards(analytics)
            
            # Monthly trends
            charts['monthly_trends'] = self.visualizer.create_monthly_cases_chart(
                analytics.get('monthly_trends', {})
            )
            
            # Severity distribution
            charts['severity_distribution'] = self.visualizer.create_severity_distribution_chart(
                analytics.get('severity_analysis', {})
            )
            
            # Product hierarchy
            charts['product_hierarchy'] = self.visualizer.create_product_hierarchy_chart(
                analytics.get('product_analysis', {})
            )
            
            # Bug analysis
            charts['bug_analysis'] = self.visualizer.create_bug_analysis_chart(
                analytics.get('bug_analysis', {})
            )
            
            # Engineer performance
            charts['engineer_performance'] = self.visualizer.create_engineer_performance_chart(
                analytics.get('engineer_performance', {})
            )
            
            # Internal vs External
            charts['internal_external'] = self.visualizer.create_internal_external_chart(
                analytics.get('internal_vs_external', {})
            )
            
            # Queue distribution
            charts['queue_distribution'] = self.visualizer.create_queue_distribution_chart(
                analytics.get('queue_analysis', {})
            )
            
            logger.debug(f"Generated {len(charts)} charts")
            return charts
            
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")
            # Return empty charts dict to prevent complete failure
            return {key: '<div class="warning">Chart generation failed</div>' for key in [
                'summary_stats', 'monthly_trends', 'severity_distribution', 'product_hierarchy',
                'bug_analysis', 'engineer_performance', 'internal_external', 'queue_distribution'
            ]}
    
    def _create_executive_summary(self, analytics: Dict[str, Any]) -> str:
        """
        Create executive summary text.
        
        Args:
            analytics: Complete analytics data
            
        Returns:
            HTML string with executive summary
        """
        try:
            summary = analytics.get('summary', {})
            total_cases = summary.get('total_cases', 0)
            date_range = summary.get('date_range', {})
            cases_per_month = summary.get('cases_per_month', 0)
            
            # Bug analysis
            bug_data = analytics.get('bug_analysis', {})
            bug_percentage = bug_data.get('bug_percentage', 0)
            
            # Severity analysis
            severity_data = analytics.get('severity_analysis', {})
            high_priority_cases = 0
            if severity_data.get('available'):
                counts = severity_data.get('counts', {})
                high_priority_cases = counts.get('1 - Critical', 0) + counts.get('2 - High', 0)
            
            # Response time analysis
            response_data = analytics.get('response_times', {})
            avg_response_days = response_data.get('avg_response_days', 0) if response_data.get('available') else 0
            
            # Date range formatting
            date_start = "Unknown"
            date_end = "Unknown"
            if date_range.get('start') and date_range.get('end'):
                date_start = date_range['start'].strftime('%B %d, %Y')
                date_end = date_range['end'].strftime('%B %d, %Y')
            
            summary_html = f"""
            <div class="section">
                <h2>Executive Summary</h2>
                <div class="executive-summary">
                    <p><strong>Period Analyzed:</strong> {date_start} to {date_end}</p>
                    
                    <p>This report analyzes <strong>{format_number(total_cases)} TAC cases</strong> 
                    created during the reporting period, representing an average of 
                    <strong>{cases_per_month:.1f} cases per month</strong>.</p>
                    
                    <h3>Key Findings:</h3>
                    <ul>
                        <li><strong>Case Volume:</strong> {format_number(total_cases)} total cases processed</li>
                        <li><strong>Bug Impact:</strong> {bug_percentage}% of cases were related to product bugs</li>
                        <li><strong>High Priority Cases:</strong> {format_number(high_priority_cases)} critical and high severity cases</li>
                        {'<li><strong>Response Time:</strong> Average response time of ' + str(avg_response_days) + ' days</li>' if avg_response_days > 0 else ''}
                    </ul>
                    
                    <p>The analysis includes comprehensive breakdowns by severity, product hierarchy, 
                    engineering assignments, and case resolution patterns to provide actionable insights 
                    for executive decision-making.</p>
                </div>
            </div>
            """
            
            return summary_html
            
        except Exception as e:
            logger.error(f"Failed to create executive summary: {e}")
            return '<div class="section"><h2>Executive Summary</h2><p>Error generating summary</p></div>'
    
    def _create_html_content(
        self,
        base_name: str,
        analytics: Dict[str, Any],
        file_analysis: Dict[str, Any],
        charts: Dict[str, str],
        executive_summary: str
    ) -> str:
        """
        Create the complete HTML content for the report.
        
        Args:
            base_name: Base filename
            analytics: Complete analytics data
            file_analysis: File analysis information
            charts: Dictionary of chart HTML strings
            executive_summary: Executive summary HTML
            
        Returns:
            Complete HTML content string
        """
        generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        summary = analytics.get('summary', {})
        total_cases = summary.get('total_cases', 0)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TAC Executive Report - {base_name.replace('_', ' ').title()}</title>
    {REPORT_CSS}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TAC Executive Report</h1>
            <p class="subtitle">{base_name.replace('_', ' ').title()}</p>
            <p class="generation-info">Generated on {generation_time}</p>
        </div>
        
        <div class="content">
            <!-- Executive Summary -->
            {executive_summary}
            
            <!-- Key Metrics -->
            <div class="section">
                <h2>Key Performance Metrics</h2>
                {charts['summary_stats']}
            </div>
            
            <!-- Monthly Trends -->
            <div class="section">
                <h2>Monthly Case Volume Trends</h2>
                <div class="chart-container">
                    {charts['monthly_trends']}
                </div>
                <p class="chart-description">
                    This chart shows the monthly distribution of TAC cases, helping identify seasonal patterns, 
                    workload trends, and capacity planning requirements.
                </p>
            </div>
            
            <!-- Severity Analysis -->
            <div class="section">
                <h2>Case Severity Distribution</h2>
                <div class="chart-container">
                    {charts['severity_distribution']}
                </div>
                <p class="chart-description">
                    Severity distribution provides insight into the criticality of support requests and 
                    helps prioritize resource allocation for high-impact issues.
                </p>
            </div>
            
            <!-- Product Analysis -->
            <div class="section">
                <h2>Product Hierarchy Analysis</h2>
                <div class="chart-container">
                    {charts['product_hierarchy']}
                </div>
                <p class="chart-description">
                    Product distribution shows which product lines generate the most support requests, 
                    enabling targeted improvement efforts and resource planning.
                </p>
            </div>
            
            <!-- Bug Analysis -->
            <div class="section">
                <h2>Bug-Related Case Analysis</h2>
                <div class="chart-container">
                    {charts['bug_analysis']}
                </div>
                <p class="chart-description">
                    Understanding the proportion of bug-related cases helps assess product quality 
                    and the effectiveness of quality assurance processes.
                </p>
            </div>
            
            <!-- Engineer Performance -->
            <div class="section">
                <h2>Engineer Case Distribution</h2>
                <div class="chart-container">
                    {charts['engineer_performance']}
                </div>
                <p class="chart-description">
                    Case distribution by engineer provides insights into workload balance and 
                    individual performance metrics for team management.
                </p>
            </div>
            
            <!-- Internal vs External -->
            <div class="section">
                <h2>Internal vs External Cases</h2>
                <div class="chart-container">
                    {charts['internal_external']}
                </div>
                <p class="chart-description">
                    The ratio of internal to external cases helps understand resource allocation 
                    between customer support and internal technical issues.
                </p>
            </div>
            
            <!-- Queue Analysis -->
            <div class="section">
                <h2>Queue Distribution</h2>
                <div class="chart-container">
                    {charts['queue_distribution']}
                </div>
                <p class="chart-description">
                    Queue distribution shows how cases are distributed across different support teams, 
                    enabling optimization of team structures and specialization areas.
                </p>
            </div>
            
            <!-- Data Summary -->
            <div class="section">
                <h2>Report Details</h2>
                <div class="data-summary">
                    <table class="summary-table">
                        <tr><td><strong>Total Cases Analyzed:</strong></td><td>{format_number(total_cases)}</td></tr>
                        <tr><td><strong>Source File:</strong></td><td>{file_analysis.get('file_size', 'Unknown')}</td></tr>
                        <tr><td><strong>Columns Processed:</strong></td><td>{file_analysis.get('columns_found', 0)}</td></tr>
                        <tr><td><strong>Date Range:</strong></td><td>{file_analysis.get('date_range', {}).get('days', 0)} days</td></tr>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>TAC Executive Report generated on {generation_time}</p>
            <p>Source: {base_name}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def _generate_pdf_report(self, html_path: Path, base_name: str) -> Path:
        """
        Generate PDF report from HTML.
        
        Args:
            html_path: Path to HTML file
            base_name: Base filename for output
            
        Returns:
            Path to generated PDF file
        """
        output_path = self.output_dir / f"{base_name}_executive_report.pdf"
        
        try:
            # Try Playwright first
            try:
                from playwright.async_api import async_playwright
                
                async def generate_pdf():
                    async with async_playwright() as p:
                        browser = await p.chromium.launch()
                        page = await browser.new_page()
                        
                        # Load the HTML file
                        file_url = f"file://{html_path.absolute()}"
                        await page.goto(file_url, wait_until='networkidle')
                        
                        # Wait for charts to render
                        await page.wait_for_timeout(3000)
                        
                        # Generate PDF
                        await page.pdf(
                            path=str(output_path),
                            format='A4',
                            margin={
                                'top': '1in',
                                'right': '0.8in',
                                'bottom': '1in',
                                'left': '0.8in'
                            },
                            print_background=True
                        )
                        
                        await browser.close()
                
                # Run the async function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(generate_pdf())
                loop.close()
                
                logger.info(f"Generated PDF using Playwright: {output_path}")
                return output_path
                
            except ImportError:
                logger.warning("Playwright not available, trying WeasyPrint...")
                
                # Try WeasyPrint as fallback
                try:
                    import weasyprint
                    
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Generate PDF
                    html_doc = weasyprint.HTML(string=html_content, base_url=str(html_path.parent))
                    html_doc.write_pdf(str(output_path))
                    
                    logger.info(f"Generated PDF using WeasyPrint: {output_path}")
                    return output_path
                    
                except ImportError:
                    logger.error("No PDF generation library available (Playwright or WeasyPrint)")
                    
                    # Create a text file with instructions instead
                    instructions_path = self.output_dir / f"{base_name}_pdf_instructions.txt"
                    
                    with open(instructions_path, 'w') as f:
                        f.write(f"""
PDF Generation Instructions
===========================

To generate a PDF from the HTML report, you can:

1. Install Playwright:
   pip install playwright
   playwright install chromium

2. Or install WeasyPrint:
   pip install weasyprint

Then re-run the report generation.

Alternatively, you can:
- Open the HTML file in a web browser and use Print to PDF
- Use online HTML to PDF conversion services

HTML Report Location: {html_path}
""")
                    
                    logger.info(f"Created PDF instructions file: {instructions_path}")
                    return instructions_path
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            raise