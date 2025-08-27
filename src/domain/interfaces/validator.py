"""
Data validation interface for ensuring data quality and business rules compliance.
Defines the contract for validating shipment data and DataFrames.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
import pandas as pd
from ..models.shipment import Shipment

class DataValidator(ABC):
    """Interface for data validation services"""
    
    @abstractmethod
    def validate_shipments(self, shipments: List[Shipment]) -> Tuple[List[Shipment], List[Dict[str, Any]]]:
        """
        Validate shipments and return valid shipments and validation errors
        
        Args:
            shipments: List of Shipment objects to validate
            
        Returns:
            Tuple of (valid_shipments, validation_errors)
            - valid_shipments: List of shipments that passed validation
            - validation_errors: List of dictionaries describing validation failures
            
        Raises:
            Exception: If validation process fails
        """
        pass
    
    @abstractmethod
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """
        Validate DataFrame and return valid data and validation errors
        
        Args:
            df: Pandas DataFrame to validate
            
        Returns:
            Tuple of (valid_dataframe, validation_errors)
            - valid_dataframe: DataFrame with valid rows only
            - validation_errors: List of dictionaries describing validation failures
            
        Raises:
            Exception: If validation process fails
        """
        pass
