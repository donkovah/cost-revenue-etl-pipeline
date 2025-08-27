import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    """Application configuration loaded from environment variables"""
    # AWS Configuration
    aws_endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str
    
    # Application Configuration
    csv_file_path: str
    s3_bucket_name: str

def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

def get_config() -> Config:
    """Get application configuration from environment variables"""
    load_env_file()
    
    return Config(
        aws_endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        aws_default_region=os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
        csv_file_path=os.getenv("CSV_FILE_PATH", "data-source.csv"),
        s3_bucket_name=os.getenv("S3_BUCKET_NAME", "shipments-bucket")
    )

# Global config instance
config = get_config()
