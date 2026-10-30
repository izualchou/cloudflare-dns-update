"""Format auto-detection and provider factory (wired in M2)."""

from __future__ import annotations

from cloudflare_dns_update.config.model import Source
from .base import SourceProvider


def build_provider(source: Source) -> SourceProvider:
    """Return the provider for ``source``, honouring ``source.format``.

    ``auto`` sniffs the first non-comment lines to pick hosts/domains/adblock.
    """
    raise NotImplementedError("provider registry is wired in milestone M2")
