"""Package initialization for services."""

from app.services.email_service import EmailService
from app.services.ai_classifier import OpenAIEmailClassifier, classify_email
from app.services.graph_service import MicrosoftGraphEmailService, fetch_emails

__all__ = [
	"EmailService",
	"OpenAIEmailClassifier",
	"classify_email",
	"MicrosoftGraphEmailService",
	"fetch_emails",
]
