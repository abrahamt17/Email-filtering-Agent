"""
Business logic services for email processing.
Handles core AI email processing operations.
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Email, EmailStatus, ProcessingLog
from app.schemas.email import EmailCreate, EmailUpdate

logger = logging.getLogger(__name__)


class EmailService:
    """Service for email processing operations."""

    def __init__(self, db: AsyncSession):
        """Initialize email service with database session."""
        self.db = db

    async def create_email(self, email_data: EmailCreate) -> Email:
        """
        Create a new email record.
        
        Args:
            email_data: Email creation schema
            
        Returns:
            Email: Created email object
        """
        db_email = Email(
            subject=email_data.subject,
            sender=email_data.sender,
            recipient=email_data.recipient,
            body=email_data.body,
            status=EmailStatus.PENDING,
        )
        self.db.add(db_email)
        await self.db.flush()

        result = await self.db.execute(
            select(Email)
            .options(selectinload(Email.logs))
            .where(Email.id == db_email.id)
        )
        
        logger.info(f"Created email with ID: {db_email.id}")
        return result.scalar_one()

    async def get_email(self, email_id: int) -> Optional[Email]:
        """
        Retrieve email by ID.
        
        Args:
            email_id: Email ID
            
        Returns:
            Optional[Email]: Email object or None if not found
        """
        result = await self.db.execute(
            select(Email)
            .options(selectinload(Email.logs))
            .where(Email.id == email_id)
        )
        return result.scalar_one_or_none()

    async def get_emails(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[EmailStatus] = None,
    ) -> tuple[list[Email], int]:
        """
        Retrieve emails with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            status: Filter by email status
            
        Returns:
            Tuple of (emails list, total count)
        """
        query = select(Email).options(selectinload(Email.logs))
        count_query = select(func.count()).select_from(Email)

        if status:
            query = query.where(Email.status == status)
            count_query = count_query.where(Email.status == status)

        # Get total count without loading all rows
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()
        
        # Get paginated results
        query = query.order_by(Email.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        emails = result.scalars().all()
        
        return emails, total

    async def update_email(
        self,
        email_id: int,
        email_data: EmailUpdate
    ) -> Optional[Email]:
        """
        Update email record.
        
        Args:
            email_id: Email ID
            email_data: Email update schema
            
        Returns:
            Optional[Email]: Updated email or None if not found
        """
        email = await self.get_email(email_id)
        if not email:
            return None
        
        update_data = email_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(email, field, value)
        
        await self.db.flush()
        logger.info(f"Updated email with ID: {email_id}")
        return email

    async def delete_email(self, email_id: int) -> bool:
        """
        Delete email record.
        
        Args:
            email_id: Email ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        email = await self.get_email(email_id)
        if not email:
            return False
        
        await self.db.delete(email)
        await self.db.flush()
        logger.info(f"Deleted email with ID: {email_id}")
        return True

    async def process_email(self, email_id: int) -> Email:
        """
        Process email with AI analysis.
        
        Args:
            email_id: Email ID to process
            
        Returns:
            Email: Processed email object
            
        Raises:
            ValueError: If email not found
        """
        email = await self.get_email(email_id)
        if not email:
            raise ValueError(f"Email with ID {email_id} not found")

        email.status = EmailStatus.PROCESSING
        await self.db.flush()
        
        start_time = datetime.utcnow()

        try:
            # Placeholder for AI processing logic
            # In production, integrate with your AI service here
            email.ai_summary = f"Summary of: {email.subject}"
            email.ai_classification = "general"
            email.ai_sentiment = "neutral"
            
            email.status = EmailStatus.COMPLETED
            email.processed_at = datetime.utcnow()
            
            # Log processing step
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            await self._log_processing_step(
                email=email,
                step="ai_analysis",
                status="success",
                message="Email processed successfully",
                duration_ms=duration_ms
            )
            
            logger.info(f"Successfully processed email {email_id}")

        except Exception as e:
            email.status = EmailStatus.FAILED
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            await self._log_processing_step(
                email=email,
                step="ai_analysis",
                status="failed",
                message=str(e),
                duration_ms=duration_ms
            )
            
            logger.error(f"Failed to process email {email_id}: {str(e)}")
            raise

        await self.db.flush()

        result = await self.db.execute(
            select(Email)
            .options(selectinload(Email.logs))
            .where(Email.id == email_id)
        )
        return result.scalar_one()

    async def _log_processing_step(
        self,
        email: Email,
        step: str,
        status: str,
        message: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ):
        """
        Log a processing step.
        
        Args:
            email: Loaded Email object
            step: Processing step name
            status: Step status (success/failed)
            message: Optional message
            duration_ms: Optional duration in milliseconds
        """
        log = ProcessingLog(
            email_id=email.id,
            step=step,
            status=status,
            message=message,
            duration_ms=duration_ms,
        )
        email.logs.append(log)
        self.db.add(log)
        await self.db.flush()
