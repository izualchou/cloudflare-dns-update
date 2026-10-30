"""Cloudflare Gateway sink: idempotent lists + policy upsert (implemented in M2)."""

from __future__ import annotations

from .base import Sink


class GatewaySink(Sink):
    async def read_remote(self) -> dict:
        raise NotImplementedError("GatewaySink is implemented in milestone M2")

    async def apply(self, domains: list[str]):
        raise NotImplementedError("GatewaySink is implemented in milestone M2")
