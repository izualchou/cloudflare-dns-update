"""GitHub Issue notifier: open or update a failure Issue (implemented in M4)."""

from __future__ import annotations

from .base import Notifier


class GitHubIssueNotifier(Notifier):
    async def notify(self, report) -> None:
        raise NotImplementedError("GitHubIssueNotifier is implemented in milestone M4")
