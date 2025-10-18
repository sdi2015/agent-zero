"""Utilities to smooth over FastMCP upgrades without touching site-packages.

This module rewrites known-problematic snippets in fastmcp<=2.3 that are
incompatible with Pydantic v2. The upstream project resolved these issues in
later releases by removing default assignments when ``default_factory`` is set.

In our offline environment we cannot upgrade the dependency at runtime, so we
patch the installed module the first time this helper is imported. The patch is
idempotent and safe to run multiple times.
"""
from __future__ import annotations

from importlib.util import find_spec
from pathlib import Path


def ensure_settings_default_factories_are_clean() -> None:
    """Remove legacy ``= <default>`` suffixes in ``fastmcp.settings``.

    Older FastMCP releases defined Pydantic fields with both a ``default``/
    ``default_factory`` and a trailing assignment (``]= []``). Pydantic v2
    forbids this combination and raises ``TypeError: cannot specify both
    default and default_factory`` during import. Upstream removed the trailing
    assignments; we do the same by editing the module in-place the first time
    FastMCP is imported.
    """

    spec = find_spec("fastmcp")
    if not spec or not spec.origin:
        return

    settings_path = Path(spec.origin).parent / "settings.py"
    if not settings_path.exists():
        return

    text = settings_path.read_text()

    replacements = {
        "] = True": "]",
        "] = False": "]",
        "] = []": "]",
    }

    if not any(token in text for token in replacements):
        return  # already patched or running on a newer FastMCP

    new_text = text
    for old, new in replacements.items():
        new_text = new_text.replace(old, new)

    settings_path.write_text(new_text)


__all__ = ["ensure_settings_default_factories_are_clean"]
