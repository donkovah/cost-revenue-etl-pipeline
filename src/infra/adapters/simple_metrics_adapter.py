"""
Simple Metrics Collector - Basic implementation of MetricsCollector interface.
Collects and logs metrics for monitoring and observability purposes.
"""

from typing import List, Dict, Any
import logging
from datetime import datetime
import json

from domain.interfaces import MetricsCollector
from domain.models.shipment import Shipment

logger = logging.getLogger(__name__)

class SimpleMetricsAdapter(MetricsCollector):
    """Simple implementation of MetricsCollector interface"""
    
    def __init__(self, enable_file_logging: bool = False, metrics_file: str = "pipeline_metrics.json"):
        """
        Initialize simple metrics collector
        
        Args:
            enable_file_logging: Whether to write metrics to a file
            metrics_file: File path for metrics logging
        """
        self.enable_file_logging = enable_file_logging
        self.metrics_file = metrics_file
        self.metrics_history = []
    
    def record_pipeline_run(self, 
                          records_processed: int, 
                          processing_time_seconds: float,
                          success: bool) -> None:
        """Record ETL pipeline run metrics"""
        try:
            pipeline_metric = {
                'timestamp': datetime.now().isoformat(),
                'metric_type': 'pipeline_run',
                'records_processed': records_processed,
                'processing_time_seconds': processing_time_seconds,
                'success': success,
                'throughput_records_per_second': records_processed / processing_time_seconds if processing_time_seconds > 0 else 0
            }
            
            self.metrics_history.append(pipeline_metric)
            
            # Log the metric
            logger.info(f"Pipeline Run Metric: {json.dumps(pipeline_metric, indent=2)}")
            
            # Write to file if enabled
            if self.enable_file_logging:
                self._write_metric_to_file(pipeline_metric)
                
        except Exception as e:
            logger.error(f"Failed to record pipeline run metrics: {e}")
    
    def record_business_metrics(self, shipments: List[Shipment]) -> None:
        """Record business-specific metrics from shipments"""
        try:
            if not shipments:
                return
            
            total_shipments = len(shipments)
            profitable_count = sum(1 for s in shipments if s.is_profitable)
            high_margin_count = sum(1 for s in shipments if s.is_high_margin)
            delayed_count = sum(1 for s in shipments if s.is_delayed)
            
            total_revenue = sum(s.revenue for s in shipments if s.revenue)
            total_cost = sum(s.cost for s in shipments if s.cost)
            total_profit = total_revenue - total_cost
            
            avg_profit_margin = sum(s.profit_margin for s in shipments if s.profit_margin) / total_shipments if total_shipments > 0 else 0
            
            business_metric = {
                'timestamp': datetime.now().isoformat(),
                'metric_type': 'business_metrics',
                'total_shipments': total_shipments,
                'profitable_shipments': profitable_count,
                'high_margin_shipments': high_margin_count,
                'delayed_shipments': delayed_count,
                'profitability_rate': (profitable_count / total_shipments * 100) if total_shipments > 0 else 0,
                'high_margin_rate': (high_margin_count / total_shipments * 100) if total_shipments > 0 else 0,
                'delayed_rate': (delayed_count / total_shipments * 100) if total_shipments > 0 else 0,
                'total_revenue': total_revenue,
                'total_cost': total_cost,
                'total_profit': total_profit,
                'avg_profit_margin': round(avg_profit_margin, 2)
            }
            
            self.metrics_history.append(business_metric)
            
            # Log the metric
            logger.info(f"Business Metric: {json.dumps(business_metric, indent=2)}")
            
            # Write to file if enabled
            if self.enable_file_logging:
                self._write_metric_to_file(business_metric)
                
        except Exception as e:
            logger.error(f"Failed to record business metrics: {e}")
    
    def record_data_quality_metrics(self, 
                                  total_records: int,
                                  valid_records: int,
                                  validation_errors: List[Dict[str, Any]]) -> None:
        """Record data quality metrics"""
        try:
            data_quality_rate = (valid_records / total_records * 100) if total_records > 0 else 0
            error_rate = ((total_records - valid_records) / total_records * 100) if total_records > 0 else 0
            
            # Categorize error types
            error_types = {}
            for error in validation_errors:
                error_type = error.get('type', 'unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            data_quality_metric = {
                'timestamp': datetime.now().isoformat(),
                'metric_type': 'data_quality',
                'total_records': total_records,
                'valid_records': valid_records,
                'invalid_records': total_records - valid_records,
                'data_quality_rate': round(data_quality_rate, 2),
                'error_rate': round(error_rate, 2),
                'error_types': error_types,
                'total_validation_errors': len(validation_errors)
            }
            
            self.metrics_history.append(data_quality_metric)
            
            # Log the metric
            logger.info(f"Data Quality Metric: {json.dumps(data_quality_metric, indent=2)}")
            
            # Write to file if enabled
            if self.enable_file_logging:
                self._write_metric_to_file(data_quality_metric)
                
        except Exception as e:
            logger.error(f"Failed to record data quality metrics: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected metrics"""
        pipeline_runs = [m for m in self.metrics_history if m['metric_type'] == 'pipeline_run']
        business_metrics = [m for m in self.metrics_history if m['metric_type'] == 'business_metrics']
        data_quality_metrics = [m for m in self.metrics_history if m['metric_type'] == 'data_quality']
        
        return {
            'total_metrics_collected': len(self.metrics_history),
            'pipeline_runs_count': len(pipeline_runs),
            'business_metrics_count': len(business_metrics),
            'data_quality_metrics_count': len(data_quality_metrics),
            'latest_pipeline_run': pipeline_runs[-1] if pipeline_runs else None,
            'latest_business_metrics': business_metrics[-1] if business_metrics else None,
            'latest_data_quality': data_quality_metrics[-1] if data_quality_metrics else None
        }
    
    def _write_metric_to_file(self, metric: Dict[str, Any]) -> None:
        """Write metric to file"""
        try:
            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metric) + '\n')
        except Exception as e:
            logger.error(f"Failed to write metric to file {self.metrics_file}: {e}")
