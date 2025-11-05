"""Runtime registry for lightweight Agent Zero tools."""
from __future__ import annotations

from typing import Any, Callable, Dict


class ToolRegistry:
    """Minimal callable registry used by helper integrations."""

    def __init__(self) -> None:
        self._registry: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}

    def register(self, name: str, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self._registry[name] = func

    def invoke(self, name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self._registry:
            raise KeyError(f"tool '{name}' not registered")
        return self._registry[name](payload)

    def __contains__(self, name: str) -> bool:  # pragma: no cover - convenience helper
        return name in self._registry


TOOLS = ToolRegistry()

# Ensure built-in tools register themselves.
from . import intel  # noqa: E402,F401  # pylint: disable=wrong-import-position

__all__ = ["TOOLS", "ToolRegistry"]
