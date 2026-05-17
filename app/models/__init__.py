"""Package initialization for models."""

from app.models.models import (
    Classification,
    ClassificationCategory,
    Email,
    EmailStatus,
    ProcessingLog,
    User,
)

__all__ = [
    "Email",
    "Classification",
    "ClassificationCategory",
    "User",
    "ProcessingLog",
    "EmailStatus",
]
