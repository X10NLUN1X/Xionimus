"""
Monitoring and Error Tracking
Integrates with Sentry for production error monitoring
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class MonitoringManager:
    """Manages error monitoring and alerting"""
    
    def __init__(self):
        self.sentry_enabled = False
        self.sentry_dsn: Optional[str] = None
        
    def initialize_sentry(self):
        """
        Initialize Sentry error tracking
        
        Set SENTRY_DSN environment variable to enable
        """
        try:
            sentry_dsn = os.getenv('SENTRY_DSN')
            
            if not sentry_dsn:
                logger.info("ℹ️ Sentry not configured (SENTRY_DSN not set)")
                return
            
            # Try to import sentry_sdk
            try:
                import sentry_sdk
                from sentry_sdk.integrations.fastapi import FastApiIntegration
                from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
                from sentry_sdk.integrations.logging import LoggingIntegration
            except ImportError:
                logger.warning("⚠️ Sentry SDK not installed. Run: pip install sentry-sdk")
                return
            
            # Get environment
            environment = os.getenv('ENVIRONMENT', 'development')
            
            # Initialize Sentry
            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=environment,
                traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
                profiles_sample_rate=0.1,  # 10% of transactions for profiling
                
                # Integrations
                integrations=[
                    FastApiIntegration(transaction_style="endpoint"),
                    SqlalchemyIntegration(),
                    LoggingIntegration(
                        level=logging.INFO,  # Capture INFO and above as breadcrumbs
                        event_level=logging.ERROR  # Send ERROR and above as events
                    ),
                ],
                
                # Release tracking
                release=os.getenv('APP_VERSION', '1.0.0'),
                
                # Filter sensitive data
                before_send=self._before_send_filter,
            )
            
            self.sentry_enabled = True
            self.sentry_dsn = sentry_dsn
            logger.info(f"✅ Sentry monitoring enabled (environment: {environment})")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Sentry: {e}")
    
    def _before_send_filter(self, event, hint):
        """
        Filter sensitive data before sending to Sentry
        """
        # Remove API keys from error messages
        if 'exception' in event:
            for exception in event['exception'].get('values', []):
                if exception.get('value'):
                    value = exception['value']
                    # Mask API keys
                    for pattern in ['sk-', 'sk-ant-']:
                        if pattern in value:
                            exception['value'] = value.replace(
                                value[value.find(pattern):value.find(pattern)+20],
                                f"{pattern}***REDACTED***"
                            )
        
        return event
    
    def capture_exception(self, error: Exception, context: dict = None):
        """
        Capture exception with context
        
        Args:
            error: Exception to capture
            context: Additional context dictionary
        """
        if not self.sentry_enabled:
            logger.debug(f"Sentry disabled, logging error locally: {error}")
            return
        
        try:
            import sentry_sdk
            
            # Add context
            if context:
                with sentry_sdk.push_scope() as scope:
                    for key, value in context.items():
                        scope.set_extra(key, value)
                    sentry_sdk.capture_exception(error)
            else:
                sentry_sdk.capture_exception(error)
                
        except Exception as e:
            logger.error(f"Failed to capture exception in Sentry: {e}")
    
    def capture_message(self, message: str, level: str = "info", context: dict = None):
        """
        Capture custom message
        
        Args:
            message: Message to capture
            level: Severity level (info, warning, error)
            context: Additional context
        """
        if not self.sentry_enabled:
            return
        
        try:
            import sentry_sdk
            
            if context:
                with sentry_sdk.push_scope() as scope:
                    for key, value in context.items():
                        scope.set_extra(key, value)
                    sentry_sdk.capture_message(message, level=level)
            else:
                sentry_sdk.capture_message(message, level=level)
                
        except Exception as e:
            logger.error(f"Failed to capture message in Sentry: {e}")
    
    def set_user_context(self, user_id: str, email: str = None, username: str = None):
        """
        Set user context for error tracking
        
        Args:
            user_id: User ID
            email: User email (optional)
            username: Username (optional)
        """
        if not self.sentry_enabled:
            return
        
        try:
            import sentry_sdk
            
            sentry_sdk.set_user({
                "id": user_id,
                "email": email,
                "username": username
            })
        except Exception as e:
            logger.error(f"Failed to set user context: {e}")
    
    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info", data: dict = None):
        """
        Add breadcrumb for debugging context
        
        Args:
            message: Breadcrumb message
            category: Category (e.g., "auth", "api", "database")
            level: Severity level
            data: Additional data
        """
        if not self.sentry_enabled:
            return
        
        try:
            import sentry_sdk
            
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data or {}
            )
        except Exception as e:
            logger.error(f"Failed to add breadcrumb: {e}")
    
    def get_stats(self) -> dict:
        """Get monitoring statistics"""
        return {
            'sentry_enabled': self.sentry_enabled,
            'sentry_configured': self.sentry_dsn is not None,
            'environment': os.getenv('ENVIRONMENT', 'development')
        }


# Global monitoring instance
monitoring_manager = MonitoringManager()


# Convenience functions
def capture_exception(error: Exception, context: dict = None):
    """Capture exception"""
    monitoring_manager.capture_exception(error, context)


def capture_message(message: str, level: str = "info", context: dict = None):
    """Capture message"""
    monitoring_manager.capture_message(message, level, context)


def set_user(user_id: str, email: str = None, username: str = None):
    """Set user context"""
    monitoring_manager.set_user_context(user_id, email, username)


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: dict = None):
    """Add breadcrumb"""
    monitoring_manager.add_breadcrumb(message, category, level, data)
