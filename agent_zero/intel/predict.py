"""User-facing prediction helpers for OSINT classifiers."""
from __future__ import annotations

from agent_zero.intel.pipelines.osint import load_classifier


def classify_text(text: str) -> dict:
    """Classify free-form text and return a serialisable payload."""

    classifier = load_classifier()
    result = classifier.predict(text)
    return result.to_dict()


__all__ = ["classify_text"]
