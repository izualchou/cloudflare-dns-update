"""Whitelist resolution: inline + remote, exact and parent-domain match (M2)."""

from __future__ import annotations


def collect_whitelist(whitelist) -> set[str]:
    raise NotImplementedError("core.whitelist is implemented in milestone M2")
