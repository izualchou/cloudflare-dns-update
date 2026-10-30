"""Notifier protocol: failure alerting channel."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Notifier(ABC):
    """Receives a finished report and alerts on failure."""

    @abstractmethod
    async def notify(self, report) -> None:
        """Send an alert for ``report`` when its status is not success."""
        raise NotImplementedError
