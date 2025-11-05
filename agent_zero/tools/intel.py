"""Intel-related helper registered with the Agent Zero tool registry."""
from __future__ import annotations

from typing import Any, Dict

from agent_zero.intel.pipelines.osint import classify_url
from agent_zero.intel.predict import classify_text

from . import TOOLS


def intel_classify(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):  # pragma: no cover - defensive check
        return {"error": "payload must be a dictionary"}

    if "url" in payload:
        return classify_url(
            payload["url"],
            user=payload.get("user"),
            justification=payload.get("justification"),
        )
    if "text" in payload:
        return classify_text(payload["text"])
    return {"error": "provide 'text' or 'url'"}


TOOLS.register("intel.classify", intel_classify)

__all__ = ["intel_classify"]
