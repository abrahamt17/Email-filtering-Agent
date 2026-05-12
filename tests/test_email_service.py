"""
Unit tests for email service.
"""

import pytest
from datetime import datetime
from app.models.models import Email, EmailStatus
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
