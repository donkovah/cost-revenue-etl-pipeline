"""
Repository interface for shipment data persistence operations.
Defines the contract for data extraction and storage.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.shipment import Shipment

class ShipmentRepository(ABC):
    """Interface for shipment data persistence"""
    
    @abstractmethod
    def extract_shipments(self, source_path: str) -> List[Dict[str, Any]]:
        """
        Extract raw shipment data from source
        
        Args:
            source_path: Path to the data source (CSV file, database connection, API endpoint, etc.)
            
        Returns:
            List of dictionaries containing raw shipment data
            
        Raises:
            Exception: If extraction fails
        """
        pass
    
    @abstractmethod
    def save_shipments(self, shipments: List[Shipment], destination: str) -> bool:
        """
        Save processed shipments to destination
        
        Args:
            shipments: List of validated Shipment objects to save
            destination: Destination location (S3 bucket, database, file path, etc.)
            
        Returns:
            True if save operation succeeded, False otherwise
            
        Raises:
            Exception: If save operation fails
        """
        pass
