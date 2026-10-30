"""Command line interface for cloudflare-dns-update.

The MVP ships a fully working ``validate-config`` command. The remaining
subcommands (``sync`` / ``plan`` / ``list-remote``) are wired here but their
implementations land in later milestones; they exit with code ``2`` and a clear
message so the interface is stable from day one.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config.loader import DEFAULT_CONFIG_PATH, ConfigError, load_config

EXIT_OK = 0
EXIT_CONFIG_ERROR = 1
EXIT_NOT_IMPLEMENTED = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cloudflare-dns-update",
        description="Declarative sync engine for Cloudflare Gateway domain lists.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-c", "--config", default=str(DEFAULT_CONFIG_PATH), help="配置文件路径（默认 config/sync.yml）"
    )
    parser.add_argument("-l", "--log-level", default="INFO", help="日志级别 INFO/DEBUG/WARNING/ERROR")
    parser.add_argument("--dry-run", action="store_true", help="解析与差分照常执行，但不写入 Cloudflare")
    parser.add_argument("--report-path", default="sync-report.json", help="结构化报告输出路径")
    parser.add_argument("--domains-path", default=None, help="额外输出最终域名清单（便于审计）")
    parser.add_argument("--force", action="store_true", help="忽略 max_removal_ratio 护栏")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("sync", help="完整同步（受 --dry-run 影响）")
    sub.add_parser("plan", help="读取云端基线并展示 diff，不写入")
    sub.add_parser("validate-config", help="仅校验 config/sync.yml")
    sub.add_parser("list-remote", help="打印当前账号的 Gateway 列表")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "validate-config":
        try:
            config = load_config(args.config)
        except (ConfigError, FileNotFoundError) as exc:
            print(f"config invalid: {exc}", file=sys.stderr)
            return EXIT_CONFIG_ERROR
        print(f"config OK | {config.summary()}")
        for target in config.targets:
            sources = ", ".join(s.name for s in target.sources if s.enabled)
            print(f"  - target '{target.name}': prefix={target.list_prefix} policy={target.policy_name} sources=[{sources}]")
        return EXIT_OK

    # sync / plan / list-remote are implemented in later milestones.
    print(
        f"command '{args.command}' is not implemented yet — see the roadmap in README.md",
        file=sys.stderr,
    )
    return EXIT_NOT_IMPLEMENTED


if __name__ == "__main__":
    raise SystemExit(main())
