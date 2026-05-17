"""
OpenAI email classification service.

Sends email content to the OpenAI API and returns a deterministic JSON result
with a category, priority, and short summary.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Mapping, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.core.config import get_settings


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 30.0

ClassificationCategory = Literal[
    "Current Course",
    "Old Course",
    "Newsletter",
    "Administrative",
]


class EmailClassificationResult(BaseModel):
    """Structured classification returned by OpenAI."""

    model_config = ConfigDict(extra="forbid")

    category: ClassificationCategory
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=240)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        """Keep the summary to one clean sentence."""
        normalized = " ".join(value.split()).strip()
        if not normalized:
            raise ValueError("summary cannot be empty")

        sentence_split = re.split(r"(?<=[.!?])\s+", normalized, maxsplit=1)
        normalized = sentence_split[0]
        if normalized and normalized[-1] not in ".!?":
            normalized = f"{normalized}."
        return normalized


@dataclass(slots=True)
class OpenAIClassifierConfig:
    """Configuration for the OpenAI email classifier."""

    api_key: str
    model: str
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_retries: int = DEFAULT_MAX_RETRIES

    @classmethod
    def from_settings(cls) -> "OpenAIClassifierConfig":
        """Build classifier configuration from application settings."""
        settings = get_settings()
        api_key = (settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")).strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required to classify emails")

        return cls(
            api_key=api_key,
            model=settings.AI_MODEL,
            timeout_seconds=float(settings.AI_REQUEST_TIMEOUT),
            max_retries=DEFAULT_MAX_RETRIES,
        )


class OpenAIEmailClassifier:
    """Classify email content using the OpenAI Responses API."""

    def __init__(
        self,
        config: OpenAIClassifierConfig | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.config = config or OpenAIClassifierConfig.from_settings()
        self._client = client or httpx.Client(timeout=self.config.timeout_seconds)

    def _build_email_text(self, email: str | Mapping[str, Any]) -> str:
        if isinstance(email, str):
            return email.strip()

        subject = str(email.get("subject", "")).strip()
        sender = str(email.get("sender", "")).strip()
        body = str(email.get("body", email.get("body_preview", ""))).strip()
        timestamp = str(email.get("timestamp", "")).strip()

        parts = [
            f"Subject: {subject}" if subject else None,
            f"Sender: {sender}" if sender else None,
            f"Timestamp: {timestamp}" if timestamp else None,
            f"Body: {body}" if body else None,
        ]
        content = "\n".join(part for part in parts if part)
        return content.strip()

    def _request_payload(self, email_text: str) -> dict[str, Any]:
        return {
            "model": self.config.model,
            "temperature": 0,
            "top_p": 1,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Classify the email into exactly one category: "
                                '"Current Course", "Old Course", "Newsletter", or '
                                '"Administrative". Return only valid JSON matching '
                                "the schema. Use the lowest priority number for urgent "
                                "or actionable messages and the highest for low-urgency "
                                "messages. Write a one-sentence summary."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": email_text,
                        }
                    ],
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "email_classification",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": [
                                    "Current Course",
                                    "Old Course",
                                    "Newsletter",
                                    "Administrative",
                                ],
                            },
                            "priority": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5,
                            },
                            "summary": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 240,
                            },
                        },
                        "required": ["category", "priority", "summary"],
                    },
                },
            },
        }

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

    def _extract_text(self, payload: dict[str, Any]) -> str:
        if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
            return payload["output_text"].strip()

        for item in payload.get("output", []):
            for content_item in item.get("content", []):
                text = content_item.get("text")
                if isinstance(text, str) and text.strip():
                    return text.strip()

        choices = payload.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()

        raise ValueError("OpenAI response did not contain JSON text")

    def _is_retryable(self, error: Exception) -> bool:
        if isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            return status_code == 429 or status_code >= 500
        return isinstance(error, (httpx.TimeoutException, httpx.TransportError, json.JSONDecodeError, ValidationError, ValueError))

    def _call_openai(self, email_text: str) -> EmailClassificationResult:
        payload = self._request_payload(email_text)

        last_error: Exception | None = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = self._client.post(
                    OPENAI_RESPONSES_URL,
                    headers=self._auth_headers(),
                    json=payload,
                )
                response.raise_for_status()

                response_payload = response.json()
                raw_text = self._extract_text(response_payload)
                parsed = EmailClassificationResult.model_validate_json(raw_text)
                return parsed
            except Exception as error:
                last_error = error
                if attempt >= self.config.max_retries or not self._is_retryable(error):
                    raise
                time.sleep(2 ** (attempt - 1))

        raise RuntimeError("OpenAI classification failed") from last_error

    def classify_email(self, email: str | Mapping[str, Any]) -> dict[str, Any]:
        """
        Classify email content and return a deterministic JSON-compatible dict.

        Parameters
        ----------
        email:
            Raw email text or a mapping with subject/sender/body/body_preview/timestamp.

        Returns
        -------
        dict[str, Any]
            JSON-safe result with category, priority, and summary.
        """
        email_text = self._build_email_text(email)
        if not email_text:
            raise ValueError("email content is required")

        result = self._call_openai(email_text)
        return result.model_dump()


def classify_email(email: str | Mapping[str, Any]) -> dict[str, Any]:
    """Classify an email using OpenAI and return JSON-compatible output."""
    classifier = OpenAIEmailClassifier()
    return classifier.classify_email(email)