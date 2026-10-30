"""Plain-domain provider (one bare domain per line)."""

from __future__ import annotations

from .base import SourceProvider


class DomainsProvider(SourceProvider):
    async def fetch(self) -> list[str]:
        raise NotImplementedError("DomainsProvider is implemented in milestone M2")
