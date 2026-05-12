"""
SQLAlchemy ORM models for the application.
Defines database schemas for emails and related entities.
"""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Text, DateTime, Boolean, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


class EmailStatus(str, PyEnum):
    """Enum for email processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Email(Base):
    """Model for storing email data."""
    
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[EmailStatus] = mapped_column(
        Enum(EmailStatus),
        default=EmailStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # AI Processing
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_classification: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_sentiment: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Metadata
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )
    
    # Relationships
    logs: Mapped[list["ProcessingLog"]] = relationship(
        "ProcessingLog",
        back_populates="email",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        Index("idx_email_sender_created", "sender", "created_at"),
        Index("idx_email_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Email(id={self.id}, subject={self.subject}, status={self.status})>"


class ProcessingLog(Base):
    """Model for logging email processing steps."""
    
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email_id: Mapped[int] = mapped_column(
        ForeignKey("emails.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    step: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # Relationships
    email: Mapped["Email"] = relationship(
        "Email",
        back_populates="logs"
    )

    def __repr__(self) -> str:
        return f"<ProcessingLog(email_id={self.email_id}, step={self.step}, status={self.status})>"


class User(Base):
    """Model for application users."""
    
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username})>"
