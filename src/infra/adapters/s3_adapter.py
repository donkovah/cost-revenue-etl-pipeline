import boto3
from app.config import config

# Use configuration from config module
s3 = boto3.client(
    "s3",
    endpoint_url=config.aws_endpoint_url,
    aws_access_key_id=config.aws_access_key_id,
    aws_secret_access_key=config.aws_secret_access_key,
    region_name=config.aws_default_region
)

def upload_to_s3(file_path: str, bucket: str, key: str):
    # Create bucket if it doesn't exist
    try:
        s3.head_bucket(Bucket=bucket)
    except:
        s3.create_bucket(Bucket=bucket)
    s3.upload_file(file_path, bucket, key)
    print(f"Uploaded {file_path} to s3://{bucket}/{key}")
