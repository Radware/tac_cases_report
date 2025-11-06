#!/usr/bin/env python3
"""
TAC Executive Report Generator API

Flask-based REST API for generating TAC case executive reports.
Supports CSV and Excel file uploads with HTML/PDF report generation.

PURPOSE:
    This API provides a web service interface to the TAC analyzer, allowing:
    - Remote file uploads and analysis
    - Integration with other systems via HTTP
    - Cloud deployment and scalability
    - Multiple concurrent report generation
    
USAGE:
    - Can be deployed as a microservice using Docker/Kubernetes
    - Alternative to command-line analyzer for web applications
    - Enables browser-based TAC report generation
    - Supports REST API integration with CI/CD pipelines

Endpoints:
    POST /api/tac/analyze - Upload file and generate report
    POST /api/tac/analyze-batch - Upload multiple files and generate batch report
    GET /api/tac/health - Health check endpoint
    GET / - API documentation
"""

import os
import json
import traceback
import tempfile
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
import logging
from threading import Lock

# Import the TAC analyzer modules
from tac_analyzer import TACAnalyzer
from tac_data_processor import TACDataProcessor
from tac_report_generator import TACReportGenerator
from tac_config import OUTPUT_FORMATS

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Create a persistent reports directory
# Use /app/reports for Docker, or reports/ for local development
REPORTS_DIR = Path(os.getenv('REPORTS_DIR', '/app/reports'))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# In-memory cache for report metadata (report_id -> file_path mapping)
# In production, use Redis or a database
report_cache = {}
cache_lock = Lock()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def perform_analysis(file_path: Path, output_formats: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Perform TAC case analysis on a single file.
    
    Args:
        file_path: Path to the input file
        output_formats: List of output formats ['html', 'pdf']
        
    Returns:
        dict: Result containing success status, report data, and any errors
    """
    if output_formats is None:
        output_formats = ['html']
    
    result = {
        'success': False,
        'error': None,
        'report_data': None,
        'stats': {},
        'generated_files': {},
        'report_ids': {}
    }
    
    try:
        # Use persistent reports directory instead of temp
        output_dir = REPORTS_DIR
        
        logger.info(f"Processing file: {file_path}")
        
        # Process the data
        processor = TACDataProcessor(file_path)
        file_analysis = processor.load_and_analyze()
        
        if file_analysis['total_cases'] == 0:
            result['error'] = "No valid TAC cases found in the file"
            return result
        
        # Process executive analytics (instead of compute_insights)
        analytics = processor.process_executive_analytics()
        
        # Generate reports using the correct method
        report_generator = TACReportGenerator(output_dir)
        generated_files = report_generator.generate_reports(
            input_filename=file_path.name,
            analytics=analytics,
            file_analysis=file_analysis,
            formats=output_formats
        )
        
        # Store generated file paths and create report IDs
        with cache_lock:
            for fmt, report_path in generated_files.items():
                if report_path and report_path.exists():
                    # Generate unique report ID
                    report_id = str(uuid.uuid4())
                    
                    # Store in cache with metadata
                    report_cache[report_id] = {
                        'path': str(report_path),
                        'format': fmt,
                        'filename': report_path.name,
                        'created_at': datetime.now(),
                        'expires_at': datetime.now() + timedelta(hours=24)  # 24-hour expiry
                    }
                    
                    result['generated_files'][fmt] = str(report_path)
                    result['report_ids'][fmt] = report_id
                    logger.info(f"Generated {fmt.upper()} report: {report_path} (ID: {report_id})")
        
        # Prepare result data
        result['success'] = len(result['generated_files']) > 0
        result['stats'] = {
            'total_cases': file_analysis['total_cases'],
            'date_range': file_analysis.get('date_range', {}),
            'columns_found': file_analysis.get('columns_found', 0),
            'analytics_sections': len(analytics)
        }
        result['report_data'] = {
            'file_name': file_path.name,
            'processed_at': datetime.now().isoformat(),
            'analytics_summary': {
                'total_cases': analytics.get('summary', {}).get('total_cases', 0),
                'severity_levels': len(analytics.get('severity_analysis', {}).get('by_severity', {})),
                'products_analyzed': len(analytics.get('product_analysis', {}).get('top_products', [])),
                'engineers_assigned': len(analytics.get('engineer_assignment', {}).get('top_engineers', []))
            }
        }
        
    except Exception as e:
        result['error'] = str(e)
        result['traceback'] = traceback.format_exc()
        logger.error(f"Analysis failed: {e}")
        logger.error(traceback.format_exc())
    
    return result


@app.route('/')
def index():
    """Display API documentation."""
    html_doc = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TAC Report Generator API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .endpoint { background: #ecf0f1; padding: 15px; margin: 15px 0; border-radius: 5px; }
            .method { color: #27ae60; font-weight: bold; }
            .path { color: #2980b9; font-family: monospace; }
            code { background: #2c3e50; color: #ecf0f1; padding: 2px 6px; border-radius: 3px; }
            pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>📊 TAC Executive Report Generator API</h1>
        <p>RESTful API for generating professional TAC (Technical Assistance Center) case reports with interactive visualizations.</p>
        
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> <span class="path">/api/tac/analyze</span></h3>
            <p>Upload a single TAC case file (CSV or Excel) and generate an executive report.</p>
            <p><strong>Request:</strong> multipart/form-data</p>
            <ul>
                <li><code>file</code> - CSV or Excel file containing TAC cases</li>
                <li><code>format</code> (optional) - Output format: "html", "pdf", or "both" (default: "html")</li>
            </ul>
            <p><strong>Response:</strong> JSON with report metadata and download URLs</p>
            <p><strong>Note:</strong> Use the <code>reports</code> URLs to download the generated files. Reports are cached for 24 hours.</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> <span class="path">/api/tac/analyze-batch</span></h3>
            <p>Upload multiple TAC case files and generate individual reports plus a batch summary.</p>
            <p><strong>Request:</strong> multipart/form-data</p>
            <ul>
                <li><code>files</code> - Multiple CSV or Excel files</li>
                <li><code>format</code> (optional) - Output format: "html", "pdf", or "both" (default: "html")</li>
            </ul>
            <p><strong>Response:</strong> JSON with batch processing results</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/tac/report/{report_id}</span></h3>
            <p>Download a generated report file using its unique ID.</p>
            <p><strong>Parameters:</strong></p>
            <ul>
                <li><code>report_id</code> - UUID returned from analyze endpoint</li>
            </ul>
            <p><strong>Response:</strong> Report file (HTML or PDF) for download</p>
            <p><strong>Note:</strong> Reports expire after 24 hours.</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">GET</span> <span class="path">/api/tac/health</span></h3>
            <p>Health check endpoint for monitoring.</p>
            <p><strong>Response:</strong> JSON with service status and cached report count</p>
        </div>
        
        <div class="endpoint">
            <h3><span class="method">POST</span> <span class="path">/api/tac/reports/cleanup</span></h3>
            <p>Clean up expired reports from cache (admin endpoint).</p>
            <p><strong>Response:</strong> JSON with cleanup results</p>
        </div>
        
        <h2>Example Usage</h2>
        <pre>
# Upload and analyze a single file
curl -X POST http://localhost:5000/api/tac/analyze \\
  -F "file=@tac_cases.csv" \\
  -F "format=html"

# Response will include:
# {
#   "reports": {
#     "html": "/api/tac/report/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
#   }
# }

# Download the report using the URL
curl -O -J http://localhost:5000/api/tac/report/a1b2c3d4-e5f6-7890-abcd-ef1234567890

# Upload multiple files for batch processing
curl -X POST http://localhost:5000/api/tac/analyze-batch \\
  -F "files=@tac_q1.csv" \\
  -F "files=@tac_q2.csv" \\
  -F "format=both"

# Check service health
curl http://localhost:5000/api/tac/health

# Clean up expired reports
curl -X POST http://localhost:5000/api/tac/reports/cleanup
        </pre>
        
        <h2>Supported File Formats</h2>
        <ul>
            <li>CSV (.csv)</li>
            <li>Excel (.xlsx, .xls)</li>
        </ul>
        
        <h2>Report Formats</h2>
        <ul>
            <li><strong>HTML</strong> - Interactive report with Plotly charts</li>
            <li><strong>PDF</strong> - Static report for sharing (requires Playwright)</li>
        </ul>
    </body>
    </html>
    """
    return render_template_string(html_doc)


@app.route('/api/tac/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    with cache_lock:
        cached_reports = len(report_cache)
    
    return jsonify({
        'status': 'healthy',
        'service': 'tac-report-generator',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'cached_reports': cached_reports
    })


@app.route('/api/tac/reports/cleanup', methods=['POST'])
def cleanup_expired_reports():
    """
    Clean up expired reports from cache and disk.
    Can be called periodically by a scheduler.
    """
    try:
        cleaned_count = 0
        with cache_lock:
            expired_ids = []
            for report_id, report_info in report_cache.items():
                if datetime.now() > report_info['expires_at']:
                    expired_ids.append(report_id)
            
            for report_id in expired_ids:
                report_info = report_cache[report_id]
                report_path = Path(report_info['path'])
                
                # Delete file if exists
                if report_path.exists():
                    try:
                        report_path.unlink()
                        logger.info(f"Deleted expired report: {report_path}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {report_path}: {e}")
                
                # Remove from cache
                del report_cache[report_id]
                cleaned_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleaned_count} expired reports',
            'cleaned_count': cleaned_count
        }), 200
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tac/analyze', methods=['POST'])
def analyze_file():
    """
    Analyze a single TAC case file and generate report.
    
    Expects:
        - file: CSV or Excel file (multipart/form-data)
        - format: Optional output format (html, pdf, both)
    """
    try:
        # Validate file presence
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if not file.filename or file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get output format
        output_format = request.form.get('format', 'html').lower()
        if output_format == 'both':
            output_formats = ['html', 'pdf']
        else:
            output_formats = [output_format]
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        file_path = Path(temp_dir) / filename
        file.save(str(file_path))
        
        logger.info(f"Received file: {filename} ({file_path.stat().st_size} bytes)")
        
        # Perform analysis
        result = perform_analysis(file_path, output_formats)
        
        # Clean up uploaded file
        if file_path.exists():
            file_path.unlink()
        
        if result['success']:
            # Store report files temporarily (in production, use cloud storage)
            report_links = {}
            for fmt, report_id in result['report_ids'].items():
                report_links[fmt] = f"/api/tac/report/{report_id}"
            
            return jsonify({
                'success': True,
                'message': 'Analysis completed successfully',
                'data': result['report_data'],
                'stats': result['stats'],
                'reports': report_links,  # Use these URLs to download reports
                'report_ids': result['report_ids']  # Keep IDs for reference
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Analysis failed'),
                'details': result.get('traceback')
            }), 500
            
    except Exception as e:
        logger.error(f"API error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/tac/analyze-batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple TAC case files and generate batch report.
    
    Expects:
        - files: Multiple CSV or Excel files (multipart/form-data)
        - format: Optional output format (html, pdf, both)
    """
    try:
        # Validate files presence
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        files = request.files.getlist('files')
        
        if len(files) == 0:
            return jsonify({
                'success': False,
                'error': 'No files provided'
            }), 400
        
        # Get output format
        output_format = request.form.get('format', 'html').lower()
        if output_format == 'both':
            output_formats = ['html', 'pdf']
        else:
            output_formats = [output_format]
        
        # Process each file
        results = []
        temp_dir = tempfile.mkdtemp()
        
        for file in files:
            if not file.filename or file.filename == '' or not allowed_file(file.filename):
                continue
            
            filename = secure_filename(file.filename)
            file_path = Path(temp_dir) / filename
            file.save(str(file_path))
            
            logger.info(f"Processing batch file: {filename}")
            
            result = perform_analysis(file_path, output_formats)
            result['filename'] = filename
            results.append(result)
        
        # Calculate batch statistics
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return jsonify({
            'success': successful > 0,
            'message': f'Batch processing completed',
            'total_files': len(results),
            'successful': successful,
            'failed': failed,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Batch API error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/tac/report/<report_id>', methods=['GET'])
def download_report(report_id):
    """
    Download a generated report file.
    
    Args:
        report_id: Unique report identifier (UUID)
    """
    try:
        # Look up report in cache
        with cache_lock:
            if report_id not in report_cache:
                return jsonify({
                    'success': False,
                    'error': 'Report not found or has expired'
                }), 404
            
            report_info = report_cache[report_id]
            
            # Check if expired
            if datetime.now() > report_info['expires_at']:
                # Clean up expired report
                report_path = Path(report_info['path'])
                if report_path.exists():
                    report_path.unlink()
                del report_cache[report_id]
                
                return jsonify({
                    'success': False,
                    'error': 'Report has expired'
                }), 410  # Gone
            
            report_path = Path(report_info['path'])
            
            # Verify file exists
            if not report_path.exists():
                del report_cache[report_id]
                return jsonify({
                    'success': False,
                    'error': 'Report file not found on disk'
                }), 404
        
        # Determine MIME type
        mime_type = 'text/html' if report_info['format'] == 'html' else 'application/pdf'
        
        # Send file
        return send_file(
            report_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=report_info['filename']
        )
        
    except Exception as e:
        logger.error(f"Download error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size: 50MB'
    }), 413


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('input_data', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    # Run the Flask app
    logger.info("Starting TAC Report Generator API...")
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')
