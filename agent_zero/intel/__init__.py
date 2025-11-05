"""Agent Zero intel package initialisation."""
from __future__ import annotations

from .store import init as _init_store

# Ensure the sqlite schema exists when the package is imported.
_init_store()

__all__: list[str] = []
