from __future__ import annotations

import argparse
import os
from pathlib import Path

from .emailer import send_email_ses
from .runner import generate_report, render_report_html


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
    parser.add_argument(
        "--no-stdout",
        action="store_true",
        help="Do not print highlights to stdout.",
    )
    parser.add_argument(
        "--email-to",
        type=str,
        default="",
        help="Comma-separated list of recipient emails.",
    )
    parser.add_argument(
        "--email-from",
        type=str,
        default="",
        help="Sender email address (must be verified in SES).",
    )
    parser.add_argument(
        "--email-subject",
        type=str,
        default="",
        help="Email subject (defaults to last X days).",
    )
    parser.add_argument(
        "--email-region",
        type=str,
        default="",
        help="AWS SES region (defaults to AWS_REGION or SES_REGION).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _load_env_file(DEFAULT_ENV)

    domain_filter = {d.strip() for d in args.domains.split(",") if d.strip()} or None
    report = generate_report(
        days=args.days,
        config_path=args.config,
        domains_filter=domain_filter,
        model=args.model,
        skip_content=args.skip_content,
    )

    if not args.no_stdout:
        print(report)

    email_to = args.email_to or os.getenv("EMAIL_TO", "")
    email_from = args.email_from or os.getenv("EMAIL_FROM", "")
    email_region = args.email_region or os.getenv("AWS_REGION") or os.getenv("SES_REGION")
    email_subject = args.email_subject or f"News highlights (last {args.days} days)"
    if email_to or email_from:
        html_report = render_report_html(report)
        send_email_ses(
            to_addresses=[addr.strip() for addr in email_to.split(",") if addr.strip()],
            from_address=email_from,
            subject=email_subject,
            body=report,
            html_body=html_report,
            region=email_region,
        )


if __name__ == "__main__":
    main()
