"""
Health check and system endpoints.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_session
from app.schemas.email import HealthCheck

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
)
async def health_check(db: AsyncSession = Depends(get_session)):
    """
    Health check endpoint for monitoring application status.
    
    Returns:
        - **status**: Application status
        - **version**: Application version
        - **environment**: Current environment
        - **database**: Database connection status
        - **timestamp**: Current timestamp
    """
    settings = get_settings()
    
    # Check database connection
    db_status = False
    try:
        # Simple query to verify database connection
        await db.execute(text("SELECT 1"))
        db_status = True
        logger.debug("Database connection check: OK")
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        db_status = False
    
    return HealthCheck(
        status="ok" if db_status else "degraded",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        timestamp=datetime.utcnow(),
    )
