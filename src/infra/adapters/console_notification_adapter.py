"""
Console Notification Adapter - Simple implementation of NotificationService interface.
Sends notifications to console/logs for development and testing purposes.
"""

from typing import Dict, Any, Optional
import logging

from domain.interfaces import NotificationService

logger = logging.getLogger(__name__)

class ConsoleNotificationAdapter(NotificationService):
    """Console-based implementation of NotificationService interface"""
    
    def __init__(self, log_level: str = "INFO"):
        """
        Initialize console notification adapter
        
        Args:
            log_level: Logging level for notifications (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_level = log_level.upper()
    
    def notify_success(self, message: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """Send success notification to console"""
        try:
            success_message = f"✅ SUCCESS: {message}"
            if details:
                success_message += f" | Details: {details}"
            
            if self.log_level in ["DEBUG", "INFO"]:
                logger.info(success_message)
                print(success_message)  # Also print to console for visibility
            
            return True
        except Exception as e:
            logger.error(f"Failed to send success notification: {e}")
            return False
    
    def notify_error(self, message: str, error_details: Optional[Dict[str, Any]] = None) -> bool:
        """Send error notification to console"""
        try:
            error_message = f"❌ ERROR: {message}"
            if error_details:
                error_message += f" | Error Details: {error_details}"
            
            logger.error(error_message)
            print(error_message)  # Always print errors to console
            
            return True
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
            return False
    
    def notify_warning(self, message: str, warning_details: Optional[Dict[str, Any]] = None) -> bool:
        """Send warning notification to console"""
        try:
            warning_message = f"⚠️ WARNING: {message}"
            if warning_details:
                warning_message += f" | Warning Details: {warning_details}"
            
            if self.log_level in ["DEBUG", "INFO", "WARNING"]:
                logger.warning(warning_message)
                print(warning_message)  # Also print to console for visibility
            
            return True
        except Exception as e:
            logger.error(f"Failed to send warning notification: {e}")
            return False
