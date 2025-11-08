"""Alerting helpers for high-risk intel findings."""
from __future__ import annotations

import json
import os
from typing import Dict

import requests

DEFAULT_THRESHOLD = float(os.environ.get("INTEL_ALERT_THRESHOLD", "0.8"))


def notify_slack(finding: Dict[str, object]) -> None:
    risk = float(finding.get("risk", 0.0) or 0.0)
    if risk < DEFAULT_THRESHOLD:
        return

    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        return

    text = finding.get("source_url") or "unknown source"
    message = {
        "text": f":rotating_light: Intel finding {risk:.2f} – {text}\n```{json.dumps(finding, indent=2)}```",
    }
    try:
        requests.post(webhook, json=message, timeout=10)
    except Exception:  # pragma: no cover - best-effort alerting
        return


__all__ = ["notify_slack", "DEFAULT_THRESHOLD"]
