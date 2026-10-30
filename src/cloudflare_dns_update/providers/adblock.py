"""AdBlock-format provider (``||domain^`` / ``||*.domain^`` / URL forms)."""

from __future__ import annotations

from .base import SourceProvider


class AdblockProvider(SourceProvider):
    async def fetch(self) -> list[str]:
        raise NotImplementedError("AdblockProvider is implemented in milestone M2")
