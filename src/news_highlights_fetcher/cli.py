from __future__ import annotations

import argparse
from pathlib import Path
import os

from .config import load_config
from .fetcher import enrich_items_with_content, fetch_feed_items
from .summarizer import summarize_domain


DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "defaults.yaml"
DEFAULT_ENV = Path(".env")


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and summarize news highlights.")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--domains",
        type=str,
        default="",
        help="Comma-separated list of domains to include (optional).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model name.",
    )
    parser.add_argument(
        "--skip-content",
        action="store_true",
        help="Skip fetching full article content (use RSS summaries only).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _load_env_file(DEFAULT_ENV)
    config = load_config(args.config)

    domain_filter = {d.strip() for d in args.domains.split(",") if d.strip()}
    domains = config.domains
    if domain_filter:
        domains = [d for d in domains if d.name in domain_filter]

    if not domains:
        print("No domains configured. Provide a config with at least one domain.")
        return

    for domain in domains:
        items = fetch_feed_items(domain.name, domain.feeds, args.days)
        if not args.skip_content:
            items = enrich_items_with_content(items)
        highlights = summarize_domain(domain.name, args.days, items, args.model)
        print(f"\n## {highlights.domain} (last {highlights.window_days} days)")
        if not highlights.highlights:
            print("- No recent items found.")
            continue
        for highlight in highlights.highlights:
            print(f"- {highlight}")


if __name__ == "__main__":
    main()
