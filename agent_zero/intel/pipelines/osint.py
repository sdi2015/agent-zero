"""Pipeline loaders for OSINT classifiers."""
from __future__ import annotations

from functools import lru_cache

from agent_zero.intel.models import IntelClassifier


@lru_cache(maxsize=1)
def load_classifier() -> IntelClassifier:
    """Return a cached instance of the default OSINT classifier."""

    return IntelClassifier()


__all__ = ["load_classifier"]
