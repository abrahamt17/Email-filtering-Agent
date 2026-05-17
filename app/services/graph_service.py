"""
Microsoft Graph email fetching service.

Uses OAuth2 refresh token flow to obtain access tokens and fetch the latest
messages from an Outlook inbox.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"
DEFAULT_MESSAGE_LIMIT = 20


@dataclass(slots=True)
class GraphAuthConfig:
    """Configuration required to authenticate against Microsoft Graph."""

    tenant_id: str
    client_id: str
    client_secret: str
    refresh_token: str
    scopes: str = "https://graph.microsoft.com/.default"

    @classmethod
    def from_env(cls) -> "GraphAuthConfig":
        """Build auth configuration from environment variables."""
        tenant_id = os.getenv("MS_GRAPH_TENANT_ID", "").strip()
        client_id = os.getenv("MS_GRAPH_CLIENT_ID", "").strip()
        client_secret = os.getenv("MS_GRAPH_CLIENT_SECRET", "").strip()
        refresh_token = os.getenv("MS_GRAPH_REFRESH_TOKEN", "").strip()
        scopes = os.getenv(
            "MS_GRAPH_SCOPES",
            "https://graph.microsoft.com/.default",
        ).strip()

        missing = [
            name
            for name, value in (
                ("MS_GRAPH_TENANT_ID", tenant_id),
                ("MS_GRAPH_CLIENT_ID", client_id),
                ("MS_GRAPH_CLIENT_SECRET", client_secret),
                ("MS_GRAPH_REFRESH_TOKEN", refresh_token),
            )
            if not value
        ]
        if missing:
            missing_vars = ", ".join(missing)
            raise ValueError(f"Missing required Graph env vars: {missing_vars}")

        return cls(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            scopes=scopes,
        )


class MicrosoftGraphEmailService:
    """Fetch emails from Microsoft Graph with automatic token refresh."""

    def __init__(self, auth_config: GraphAuthConfig | None = None) -> None:
        self.auth_config = auth_config or GraphAuthConfig.from_env()
        self._access_token: str | None = None
        self._token_type: str = "Bearer"

    def _token_url(self) -> str:
        return (
            f"https://login.microsoftonline.com/{self.auth_config.tenant_id}"
            f"/oauth2/v2.0/token"
        )

    def _request_access_token(self) -> dict[str, Any]:
        """Exchange the refresh token for a fresh access token."""
        data = {
            "client_id": self.auth_config.client_id,
            "client_secret": self.auth_config.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.auth_config.refresh_token,
            "scope": self.auth_config.scopes,
        }

        response = httpx.post(self._token_url(), data=data, timeout=30.0)
        response.raise_for_status()
        payload = response.json()

        access_token = payload.get("access_token")
        if not access_token:
            raise RuntimeError("Microsoft Graph token response missing access_token")

        self._access_token = access_token
        self._token_type = payload.get("token_type", "Bearer")
        return payload

    def _get_authorization_headers(self) -> dict[str, str]:
        if not self._access_token:
            self._request_access_token()

        return {"Authorization": f"{self._token_type} {self._access_token}"}

    def _fetch_messages_once(self, limit: int) -> list[dict[str, Any]]:
        select_fields = "subject,from,bodyPreview,receivedDateTime"
        url = (
            f"{GRAPH_API_BASE_URL}/me/mailFolders/inbox/messages"
            f"?$top={limit}&$orderby=receivedDateTime desc&$select={select_fields}"
        )

        response = httpx.get(
            url,
            headers=self._get_authorization_headers(),
            timeout=30.0,
        )

        if response.status_code == 401:
            self._request_access_token()
            response = httpx.get(
                url,
                headers=self._get_authorization_headers(),
                timeout=30.0,
            )

        response.raise_for_status()
        payload = response.json()
        return payload.get("value", [])

    def fetch_emails(self, limit: int = DEFAULT_MESSAGE_LIMIT) -> list[dict[str, Any]]:
        """
        Fetch the latest emails from an Outlook inbox.

        Returns a list of normalized dictionaries with:
        - subject
        - sender
        - body_preview
        - timestamp
        """
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        messages = self._fetch_messages_once(limit=limit)
        normalized_messages: list[dict[str, Any]] = []

        for message in messages[:limit]:
            sender = message.get("from", {}) or {}
            email_address = sender.get("emailAddress", {}) or {}
            normalized_messages.append(
                {
                    "subject": message.get("subject", ""),
                    "sender": email_address.get("address", ""),
                    "body_preview": message.get("bodyPreview", ""),
                    "timestamp": message.get("receivedDateTime", ""),
                }
            )

        return normalized_messages


def fetch_emails(limit: int = DEFAULT_MESSAGE_LIMIT) -> list[dict[str, Any]]:
    """Fetch the latest Outlook inbox emails using Microsoft Graph."""
    service = MicrosoftGraphEmailService()
    return service.fetch_emails(limit=limit)