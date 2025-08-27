"""
Metrics collection interface for observability and monitoring.
Defines the contract for collecting pipeline, business, and data quality metrics.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.shipment import Shipment

class MetricsCollector(ABC):
    """Interface for collecting and reporting metrics"""
    
    @abstractmethod
    def record_pipeline_run(self, 
                          records_processed: int, 
                          processing_time_seconds: float,
                          success: bool) -> None:
        """
        Record ETL pipeline run metrics
        
        Args:
            records_processed: Number of records processed in this run
            processing_time_seconds: Time taken to complete the pipeline
            success: Whether the pipeline run was successful
            
        Raises:
            Exception: If metric recording fails
        """
        pass
    
    @abstractmethod
    def record_business_metrics(self, shipments: List[Shipment]) -> None:
        """
        Record business-specific metrics from shipments
        
        Args:
            shipments: List of processed shipments to extract metrics from
            
        Raises:
            Exception: If metric recording fails
        """
        pass
    
    @abstractmethod
    def record_data_quality_metrics(self, 
                                  total_records: int,
                                  valid_records: int,
                                  validation_errors: List[Dict[str, Any]]) -> None:
        """
        Record data quality metrics
        
        Args:
            total_records: Total number of records processed
            valid_records: Number of records that passed validation
            validation_errors: List of validation error details
            
        Raises:
            Exception: If metric recording fails
        """
        pass
