"""Renderers: JSON / Markdown / GitHub Step Summary (implemented in M2)."""

from __future__ import annotations

from .report import SyncReport


def render_markdown(report: SyncReport) -> str:
    raise NotImplementedError("render.render_markdown is implemented in milestone M2")
