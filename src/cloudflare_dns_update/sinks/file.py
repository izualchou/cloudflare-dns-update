"""Local-file sink: write the final domain list for audit / debugging (M2)."""

from __future__ import annotations

from .base import Sink


class FileSink(Sink):
    async def read_remote(self) -> dict:
        raise NotImplementedError("FileSink is implemented in milestone M2")

    async def apply(self, domains: list[str]):
        raise NotImplementedError("FileSink is implemented in milestone M2")
