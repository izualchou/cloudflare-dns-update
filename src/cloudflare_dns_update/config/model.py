"""Configuration data models for cloudflare-dns-update.

All models are frozen dataclasses so a loaded config is immutable once
validated. See :mod:`cloudflare_dns_update.config.loader` for the strict
validation that produces these objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class Settings:
    """Global runtime parameters, populated from ``settings`` in sync.yml."""

    list_name_prefix: str = "adblock-list"
    list_type: str = "DOMAIN"
    list_description: str = "Managed domain list"
    policy_name: str = "Block Ads"
    chunk_size: int = 1000
    timeout: int = 30
    max_retries: int = 3
    backoff_base: float = 1.5
    max_concurrency: int = 5
    user_agent: str = "cloudflare-dns-update/1.0"
    min_domains_per_source: int = 100
    fail_safe_min_domains: int = 1000
    max_domains: int = 400000
    max_removal_ratio: float = 0.5
    fail_on_source_error: bool = False


@dataclass(frozen=True)
class Source:
    """A single rule source: a URL plus how to interpret its contents."""

    name: str
    url: str
    format: str = "auto"  # auto | hosts | domains | adblock
    enabled: bool = True


@dataclass(frozen=True)
class Whitelist:
    """A whitelist: inline domains plus optional remote sources."""

    enabled: bool = True
    sources: Tuple[Source, ...] = field(default_factory=tuple)
    inline: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Target:
    """A named group of lists, optionally bound to one Gateway policy."""

    name: str
    list_prefix: str
    policy_name: str | None = None
    sources: Tuple[Source, ...] = field(default_factory=tuple)
    whitelist: Whitelist = field(default_factory=Whitelist)


@dataclass(frozen=True)
class SyncConfig:
    """The fully validated configuration."""

    settings: Settings
    targets: Tuple[Target, ...]
    whitelist: Whitelist

    def summary(self) -> str:
        return (
            f"{len(self.targets)} target(s), "
            f"chunk={self.settings.chunk_size}, timeout={self.settings.timeout}s, "
            f"retries={self.settings.max_retries}"
        )
