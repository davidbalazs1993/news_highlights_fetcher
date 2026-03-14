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


def render_report_html(report: str) -> str:
    lines = report.splitlines()
    html_lines: list[str] = ["<html>", "<body>"]
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            title = stripped.replace("## ", "", 1)
            html_lines.append(f"<h2>{title}</h2>")
            continue
        if stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            item = stripped.replace("- ", "", 1)
            html_lines.append(f"<li>{item}</li>")
            continue
        if stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{stripped}</p>")
    if in_list:
        html_lines.append("</ul>")
    html_lines.extend(["</body>", "</html>"])
    return "\n".join(html_lines)
