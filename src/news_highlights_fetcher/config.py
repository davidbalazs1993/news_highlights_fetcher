from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class DomainConfig:
    name: str
    feeds: list[str]


@dataclass(frozen=True)
class AppConfig:
    domains: list[DomainConfig]


def load_config(path: Path) -> AppConfig:
    payload = yaml.safe_load(path.read_text()) or {}
    domains_payload = payload.get("domains", {})
    domains: list[DomainConfig] = []
    for name, entry in domains_payload.items():
        feeds = entry.get("feeds", [])
        if not feeds:
            continue
        domains.append(DomainConfig(name=name, feeds=list(feeds)))
    return AppConfig(domains=domains)
