from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FeedItem:
    title: str
    link: str
    published_at: datetime
    source_feed: str
    domain: str
    summary: str | None = None
    content: str | None = None


@dataclass(frozen=True)
class DomainHighlights:
    domain: str
    window_days: int
    highlights: list[str]
