"""Concurrent fetching of rule sources.

Implemented in milestone M2: httpx-based, with timeout, exponential backoff and
``Retry-After`` support, returning a structured :class:`FetchResult` per source
instead of aborting the whole run on a single failure.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FetchResult:
    name: str
    text: str = ""
    ok: bool = False
    error: str | None = None
    bytes: int = 0
    lines: int = 0


async def fetch_sources(sources, settings) -> list[FetchResult]:
    raise NotImplementedError("core.fetcher is implemented in milestone M2")
