"""Generic webhook notifier (Slack / Discord / others), optional (M4)."""

from __future__ import annotations

from .base import Notifier


class WebhookNotifier(Notifier):
    async def notify(self, report) -> None:
        raise NotImplementedError("WebhookNotifier is implemented in milestone M4")
