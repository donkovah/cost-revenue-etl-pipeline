import pandas as pd
import pandera as pa
from pandera import Column, Check
from pandera.errors import SchemaError
from infra.adapters.s3_adapter import upload_to_s3
from domain.shipment import Shipment
from datetime import datetime
import logging
from typing import List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract(csv_path: str) -> pd.DataFrame:
    """Extract data from CSV file"""
    logger.info(f"Extracting data from {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Extracted {len(df)} rows from CSV")
    return df

def create_shipment_objects(df: pd.DataFrame) -> List[Shipment]:
    """Convert DataFrame rows to Shipment objects"""
    logger.info("Converting DataFrame to Shipment objects")
    shipments = []
    
    for _, row in df.iterrows():
        try:
            shipment = Shipment.from_dict(row.to_dict())
            shipments.append(shipment)
        except Exception as e:
            logger.warning(f"Failed to create Shipment from row {row.name}: {e}")
            continue
    
    logger.info(f"Successfully created {len(shipments)} Shipment objects")
    return shipments

def shipments_to_dataframe(shipments: List[Shipment]) -> pd.DataFrame:
    """Convert Shipment objects back to DataFrame"""
    logger.info("Converting Shipment objects to DataFrame")
    data = [shipment.to_dict() for shipment in shipments]
    df = pd.DataFrame(data)
    logger.info(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transform and validate the data using Shipment domain model and pandera"""
    logger.info("Starting data transformation using Shipment domain model")
    
    # 1. Data Cleaning and Type Conversion (same as before)
    df_transformed = df.copy()
    
    # Clean and convert date columns
    df_transformed['shipping_date'] = pd.to_datetime(df_transformed['shipping_date'], errors='coerce')
    df_transformed['delivery_date'] = pd.to_datetime(df_transformed['delivery_date'], errors='coerce')
    
    # Clean numeric columns - remove any non-numeric characters and convert
    df_transformed['cost'] = pd.to_numeric(df_transformed['cost'], errors='coerce')
    df_transformed['revenue'] = pd.to_numeric(df_transformed['revenue'], errors='coerce')
    
    # Clean string columns
    df_transformed['guid'] = df_transformed['guid'].astype(str).str.strip().str.upper()
    df_transformed['origin'] = df_transformed['origin'].astype(str).str.strip()
    df_transformed['destination'] = df_transformed['destination'].astype(str).str.strip()
    
    # 2. Remove rows with critical missing data early
    df_clean = df_transformed.dropna(subset=['guid', 'origin', 'destination', 'cost', 'revenue', 'shipping_date', 'delivery_date'])
    removed_rows = len(df_transformed) - len(df_clean)
    if removed_rows > 0:
        logger.warning(f"Removed {removed_rows} rows with missing critical data")
    
    # 3. Convert to Shipment objects (this automatically calculates derived fields)
    shipments = create_shipment_objects(df_clean)
    
    # 4. Convert back to DataFrame with all calculated fields
    df_with_calculated_fields = shipments_to_dataframe(shipments)
    
    # 5. Create schema based on Shipment model structure
    shipment_schema = pa.DataFrameSchema({
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
            Check.le(10000000)  # Reasonable upper limit
        ]),
        "revenue": Column(float, checks=[
            Check.ge(0),
            Check.le(10000000)  # Reasonable upper limit
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
            Check.ge(-1000),  # Allow for significant losses
            Check.le(1000)    # Allow for high margin business
        ]),
        "shipping_duration_days": Column(float, checks=[
            Check.ge(-365),   # Allow for some date inconsistencies
            Check.le(730)     # Max 2 years shipping time
        ]),
        "processed_at": Column(pd.Timestamp),
        "year": Column(int, checks=[
            Check.ge(2020),
            Check.le(2030)
        ]),
        "month": Column(int, checks=[
            Check.ge(1),
            Check.le(12)
        ]),
        "quarter": Column(int, checks=[
            Check.ge(1),
            Check.le(4)
        ])
    })
    
    # 6. Apply validation and handle errors
    try:
        df_validated = shipment_schema.validate(df_with_calculated_fields)
        logger.info(f"Data validation passed for {len(df_validated)} rows")
        
        # Log some business insights
        profitable_shipments = sum(1 for shipment in shipments if shipment.is_profitable)
        high_margin_shipments = sum(1 for shipment in shipments if shipment.is_high_margin)
        delayed_shipments = sum(1 for shipment in shipments if shipment.is_delayed)
        
        logger.info(f"Business metrics: {profitable_shipments} profitable, {high_margin_shipments} high-margin, {delayed_shipments} delayed shipments")
        
    except SchemaError as e:
        logger.error(f"Schema validation failed: {e}")
        # Log which rows failed validation
        failure_cases = e.failure_cases
        if failure_cases is not None:
            logger.error(f"Failed validation for {len(failure_cases)} cases")
            logger.error(f"First few failures:\n{failure_cases.head()}")
        raise
    
    logger.info(f"Transformation completed successfully using Shipment domain model. Final dataset: {len(df_validated)} rows, {len(df_validated.columns)} columns")
    
    return df_validated

def load(df: pd.DataFrame, bucket: str):
    """Load the transformed data to local files and S3"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate timestamped filenames
    csv_filename = f"validated_shipments_{timestamp}.csv"
    parquet_filename = f"validated_shipments_{timestamp}.parquet"
    
    logger.info(f"Saving data to local files: {csv_filename}, {parquet_filename}")
    
    # Save CSV locally
    df.to_csv(csv_filename, index=False)
    logger.info(f"Saved {len(df)} rows to {csv_filename}")
    
    # Save Parquet locally (more efficient for analytics)
    df.to_parquet(parquet_filename, index=False, engine='pyarrow')
    logger.info(f"Saved {len(df)} rows to {parquet_filename}")
    
    # Upload to S3 with organized structure
    try:
        # Upload to date-partitioned paths
        date_partition = datetime.now().strftime("%Y/%m/%d")
        csv_s3_key = f"shipments/csv/{date_partition}/{csv_filename}"
        parquet_s3_key = f"shipments/parquet/{date_partition}/{parquet_filename}"
        
        upload_to_s3(csv_filename, bucket, csv_s3_key)
        upload_to_s3(parquet_filename, bucket, parquet_s3_key)
        
        logger.info("Data successfully loaded to S3")
    except Exception as e:
        logger.error(f"Failed to upload to S3: {e}")
        raise
