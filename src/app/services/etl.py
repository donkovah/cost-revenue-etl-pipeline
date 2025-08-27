import pandas as pd
import pandera as pa
from pandera import Column, Check
from pandera.errors import SchemaError
from infra.adapters.s3_adapter import upload_to_s3
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract(csv_path: str) -> pd.DataFrame:
    """Extract data from CSV file"""
    logger.info(f"Extracting data from {csv_path}")
    df = pd.read_csv(csv_path)
    logger.info(f"Extracted {len(df)} rows from CSV")
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transform and validate the data using pandas and pandera"""
    logger.info("Starting data transformation")
    
    # 1. Data Cleaning and Type Conversion
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
    
    # 2. Create derived columns
    df_transformed['profit'] = df_transformed['revenue'] - df_transformed['cost']
    df_transformed['profit_margin'] = (df_transformed['profit'] / df_transformed['revenue'] * 100).round(2)
    df_transformed['shipping_duration_days'] = (df_transformed['delivery_date'] - df_transformed['shipping_date']).dt.days
    
    # Add processing metadata
    df_transformed['processed_at'] = datetime.now()
    df_transformed['year'] = df_transformed['shipping_date'].dt.year
    df_transformed['month'] = df_transformed['shipping_date'].dt.month
    df_transformed['quarter'] = df_transformed['shipping_date'].dt.quarter
    
    # 3. Data Validation Schema with Pandera
    schema = pa.DataFrameSchema({
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
    
    # 4. Apply validation and handle errors
    try:
        df_validated = schema.validate(df_transformed)
        logger.info(f"Data validation passed for {len(df_validated)} rows")
    except SchemaError as e:
        logger.error(f"Schema validation failed: {e}")
        # Log which rows failed validation
        failure_cases = e.failure_cases
        if failure_cases is not None:
            logger.error(f"Failed validation for {len(failure_cases)} cases")
            logger.error(f"First few failures:\n{failure_cases.head()}")
        raise
    
    # 5. Remove rows with critical missing data
    initial_count = len(df_validated)
    df_validated = df_validated.dropna(subset=['guid', 'origin', 'destination', 'cost', 'revenue'])
    final_count = len(df_validated)
    
    if initial_count != final_count:
        logger.warning(f"Removed {initial_count - final_count} rows with missing critical data")
    
    logger.info(f"Transformation completed successfully. Final dataset: {final_count} rows, {len(df_validated.columns)} columns")
    
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
