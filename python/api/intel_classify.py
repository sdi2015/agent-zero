"""Expose OSINT classification helpers to the UI."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from flask import Request, Response

from agent_zero.intel.predict import classify_text
from agent_zero.intel.pipelines.osint import classify_url
from python.helpers.api import ApiHandler

LOGGER = logging.getLogger(__name__)


class IntelClassify(ApiHandler):
    """Classify free-form text or remote URLs using the intel helpers."""

    async def process(self, input: dict[str, Any], request: Request) -> dict[str, Any] | Response:  # type: ignore[override]
        payload = input or {}
        text = payload.get("text")
        url = payload.get("url")
        user = payload.get("user")
        justification = payload.get("justification")

        if text and url:
            return {
                "success": False,
                "error": "Provide text or a URL, not both.",
            }

        try:
            if text:
                if not isinstance(text, str) or not text.strip():
                    return {
                        "success": False,
                        "error": "Text must be a non-empty string.",
                    }
                result = await asyncio.to_thread(classify_text, text.strip())
            elif url:
                if not isinstance(url, str) or not url.strip():
                    return {
                        "success": False,
                        "error": "URL must be a non-empty string.",
                    }
                result = await asyncio.to_thread(
                    classify_url,
                    url.strip(),
                    user=_normalize_optional(user),
                    justification=_normalize_optional(justification),
                )
            else:
                return {
                    "success": False,
                    "error": "Provide text or a URL to classify.",
                }
        except Exception as exc:  # pragma: no cover - defensive guard for UI flow
            LOGGER.exception("intel classification failed")
            return {
                "success": False,
                "error": str(exc),
            }

        return {
            "success": True,
            "result": result,
        }


def _normalize_optional(value: Any) -> str | None:
    if isinstance(value, str):
        trimmed = value.strip()
        if trimmed:
            return trimmed
    return None


__all__ = ["IntelClassify"]
