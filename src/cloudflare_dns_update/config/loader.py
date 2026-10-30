"""Strict loader for ``config/sync.yml``.

Unknown keys, bad URLs, invalid formats and contradictory thresholds all raise
:class:`ConfigError` with a message that points at the offending field path, so
misconfiguration fails fast and loudly instead of silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from .model import Settings, Source, Whitelist, Target, SyncConfig

DEFAULT_CONFIG_PATH = Path("config/sync.yml")

_VALID_FORMATS = frozenset({"auto", "hosts", "domains", "adblock"})
_ALLOWED_SCHEMES = frozenset({"http", "https"})
_TOP_LEVEL_KEYS = frozenset({"settings", "whitelist", "targets"})
_SETTINGS_KEYS = frozenset(
    {
        "list_name_prefix",
        "list_type",
        "list_description",
        "policy_name",
        "chunk_size",
        "timeout",
        "max_retries",
        "backoff_base",
        "max_concurrency",
        "user_agent",
        "min_domains_per_source",
        "fail_safe_min_domains",
        "max_domains",
        "max_removal_ratio",
        "fail_on_source_error",
    }
)
_INT_KEYS = frozenset(
    {
        "chunk_size",
        "timeout",
        "max_retries",
        "max_concurrency",
        "min_domains_per_source",
        "fail_safe_min_domains",
        "max_domains",
    }
)


class ConfigError(ValueError):
    """Raised when sync.yml is structurally or semantically invalid."""


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> SyncConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: 顶层必须是一个映射（map），收到 {type(raw).__name__}")

    _check_unknown_keys(raw, _TOP_LEVEL_KEYS, "sync.yml")

    settings = _load_settings(raw.get("settings", {}), "settings")
    whitelist = _load_whitelist(raw.get("whitelist", {}), "whitelist")
    targets = _load_targets(raw.get("targets", []), "targets")

    if not targets:
        raise ConfigError("targets: 至少需要一个目标组（target），当前为空")

    return SyncConfig(settings=settings, targets=tuple(targets), whitelist=whitelist)


# --------------------------------------------------------------------------- #
# internal helpers
# --------------------------------------------------------------------------- #
def _check_unknown_keys(mapping: dict, allowed: frozenset, ctx: str) -> None:
    unknown = set(mapping) - allowed
    if unknown:
        raise ConfigError(f"{ctx}: 未知字段 {sorted(unknown)}（允许：{sorted(allowed)}）")


def _as_str(value: Any, ctx: str, *, required: bool = False, default: str = "") -> str:
    if value is None:
        if required:
            raise ConfigError(f"{ctx}: 缺少必填字符串")
        return default
    if not isinstance(value, str) or value == "":
        raise ConfigError(f"{ctx}: 必须是非空字符串，收到 {value!r}")
    return value


def _as_bool(value: Any, ctx: str, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ConfigError(f"{ctx}: 必须是布尔值（true/false），收到 {value!r}")
    return value


def _as_int(value: Any, ctx: str, default: int, *, minimum: int | None = None) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError(f"{ctx}: 必须是整数，收到 {value!r}")
    if minimum is not None and value < minimum:
        raise ConfigError(f"{ctx}: 必须 >= {minimum}，收到 {value}")
    return value


def _as_float(value: Any, ctx: str, default: float, *, gt: float | None = None) -> float:
    if value is None:
        return default
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ConfigError(f"{ctx}: 必须是数字，收到 {value!r}")
    if gt is not None and value <= gt:
        raise ConfigError(f"{ctx}: 必须 > {gt}，收到 {value}")
    return float(value)


def _validate_url(value: str, ctx: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ConfigError(f"{ctx}: URL 协议必须是 http/https，收到 {value!r}")
    if not parsed.netloc:
        raise ConfigError(f"{ctx}: URL 缺少主机名，收到 {value!r}")
    return value


def _load_settings(raw: Any, ctx: str) -> Settings:
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError(f"{ctx}: 必须是映射，收到 {type(raw).__name__}")
    _check_unknown_keys(raw, _SETTINGS_KEYS, ctx)

    kwargs = {}
    for key in _SETTINGS_KEYS:
        if key in _INT_KEYS:
            minimum = 1 if key not in {"max_removal_ratio"} else None
            kwargs[key] = _as_int(raw.get(key), f"{ctx}.{key}", getattr(Settings(), key), minimum=minimum)
        elif key == "max_removal_ratio":
            ratio = _as_float(raw.get(key), f"{ctx}.{key}", getattr(Settings(), key), gt=0.0)
            if ratio > 1.0:
                raise ConfigError(f"{ctx}.max_removal_ratio: 必须 <= 1.0，收到 {ratio}")
            kwargs[key] = ratio
        elif key == "backoff_base":
            kwargs[key] = _as_float(raw.get(key), f"{ctx}.{key}", getattr(Settings(), key), gt=0.0)
        elif key == "fail_on_source_error":
            kwargs[key] = _as_bool(raw.get(key), f"{ctx}.{key}", getattr(Settings(), key))
        else:
            kwargs[key] = _as_str(raw.get(key), f"{ctx}.{key}", default=getattr(Settings(), key))

    min_d = kwargs["min_domains_per_source"]
    safe = kwargs["fail_safe_min_domains"]
    if min_d > safe:
        raise ConfigError(
            f"{ctx}: min_domains_per_source({min_d}) 不能大于 fail_safe_min_domains({safe})"
        )
    return Settings(**kwargs)


def _load_source(raw: Any, ctx: str) -> Source:
    if not isinstance(raw, dict):
        raise ConfigError(f"{ctx}: 每个源必须是映射，收到 {type(raw).__name__}")
    _check_unknown_keys(raw, frozenset({"name", "url", "format", "enabled"}), ctx)
    name = _as_str(raw.get("name"), f"{ctx}.name", required=True)
    url = _validate_url(_as_str(raw.get("url"), f"{ctx}.url", required=True), f"{ctx}.url")
    fmt = _as_str(raw.get("format"), f"{ctx}.format", default="auto")
    if fmt not in _VALID_FORMATS:
        raise ConfigError(f"{ctx}.format: 必须是 {sorted(_VALID_FORMATS)} 之一，收到 {fmt!r}")
    enabled = _as_bool(raw.get("enabled"), f"{ctx}.enabled", True)
    return Source(name=name, url=url, format=fmt, enabled=enabled)


def _load_sources(raw: Any, ctx: str) -> tuple[Source, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ConfigError(f"{ctx}: 必须是列表，收到 {type(raw).__name__}")
    sources: list[Source] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        source = _load_source(item, f"{ctx}[{index}]")
        if source.name in seen:
            raise ConfigError(f"{ctx}: 源名称重复 {source.name!r}")
        seen.add(source.name)
        sources.append(source)
    return tuple(sources)


def _load_whitelist(raw: Any, ctx: str) -> Whitelist:
    if raw is None:
        return Whitelist()
    if not isinstance(raw, dict):
        raise ConfigError(f"{ctx}: 必须是映射，收到 {type(raw).__name__}")
    _check_unknown_keys(raw, frozenset({"enabled", "sources", "inline"}), ctx)
    enabled = _as_bool(raw.get("enabled"), f"{ctx}.enabled", True)
    sources = _load_sources(raw.get("sources"), f"{ctx}.sources")
    inline_raw = raw.get("inline") or []
    if not isinstance(inline_raw, list):
        raise ConfigError(f"{ctx}.inline: 必须是字符串列表，收到 {type(inline_raw).__name__}")
    inline = tuple(str(d).strip().lower().rstrip(".") for d in inline_raw if str(d).strip())
    return Whitelist(enabled=enabled, sources=sources, inline=inline)


def _load_targets(raw: Any, ctx: str) -> list[Target]:
    if not isinstance(raw, list):
        raise ConfigError(f"{ctx}: 必须是列表，收到 {type(raw).__name__}")
    targets: list[Target] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        tctx = f"{ctx}[{index}]"
        if not isinstance(item, dict):
            raise ConfigError(f"{tctx}: 每个目标组必须是映射，收到 {type(item).__name__}")
        _check_unknown_keys(
            item, frozenset({"name", "list_prefix", "policy_name", "sources", "whitelist"}), tctx
        )
        name = _as_str(item.get("name"), f"{tctx}.name", required=True)
        if name in seen:
            raise ConfigError(f"{tctx}.name: 目标组名称重复 {name!r}")
        seen.add(name)
        list_prefix = _as_str(item.get("list_prefix"), f"{tctx}.list_prefix", required=True)
        policy_name = item.get("policy_name")
        if policy_name is not None:
            policy_name = _as_str(policy_name, f"{tctx}.policy_name", required=True)
        sources = _load_sources(item.get("sources"), f"{tctx}.sources")
        if not sources:
            raise ConfigError(f"{tctx}.sources: 至少需要一个启用的源")
        whitelist = _load_whitelist(item.get("whitelist"), f"{tctx}.whitelist")
        targets.append(
            Target(
                name=name,
                list_prefix=list_prefix,
                policy_name=policy_name,
                sources=sources,
                whitelist=whitelist,
            )
        )
    return targets
