from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime, timedelta

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .models import FeedItem


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return date_parser.parse(value)
    except (ValueError, TypeError):
        return None


def _select_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for selector in ["article", "main"]:
        node = soup.select_one(selector)
        if node:
            text = node.get_text(separator=" ", strip=True)
            if text:
                return text
    return soup.get_text(separator=" ", strip=True)


def fetch_feed_items(
    domain: str,
    feeds: Iterable[str],
    window_days: int,
) -> list[FeedItem]:
    cutoff = datetime.now(tz=UTC) - timedelta(days=window_days)
    items: list[FeedItem] = []
    for feed_url in feeds:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            published = _parse_date(entry.get("published") or entry.get("updated"))
            if not published:
                continue
            published_utc = published.astimezone(UTC)
            if published_utc < cutoff:
                continue
            summary = entry.get("summary")
            items.append(
                FeedItem(
                    title=entry.get("title", "(untitled)"),
                    link=entry.get("link", ""),
                    published_at=published_utc,
                    source_feed=feed_url,
                    domain=domain,
                    summary=summary,
                )
            )
    return items


def enrich_items_with_content(items: list[FeedItem]) -> list[FeedItem]:
    enriched: list[FeedItem] = []
    for item in items:
        if not item.link:
            enriched.append(item)
            continue
        try:
            resp = requests.get(item.link, timeout=20)
            resp.raise_for_status()
            text = _select_text(resp.text)
        except requests.RequestException:
            text = None
        enriched.append(
            FeedItem(
                title=item.title,
                link=item.link,
                published_at=item.published_at,
                source_feed=item.source_feed,
                domain=item.domain,
                summary=item.summary,
                content=text,
            )
        )
    return enriched
