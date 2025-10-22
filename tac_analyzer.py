#!/usr/bin/env python3
"""
TAC Executive Report Analyzer

Main orchestrator script that processes TAC case data from CSV/Excel files
and generates comprehensive executive-level HTML and PDF reports with 
interactive visualizations and business insights.

Usage:
    python tac_analyzer.py [options]

Example:
    python tac_analyzer.py --input-dir input_data --output-dir reports --verbose
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import our modules
from tac_utils import setup_logging, get_file_info, format_duration
from tac_data_processor import TACDataProcessor
from tac_report_generator import TACReportGenerator
from tac_config import OUTPUT_FORMATS

logger = logging.getLogger(__name__)


class TACAnalyzer:
    """
    Main orchestrator class for TAC case analysis and report generation.
    """
    
    def __init__(self, input_dir: Path, output_dir: Path, verbose: bool = False):
        """
        Initialize the analyzer.
        
        Args:
            input_dir: Directory containing input files
            output_dir: Directory for output reports
            verbose: Enable verbose logging
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        
        # Setup logging
        setup_logging(verbose)
        logger.info("Initialized TAC Executive Report Analyzer")
        
        # Ensure directories exist
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.report_generator = TACReportGenerator(self.output_dir)
        
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def discover_input_files(self) -> List[Path]:
        """
        Discover TAC case files in the input directory.
        
        Returns:
            List of discovered file paths
        """
        logger.info("Discovering input files...")
        
        # Supported file extensions
        supported_extensions = ['.csv', '.xlsx', '.xls']
        
        files = []
        for ext in supported_extensions:
            pattern = f"*{ext}"
            found_files = list(self.input_dir.glob(pattern))
            files.extend(found_files)
        
        # Remove duplicates and sort
        unique_files = list(set(files))
        unique_files.sort()
        
        logger.info(f"Found {len(unique_files)} TAC case files")
        for file_path in unique_files:
            logger.info(f"  - {file_path.name}")
        
        return unique_files
    
    def validate_input_file(self, file_path: Path) -> bool:
        """
        Validate that input file is accessible and has reasonable size.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if file is valid
        """
        try:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            
            if not file_path.is_file():
                logger.error(f"Path is not a file: {file_path}")
                return False
            
            # Check file size (warn if over 100MB)
            file_size = file_path.stat().st_size
            if file_size > 100 * 1024 * 1024:
                logger.warning(f"Large file detected ({file_size / 1024 / 1024:.1f} MB): {file_path}")
            
            if file_size == 0:
                logger.error(f"Empty file: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate file {file_path}: {e}")
            return False
    
    def process_single_file(
        self, 
        file_path: Path, 
        formats: List[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single TAC case file and generate reports.
        
        Args:
            file_path: Path to the TAC case file
            formats: List of output formats ('html', 'pdf', or both)
            
        Returns:
            Dictionary with processing results
        """
        if formats is None:
            formats = OUTPUT_FORMATS.copy()
        
        start_time = time.time()
        
        logger.info(f"Processing file: {file_path.name}")
        
        try:
            # Validate input file
            if not self.validate_input_file(file_path):
                return {
                    'success': False,
                    'file_path': file_path,
                    'error': 'File validation failed',
                    'processing_time': 0
                }
            
            # Initialize data processor
            processor = TACDataProcessor(file_path)
            
            # Load and analyze file
            logger.info("Loading and analyzing file structure...")
            file_analysis = processor.load_and_analyze()
            
            # Process executive analytics
            logger.info("Processing executive analytics...")
            analytics = processor.process_executive_analytics()
            
            # Generate reports
            logger.info(f"Generating reports in formats: {formats}")
            generated_files = self.report_generator.generate_reports(
                file_path.name,
                analytics,
                file_analysis,
                formats
            )
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'file_path': file_path,
                'generated_files': generated_files,
                'analytics': analytics,
                'file_analysis': file_analysis,
                'processing_time': processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Failed to process {file_path.name}: {e}")
            
            return {
                'success': False,
                'file_path': file_path,
                'error': str(e),
                'processing_time': processing_time
            }
    
    def process_all_files(self, formats: List[str] = None) -> Dict[str, Any]:
        """
        Process all TAC case files in the input directory.
        
        Args:
            formats: List of output formats ('html', 'pdf', or both)
            
        Returns:
            Dictionary with batch processing results
        """
        if formats is None:
            formats = OUTPUT_FORMATS.copy()
        
        start_time = time.time()
        
        # Discover input files
        input_files = self.discover_input_files()
        
        if not input_files:
            logger.warning("No TAC case files found in input directory")
            return {
                'success': False,
                'total_files': 0,
                'processed_files': 0,
                'failed_files': 0,
                'results': [],
                'total_processing_time': 0
            }
        
        # Process each file
        results = []
        successful_files = 0
        failed_files = 0
        
        for file_path in input_files:
            result = self.process_single_file(file_path, formats)
            results.append(result)
            
            if result['success']:
                successful_files += 1
            else:
                failed_files += 1
        
        total_processing_time = time.time() - start_time
        
        return {
            'success': failed_files == 0,
            'total_files': len(input_files),
            'processed_files': successful_files,
            'failed_files': failed_files,
            'results': results,
            'total_processing_time': total_processing_time
        }
    
    def generate_batch_summary_report(self, batch_results: Dict[str, Any]) -> Path:
        """
        Generate a summary report for batch processing.
        
        Args:
            batch_results: Results from process_all_files
            
        Returns:
            Path to generated summary report
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        summary_path = self.output_dir / f"tac_batch_summary_{timestamp}.html"
        
        try:
            # Collect summary statistics
            total_cases = 0
            products_summary = {}
            severity_summary = {}
            
            for result in batch_results['results']:
                if result['success']:
                    analytics = result.get('analytics', {})
                    summary = analytics.get('summary', {})
                    total_cases += summary.get('total_cases', 0)
                    
                    # Aggregate product data
                    product_data = analytics.get('product_analysis', {})
                    if product_data.get('available'):
                        for product, count in product_data.get('product_counts', {}).items():
                            products_summary[product] = products_summary.get(product, 0) + count
                    
                    # Aggregate severity data
                    severity_data = analytics.get('severity_analysis', {})
                    if severity_data.get('available'):
                        for severity, count in severity_data.get('counts', {}).items():
                            severity_summary[severity] = severity_summary.get(severity, 0) + count
            
            # Create HTML content
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TAC Batch Processing Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .summary-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #003f7f; }}
        .stat-label {{ color: #666; }}
        .files-list {{ margin: 30px 0; }}
        .file-item {{ padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 4px; }}
        .success {{ border-left: 4px solid #28a745; }}
        .error {{ border-left: 4px solid #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #003f7f; color: white; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>TAC Batch Processing Summary</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary-stats">
        <div class="stat-card">
            <div class="stat-number">{batch_results['total_files']}</div>
            <div class="stat-label">Files Processed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{batch_results['processed_files']}</div>
            <div class="stat-label">Successful</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{batch_results['failed_files']}</div>
            <div class="stat-label">Failed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_cases:,}</div>
            <div class="stat-label">Total Cases</div>
        </div>
    </div>
    
    <h2>Processing Results</h2>
    <div class="files-list">
"""
            
            for result in batch_results['results']:
                status_class = "success" if result['success'] else "error"
                status_text = "✓ Success" if result['success'] else f"✗ Error: {result.get('error', 'Unknown error')}"
                
                html_content += f"""
        <div class="file-item {status_class}">
            <strong>{result['file_path'].name}</strong> - {status_text}
            <br><small>Processing time: {format_duration(result['processing_time'])}</small>
        </div>
"""
            
            html_content += """
    </div>
    
    <h2>Processing Details</h2>
    <p><strong>Total processing time:</strong> """ + format_duration(batch_results['total_processing_time']) + """</p>
    
</body>
</html>
"""
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Generated batch summary report: {summary_path}")
            return summary_path
            
        except Exception as e:
            logger.error(f"Failed to generate batch summary report: {e}")
            raise


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='TAC Executive Report Analyzer - Generate executive reports from TAC case data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tac_analyzer.py
  python tac_analyzer.py --input-dir data --output-dir results
  python tac_analyzer.py --format html --verbose
  python tac_analyzer.py --format pdf
        """
    )
    
    parser.add_argument(
        '--input-dir',
        type=Path,
        default=Path('input_data'),
        help='Input directory containing TAC case files (default: input_data)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('reports'),
        help='Output directory for generated reports (default: reports)'
    )
    
    parser.add_argument(
        '--format',
        choices=['html', 'pdf', 'both'],
        default='both',
        help='Output format(s) to generate (default: both)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


def main():
    """
    Main entry point for the application.
    """
    # Parse command-line arguments
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Determine output formats
    if args.format == 'both':
        formats = OUTPUT_FORMATS.copy()  # Use config default
    else:
        formats = [args.format]
    
    try:
        # Initialize analyzer
        analyzer = TACAnalyzer(
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            verbose=args.verbose
        )
        
        print("🔍 TAC Executive Report Analyzer")
        print("=" * 50)
        
        # Process all files
        batch_results = analyzer.process_all_files(formats)
        
        # Generate batch summary report
        if batch_results['total_files'] > 1:
            summary_path = analyzer.generate_batch_summary_report(batch_results)
            print(f"\n📊 Batch summary report: {summary_path}")
        
        # Print results summary
        print(f"\n✅ Processing complete!")
        print(f"   Total files: {batch_results['total_files']}")
        print(f"   Successful: {batch_results['processed_files']}")
        print(f"   Failed: {batch_results['failed_files']}")
        print(f"   Total time: {format_duration(batch_results['total_processing_time'])}")
        
        # List generated files
        if batch_results['processed_files'] > 0:
            print(f"\n📁 Generated reports:")
            for result in batch_results['results']:
                if result['success']:
                    for fmt, path in result['generated_files'].items():
                        print(f"   {fmt.upper()}: {path}")
        
        # Exit with appropriate code
        sys.exit(0 if batch_results['success'] else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.exception("Fatal error in main()")
        sys.exit(1)


if __name__ == "__main__":
    main()