"""Tool wrapper around the intel classification helpers."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

from agent_zero.tools import TOOLS
from python.helpers.tool import Response, Tool


class IntelClassify(Tool):
    async def execute(self, **kwargs: Any) -> Response:
        payload: Dict[str, Any] = {
            key: value for key, value in (self.args or {}).items() if value is not None
        }
        payload.update({key: value for key, value in kwargs.items() if value is not None})

        if "text" not in payload and "url" not in payload:
            return Response(
                message="intel.classify requires 'text' or 'url' in the payload",
                break_loop=False,
            )

        payload.setdefault("user", getattr(self.agent, "agent_name", None))
        payload.setdefault("justification", "agent workflow")

        try:
            result = await asyncio.to_thread(TOOLS.invoke, "intel.classify", payload)
        except Exception as exc:  # pragma: no cover - runtime safety net
            return Response(message=f"intel.classify failed: {exc}", break_loop=False)

        return Response(
            message=json.dumps(result, indent=2),
            break_loop=False,
            additional={"intel_result": result},
        )
