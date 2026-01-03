"""
Application configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Interior Design AI"
    debug: bool = False
    api_prefix: str = "/api"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/interior_design"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # AI Services
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    replicate_api_token: str = ""

    # Cloud Storage (S3/R2)
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "interior-design-images"
    s3_endpoint_url: str | None = None  # For R2 or MinIO

    # Image Generation
    default_image_model: str = "stability-ai/sdxl:latest"
    max_images_per_session: int = 50

    # JWT (for future auth)
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
