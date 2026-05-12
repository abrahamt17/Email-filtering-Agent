"""
Logging configuration for the application.
Sets up structured logging with file and console handlers.
"""

import logging
import logging.config
import os
from pathlib import Path

from app.core.config import get_settings


def setup_logging():
    """
    Configure logging for the application.
    Sets up both console and file handlers with appropriate formatting.
    """
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    if settings.LOG_FILE:
        log_dir = Path(settings.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.LOG_LEVEL,
                "handlers": ["console"],
            },
            "app": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING" if not settings.DB_ECHO else "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    # Add file handler if log file is specified
    if settings.LOG_FILE:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "detailed",
            "filename": settings.LOG_FILE,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        # Add file handler to root logger
        logging_config["loggers"][""]["handlers"].append("file")
        logging_config["loggers"]["app"]["handlers"].append("file")

    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured. Level: {settings.LOG_LEVEL}, Environment: {settings.ENVIRONMENT}")
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module name.
    
    Args:
        name: Module name for the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
