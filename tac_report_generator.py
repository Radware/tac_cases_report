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
                html_path = self._generate_html_report(base_name, analytics, file_analysis, output_format='html')
                generated_files['html'] = html_path
                logger.info(f"Generated HTML report: {html_path}")
            
            # Generate PDF report
            if 'pdf' in formats:
                if 'html' in generated_files:
                    # Generate separate PDF-optimized HTML
                    pdf_html_path = self._generate_html_report(base_name, analytics, file_analysis, output_format='pdf')
                    pdf_path = self._generate_pdf_report(pdf_html_path, base_name)
                    # Clean up temporary PDF-optimized HTML
                    pdf_html_path.unlink()
                else:
                    # Generate PDF-optimized HTML first for PDF conversion
                    pdf_html_path = self._generate_html_report(base_name, analytics, file_analysis, output_format='pdf')
                    pdf_path = self._generate_pdf_report(pdf_html_path, base_name)
                    # Clean up temporary HTML if we only wanted PDF
                    pdf_html_path.unlink()
                
                generated_files['pdf'] = pdf_path
                logger.info(f"Generated PDF report: {pdf_path}")
            
            return generated_files
            
        except Exception as e:
            logger.error(f"Failed to generate reports: {e}")
            raise
    
    def _generate_html_report(
        self,
        base_name: str,
        analytics: Dict[str, Any],
        file_analysis: Dict[str, Any],
        output_format: str = 'html'
    ) -> Path:
        """
        Generate HTML report with embedded visualizations.
        
        Args:
            base_name: Base filename for the report
            analytics: Complete analytics data
            file_analysis: File analysis information
            output_format: Target output format ('html' or 'pdf')
            
        Returns:
            Path to generated HTML file
        """
        if output_format == 'pdf':
            output_path = self.output_dir / f"{base_name}_executive_report_pdf_temp.html"
        else:
            output_path = self.output_dir / f"{base_name}_executive_report.html"
        
        try:
            # Create format-specific visualizer
            format_visualizer = TACVisualizer(output_format=output_format)
            
            # Generate all visualizations with format-specific settings
            charts = self._generate_all_charts(analytics, format_visualizer)
            
            # Create executive summary
            executive_summary = self._create_executive_summary(analytics)
            
            # Create table of contents
            table_of_contents = self._create_table_of_contents(analytics)
            
            # Create bug cases table
            bug_cases_table = self._create_bug_cases_table(analytics)
            
            # Generate the HTML content
            html_content = self._create_html_content(
                base_name, analytics, file_analysis, charts, executive_summary, table_of_contents, bug_cases_table
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            raise
    
    def _generate_all_charts(self, analytics: Dict[str, Any], visualizer: TACVisualizer = None) -> Dict[str, str]:
        """
        Generate all charts for the report.
        
        Args:
            analytics: Complete analytics data
            visualizer: TACVisualizer instance (uses self.visualizer if not provided)
            
        Returns:
            Dictionary of chart HTML strings
        """
        try:
            # Use provided visualizer or default
            viz = visualizer or self.visualizer
            charts = {}
            
            # Summary statistics cards
            charts['summary_stats'] = viz.create_summary_statistics_cards(analytics)
            
            # Monthly trends
            charts['monthly_trends'] = viz.create_monthly_cases_chart(
                analytics.get('monthly_trends', {})
            )
            
            # Severity distribution
            charts['severity_distribution'] = viz.create_severity_distribution_chart(
                analytics.get('severity_analysis', {})
            )
            
            # Status distribution
            charts['status_distribution'] = viz.create_status_distribution_chart(
                analytics.get('status_analysis', {})
            )
            
            # Product hierarchy
            charts['product_hierarchy'] = viz.create_product_hierarchy_chart(
                analytics.get('product_analysis', {})
            )
            
            # Bug analysis
            charts['bug_analysis'] = viz.create_bug_analysis_chart(
                analytics.get('bug_analysis', {})
            )
            
            # Engineer performance
            charts['engineer_assignment'] = viz.create_engineer_assignment_chart(
                analytics.get('engineer_assignment', {})
            )
            
            # Case owner assignment
            charts['case_owner_assignment'] = viz.create_case_owner_assignment_chart(
                analytics.get('case_owner_assignment', {})
            )
            
            # Internal vs External
            charts['internal_external'] = viz.create_internal_external_chart(
                analytics.get('internal_vs_external', {})
            )
            
            # Queue distribution
            charts['queue_distribution'] = viz.create_queue_distribution_chart(
                analytics.get('queue_analysis', {})
            )
            
            logger.debug(f"Generated {len(charts)} charts")
            return charts
            
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")
            # Return empty charts dict to prevent complete failure
            return {key: '<div class="warning">Chart generation failed</div>' for key in [
                'summary_stats', 'monthly_trends', 'severity_distribution', 'status_distribution', 
                'product_hierarchy', 'bug_analysis', 'engineer_assignment', 'case_owner_assignment',
                'internal_external', 'queue_distribution'
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
            
            # Bug analysis - get total count instead of percentage
            bug_data = analytics.get('bug_analysis', {})
            bug_total = 0
            if bug_data.get('available') and bug_data.get('bug_vs_non_bug'):
                bug_total = bug_data['bug_vs_non_bug'].get('Bug Cases', 0)
            
            # Severity analysis
            severity_data = analytics.get('severity_analysis', {})
            high_priority_cases = 0
            if severity_data.get('available'):
                counts = severity_data.get('counts', {})
                high_priority_cases = counts.get('1 - Critical', 0) + counts.get('2 - High', 0)
            
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
                        <li><strong>Bug Impact:</strong> {bug_total} cases were related to product bugs</li>
                        <li><strong>High Priority Cases:</strong> {format_number(high_priority_cases)} critical and high severity cases</li>
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
    
    def _create_bug_cases_table(self, analytics: Dict[str, Any]) -> str:
        """
        Create a table showing detailed information for bug cases.
        
        Args:
            analytics: Complete analytics data
            
        Returns:
            HTML string with bug cases table or empty string if no bug cases
        """
        try:
            bug_data = analytics.get('bug_analysis', {})
            
            # Check if we have bug data and bug cases
            if not bug_data.get('available') or not bug_data.get('bug_cases_details'):
                return ""
            
            bug_cases_details = bug_data['bug_cases_details']
            
            if not bug_cases_details:
                return ""
            
            # Start building the table HTML
            table_html = """
            <div class="section">
                <h3>Bug Cases Details</h3>
                <div class="data-summary">
                    <table class="bug-cases-table">
                        <thead>
                            <tr>
                                <th>Case Number</th>
                                <th>TAC Case Subject</th>
                                <th>Status</th>
                                <th>Product</th>
                                <th>Product Version</th>
                                <th>BUG ID</th>
                            </tr>
                        </thead>
                        <tbody>
            """
            
            # Add rows for each bug case
            for case in bug_cases_details:
                case_number = str(case.get('case_number', 'N/A'))
                subject = str(case.get('subject', 'N/A'))
                status = str(case.get('status', 'N/A'))
                product = str(case.get('product', 'N/A'))
                product_version = str(case.get('product_version', 'N/A'))
                bug_id = str(case.get('bug_id', 'N/A'))
                
                # Truncate long subjects for table display
                if len(subject) > 50:
                    subject = subject[:47] + "..."
                
                table_html += f"""
                            <tr>
                                <td>{case_number}</td>
                                <td title="{str(case.get('subject', 'N/A'))}">{subject}</td>
                                <td>{status}</td>
                                <td>{product}</td>
                                <td>{product_version}</td>
                                <td>{bug_id}</td>
                            </tr>
                """
            
            table_html += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            
            return table_html
            
        except Exception as e:
            logger.error(f"Failed to create bug cases table: {e}")
            return ""
    
    def _create_table_of_contents(self, analytics: Dict[str, Any]) -> str:
        """
        Create a table of contents for the report.
        
        Args:
            analytics: Complete analytics data
            
        Returns:
            HTML string with table of contents
        """
        try:
            # Check which sections are available
            sections = []
            
            # Always available sections
            sections.append(("executive-summary", "Executive Summary"))
            sections.append(("key-metrics", "Key Performance Metrics"))
            
            # Monthly trends
            monthly_data = analytics.get('monthly_trends', {})
            if monthly_data.get('available'):
                sections.append(("monthly-trends", "Monthly Case Volume Trends"))
            
            # Severity analysis
            severity_data = analytics.get('severity_analysis', {})
            if severity_data.get('available'):
                sections.append(("severity-analysis", "Case Severity Distribution"))
            
            # Status analysis
            status_data = analytics.get('status_analysis', {})
            if status_data.get('available'):
                sections.append(("status-analysis", "Case Status Distribution"))
            
            # Product analysis
            product_data = analytics.get('product_analysis', {})
            if product_data.get('available'):
                sections.append(("product-analysis", "Product Hierarchy Analysis"))
            
            # Bug analysis
            bug_data = analytics.get('bug_analysis', {})
            if bug_data.get('available'):
                sections.append(("bug-analysis", "Bug-Related Case Analysis"))
            
            # Engineer assignment
            engineer_data = analytics.get('engineer_assignment', {})
            if engineer_data.get('available'):
                sections.append(("engineer-assignment", "Engineer Case Distribution"))
            
            # Case owner assignment
            case_owner_data = analytics.get('case_owner_assignment', {})
            if case_owner_data.get('available'):
                sections.append(("case-owner-assignment", "Case Owner Distribution"))
            
            # Internal vs External
            internal_external_data = analytics.get('internal_vs_external', {})
            if internal_external_data.get('available'):
                sections.append(("internal-external", "Internal vs External Cases"))
            
            # Queue analysis
            queue_data = analytics.get('queue_analysis', {})
            if queue_data.get('available'):
                sections.append(("queue-analysis", "Queue Distribution"))
            
            # Build table of contents HTML
            toc_html = """
            <div class="section" id="table-of-contents">
                <h2>Table of Contents</h2>
                <div class="toc-container">
                    <nav class="toc-nav">
                        <ol class="toc-list">
            """
            
            for section_id, section_title in sections:
                toc_html += f"""
                            <li class="toc-item">
                                <a href="#{section_id}" class="toc-link">{section_title}</a>
                            </li>
                """
            
            toc_html += """
                        </ol>
                    </nav>
                </div>
            </div>
            """
            
            return toc_html
            
        except Exception as e:
            logger.error(f"Failed to create table of contents: {e}")
            return ""
    
    def _create_html_content(
        self,
        base_name: str,
        analytics: Dict[str, Any],
        file_analysis: Dict[str, Any],
        charts: Dict[str, str],
        executive_summary: str,
        table_of_contents: str,
        bug_cases_table: str
    ) -> str:
        """
        Create the complete HTML content for the report.
        
        Args:
            base_name: Base filename
            analytics: Complete analytics data
            file_analysis: File analysis information
            charts: Dictionary of chart HTML strings
            executive_summary: Executive summary HTML
            table_of_contents: Table of contents HTML
            bug_cases_table: Bug cases table HTML
            
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
    <title>TAC Cases Report - {base_name.replace('_', ' ').title()}</title>
    {REPORT_CSS}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>TAC Cases Report</h1>
            <p class="subtitle">{base_name.replace('_', ' ').title()}</p>
            <p class="generation-info">Generated on {generation_time}</p>
        </div>
        
        <div class="content">
            <!-- Table of Contents -->
            {table_of_contents}
            
            <!-- Executive Summary -->
            <div id="executive-summary">
                {executive_summary}
            </div>
            
            <!-- Key Metrics -->
            <div class="section" id="key-metrics">
                <h2>Key Performance Metrics</h2>
                {charts['summary_stats']}
            </div>
            
            <!-- Monthly Trends -->
            <div class="section" id="monthly-trends">
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
            <div class="section" id="severity-analysis">
                <h2>Case Severity Distribution</h2>
                <div class="chart-container">
                    {charts['severity_distribution']}
                </div>
                <p class="chart-description">
                    Severity distribution provides insight into the criticality of support requests and 
                    helps prioritize resource allocation for high-impact issues.
                </p>
            </div>
            
            <!-- Status Analysis -->
            <div class="section" id="status-analysis">
                <h2>Case Status Distribution</h2>
                <div class="chart-container">
                    {charts['status_distribution']}
                </div>
                <p class="chart-description">
                    Status distribution shows the current state of cases, helping track progress and 
                    identify bottlenecks in the resolution process.
                </p>
            </div>
            
            <!-- Product Analysis -->
            <div class="section" id="product-analysis">
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
            <div class="section" id="bug-analysis">
                <h2>Bug-Related Case Analysis</h2>
                <div class="chart-container">
                    {charts['bug_analysis']}
                </div>
                {bug_cases_table}
            </div>
            
            <!-- Engineer Performance -->
            <div class="section" id="engineer-assignment">
                <h2>Engineer Case Distribution</h2>
                <div class="chart-container">
                    {charts['engineer_assignment']}
                </div>
                <p class="chart-description">
                    Case distribution by engineer provides insights into workload balance and 
                    individual performance metrics for team management.
                </p>
            </div>
            
            <!-- Case Owner Assignment -->
            <div class="section" id="case-owner-assignment">
                <h2>Case Owner Distribution</h2>
                <div class="chart-container">
                    {charts['case_owner_assignment']}
                </div>
                <p class="chart-description">
                    Case distribution by case owner shows who is creating or owning the most cases, 
                    providing insights into customer activity and case ownership patterns.
                </p>
            </div>
            
            <!-- Internal vs External -->
            <div class="section" id="internal-external">
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
            <div class="section" id="queue-analysis">
                <h2>Queue Distribution</h2>
                <div class="chart-container">
                    {charts['queue_distribution']}
                </div>
                <p class="chart-description">
                    Queue distribution shows how cases are distributed across different support teams, 
                    enabling optimization of team structures and specialization areas.
                </p>
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
                logger.error("Playwright not available - this is required for PDF generation with JavaScript charts")
                
                # Create a text file with instructions instead
                instructions_path = self.output_dir / f"{base_name}_pdf_instructions.txt"
                
                with open(instructions_path, 'w') as f:
                    f.write(f"""
PDF Generation Instructions
===========================

To generate a PDF from the HTML report, you need to install Playwright:

1. Install Playwright:
   pip install playwright
   playwright install chromium

Then re-run the report generation.

Note: WeasyPrint and other PDF libraries cannot render JavaScript-based 
Plotly charts, so Playwright (or similar browser-based solution) is required.

Alternatively, you can:
- Open the HTML file in a web browser and use Print to PDF

HTML Report Location: {html_path}
""")
                    
                    logger.info(f"Created PDF instructions file: {instructions_path}")
                    return instructions_path
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            raise