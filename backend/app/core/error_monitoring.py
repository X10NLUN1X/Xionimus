"""
Error Monitoring and Alerting System
Tracks errors, exceptions, and system health for production monitoring
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from pathlib import Path
import traceback

logger = logging.getLogger(__name__)


class ErrorMonitor:
    """
    Centralized error monitoring and alerting system
    Tracks errors, generates reports, and provides metrics
    """
    
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_details = []
        self.max_error_history = 1000
        self.alert_thresholds = {
            'critical': 5,  # Alert after 5 critical errors
            'error': 20,    # Alert after 20 errors
            'warning': 50   # Alert after 50 warnings
        }
        self.time_window = timedelta(minutes=5)  # 5-minute window
        
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: str = 'error',
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        """
        Log an error with context for monitoring
        
        Args:
            error: The exception that occurred
            context: Additional context information
            severity: Error severity (critical, error, warning)
            user_id: User ID if applicable
            endpoint: API endpoint where error occurred
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Increment counter
        self.error_counts[error_type] += 1
        
        # Create detailed error record
        error_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'severity': severity,
            'error_type': error_type,
            'error_message': error_message,
            'context': context,
            'user_id': user_id,
            'endpoint': endpoint,
            'traceback': traceback.format_exc(),
            'count': self.error_counts[error_type]
        }
        
        # Add to history
        self.error_details.append(error_record)
        
        # Maintain max history size
        if len(self.error_details) > self.max_error_history:
            self.error_details = self.error_details[-self.max_error_history:]
        
        # Log to file
        logger.error(
            f"[{severity.upper()}] {error_type}: {error_message}",
            extra={'context': context, 'user_id': user_id, 'endpoint': endpoint}
        )
        
        # Check if alert threshold exceeded
        self._check_alert_threshold(error_type, severity)
        
        return error_record
    
    def _check_alert_threshold(self, error_type: str, severity: str):
        """Check if error count exceeds alert threshold"""
        threshold = self.alert_thresholds.get(severity, float('inf'))
        
        # Count recent errors in time window
        cutoff_time = datetime.utcnow() - self.time_window
        recent_errors = [
            e for e in self.error_details
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
            and e['error_type'] == error_type
        ]
        
        if len(recent_errors) >= threshold:
            self._trigger_alert(error_type, len(recent_errors), severity)
    
    def _trigger_alert(self, error_type: str, count: int, severity: str):
        """Trigger alert when threshold exceeded"""
        alert_message = (
            f"🚨 ALERT: {error_type} occurred {count} times "
            f"in the last {self.time_window.seconds // 60} minutes "
            f"(severity: {severity})"
        )
        logger.critical(alert_message)
        
        # Here you could integrate with:
        # - Slack notifications
        # - Email alerts
        # - PagerDuty
        # - Sentry
        # - Custom webhook
    
    def get_error_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Get error summary for the last N minutes
        
        Args:
            minutes: Time window in minutes
            
        Returns:
            Dict with error statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        recent_errors = [
            e for e in self.error_details
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]
        
        # Group by error type
        error_by_type = defaultdict(int)
        error_by_severity = defaultdict(int)
        error_by_endpoint = defaultdict(int)
        
        for error in recent_errors:
            error_by_type[error['error_type']] += 1
            error_by_severity[error['severity']] += 1
            if error.get('endpoint'):
                error_by_endpoint[error['endpoint']] += 1
        
        return {
            'time_window_minutes': minutes,
            'total_errors': len(recent_errors),
            'by_type': dict(error_by_type),
            'by_severity': dict(error_by_severity),
            'by_endpoint': dict(error_by_endpoint),
            'most_common_error': max(error_by_type.items(), key=lambda x: x[1])[0] if error_by_type else None
        }
    
    def get_error_details(
        self,
        limit: int = 50,
        severity: Optional[str] = None,
        error_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed error records with filters
        
        Args:
            limit: Maximum number of records to return
            severity: Filter by severity level
            error_type: Filter by error type
            
        Returns:
            List of error records
        """
        filtered_errors = self.error_details.copy()
        
        if severity:
            filtered_errors = [e for e in filtered_errors if e['severity'] == severity]
        
        if error_type:
            filtered_errors = [e for e in filtered_errors if e['error_type'] == error_type]
        
        # Return most recent first
        return list(reversed(filtered_errors[-limit:]))
    
    def export_error_report(self, filepath: str):
        """Export error report to JSON file"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'summary_1h': self.get_error_summary(60),
            'summary_24h': self.get_error_summary(1440),
            'error_counts': dict(self.error_counts),
            'recent_errors': self.get_error_details(limit=100)
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Error report exported to {filepath}")
        return report
    
    def clear_old_errors(self, days: int = 7):
        """Clear errors older than specified days"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        before_count = len(self.error_details)
        self.error_details = [
            e for e in self.error_details
            if datetime.fromisoformat(e['timestamp']) > cutoff_time
        ]
        after_count = len(self.error_details)
        
        cleared_count = before_count - after_count
        logger.info(f"Cleared {cleared_count} old error records (older than {days} days)")
        return cleared_count


# Global error monitor instance
error_monitor = ErrorMonitor()


def monitor_exception(
    severity: str = 'error',
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None
):
    """
    Decorator to monitor exceptions in functions
    
    Usage:
        @monitor_exception(severity='critical', endpoint='/api/critical-operation')
        def critical_operation():
            # Your code here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args)[:200],  # Limit size
                    'kwargs': str(kwargs)[:200]
                }
                error_monitor.log_error(e, context, severity, user_id, endpoint)
                raise  # Re-raise the exception
        return wrapper
    return decorator


async def monitor_exception_async(
    severity: str = 'error',
    user_id: Optional[str] = None,
    endpoint: Optional[str] = None
):
    """Async version of monitor_exception decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'module': func.__module__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                }
                error_monitor.log_error(e, context, severity, user_id, endpoint)
                raise
        return wrapper
    return decorator
