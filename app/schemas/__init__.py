"""Package initialization for schemas."""

from app.schemas.email import (
    EmailCreate,
    EmailUpdate,
    EmailResponse,
    EmailListResponse,
    EmailStatus,
    UserCreate,
    UserResponse,
    HealthCheck,
)

__all__ = [
    "EmailCreate",
    "EmailUpdate",
    "EmailResponse",
    "EmailListResponse",
    "EmailStatus",
    "UserCreate",
    "UserResponse",
    "HealthCheck",
]
