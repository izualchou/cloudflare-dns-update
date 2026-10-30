"""Sink protocol: decouples the pipeline from the destination backend."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Sink(ABC):
    """A destination for a resolved domain set."""

    @abstractmethod
    async def read_remote(self) -> dict:
        """Return the current remote state used as the diff baseline."""
        raise NotImplementedError

    @abstractmethod
    async def apply(self, domains: list[str]):
        """Reconcile the remote state with ``domains`` (idempotently)."""
        raise NotImplementedError
