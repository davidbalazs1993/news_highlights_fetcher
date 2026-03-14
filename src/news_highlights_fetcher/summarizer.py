from __future__ import annotations

import os
from typing import Iterable

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import DomainHighlights, FeedItem


SYSTEM_PROMPT = (
    "You are a precise technical news analyst. "
    "Summarize only what is present in the input. "
    "Return 3-7 bullet highlights, concise and informative."
)


def _build_domain_prompt(domain: str, window_days: int, items: Iterable[FeedItem]) -> str:
    lines = [
        f"Domain: {domain}",
        f"Window: last {window_days} days",
        "",
        "Items:",
    ]
    for item in items:
        content = item.content or item.summary or ""
        lines.append(f"- Title: {item.title}")
        lines.append(f"  Link: {item.link}")
        lines.append(f"  Published: {item.published_at.isoformat()}")
        if content:
            lines.append(f"  Content: {content[:2000]}")
    return "\n".join(lines)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def summarize_domain(
    domain: str,
    window_days: int,
    items: list[FeedItem],
    model: str,
) -> DomainHighlights:
    if not items:
        return DomainHighlights(domain=domain, window_days=window_days, highlights=[])

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for summarization.")

    client = OpenAI(api_key=api_key)
    prompt = _build_domain_prompt(domain, window_days, items)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    message = response.choices[0].message.content or ""
    highlights = [line.strip("- ").strip() for line in message.splitlines() if line.strip()]
    return DomainHighlights(domain=domain, window_days=window_days, highlights=highlights)
