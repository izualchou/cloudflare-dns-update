"""Hosts-format provider (``0.0.0.0 host`` / ``127.0.0.1 host`` / ``::1 host``)."""

from __future__ import annotations

from .base import SourceProvider


class HostsProvider(SourceProvider):
    async def fetch(self) -> list[str]:
        raise NotImplementedError("HostsProvider is implemented in milestone M2")
