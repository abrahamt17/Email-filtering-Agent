"""
Telegram daily digest bot for important emails.

Fetches emails from the local PostgreSQL database, groups them by classification
category, filters to high-priority items only, and sends a clean formatted digest
message to a Telegram chat.
"""

from __future__ import annotations

import asyncio
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, DefaultDict

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.models import Classification, ClassificationCategory, Email

TELEGRAM_API_BASE_URL = "https://api.telegram.org"
DEFAULT_LOOKBACK_HOURS = 24
DEFAULT_HIGH_PRIORITY_THRESHOLD = 2
CATEGORY_EMOJIS: dict[str, str] = {
    ClassificationCategory.CURRENT_COURSE.value: "📚",
    ClassificationCategory.OLD_COURSE.value: "🕰️",
    ClassificationCategory.NEWSLETTER.value: "📰",
    ClassificationCategory.ADMINISTRATIVE.value: "🛠️",
}
CATEGORY_ORDER = [
    ClassificationCategory.CURRENT_COURSE.value,
    ClassificationCategory.ADMINISTRATIVE.value,
    ClassificationCategory.NEWSLETTER.value,
    ClassificationCategory.OLD_COURSE.value,
]


@dataclass(slots=True)
class TelegramBotConfig:
    """Runtime configuration for the Telegram digest bot."""

    bot_token: str
    chat_id: str
    database_url: str
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS
    high_priority_threshold: int = DEFAULT_HIGH_PRIORITY_THRESHOLD

    @classmethod
    def from_env(cls) -> "TelegramBotConfig":
        """Load configuration from environment variables and app settings."""
        settings = get_settings()
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL).strip()
        lookback_hours = int(os.getenv("TELEGRAM_LOOKBACK_HOURS", str(DEFAULT_LOOKBACK_HOURS)))
        high_priority_threshold = int(
            os.getenv("TELEGRAM_HIGH_PRIORITY_THRESHOLD", str(DEFAULT_HIGH_PRIORITY_THRESHOLD))
        )

        missing = [
            name
            for name, value in (
                ("TELEGRAM_BOT_TOKEN", bot_token),
                ("TELEGRAM_CHAT_ID", chat_id),
                ("DATABASE_URL", database_url),
            )
            if not value
        ]
        if missing:
            raise ValueError(f"Missing required Telegram env vars: {', '.join(missing)}")

        return cls(
            bot_token=bot_token,
            chat_id=chat_id,
            database_url=database_url,
            lookback_hours=lookback_hours,
            high_priority_threshold=high_priority_threshold,
        )


@dataclass(slots=True)
class DigestItem:
    """Normalized digest item for display and sending."""

    category: str
    subject: str
    summary: str
    priority: int
    sender: str
    timestamp: datetime


class TelegramDigestBot:
    """Build and send daily email digests to Telegram."""

    def __init__(
        self,
        config: TelegramBotConfig | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config or TelegramBotConfig.from_env()
        self._engine = create_async_engine(self.config.database_url, pool_pre_ping=True)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)
        self._http_client = http_client or httpx.AsyncClient(timeout=30.0)

    def _cutoff_timestamp(self) -> datetime:
        return datetime.now(timezone.utc) - timedelta(hours=self.config.lookback_hours)

    async def _fetch_digest_items(self) -> list[DigestItem]:
        """Fetch the newest classification per email in the lookback window."""
        cutoff = self._cutoff_timestamp()
        ranking = func.row_number().over(
            partition_by=Classification.email_id,
            order_by=(Classification.created_at.desc(), Classification.id.desc()),
        ).label("row_number")

        ranked_rows = (
            select(
                Classification.email_id.label("email_id"),
                Classification.category.label("category"),
                Classification.priority.label("priority"),
                Classification.summary.label("summary"),
                Classification.created_at.label("classification_created_at"),
                Email.subject.label("subject"),
                Email.sender.label("sender"),
                Email.created_at.label("email_created_at"),
                ranking,
            )
            .join(Email, Email.id == Classification.email_id)
            .where(Classification.created_at >= cutoff)
            .subquery()
        )

        stmt = (
            select(ranked_rows)
            .where(
                ranked_rows.c.row_number == 1,
                ranked_rows.c.priority <= self.config.high_priority_threshold,
            )
            .order_by(
                ranked_rows.c.category.asc(),
                ranked_rows.c.priority.asc(),
                ranked_rows.c.email_created_at.desc(),
            )
        )

        async with self._session_factory() as session:
            result = await session.execute(stmt)
            rows = result.all()

        items: list[DigestItem] = []
        for row in rows:
            items.append(
                DigestItem(
                    category=row.category,
                    subject=row.subject,
                    summary=row.summary,
                    priority=row.priority,
                    sender=row.sender,
                    timestamp=row.email_created_at,
                )
            )
        return items

    def group_by_category(self, items: list[DigestItem]) -> dict[str, list[DigestItem]]:
        """Group digest items by category in a predictable order."""
        grouped: DefaultDict[str, list[DigestItem]] = defaultdict(list)
        for item in items:
            grouped[item.category].append(item)
        return dict(grouped)

    def build_message(self, items: list[DigestItem]) -> str:
        """Build a clean Telegram message for the daily digest."""
        grouped = self.group_by_category(items)
        lines: list[str] = ["📚 Important Today:"]

        if not grouped:
            lines.append("- No high priority emails in the selected window.")
            return "\n".join(lines)

        for category in CATEGORY_ORDER:
            category_items = grouped.get(category, [])
            if not category_items:
                continue

            emoji = CATEGORY_EMOJIS.get(category, "📌")
            lines.append("")
            lines.append(f"{emoji} {category} ({len(category_items)})")
            for item in category_items:
                lines.append(f"- {item.subject} ({item.summary})")

        return "\n".join(lines)

    async def _send_message(self, message: str) -> dict[str, Any]:
        url = f"{TELEGRAM_API_BASE_URL}/bot{self.config.bot_token}/sendMessage"
        response = await self._http_client.post(
            url,
            json={
                "chat_id": self.config.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
        )
        response.raise_for_status()
        return response.json()

    async def send_daily_digest(self) -> dict[str, Any]:
        """Fetch important emails, format them, and send them to Telegram."""
        items = await self._fetch_digest_items()
        message = self.build_message(items)
        telegram_response = await self._send_message(message)
        return {
            "ok": True,
            "message": message,
            "telegram_response": telegram_response,
            "item_count": len(items),
        }

    async def aclose(self) -> None:
        """Clean up network and database resources."""
        await self._http_client.aclose()
        await self._engine.dispose()


async def send_daily_digest() -> dict[str, Any]:
    """Convenience function that sends the digest using environment settings."""
    bot = TelegramDigestBot()
    try:
        return await bot.send_daily_digest()
    finally:
        await bot.aclose()


if __name__ == "__main__":
    asyncio.run(send_daily_digest())
