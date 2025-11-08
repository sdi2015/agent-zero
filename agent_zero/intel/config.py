"""Configuration helpers for the intel subsystem."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
from typing import Iterable, Set

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - fallback for older runtimes
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(frozen=True)
class IntelConfig:
    """Runtime configuration for remote collection guardrails."""

    allow_remote_fetch: bool
    allowlist: frozenset[str]

    def is_domain_allowed(self, domain: str) -> bool:
        domain = domain.lower()
        if not domain:
            return False
        if not self.allowlist:
            return False
        if "*" in self.allowlist:
            return True
        if domain in self.allowlist:
            return True
        return any(domain.endswith(f".{item}") for item in self.allowlist)


def _parse_bool(value: str | bool | None, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _parse_allowlist(raw: Iterable[str]) -> Set[str]:
    items = {item.strip().lower() for item in raw if item.strip()}
    return items


@lru_cache(maxsize=1)
def get_config() -> IntelConfig:
    """Load configuration from disk and environment variables."""

    default = IntelConfig(
        allow_remote_fetch=False,
        allowlist=frozenset(),
    )

    path = Path(os.environ.get("INTEL_CONFIG_PATH", "conf/intel.toml"))
    data: dict[str, object] = {}
    if path.is_file():
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
            section = raw.get("intel") if isinstance(raw, dict) else None
            if isinstance(section, dict):
                data = section
            elif isinstance(raw, dict):
                data = raw  # backwards compatibility with flat config files

    allow_remote_fetch = _parse_bool(data.get("allow_remote_fetch"), default.allow_remote_fetch)
    raw_allowlist = data.get("allowlist", [])
    if isinstance(raw_allowlist, str):
        raw_allowlist = raw_allowlist.split(",")
    elif not isinstance(raw_allowlist, (list, tuple, set)):
        raw_allowlist = []
    allowlist = _parse_allowlist(raw_allowlist)

    # Environment variables override file configuration.
    allow_remote_fetch = _parse_bool(
        os.environ.get("INTEL_ALLOW_REMOTE_FETCH"), allow_remote_fetch
    )
    env_allowlist = os.environ.get("INTEL_ALLOWLIST")
    if env_allowlist:
        allowlist = _parse_allowlist(env_allowlist.split(","))

    # Provide safe defaults to ensure smoke tests do not leak data.
    if not allowlist:
        allowlist = {"localhost", "127.0.0.1"}

    return IntelConfig(
        allow_remote_fetch=allow_remote_fetch,
        allowlist=frozenset(allowlist),
    )


def reload_config() -> None:
    """Clear the cached configuration (useful for tests)."""

    get_config.cache_clear()  # type: ignore[attr-defined]


__all__ = ["IntelConfig", "get_config", "reload_config"]
