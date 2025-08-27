"""
S3 Storage Adapter - Implementation of FileStorageService interface for AWS S3.
Handles file upload, download, listing, and bucket management operations.
"""

import boto3
from typing import List
import logging

from domain.interfaces import FileStorageService

logger = logging.getLogger(__name__)

class S3StorageAdapter(FileStorageService):
    """S3 implementation of FileStorageService interface"""
    
    def __init__(self, s3_client=None, **s3_config):
        """
        Initialize S3 storage adapter
        
        Args:
            s3_client: Pre-configured boto3 S3 client (optional)
            **s3_config: S3 configuration parameters (endpoint_url, credentials, etc.)
        """
        if s3_client:
            self.s3 = s3_client
        else:
            # Use config if provided
            self.s3 = boto3.client('s3', **s3_config)
    
    def upload_file(self, local_path: str, remote_key: str, bucket: str) -> bool:
        """Upload a file to S3"""
        try:
            # Create bucket if it doesn't exist
            self.create_bucket(bucket)
            self.s3.upload_file(local_path, bucket, remote_key)
            logger.info(f"Uploaded {local_path} to s3://{bucket}/{remote_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to S3: {e}")
            return False
    
    def download_file(self, remote_key: str, bucket: str, local_path: str) -> bool:
        """Download a file from S3"""
        try:
            self.s3.download_file(bucket, remote_key, local_path)
            logger.info(f"Downloaded s3://{bucket}/{remote_key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download s3://{bucket}/{remote_key}: {e}")
            return False
    
    def list_files(self, bucket: str, prefix: str = "") -> List[str]:
        """List files in S3 bucket"""
        try:
            response = self.s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            logger.error(f"Failed to list files in s3://{bucket}/{prefix}: {e}")
            return []
    
    def create_bucket(self, bucket: str) -> bool:
        """Create S3 bucket if it doesn't exist"""
        try:
            self.s3.head_bucket(Bucket=bucket)
            return True  # Bucket already exists
        except:
            try:
                self.s3.create_bucket(Bucket=bucket)
                logger.info(f"Created S3 bucket: {bucket}")
                return True
            except Exception as e:
                logger.error(f"Failed to create bucket {bucket}: {e}")
                return False
