from __future__ import annotations

from typing import Iterable

import boto3


def send_email_ses(
    *,
    to_addresses: Iterable[str],
    from_address: str,
    subject: str,
    body: str,
    html_body: str | None = None,
    region: str | None = None,
) -> None:
    to_list = [addr.strip() for addr in to_addresses if addr.strip()]
    if not to_list:
        raise ValueError("At least one recipient is required.")
    if not from_address:
        raise ValueError("from_address is required.")

    client = boto3.client("ses", region_name=region)
    client.send_email(
        Source=from_address,
        Destination={"ToAddresses": to_list},
        Message={
            "Subject": {"Data": subject},
            "Body": {
                "Text": {"Data": body},
                **({"Html": {"Data": html_body}} if html_body else {}),
            },
        },
    )
