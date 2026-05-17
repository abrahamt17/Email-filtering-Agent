"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmailStatus(str, Enum):
    """Email processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Email Schemas
class EmailBase(BaseModel):
    """Base email schema."""
    subject: str = Field(..., min_length=1, max_length=255)
    sender: EmailStr
    recipient: EmailStr
    body: str = Field(..., min_length=1)


class EmailCreate(EmailBase):
    """Schema for creating emails."""
    ...


class EmailUpdate(BaseModel):
    """Schema for updating emails."""
    subject: Optional[str] = Field(None, max_length=255)
    body: Optional[str] = None
    status: Optional[EmailStatus] = None


class ProcessingLogResponse(BaseModel):
    """Schema for processing log responses."""
    id: int
    email_id: int
    step: str
    status: str
    message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmailResponse(EmailBase):
    """Schema for email responses."""
    id: int
    status: EmailStatus
    ai_summary: Optional[str] = None
    ai_classification: Optional[str] = None
    ai_sentiment: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    logs: list[ProcessingLogResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class EmailListResponse(BaseModel):
    """Schema for email list responses."""
    total: int
    page: int
    size: int
    items: list[EmailResponse]


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating users."""
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    """Schema for user responses."""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Health Check
class HealthCheck(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    environment: str
    database: bool
    timestamp: datetime


# Error Response
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    status_code: int
    timestamp: datetime
