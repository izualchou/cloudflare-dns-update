"""Provider protocol: isolates format-specific parsing from the pipeline."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cloudflare_dns_update.config.model import Source


class SourceProvider(ABC):
    """Fetches and parses one :class:`Source` into raw domain strings."""

    def __init__(self, source: Source) -> None:
        self.source = source

    @abstractmethod
    async def fetch(self) -> list[str]:
        """Return the domain strings for this source (not yet cleaned)."""
        raise NotImplementedError
