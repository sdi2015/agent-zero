"""Lightweight heuristics-based classifiers for open-source intelligence (OSINT).

These classes intentionally avoid heavyweight ML dependencies so they can be
used in environments where a full model may not yet be available. They provide
simple scoring suitable for demos and smoke tests while sharing an interface
compatible with future ML-backed implementations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass
class IntelClassification:
    """Represents a single classification result."""

    label: str
    confidence: float
    keywords: List[str]

    def to_dict(self) -> Dict[str, object]:
        """Convert the classification to a serialisable dictionary."""

        return {
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "keywords": self.keywords,
        }


class IntelClassifier:
    """A simple keyword-matching classifier for OSINT text."""

    def __init__(self, taxonomy: Dict[str, Iterable[str]] | None = None) -> None:
        if taxonomy is None:
            taxonomy = {
                "phishing": ["phish", "spoof", "credential", "login", "fraud"],
                "malware": ["malware", "ransom", "trojan", "botnet", "payload"],
                "vulnerability": ["cve", "zero-day", "exploit", "patch"],
                "threat-intel": ["campaign", "actor", "indicator", "osint"],
            }
        self._taxonomy = {
            label: {keyword.lower() for keyword in keywords}
            for label, keywords in taxonomy.items()
        }

    def predict(self, text: str) -> IntelClassification:
        """Produce a pseudo-probabilistic label for the provided text."""

        text_lower = text.lower()
        scores: Dict[str, int] = {}
        matched_keywords: Dict[str, List[str]] = {}
        for label, keywords in self._taxonomy.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                scores[label] = len(matches)
                matched_keywords[label] = matches

        if not scores:
            return IntelClassification(
                label="general",
                confidence=0.15,
                keywords=[],
            )

        best_label = max(scores, key=scores.get)
        max_score = scores[best_label]
        total = sum(scores.values()) or max_score
        confidence = max_score / total
        return IntelClassification(
            label=best_label,
            confidence=confidence,
            keywords=matched_keywords.get(best_label, []),
        )


__all__ = ["IntelClassification", "IntelClassifier"]
