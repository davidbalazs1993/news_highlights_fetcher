from __future__ import annotations

import os
from pathlib import Path

import boto3

from .cli import _load_env_file
from .emailer import send_email_ses
from .runner import generate_report, render_report_html


def _resolve_default_config() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "config" / "defaults.yaml"
        if candidate.exists():
            return candidate
    return Path(__file__).resolve().parents[1] / "config" / "defaults.yaml"


DEFAULT_CONFIG = _resolve_default_config()
DEFAULT_ENV = Path(".env")


def handler(event: dict, context: object) -> dict:
    _load_env_file(DEFAULT_ENV)

    if not os.getenv("OPENAI_API_KEY"):
        ssm_param = os.getenv("OPENAI_API_KEY_SSM_PARAM")
        if ssm_param:
            region = os.getenv("AWS_REGION") or os.getenv("SSM_REGION")
            ssm = boto3.client("ssm", region_name=region)
            response = ssm.get_parameter(Name=ssm_param, WithDecryption=True)
            os.environ["OPENAI_API_KEY"] = response["Parameter"]["Value"]

    days = int(os.getenv("DAYS", "7"))
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    skip_content = os.getenv("SKIP_CONTENT", "false").lower() == "true"
    domains_raw = os.getenv("DOMAINS", "")
    domains_filter = {d.strip() for d in domains_raw.split(",") if d.strip()} or None

    report = generate_report(
        days=days,
        config_path=DEFAULT_CONFIG,
        domains_filter=domains_filter,
        model=model,
        skip_content=skip_content,
    )

    email_to = os.getenv("EMAIL_TO", "")
    email_from = os.getenv("EMAIL_FROM", "")
    email_region = os.getenv("AWS_REGION") or os.getenv("SES_REGION")
    subject = os.getenv("EMAIL_SUBJECT") or f"News highlights (last {days} days)"
    if email_to and email_from:
        html_report = render_report_html(report)
        send_email_ses(
            to_addresses=[addr.strip() for addr in email_to.split(",") if addr.strip()],
            from_address=email_from,
            subject=subject,
            body=report,
            html_body=html_report,
            region=email_region,
        )

    return {
        "statusCode": 200,
        "body": report,
    }
