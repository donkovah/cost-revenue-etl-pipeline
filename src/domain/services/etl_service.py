from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..models.shipment import Shipment
from ..interfaces import (
    ShipmentRepository, 
    FileStorageService, 
    DataValidator, 
    NotificationService, 
    MetricsCollector
)

logger = logging.getLogger(__name__)

class ShipmentETLService:
    """Domain service that orchestrates the ETL pipeline"""
    
    def __init__(self, 
                 repository: ShipmentRepository,
                 storage_service: FileStorageService,
                 validator: DataValidator,
                 notification_service: Optional[NotificationService] = None,
                 metrics_collector: Optional[MetricsCollector] = None):
        self.repository = repository
        self.storage_service = storage_service
        self.validator = validator
        self.notification_service = notification_service
        self.metrics_collector = metrics_collector
    
    def process_shipments(self, source_path: str, bucket: str) -> Dict[str, Any]:
        """
        Main ETL process orchestration
        Returns processing summary
        """
        start_time = datetime.now()
        processing_summary = {
            'success': False,
            'records_processed': 0,
            'valid_records': 0,
            'validation_errors': [],
            'processing_time_seconds': 0,
            'business_metrics': {}
        }
        
        try:
            logger.info(f"Starting ETL process for {source_path}")
            
            # Extract
            raw_data = self.repository.extract_shipments(source_path)
            logger.info(f"Extracted {len(raw_data)} raw records")
            
            # Transform
            shipments = self._transform_data(raw_data)
            logger.info(f"Transformed {len(shipments)} shipment objects")
            
            # Validate
            valid_shipments, validation_errors = self.validator.validate_shipments(shipments)
            logger.info(f"Validation: {len(valid_shipments)} valid, {len(validation_errors)} errors")
            
            # Calculate business metrics
            business_metrics = self._calculate_business_metrics(valid_shipments)
            
            # Load
            success = self.repository.save_shipments(valid_shipments, bucket)
            
            # Update processing summary
            end_time = datetime.now()
            processing_summary.update({
                'success': success,
                'records_processed': len(raw_data),
                'valid_records': len(valid_shipments),
                'validation_errors': validation_errors,
                'processing_time_seconds': (end_time - start_time).total_seconds(),
                'business_metrics': business_metrics
            })
            
            # Record metrics if available
            if self.metrics_collector:
                self.metrics_collector.record_pipeline_run(
                    records_processed=len(raw_data),
                    processing_time_seconds=processing_summary['processing_time_seconds'],
                    success=success
                )
                self.metrics_collector.record_business_metrics(valid_shipments)
                self.metrics_collector.record_data_quality_metrics(
                    total_records=len(raw_data),
                    valid_records=len(valid_shipments),
                    validation_errors=validation_errors
                )
            
            # Send notifications
            if success and self.notification_service:
                self.notification_service.notify_success(
                    f"ETL pipeline completed successfully",
                    details=processing_summary
                )
            
            logger.info(f"ETL process completed successfully in {processing_summary['processing_time_seconds']:.2f}s")
            
        except Exception as e:
            end_time = datetime.now()
            processing_summary.update({
                'success': False,
                'processing_time_seconds': (end_time - start_time).total_seconds(),
                'error': str(e)
            })
            
            logger.error(f"ETL process failed: {e}")
            
            if self.notification_service:
                self.notification_service.notify_error(
                    f"ETL pipeline failed",
                    error_details={'error': str(e), 'source_path': source_path}
                )
            
            raise
        
        return processing_summary
    
    def _transform_data(self, raw_data: List[Dict[str, Any]]) -> List[Shipment]:
        """Transform raw data into Shipment domain objects"""
        shipments = []
        
        for record in raw_data:
            try:
                shipment = Shipment.from_dict(record)
                shipments.append(shipment)
            except Exception as e:
                logger.warning(f"Failed to create Shipment from record: {e}")
                continue
        
        return shipments
    
    def _calculate_business_metrics(self, shipments: List[Shipment]) -> Dict[str, Any]:
        """Calculate business metrics from processed shipments"""
        if not shipments:
            return {}
        
        total_shipments = len(shipments)
        profitable_shipments = sum(1 for s in shipments if s.is_profitable)
        high_margin_shipments = sum(1 for s in shipments if s.is_high_margin)
        delayed_shipments = sum(1 for s in shipments if s.is_delayed)
        
        total_revenue = sum(s.revenue for s in shipments if s.revenue)
        total_cost = sum(s.cost for s in shipments if s.cost)
        total_profit = total_revenue - total_cost
        
        avg_profit_margin = sum(s.profit_margin for s in shipments if s.profit_margin) / total_shipments if total_shipments > 0 else 0
        avg_shipping_duration = sum(s.shipping_duration_days for s in shipments if s.shipping_duration_days) / total_shipments if total_shipments > 0 else 0
        
        return {
            'total_shipments': total_shipments,
            'profitable_shipments': profitable_shipments,
            'high_margin_shipments': high_margin_shipments,
            'delayed_shipments': delayed_shipments,
            'profitability_rate': profitable_shipments / total_shipments * 100 if total_shipments > 0 else 0,
            'high_margin_rate': high_margin_shipments / total_shipments * 100 if total_shipments > 0 else 0,
            'delayed_rate': delayed_shipments / total_shipments * 100 if total_shipments > 0 else 0,
            'total_revenue': total_revenue,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'avg_profit_margin': round(avg_profit_margin, 2),
            'avg_shipping_duration_days': round(avg_shipping_duration, 2)
        }
