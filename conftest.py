"""
Pytest configuration file.
"""

import pytest
from typing import Generator


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


@pytest.fixture
def test_settings():
    """Fixture for test settings."""
    from app.core.config import Settings
    
    return Settings(
        DEBUG=True,
        ENVIRONMENT="testing",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        DB_ECHO=False,
    )
