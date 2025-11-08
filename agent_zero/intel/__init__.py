"""Agent Zero intel package initialisation."""
from __future__ import annotations

from .store import init as _init_store

# Ensure the persistence layer is ready when the package is imported.
_init_store()

__all__: list[str] = []
