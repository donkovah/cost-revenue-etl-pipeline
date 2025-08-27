"""
Pandera Data Validator - Implementation of DataValidator interface using Pandera.
Provides comprehensive data validation for shipments using schema validation.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
import logging

from domain.interfaces import DataValidator
from domain.models.shipment import Shipment
from pandera import Column, Check, DataFrameSchema
from pandera.errors import SchemaError

logger = logging.getLogger(__name__)

class PanderaDataValidator(DataValidator):
    """Pandera-based implementation of DataValidator interface"""
    
    def __init__(self):
        """Initialize the Pandera data validator with comprehensive schema"""
        self.schema = DataFrameSchema({
            "guid": Column(str, checks=[
                Check.str_matches(r"[0-9A-F-]{36}"),
                Check.str_length(36)
            ]),
            "origin": Column(str, checks=[
                Check.str_length(min_val=1, max_val=100),
                Check.notin(['', 'NULL', 'null', 'N/A'])
            ]),
            "destination": Column(str, checks=[
                Check.str_length(min_val=1, max_val=100),
                Check.notin(['', 'NULL', 'null', 'N/A'])
            ]),
            "cost": Column(float, checks=[
                Check.ge(0),
                Check.le(10000000)
            ]),
            "revenue": Column(float, checks=[
                Check.ge(0),
                Check.le(10000000)
            ]),
            "shipping_date": Column(pd.Timestamp, checks=[
                Check.greater_than(pd.Timestamp('2020-01-01')),
                Check.less_than(pd.Timestamp('2030-12-31'))
            ]),
            "delivery_date": Column(pd.Timestamp, checks=[
                Check.greater_than(pd.Timestamp('2020-01-01')),
                Check.less_than(pd.Timestamp('2030-12-31'))
            ]),
            "profit": Column(float),
            "profit_margin": Column(float, checks=[
                Check.ge(-1000),
                Check.le(1000)
            ]),
            "shipping_duration_days": Column(float, checks=[
                Check.ge(-365),
                Check.le(730)
            ]),
            "processed_at": Column(pd.Timestamp),
            "year": Column(int, checks=[Check.ge(2020), Check.le(2030)]),
            "month": Column(int, checks=[Check.ge(1), Check.le(12)]),
            "quarter": Column(int, checks=[Check.ge(1), Check.le(4)])
        })
    
    def validate_shipments(self, shipments: List[Shipment]) -> Tuple[List[Shipment], List[Dict[str, Any]]]:
        """Validate shipments using domain business rules and data schema"""
        valid_shipments = []
        validation_errors = []
        
        # Convert to DataFrame for schema validation
        data = [shipment.to_dict() for shipment in shipments]
        df = pd.DataFrame(data)
        
        try:
            # Schema validation
            validated_df = self.schema.validate(df)
            
            # Convert back to shipments
            for _, row in validated_df.iterrows():
                try:
                    shipment = Shipment.from_dict(row.to_dict())
                    valid_shipments.append(shipment)
                except Exception as e:
                    validation_errors.append({
                        'row': row.to_dict(),
                        'error': str(e),
                        'type': 'shipment_creation_error'
                    })
            
            logger.info(f"Validation successful: {len(valid_shipments)} valid shipments")
            
        except SchemaError as e:
            logger.error(f"Schema validation failed: {e}")
            
            # Handle partial validation - return what we can
            if e.failure_cases is not None:
                for _, failure in e.failure_cases.iterrows():
                    validation_errors.append({
                        'row': failure.to_dict(),
                        'error': str(failure),
                        'type': 'schema_validation_error'
                    })
            
            # Try to salvage valid records
            for shipment in shipments:
                try:
                    # Basic validation - at least check required fields
                    if all([shipment.guid, shipment.origin, shipment.destination, 
                           shipment.cost is not None, shipment.revenue is not None]):
                        valid_shipments.append(shipment)
                except:
                    continue
        
        return valid_shipments, validation_errors
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
        """Validate DataFrame directly"""
        try:
            validated_df = self.schema.validate(df)
            return validated_df, []
        except SchemaError as e:
            validation_errors = []
            if e.failure_cases is not None:
                validation_errors = e.failure_cases.to_dict('records')
            return df, validation_errors
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the validation schema"""
        return {
            'columns': list(self.schema.columns.keys()),
            'column_count': len(self.schema.columns),
            'validation_rules': {
                col_name: {
                    'data_type': str(col.dtype),
                    'nullable': col.nullable,
                    'checks_count': len(col.checks) if col.checks else 0
                }
                for col_name, col in self.schema.columns.items()
            }
        }
    
    def validate_single_shipment(self, shipment: Shipment) -> Tuple[bool, List[str]]:
        """
        Validate a single shipment object
        
        Args:
            shipment: Shipment object to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            # Convert single shipment to DataFrame
            data = [shipment.to_dict()]
            df = pd.DataFrame(data)
            
            # Validate using schema
            self.schema.validate(df)
            return True, []
            
        except SchemaError as e:
            error_messages = []
            if e.failure_cases is not None:
                for _, failure in e.failure_cases.iterrows():
                    error_messages.append(str(failure))
            return False, error_messages
        except Exception as e:
            return False, [str(e)]
