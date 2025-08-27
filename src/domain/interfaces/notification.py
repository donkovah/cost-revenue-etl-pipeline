"""
Notification interface for sending alerts and status updates.
Defines the contract for different types of notifications (success, error, warning).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class NotificationService(ABC):
    """Interface for notifications (email, slack, teams, etc.)"""
    
    @abstractmethod
    def notify_success(self, message: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send success notification
        
        Args:
            message: Success message to send
            details: Optional additional details to include
            
        Returns:
            True if notification was sent successfully, False otherwise
            
        Raises:
            Exception: If notification sending fails
        """
        pass
    
    @abstractmethod
    def notify_error(self, message: str, error_details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send error notification
        
        Args:
            message: Error message to send
            error_details: Optional error details to include
            
        Returns:
            True if notification was sent successfully, False otherwise
            
        Raises:
            Exception: If notification sending fails
        """
        pass
    
    @abstractmethod
    def notify_warning(self, message: str, warning_details: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send warning notification
        
        Args:
            message: Warning message to send
            warning_details: Optional warning details to include
            
        Returns:
            True if notification was sent successfully, False otherwise
            
        Raises:
            Exception: If notification sending fails
        """
        pass
