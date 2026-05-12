"""
Configuration management for the AI Email Processing System.
Handles environment variables and application settings.
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = Field(default="AI Email Processing System", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # API Configuration
    API_V1_STR: str = "/api/v1"
    API_TITLE: str = "AI Email Processing API"
    API_DESCRIPTION: str = "API for processing emails with AI"
    ALLOWED_HOSTS: list[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/email_db",
        env="DATABASE_URL"
    )
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    DB_POOL_PRE_PING: bool = Field(default=True, env="DB_POOL_PRE_PING")

    # Authentication
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Email Configuration
    SMTP_HOST: str = Field(default="localhost", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_FROM_EMAIL: str = Field(default="noreply@example.com", env="SMTP_FROM_EMAIL")

    # AI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    AI_MODEL: str = Field(default="gpt-4", env="AI_MODEL")
    AI_REQUEST_TIMEOUT: int = Field(default=30, env="AI_REQUEST_TIMEOUT")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    LOG_FILE: Optional[str] = Field(default="logs/app.log", env="LOG_FILE")

    # Redis (for caching and task queue)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_ENABLED: bool = Field(default=False, env="REDIS_ENABLED")

    # Workers
    WORKERS: int = Field(default=4, env="WORKERS")

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from comma-separated string."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses @lru_cache for single instance across the application.
    """
    return Settings()
