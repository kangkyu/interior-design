"""
Cloud storage service for images (S3/R2 compatible)
"""

import io
import uuid
from typing import Optional
from datetime import datetime

import boto3
from botocore.config import Config
from PIL import Image

from app.config import settings


class StorageService:
    """Handle image storage to S3/R2"""

    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
            endpoint_url=settings.s3_endpoint_url,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.s3_bucket_name

    async def upload_image(
        self,
        image_bytes: bytes,
        folder: str = "uploads",
        filename: Optional[str] = None,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        Upload an image to cloud storage

        Args:
            image_bytes: Raw image bytes
            folder: Folder path in bucket
            filename: Optional custom filename
            content_type: MIME type of the image

        Returns:
            Public URL of the uploaded image
        """
        if filename is None:
            ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]
            filename = f"{uuid.uuid4()}.{ext}"

        key = f"{folder}/{datetime.utcnow().strftime('%Y/%m/%d')}/{filename}"

        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=image_bytes,
            ContentType=content_type,
        )

        # Generate URL
        if settings.s3_endpoint_url:
            # For R2 or custom endpoint
            url = f"{settings.s3_endpoint_url}/{self.bucket}/{key}"
        else:
            # For standard S3
            url = f"https://{self.bucket}.s3.{settings.aws_region}.amazonaws.com/{key}"

        return url

    async def upload_from_url(
        self,
        image_url: str,
        folder: str = "generated",
    ) -> str:
        """
        Download image from URL and upload to storage

        Args:
            image_url: URL of image to download
            folder: Folder path in bucket

        Returns:
            New URL in our storage
        """
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_bytes = response.content
            content_type = response.headers.get("content-type", "image/jpeg")

        return await self.upload_image(
            image_bytes=image_bytes,
            folder=folder,
            content_type=content_type,
        )

    async def create_thumbnail(
        self,
        image_bytes: bytes,
        size: tuple[int, int] = (200, 200),
        folder: str = "thumbnails",
    ) -> str:
        """
        Create a thumbnail from image bytes and upload

        Args:
            image_bytes: Original image bytes
            size: Thumbnail dimensions
            folder: Folder path in bucket

        Returns:
            URL of the thumbnail
        """
        # Open image and create thumbnail
        image = Image.open(io.BytesIO(image_bytes))
        image.thumbnail(size, Image.Resampling.LANCZOS)

        # Convert to bytes
        thumb_buffer = io.BytesIO()
        image.save(thumb_buffer, format="JPEG", quality=85)
        thumb_bytes = thumb_buffer.getvalue()

        return await self.upload_image(
            image_bytes=thumb_bytes,
            folder=folder,
            content_type="image/jpeg",
        )

    async def delete_image(self, url: str) -> bool:
        """
        Delete an image from storage

        Args:
            url: URL of the image to delete

        Returns:
            True if successful
        """
        # Extract key from URL
        try:
            if settings.s3_endpoint_url:
                key = url.replace(f"{settings.s3_endpoint_url}/{self.bucket}/", "")
            else:
                key = url.split(f"{self.bucket}.s3.{settings.aws_region}.amazonaws.com/")[1]

            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False


# Singleton instance
storage_service = StorageService()
