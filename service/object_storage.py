import boto3
import tempfile
import os
from pathlib import Path
from typing import Optional
from botocore.exceptions import ClientError
from botocore.config import Config
from fastapi import UploadFile
from PIL import Image
import mimetypes
import time
import logging
import base64
import io

logger = logging.getLogger(__name__)

class UploadFileWithCleanup(UploadFile):
    """Extended UploadFile with temp_path tracking"""
    def __init__(self, file, filename: str, headers=None, temp_path: str = None):
        super().__init__(file=file, filename=filename, headers=headers)
        self._temp_path = temp_path
    
    @property
    def temp_path(self) -> Optional[str]:
        return self._temp_path


class S3FileHandler:
    """Handler untuk download dan manage file dari S3"""
    
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        bucket_name: str,
        endpoint_url: str
    ):
        self.bucket_name = bucket_name
        
        config = Config(
            retries={'max_attempts': 2, 'mode': 'standard'},  
            connect_timeout=5,      
            read_timeout=60,       
            max_pool_connections=20, 
            tcp_keepalive=True      # Keep connection alive
        )
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            endpoint_url=endpoint_url,
            config=config,
            use_ssl=True  # Pastikan SSL enable
        )
        
        logger.info(f"S3 Client initialized - Endpoint: {endpoint_url}, Bucket: {bucket_name}")

    def _visualize_from_uploadfile(self, upload_file: UploadFileWithCleanup) -> None:
        try:
            content_type = upload_file.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                logger.info(f"Skip visualization - not an image: {content_type}")
                return
            
            temp_path = upload_file.temp_path
            with Image.open(temp_path) as img:
                print(f"IMAGE INFO:")
                print(f"  Format: {img.format}")
                print(f"  Mode: {img.mode}")
                print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
                
                img_copy = img.copy()
                
                if img_copy.mode not in ('RGB', 'RGBA'):
                    img_copy = img_copy.convert('RGB')
                
                img_copy.thumbnail((300, 300))
                img_copy.show()
                
                print(f"Image preview opened")
                
        except Exception as e:
            logger.error(f"Failed to visualize: {str(e)}")
    
    def extract_s3_key_from_url(self, url: str) -> str:
        """Extract S3 key dari URL"""
        parts = url.replace(self.s3_client.meta.endpoint_url, '').strip('/')
        if parts.startswith(self.bucket_name):
            parts = parts[len(self.bucket_name):].strip('/')
        return parts
    
    def _get_content_type(self, filename: str) -> str:
        """Get content type berdasarkan extension file"""
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'
    
    async def download_to_uploadfile(
        self, 
        file_url: str, 
        suffix: Optional[str] = None
    ) -> UploadFileWithCleanup:
        """Download file dari S3 dan convert ke UploadFile"""
        temp_path = None
        try:
            s3_key = self.extract_s3_key_from_url(file_url)
            logger.info(f"Starting download: {s3_key}")
            
            if suffix is None:
                suffix = Path(s3_key).suffix or ''
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_path = temp_file.name
            temp_file.close()
            
            head_start = time.time()
            head_response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            head_duration = time.time() - head_start
            file_size = head_response.get('ContentLength', 0)
            
            if head_duration > 2:
                logger.warning(f"Slow HEAD request: {head_duration:.2f}s - Network issue detected")
            
            download_start = time.time()
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                temp_path
            )
            download_duration = time.time() - download_start
            download_speed = (file_size / 1024) / download_duration if download_duration > 0 else 0
            
            if download_speed < 100:
                logger.error(f"VERY SLOW: {download_speed:.2f} KB/s - Check network/endpoint!")
            elif download_duration > 5:
                logger.warning(f"Slow download: {download_duration:.2f}s")
            
            actual_size = os.path.getsize(temp_path)
            if actual_size != file_size:
                logger.warning(f"Size mismatch - Expected: {file_size}, Actual: {actual_size}")
            
            original_filename = Path(s3_key).name
            content_type = self._get_content_type(original_filename)
            file_obj = open(temp_path, 'rb')

            upload_file = UploadFileWithCleanup(
                file=file_obj,
                filename=original_filename,
                headers={'content-type': content_type},
                temp_path=temp_path
            )

            # self._visualize_from_uploadfile(upload_file)
            
            return upload_file
            
        except ClientError as e:
            logger.error(f"S3 ClientError: {str(e)}")
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise Exception(f"Failed to download file from S3: {str(e)}")
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    
    @staticmethod
    async def cleanup_uploadfile(upload_file: UploadFile) -> None:
        """Hapus temporary file dari UploadFile"""
        try:
            if upload_file is None:
                return
            
            if hasattr(upload_file, 'file') and upload_file.file and not upload_file.file.closed:
                upload_file.file.close()
            
            if hasattr(upload_file, 'temp_path'):
                temp_path = upload_file.temp_path
                if temp_path and os.path.exists(temp_path):
                    file_size = os.path.getsize(temp_path)
                    os.unlink(temp_path)
                    logger.info(f"Temp file deleted: {file_size/1024:.2f} KB freed")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
    
    @staticmethod
    async def cleanup_multiple_uploadfiles(*upload_files: UploadFile) -> None:
        """Hapus multiple temporary files dari UploadFile"""
        for upload_file in upload_files:
            if upload_file is not None:
                await S3FileHandler.cleanup_uploadfile(upload_file)