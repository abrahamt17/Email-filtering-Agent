"""
Unit tests for email service.
"""

import pytest

from app.models.models import EmailStatus
from app.schemas.email import EmailCreate
from app.services.email_service import EmailService


@pytest.mark.asyncio
async def test_create_email(db_session):
    """Test creating an email."""
    service = EmailService(db_session)
    
    email_data = EmailCreate(
        subject="Test Email",
        sender="sender@example.com",
        recipient="recipient@example.com",
        body="Test body"
    )
    
    email = await service.create_email(email_data)
    
    assert email.subject == "Test Email"
    assert email.sender == "sender@example.com"
    assert email.status == EmailStatus.PENDING


@pytest.mark.asyncio
async def test_get_email(db_session):
    """Test retrieving an email."""
    service = EmailService(db_session)
    
    email_data = EmailCreate(
        subject="Test Email",
        sender="sender@example.com",
        recipient="recipient@example.com",
        body="Test body"
    )
    
    created = await service.create_email(email_data)
    retrieved = await service.get_email(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id


@pytest.mark.asyncio
async def test_delete_email(db_session):
    """Test deleting an email."""
    service = EmailService(db_session)
    
    email_data = EmailCreate(
        subject="Test Email",
        sender="sender@example.com",
        recipient="recipient@example.com",
        body="Test body"
    )
    
    created = await service.create_email(email_data)
    deleted = await service.delete_email(created.id)
    
    assert deleted is True


@pytest.mark.asyncio
async def test_list_emails_counts_only_matching_status(db_session):
    """Test that filtered email counts are correct."""
    service = EmailService(db_session)

    pending_email = EmailCreate(
        subject="Pending Email",
        sender="pending@example.com",
        recipient="recipient@example.com",
        body="Pending body",
    )
    completed_email = EmailCreate(
        subject="Completed Email",
        sender="completed@example.com",
        recipient="recipient@example.com",
        body="Completed body",
    )

    await service.create_email(pending_email)
    completed = await service.create_email(completed_email)
    completed.status = EmailStatus.COMPLETED
    await db_session.flush()

    emails, total = await service.get_emails(status=EmailStatus.PENDING)

    assert total == 1
    assert len(emails) == 1
    assert emails[0].subject == "Pending Email"


@pytest.mark.asyncio
async def test_process_email_updates_fields_and_logs(db_session):
    """Test that processing fills AI fields and creates a log row."""
    service = EmailService(db_session)

    email_data = EmailCreate(
        subject="Process Me",
        sender="sender@example.com",
        recipient="recipient@example.com",
        body="Process body",
    )

    created = await service.create_email(email_data)
    processed = await service.process_email(created.id)

    assert processed.status == EmailStatus.COMPLETED
    assert processed.ai_summary == "Summary of: Process Me"
    assert processed.ai_classification == "general"
    assert processed.ai_sentiment == "neutral"
    assert processed.processed_at is not None
    assert len(processed.logs) == 1
    assert processed.logs[0].step == "ai_analysis"
    assert processed.logs[0].status == "success"
