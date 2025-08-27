"""
CSV Shipment Repository - Implementation of ShipmentRepository interface for CSV files.
Handles extraction from CSV files and saving processed shipments back to CSV/Parquet.
"""

import pandas as pd
from typing import List, Dict, Any
import logging
from datetime import datetime

from domain.interfaces import FileStorageService, ShipmentRepository
from domain.models.shipment import Shipment

logger = logging.getLogger(__name__)

class CSVShipmentRepository(ShipmentRepository):
    """CSV-based implementation of ShipmentRepository interface"""
    
    def __init__(self, storage_service: FileStorageService):
        """
        Initialize CSV shipment repository
        
        Args:
            storage_service: FileStorageService implementation for file operations
        """
        self.storage_service = storage_service
    
    def extract_shipments(self, source_path: str) -> List[Dict[str, Any]]:
        """Extract shipment data from CSV file"""
        try:
            df = pd.read_csv(source_path)
            
            # Clean and convert data types
            df['shipping_date'] = pd.to_datetime(df['shipping_date'], errors='coerce')
            df['delivery_date'] = pd.to_datetime(df['delivery_date'], errors='coerce')
            df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
            df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
            df['guid'] = df['guid'].astype(str).str.strip().str.upper()
            df['origin'] = df['origin'].astype(str).str.strip()
            df['destination'] = df['destination'].astype(str).str.strip()
            
            logger.info(f"Extracted {len(df)} records from {source_path}")
            records = df.to_dict('records')
            return [{str(k): v for k, v in record.items()} for record in records]
            
        except Exception as e:
            logger.error(f"Failed to extract shipments from {source_path}: {e}")
            raise
    
    def save_shipments(self, shipments: List[Shipment], destination: str) -> bool:
        """Save shipments to CSV and Parquet files, then upload to S3"""
        try:
            # Convert shipments to DataFrame
            data = [shipment.to_dict() for shipment in shipments]
            df = pd.DataFrame(data)
            
            # Generate timestamped filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"validated_shipments_{timestamp}.csv"
            parquet_filename = f"validated_shipments_{timestamp}.parquet"
            
            # Save locally
            df.to_csv(csv_filename, index=False)
            df.to_parquet(parquet_filename, index=False, engine='pyarrow')
            
            logger.info(f"Saved {len(df)} shipments to local files")
            
            # Upload to S3 with date partitioning (destination is bucket name)
            bucket = destination
            date_partition = datetime.now().strftime("%Y/%m/%d")
            csv_s3_key = f"shipments/csv/{date_partition}/{csv_filename}"
            parquet_s3_key = f"shipments/parquet/{date_partition}/{parquet_filename}"
            
            csv_success = self.storage_service.upload_file(csv_filename, csv_s3_key, bucket)
            parquet_success = self.storage_service.upload_file(parquet_filename, parquet_s3_key, bucket)
            
            return csv_success and parquet_success
            
        except Exception as e:
            logger.error(f"Failed to save shipments: {e}")
            return False
