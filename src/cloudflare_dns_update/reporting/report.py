"""The single structured contract produced by every run (M2 rendering)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SyncReport:
    """Everything a run needs to surface: status, diff, write counters, errors."""

    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0
    trigger: str = "manual"
    dry_run: bool = False
    status: str = "success"  # success | failure | aborted
    failure_reason: str | None = None
    domains_total: int = 0
    domains_added: int = 0
    domains_removed: int = 0
    domains_unchanged: int = 0
    cloud_before: int = 0
    lists_created: int = 0
    lists_updated: int = 0
    lists_deleted: int = 0
    policy_id: str | None = None
    account_masked: str = ""
    errors: list[dict[str, Any]] = field(default_factory=list)

    def to_json(self, path: str) -> None:
        raise NotImplementedError("SyncReport.to_json is implemented in milestone M2")

    def to_markdown(self) -> str:
        raise NotImplementedError("SyncReport.to_markdown is implemented in milestone M2")
