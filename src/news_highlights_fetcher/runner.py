from __future__ import annotations

from pathlib import Path

from .config import load_config
from .fetcher import enrich_items_with_content, fetch_feed_items
from .summarizer import summarize_domain


def generate_report(
    *,
    days: int,
    config_path: Path,
    domains_filter: set[str] | None,
    model: str,
    skip_content: bool,
) -> str:
    config = load_config(config_path)
    domains = config.domains
    if domains_filter:
        domains = [d for d in domains if d.name in domains_filter]

    if not domains:
        return "No domains configured. Provide a config with at least one domain."

    lines: list[str] = []
    for domain in domains:
        items = fetch_feed_items(domain.name, domain.feeds, days)
        if not skip_content:
            items = enrich_items_with_content(items)
        highlights = summarize_domain(domain.name, days, items, model)
        lines.append(f"## {highlights.domain} (last {highlights.window_days} days)")
        if not highlights.highlights:
            lines.append("- No recent items found.")
            lines.append("")
            continue
        for highlight in highlights.highlights:
            lines.append(f"- {highlight}")
        lines.append("")

    return "\n".join(lines).strip()
