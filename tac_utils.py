"""
Utility functions for TAC Executive Report Generator
"""

import re
import logging
import chardet
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from dateutil import parser as date_parser
import psutil
import os

logger = logging.getLogger(__name__)


def detect_file_encoding(file_path: Path) -> str:
    """
    Detect file encoding with robust fallback for CSV files.
    
    Args:
        file_path: Path to file
        
    Returns:
        Detected encoding string
    """
    try:
        # Read a larger sample for better detection
        with open(file_path, 'rb') as f:
            sample = f.read(50000)  # Read first 50KB for better detection
            result = chardet.detect(sample)
            detected_encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            
        logger.debug(f"Chardet detected: {detected_encoding} (confidence: {confidence})")
        
        # Test the detected encoding by trying to read the entire file
        if detected_encoding:
            try:
                with open(file_path, 'r', encoding=detected_encoding) as f:
                    f.read()  # Try to read entire file
                logger.debug(f"Successfully validated encoding: {detected_encoding}")
                return detected_encoding
            except UnicodeDecodeError as e:
                logger.debug(f"Detected encoding {detected_encoding} failed validation: {e}")
        
        # If detection failed or validation failed, try common encodings
        encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'ascii']
        for enc in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    f.read()  # Try to read entire file
                logger.debug(f"Successfully validated fallback encoding: {enc}")
                return enc
            except UnicodeDecodeError:
                continue
                
        # Final fallback
        logger.warning("All encoding attempts failed, using utf-8 with error handling")
        return 'utf-8'
        
    except Exception as e:
        logger.warning(f"Failed to detect encoding, using utf-8: {e}")
        return 'utf-8'


def parse_date_flexible(date_str: str, date_format: Optional[str] = None) -> Optional[datetime]:
    """
    Parse date string with multiple format attempts.
    
    Args:
        date_str: Date string to parse
        date_format: Optional specific format to try first
        
    Returns:
        Parsed datetime object or None
    """
    if not date_str or str(date_str).lower() in ['nan', 'none', 'null', '']:
        return None
    
    date_str = str(date_str).strip()
    
    # Try specific format first if provided
    if date_format:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            pass
    
    # Common date formats to try
    common_formats = [
        '%m/%d/%Y %I:%M %p',    # 02/18/2025 10:56 AM
        '%m/%d/%Y %H:%M:%S',    # 02/18/2025 10:56:30
        '%m/%d/%Y',             # 02/18/2025
        '%Y-%m-%d %H:%M:%S',    # 2025-02-18 10:56:30
        '%Y-%m-%d',             # 2025-02-18
        '%d/%m/%Y %H:%M:%S',    # 18/02/2025 10:56:30
        '%d/%m/%Y',             # 18/02/2025
        '%Y/%m/%d %H:%M:%S',    # 2025/02/18 10:56:30
        '%Y/%m/%d',             # 2025/02/18
        '%m-%d-%Y %H:%M:%S',    # 02-18-2025 10:56:30
        '%m-%d-%Y',             # 02-18-2025
    ]
    
    # Try each format
    for fmt in common_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try dateutil parser as last resort
    try:
        return date_parser.parse(date_str)
    except (ValueError, TypeError):
        logger.debug(f"Failed to parse date: {date_str}")
        return None


def format_number(number: Any) -> str:
    """
    Format number with commas for readability.
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string
    """
    try:
        if isinstance(number, (int, float)):
            if number == int(number):
                return f"{int(number):,}"
            else:
                return f"{number:,.2f}"
        return str(number)
    except:
        return str(number)


def clean_text(text: str) -> str:
    """
    Clean and normalize text data.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text or str(text).lower() in ['nan', 'none', 'null']:
        return 'N/A'
    
    text = str(text).strip()
    
    # Replace common null representations
    if text.lower() in ['no value', 'not available', 'na', 'n/a', '']:
        return 'N/A'
    
    return text


def normalize_severity(severity: str) -> str:
    """
    Normalize severity values to standard format.
    
    Args:
        severity: Raw severity value
        
    Returns:
        Normalized severity
    """
    if not severity or str(severity).lower() in ['nan', 'none', 'null', 'no value']:
        return 'Unknown'
    
    severity = clean_text(str(severity)).lower()
    
    # Map common severity variations
    severity_mapping = {
        '1': '1 - Critical',
        'critical': '1 - Critical',
        '1 - critical': '1 - Critical',
        '2': '2 - High',
        'high': '2 - High',
        '2 - high': '2 - High',
        '3': '3 - Medium',
        'medium': '3 - Medium',
        '3 - medium': '3 - Medium',
        '4': '4 - Low',
        'low': '4 - Low',
        '4 - low': '4 - Low'
    }
    
    normalized = severity_mapping.get(severity, severity)
    return normalized.title()


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        verbose: Enable debug logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('tac_report.log')
        ]
    )


def check_memory_usage() -> Dict[str, Any]:
    """
    Check current memory usage.
    
    Returns:
        Memory usage information
    """
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        return {
            'process_mb': memory_mb,
            'warning': memory_mb > 1000  # Warn if over 1GB
        }
    except Exception:
        return {
            'process_mb': 0,
            'warning': False
        }


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted file size
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f} hours"
    else:
        days = seconds / 86400
        return f"{days:.1f} days"


def clean_filename(filename: str) -> str:
    """
    Clean filename for safe file creation.
    
    Args:
        filename: Original filename
        
    Returns:
        Clean filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('._')
    
    return filename[:100]  # Limit length


def calculate_percentage(part: int, total: int) -> float:
    """
    Calculate percentage with zero division protection.
    
    Args:
        part: Part value
        total: Total value
        
    Returns:
        Percentage as float
    """
    if total == 0:
        return 0.0
    return round((part / total) * 100, 1)


def extract_month_year(date_str: str) -> Optional[str]:
    """
    Extract month-year string from date.
    
    Args:
        date_str: Date string
        
    Returns:
        Month-year string (YYYY-MM) or None
    """
    parsed_date = parse_date_flexible(date_str)
    if parsed_date:
        return parsed_date.strftime('%Y-%m')
    return None


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Get comprehensive file information.
    
    Args:
        file_path: Path to file
        
    Returns:
        File information dictionary
    """
    try:
        stat = file_path.stat()
        return {
            'name': file_path.name,
            'size': stat.st_size,
            'size_formatted': format_file_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'extension': file_path.suffix.lower()
        }
    except Exception as e:
        logger.error(f"Failed to get file info for {file_path}: {e}")
        return {
            'name': file_path.name,
            'size': 0,
            'size_formatted': '0 B',
            'modified': datetime.now(),
            'extension': file_path.suffix.lower()
        }