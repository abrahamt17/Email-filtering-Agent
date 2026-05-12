"""
API route handlers for email endpoints.
Implements RESTful endpoints for email management and processing.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.models import EmailStatus
from app.schemas.email import (
    EmailCreate,
    EmailResponse,
    EmailUpdate,
    EmailListResponse,
)
from app.services.email_service import EmailService

router = APIRouter(
    prefix="/emails",
    tags=["emails"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=EmailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new email",
)
async def create_email(
    email_data: EmailCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Create a new email record.
    
    - **subject**: Email subject (1-255 characters)
    - **sender**: Sender email address
    - **recipient**: Recipient email address
    - **body**: Email body content
    """
    try:
        service = EmailService(db)
        email = await service.create_email(email_data)
        return email
    except Exception as e:
        logger.error(f"Error creating email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create email",
        )


@router.get(
    "/{email_id}",
    response_model=EmailResponse,
    summary="Retrieve email by ID",
)
async def get_email(
    email_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Retrieve a specific email by ID.
    
    - **email_id**: Email ID (path parameter)
    """
    service = EmailService(db)
    email = await service.get_email(email_id)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email with ID {email_id} not found",
        )
    
    return email


@router.get(
    "",
    response_model=EmailListResponse,
    summary="List all emails",
)
async def list_emails(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    status: Annotated[EmailStatus | None, Query()] = None,
    db: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """
    List emails with pagination and optional filtering.
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return (max 100)
    - **status**: Filter by email status (optional)
    """
    try:
        service = EmailService(db)
        emails, total = await service.get_emails(
            skip=skip,
            limit=limit,
            status=status,
        )
        
        return EmailListResponse(
            total=total,
            page=skip // limit + 1,
            size=limit,
            items=emails,
        )
    except Exception as e:
        logger.error(f"Error listing emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list emails",
        )


@router.patch(
    "/{email_id}",
    response_model=EmailResponse,
    summary="Update email",
)
async def update_email(
    email_id: int,
    email_data: EmailUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Update an email record.
    
    - **email_id**: Email ID (path parameter)
    """
    try:
        service = EmailService(db)
        email = await service.update_email(email_id, email_data)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email with ID {email_id} not found",
            )
        
        return email
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email",
        )


@router.delete(
    "/{email_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete email",
)
async def delete_email(
    email_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Delete an email record.
    
    - **email_id**: Email ID (path parameter)
    """
    try:
        service = EmailService(db)
        deleted = await service.delete_email(email_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email with ID {email_id} not found",
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete email",
        )


@router.post(
    "/{email_id}/process",
    response_model=EmailResponse,
    summary="Process email with AI",
)
async def process_email(
    email_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Process an email with AI analysis.
    
    - **email_id**: Email ID (path parameter)
    """
    try:
        service = EmailService(db)
        email = await service.process_email(email_id)
        return email
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error processing email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process email",
        )
