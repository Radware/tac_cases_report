"""
TAC Cases Data Processing Module

This module processes TAC (Technical Assistance Center) case data from CSV/Excel files
and prepares executive-level insights and analytics.
"""

import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
import pandas as pd
from dateutil import parser
from collections import defaultdict, Counter

from tac_utils import (
    detect_file_encoding, format_number, parse_date_flexible,
    clean_text, normalize_severity
)

logger = logging.getLogger(__name__)


class TACDataProcessor:
    """
    Processes TAC case data with flexible column mapping and executive insights.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize the TAC data processor.
        
        Args:
            file_path: Path to the CSV or Excel file
        """
        self.file_path = Path(file_path)
        self.encoding = None
        self.data = None
        self.column_mapping = {}
        self.processed_data = {}
        
        # Standard column names we expect
        self.expected_columns = {
            'reference': ['Reference #', 'Reference', 'Case #', 'Case Number', 'Ticket #'],
            'subject': ['Subject', 'Title', 'Summary', 'Description'],
            'status': ['Status', 'Case Status', 'State'],
            'date_created': ['Date Created', 'Created Date', 'Created', 'Open Date'],
            'queue': ['Queue', 'Team', 'Group', 'Assignment Group'],
            'internal_case': ['Internal Case', 'Internal', 'Is Internal'],
            'end_customer': ['End Customer', 'Customer', 'Company', 'Organization'],
            'full_name': ['Full Name', 'Name', 'Contact Name', 'Engineer Name'],
            'email': ['Email Address', 'Email', 'Contact Email'],
            'date_responded': ['Date Last Responded', 'Last Response', 'Last Updated'],
            'assigned_account': ['Assigned Account', 'Assigned Engineer', 'Owner'],
            'product_hierarchy': ['Product Hierarchy', 'Product', 'Product Line'],
            'product_version': ['Product_Version', 'Version', 'Product Version'],
            'jira_case': ['Jira Case', 'Jira', 'Jira Ticket'],
            'nfr': ['NFR', 'Enhancement Request'],
            'severity': ['Severity', 'Priority', 'Urgency'],
            'jira_bug': ['Jira Bug', 'Bug', 'Bug ID'],
            'experienced_bug': ['Experienced Bug', 'Known Bug', 'Bug Found'],
            'related_case': ['Similar/Related Case', 'Related Cases', 'Similar Cases']
        }
        
        logger.info(f"Initializing TAC processor for {self.file_path.name}")
    
    def load_and_analyze(self) -> Dict[str, Any]:
        """
        Load the file and perform initial analysis.
        
        Returns:
            Dictionary with file analysis results
        """
        logger.info("Loading and analyzing TAC cases file...")
        
        try:
            # Determine file type and load accordingly
            if self.file_path.suffix.lower() in ['.xlsx', '.xls']:
                self._load_excel_file()
            else:
                self._load_csv_file()
            
            # Create column mapping
            self._create_column_mapping()
            
            # Validate required columns
            self._validate_columns()
            
            # Clean and standardize data
            self._clean_data()
            
            # Analyze file structure
            analysis = {
                'file_size': self.file_path.stat().st_size,
                'total_cases': len(self.data),
                'columns_found': len(self.data.columns),
                'date_range': self._get_date_range(),
                'column_mapping': self.column_mapping,
                'missing_columns': self._get_missing_columns()
            }
            
            logger.info(f"Analysis complete: {analysis['total_cases']} cases found")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to load and analyze file: {e}")
            raise
    
    def _load_csv_file(self):
        """Load CSV file with proper encoding detection."""
        try:
            # Detect encoding
            self.encoding = detect_file_encoding(self.file_path)
            
            # Read CSV, handling potential issues with the first row
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                lines = f.readlines()
            
            # Check if first line is a title (common in exported files)
            skip_rows = 0
            if len(lines) > 1:
                first_line = lines[0].strip().strip('"')
                
                # If first line doesn't look like headers but second does, skip first
                if (',' not in first_line or 
                    first_line.lower() in ['open cases all', 'all cases', 'case report']):
                    skip_rows = 1
            
            # Load with pandas for better handling of mixed data types
            try:
                self.data = pd.read_csv(
                    self.file_path,
                    encoding=self.encoding,
                    skiprows=skip_rows,
                    low_memory=False
                )
            except UnicodeDecodeError as e:
                logger.warning(f"Encoding {self.encoding} failed, trying UTF-8: {e}")
                # Fallback to UTF-8 with error handling
                try:
                    self.data = pd.read_csv(
                        self.file_path,
                        encoding='utf-8',
                        skiprows=skip_rows,
                        low_memory=False
                    )
                    self.encoding = 'utf-8'
                except UnicodeDecodeError:
                    # Final fallback with error replacement
                    self.data = pd.read_csv(
                        self.file_path,
                        encoding='utf-8',
                        skiprows=skip_rows,
                        low_memory=False,
                        encoding_errors='replace'
                    )
                    self.encoding = 'utf-8'
                    logger.warning("Used UTF-8 encoding with character replacement")
            
            # Remove any footer rows (like "Record Count: 18")
            # Filter out rows where the first column contains "Record Count" or similar
            if len(self.data) > 0:
                first_col = self.data.columns[0]
                # Remove rows where first column contains record count or is not a valid case reference
                mask = ~self.data[first_col].astype(str).str.contains(
                    r'Record Count|Total|Summary|^$', 
                    case=False, 
                    na=False, 
                    regex=True
                )
                self.data = self.data[mask].copy()
            
            logger.info(f"Loaded CSV file with {len(self.data)} rows and {len(self.data.columns)} columns")
            
        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            raise
    
    def _load_excel_file(self):
        """Load Excel file."""
        try:
            # First, check the structure of the Excel file
            temp_df = pd.read_excel(self.file_path, sheet_name=0, nrows=3)
            
            # Check if first row is a title and second row contains headers
            skip_rows = 0
            if len(temp_df) >= 2:
                # Check if the column names look like "Unnamed" (indicating first row might be title)
                if any('unnamed' in str(col).lower() for col in temp_df.columns):
                    # Check if first row contains actual headers
                    first_row = temp_df.iloc[0].fillna('').astype(str)
                    if any(header in first_row.str.lower().tolist() for header in ['reference', 'subject', 'status', 'date']):
                        # First row contains headers, skip the title row
                        skip_rows = 1
            
            # Load the Excel file with proper headers
            if skip_rows > 0:
                self.data = pd.read_excel(self.file_path, sheet_name=0, skiprows=skip_rows)
            else:
                self.data = pd.read_excel(self.file_path, sheet_name=0)
            
            # Remove any footer rows (like "Record Count: 18")
            if len(self.data) > 0:
                first_col = self.data.columns[0]
                # Remove rows where first column contains record count or is not a valid case reference
                mask = ~self.data[first_col].astype(str).str.contains(
                    r'Record Count|Total|Summary|^$', 
                    case=False, 
                    na=False, 
                    regex=True
                )
                self.data = self.data[mask].copy()
            
            logger.info(f"Loaded Excel file with {len(self.data)} rows and {len(self.data.columns)} columns")
            
        except Exception as e:
            logger.error(f"Failed to load Excel file: {e}")
            raise
    
    def _create_column_mapping(self):
        """Create mapping from expected columns to actual columns."""
        actual_columns = [col.strip() for col in self.data.columns]
        
        for standard_name, variants in self.expected_columns.items():
            for variant in variants:
                for actual_col in actual_columns:
                    if actual_col.lower() == variant.lower():
                        self.column_mapping[standard_name] = actual_col
                        break
                if standard_name in self.column_mapping:
                    break
        
        logger.info(f"Mapped {len(self.column_mapping)} columns")
    
    def _validate_columns(self):
        """Validate that essential columns are present."""
        essential_columns = ['reference', 'status', 'date_created']
        missing_essential = []
        
        for col in essential_columns:
            if col not in self.column_mapping:
                missing_essential.append(col)
        
        if missing_essential:
            logger.warning(f"Missing essential columns: {missing_essential}")
            # Try to find alternatives based on partial matches
            self._find_alternative_columns(missing_essential)
    
    def _find_alternative_columns(self, missing_columns: List[str]):
        """Find alternative column names for missing essential columns."""
        actual_columns = list(self.data.columns)
        
        for missing in missing_columns:
            if missing == 'reference':
                # Look for any column with 'case', 'ticket', or 'ref'
                for col in actual_columns:
                    if any(word in col.lower() for word in ['case', 'ticket', 'ref', '#']):
                        self.column_mapping['reference'] = col
                        logger.info(f"Using '{col}' for reference column")
                        break
            elif missing == 'status':
                # Look for any column with 'status', 'state'
                for col in actual_columns:
                    if any(word in col.lower() for word in ['status', 'state']):
                        self.column_mapping['status'] = col
                        logger.info(f"Using '{col}' for status column")
                        break
            elif missing == 'date_created':
                # Look for any column with 'date', 'created'
                for col in actual_columns:
                    if any(word in col.lower() for word in ['date', 'created', 'open']):
                        self.column_mapping['date_created'] = col
                        logger.info(f"Using '{col}' for date created column")
                        break
    
    def _clean_data(self):
        """Clean and standardize the data."""
        logger.info("Cleaning and standardizing data...")
        
        # Clean text columns
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                self.data[col] = self.data[col].astype(str)
                self.data[col] = self.data[col].apply(clean_text)
        
        # Standardize severity values
        if 'severity' in self.column_mapping:
            severity_col = self.column_mapping['severity']
            self.data[severity_col] = self.data[severity_col].apply(normalize_severity)
    
    def _get_date_range(self) -> Dict[str, Any]:
        """Get the date range of cases."""
        if 'date_created' not in self.column_mapping:
            return {'start': None, 'end': None, 'days': 0}
        
        date_col = self.column_mapping['date_created']
        dates = []
        
        for date_str in self.data[date_col]:
            if pd.notna(date_str) and str(date_str) != 'nan':
                parsed_date = parse_date_flexible(str(date_str))
                if parsed_date:
                    dates.append(parsed_date)
        
        if dates:
            start_date = min(dates)
            end_date = max(dates)
            return {
                'start': start_date,
                'end': end_date,
                'days': (end_date - start_date).days + 1
            }
        
        return {'start': None, 'end': None, 'days': 0}
    
    def _get_missing_columns(self) -> List[str]:
        """Get list of expected columns that are missing."""
        return [col for col in self.expected_columns.keys() if col not in self.column_mapping]
    
    def get_column_value(self, row: pd.Series, column_key: str) -> str:
        """Get value from row using column mapping."""
        if column_key in self.column_mapping:
            actual_col = self.column_mapping[column_key]
            return clean_text(str(row.get(actual_col, 'N/A')))
        return 'N/A'
    
    def process_executive_analytics(self) -> Dict[str, Any]:
        """
        Process data for executive-level analytics.
        
        Returns:
            Dictionary with executive analytics
        """
        logger.info("Processing executive analytics...")
        
        analytics = {
            'summary': self._get_summary_metrics(),
            'monthly_trends': self._get_monthly_trends(),
            'severity_analysis': self._get_severity_analysis(),
            'product_analysis': self._get_product_analysis(),
            'bug_analysis': self._get_bug_analysis(),
            'customer_analysis': self._get_customer_analysis(),
            'internal_vs_external': self._get_internal_external_analysis(),
            'queue_analysis': self._get_queue_analysis(),
            'engineer_assignment': self._get_engineer_assignment(),
            'case_owner_assignment': self._get_case_owner_assignment(),
            'status_analysis': self._get_status_analysis(),
            'response_times': self._get_response_time_analysis()
        }
        
        logger.info("Executive analytics processing complete")
        return analytics
    
    def _get_summary_metrics(self) -> Dict[str, Any]:
        """Get high-level summary metrics."""
        total_cases = len(self.data)
        date_range = self._get_date_range()
        
        # Status breakdown
        status_counts = {}
        if 'status' in self.column_mapping:
            status_col = self.column_mapping['status']
            status_counts = self.data[status_col].value_counts().to_dict()
        
        # Calculate case velocity (cases per month)
        cases_per_month = 0
        if date_range['start'] and date_range['end']:
            months = ((date_range['end'] - date_range['start']).days + 1) / 30.44
            cases_per_month = total_cases / max(months, 1)
        
        return {
            'total_cases': total_cases,
            'date_range': date_range,
            'status_breakdown': status_counts,
            'cases_per_month': round(cases_per_month, 1),
            'avg_cases_per_day': round(total_cases / max(date_range.get('days', 1), 1), 1)
        }
    
    def _get_monthly_trends(self) -> Dict[str, Any]:
        """Analyze monthly case creation trends."""
        if 'date_created' not in self.column_mapping:
            return {'available': False, 'reason': 'No date created column found'}
        
        monthly_data = defaultdict(int)
        monthly_status = defaultdict(lambda: defaultdict(int))
        monthly_severity = defaultdict(lambda: defaultdict(int))
        
        date_col = self.column_mapping['date_created']
        status_col = self.column_mapping.get('status')
        severity_col = self.column_mapping.get('severity')
        
        for _, row in self.data.iterrows():
            date_str = str(row[date_col])
            if date_str and date_str != 'nan':
                parsed_date = parse_date_flexible(date_str)
                if parsed_date:
                    month_key = parsed_date.strftime('%Y-%m')
                    monthly_data[month_key] += 1
                    
                    # Status breakdown by month
                    if status_col:
                        status = clean_text(str(row.get(status_col, 'Unknown')))
                        monthly_status[month_key][status] += 1
                    
                    # Severity breakdown by month
                    if severity_col:
                        severity = clean_text(str(row.get(severity_col, 'Unknown')))
                        monthly_severity[month_key][severity] += 1
        
        return {
            'available': True,
            'monthly_counts': dict(monthly_data),
            'monthly_status': dict(monthly_status),
            'monthly_severity': dict(monthly_severity)
        }
    
    def _get_severity_analysis(self) -> Dict[str, Any]:
        """Analyze case severity distribution."""
        if 'severity' not in self.column_mapping:
            return {'available': False, 'reason': 'No severity column found'}
        
        severity_col = self.column_mapping['severity']
        severity_counts = self.data[severity_col].value_counts().to_dict()
        
        # Calculate percentages
        total = sum(severity_counts.values())
        severity_percentages = {k: round((v/total)*100, 1) for k, v in severity_counts.items()}
        
        return {
            'available': True,
            'counts': severity_counts,
            'percentages': severity_percentages,
            'total': total
        }
    
    def _get_product_analysis(self) -> Dict[str, Any]:
        """Analyze product hierarchy distribution."""
        if 'product_hierarchy' not in self.column_mapping:
            return {'available': False, 'reason': 'No product hierarchy column found'}
        
        product_col = self.column_mapping['product_hierarchy']
        product_counts = self.data[product_col].value_counts().to_dict()
        
        # Also analyze by product version if available
        version_analysis = {}
        if 'product_version' in self.column_mapping:
            version_col = self.column_mapping['product_version']
            for product in product_counts.keys():
                product_data = self.data[self.data[product_col] == product]
                version_counts = product_data[version_col].value_counts().to_dict()
                version_analysis[product] = version_counts
        
        return {
            'available': True,
            'product_counts': product_counts,
            'version_analysis': version_analysis
        }
    
    def _get_bug_analysis(self) -> Dict[str, Any]:
        """Analyze bug-related cases."""
        analysis = {
            'available': False,
            'bug_vs_non_bug': {},
            'bug_types': {},
            'bug_severity': {}
        }
        
        if 'experienced_bug' not in self.column_mapping:
            return {**analysis, 'reason': 'No experienced bug column found'}
        
        bug_col = self.column_mapping['experienced_bug']
        bug_cases = 0
        non_bug_cases = 0
        bug_types = defaultdict(int)
        
        for _, row in self.data.iterrows():
            bug_value = clean_text(str(row.get(bug_col, '')))
            
            # Determine if it's a bug case
            if self._is_bug_case(bug_value):
                bug_cases += 1
                # Extract bug type (AL-, CYCON-, etc.)
                bug_type = self._extract_bug_type(bug_value)
                if bug_type:
                    bug_types[bug_type] += 1
            else:
                non_bug_cases += 1
        
        # Analyze severity distribution for bug cases
        bug_severity = {}
        if 'severity' in self.column_mapping:
            severity_col = self.column_mapping['severity']
            bug_data = self.data[self.data[bug_col].apply(lambda x: self._is_bug_case(clean_text(str(x))))]
            bug_severity = bug_data[severity_col].value_counts().to_dict()
        
        return {
            'available': True,
            'bug_vs_non_bug': {
                'Bug Cases': bug_cases,
                'Non-Bug Cases': non_bug_cases
            },
            'bug_types': dict(bug_types),
            'bug_severity': bug_severity,
            'bug_percentage': round((bug_cases / (bug_cases + non_bug_cases)) * 100, 1) if (bug_cases + non_bug_cases) > 0 else 0
        }
    
    def _is_bug_case(self, bug_value: str) -> bool:
        """Determine if a case is bug-related."""
        if not bug_value or bug_value.lower() in ['n/a', 'no value', 'none', '']:
            return False
        
        # Check for bug ID patterns
        bug_patterns = [r'AL-\d+', r'CYCON-\d+', r'BUG-\d+', r'DEF-\d+']
        for pattern in bug_patterns:
            if re.search(pattern, bug_value, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_bug_type(self, bug_value: str) -> Optional[str]:
        """Extract bug type prefix from bug value."""
        if not bug_value:
            return None
        
        # Map bug prefixes to product names
        if bug_value.upper().startswith('AL-'):
            return 'Alteon'
        elif bug_value.upper().startswith('CYCON-'):
            return 'CyberController'
        elif bug_value.upper().startswith('DP-'):
            return 'DefensePro'
        elif any(prefix in bug_value.upper() for prefix in ['BUG-', 'DEF-']):
            return 'General'
        
        return 'Other'
    
    def _get_customer_analysis(self) -> Dict[str, Any]:
        """Analyze customer-related metrics."""
        analysis = {'available': True}
        
        # Customer case distribution
        if 'end_customer' in self.column_mapping:
            customer_col = self.column_mapping['end_customer']
            customer_counts = self.data[customer_col].value_counts().to_dict()
            analysis['customer_counts'] = customer_counts
        
        # Engineer case distribution
        if 'full_name' in self.column_mapping:
            engineer_col = self.column_mapping['full_name']
            engineer_counts = self.data[engineer_col].value_counts().to_dict()
            analysis['engineer_counts'] = engineer_counts
        
        return analysis
    
    def _get_internal_external_analysis(self) -> Dict[str, Any]:
        """Analyze internal vs external cases."""
        if 'internal_case' not in self.column_mapping:
            return {'available': False, 'reason': 'No internal case column found'}
        
        internal_col = self.column_mapping['internal_case']
        internal_counts = self.data[internal_col].value_counts().to_dict()
        
        return {
            'available': True,
            'breakdown': internal_counts
        }
    
    def _get_queue_analysis(self) -> Dict[str, Any]:
        """Analyze queue distribution."""
        if 'queue' not in self.column_mapping:
            return {'available': False, 'reason': 'No queue column found'}
        
        queue_col = self.column_mapping['queue']
        queue_counts = self.data[queue_col].value_counts().to_dict()
        
        return {
            'available': True,
            'queue_counts': queue_counts
        }
    
    def _get_case_owner_assignment(self) -> Dict[str, Any]:
        """Analyze case owner assignment metrics."""
        if 'full_name' not in self.column_mapping:
            return {'available': False, 'reason': 'No case owner/full name column found'}
        
        owner_col = self.column_mapping['full_name']
        owner_counts = self.data[owner_col].value_counts().to_dict()
        
        # Analyze by status
        owner_status = {}
        if 'status' in self.column_mapping:
            status_col = self.column_mapping['status']
            for owner in owner_counts.keys():
                owner_data = self.data[self.data[owner_col] == owner]
                status_counts = owner_data[status_col].value_counts().to_dict()
                owner_status[owner] = status_counts
        
        return {
            'available': True,
            'case_counts': owner_counts,
            'status_breakdown': owner_status
        }
    
    def _get_status_analysis(self) -> Dict[str, Any]:
        """Analyze case status distribution."""
        if 'status' not in self.column_mapping:
            return {'available': False, 'reason': 'No status column found'}
        
        status_col = self.column_mapping['status']
        status_counts = self.data[status_col].value_counts().to_dict()
        
        return {
            'available': True,
            'counts': status_counts
        }

    def _get_engineer_assignment(self) -> Dict[str, Any]:
        """Analyze engineer performance metrics."""
        if 'assigned_account' not in self.column_mapping:
            return {'available': False, 'reason': 'No assigned account column found'}
        
        engineer_col = self.column_mapping['assigned_account']
        engineer_counts = self.data[engineer_col].value_counts().to_dict()
        
        # Analyze by status
        engineer_status = {}
        if 'status' in self.column_mapping:
            status_col = self.column_mapping['status']
            for engineer in engineer_counts.keys():
                engineer_data = self.data[self.data[engineer_col] == engineer]
                status_counts = engineer_data[status_col].value_counts().to_dict()
                engineer_status[engineer] = status_counts
        
        return {
            'available': True,
            'case_counts': engineer_counts,
            'status_breakdown': engineer_status
        }
    
    def _get_response_time_analysis(self) -> Dict[str, Any]:
        """Analyze response time metrics."""
        if 'date_created' not in self.column_mapping or 'date_responded' not in self.column_mapping:
            return {'available': False, 'reason': 'Missing date columns for response time analysis'}
        
        created_col = self.column_mapping['date_created']
        responded_col = self.column_mapping['date_responded']
        
        response_times = []
        for _, row in self.data.iterrows():
            created_str = str(row.get(created_col, ''))
            responded_str = str(row.get(responded_col, ''))
            
            if created_str and responded_str and created_str != 'nan' and responded_str != 'nan':
                created_date = parse_date_flexible(created_str)
                responded_date = parse_date_flexible(responded_str)
                
                if created_date and responded_date and responded_date > created_date:
                    response_time_hours = (responded_date - created_date).total_seconds() / 3600
                    response_times.append(response_time_hours)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            return {
                'available': True,
                'avg_response_hours': round(avg_response_time, 1),
                'avg_response_days': round(avg_response_time / 24, 1),
                'total_cases_with_response': len(response_times)
            }
        
        return {'available': False, 'reason': 'No valid response time data found'}