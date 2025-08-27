import pandas as pd
import pandera as pa
from pandera import Column, Check
from infra.adapters.s3_adapter import upload_to_s3

def extract(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    schema = pa.DataFrameSchema({
        "guid": Column(str, checks=Check.str_matches(r"[0-9A-F-]{36}")),
        "origin": Column(str),
        "destination": Column(str),
        "cost": Column(int, checks=Check.ge(0)),
        "revenue": Column(int, checks=Check.ge(0)),
        "shipping_date": Column(pd.Timestamp),
        "delivery_date": Column(pd.Timestamp)
    })
    return schema.validate(df)

def load(df: pd.DataFrame, bucket: str):
    # Save CSV locally
    df.to_csv("validated_shipments.csv", index=False)
    # Save Parquet locally
    df.to_parquet("validated_shipments.parquet", index=False)
    # Upload to S3
    upload_to_s3("validated_shipments.csv", bucket, "shipments/csv/validated_shipments.csv")
    upload_to_s3("validated_shipments.parquet", bucket, "shipments/parquet/validated_shipments.parquet")
