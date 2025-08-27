"""
File storage interface for remote file operations.
Defines the contract for file upload, download, and management operations.
"""

from abc import ABC, abstractmethod
from typing import List

class FileStorageService(ABC):
    """Interface for file storage operations"""
    
    @abstractmethod
    def upload_file(self, local_path: str, remote_key: str, bucket: str) -> bool:
        """
        Upload a file to remote storage
        
        Args:
            local_path: Path to the local file to upload
            remote_key: Key/path for the file in remote storage
            bucket: Storage bucket name
            
        Returns:
            True if upload succeeded, False otherwise
            
        Raises:
            Exception: If upload operation fails
        """
        pass
    
    @abstractmethod
    def download_file(self, remote_key: str, bucket: str, local_path: str) -> bool:
        """
        Download a file from remote storage
        
        Args:
            remote_key: Key/path of the file in remote storage
            bucket: Storage bucket name
            local_path: Local path where the file should be saved
            
        Returns:
            True if download succeeded, False otherwise
            
        Raises:
            Exception: If download operation fails
        """
        pass
    
    @abstractmethod
    def list_files(self, bucket: str, prefix: str = "") -> List[str]:
        """
        List files in remote storage
        
        Args:
            bucket: Storage bucket name
            prefix: Optional prefix to filter files
            
        Returns:
            List of file keys/paths in the bucket
            
        Raises:
            Exception: If list operation fails
        """
        pass
    
    @abstractmethod
    def create_bucket(self, bucket: str) -> bool:
        """
        Create a bucket if it doesn't exist
        
        Args:
            bucket: Name of the bucket to create
            
        Returns:
            True if bucket was created or already exists, False otherwise
            
        Raises:
            Exception: If bucket creation fails
        """
        pass
