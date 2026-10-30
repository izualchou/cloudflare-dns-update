"""Pipeline orchestration (implemented in M2).

Reads config -> per target: fetch -> normalize -> whitelist -> guard -> baseline
-> diff -> (write) -> report -> notify. Strict error propagation so failures
always become a non-zero exit and an alert.
"""

from __future__ import annotations

from pathlib import Path

from .config.loader import DEFAULT_CONFIG_PATH, load_config


def run_sync(
    *,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    dry_run: bool = False,
    force: bool = False,
    report_path: str | Path = "sync-report.json",
    domains_path: str | Path | None = None,
):
    raise NotImplementedError("pipeline.run_sync is implemented in milestone M2")
