"""Pipeline helpers for OSINT intelligence collection."""
from __future__ import annotations

import logging
import os
import re
import threading
import time
from typing import Dict
from urllib.parse import urljoin, urlparse
from urllib import robotparser

import requests
from bs4 import BeautifulSoup

from ..config import get_config
from ..predict import classify_text
from ..store import save_finding

logger = logging.getLogger(__name__)

IOC_RE: Dict[str, re.Pattern[str]] = {
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "sha256": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "domain": re.compile(r"\b[a-z0-9.-]+\.[a-z]{2,}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}

_USER_AGENT = os.environ.get("INTEL_USER_AGENT", "AgentZeroIntel/1.0")
_FETCH_TIMEOUT = float(os.environ.get("INTEL_FETCH_TIMEOUT", "15"))
_RATE_LIMIT_SECONDS = float(os.environ.get("INTEL_FETCH_COOLDOWN", "5"))

_last_request: Dict[str, float] = {}
_last_request_lock = threading.Lock()
_robot_cache: Dict[str, robotparser.RobotFileParser | None] = {}
_robot_lock = threading.Lock()


def allowed(url: str) -> bool:
    parsed = urlparse(url)
    return get_config().is_domain_allowed(parsed.netloc)


def _check_rate_limit(domain: str) -> None:
    now = time.monotonic()
    with _last_request_lock:
        last = _last_request.get(domain)
        if last is not None and now - last < _RATE_LIMIT_SECONDS:
            raise RuntimeError(f"rate limit exceeded for domain {domain}")
        _last_request[domain] = now


def _robots_allows(url: str) -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    with _robot_lock:
        parser = _robot_cache.get(base)
        if parser is None:
            parser = robotparser.RobotFileParser()
            parser.set_url(urljoin(base, "robots.txt"))
            try:
                parser.read()
            except Exception:  # pragma: no cover - network failures are logged elsewhere
                parser = None
            _robot_cache[base] = parser
    if parser is None:
        return True
    return parser.can_fetch(_USER_AGENT, url)


def _enforce_guardrails(url: str, *, user: str | None, justification: str | None) -> None:
    cfg = get_config()

    if not cfg.allow_remote_fetch:
        raise PermissionError("remote fetching disabled via INTEL_ALLOW_REMOTE_FETCH")

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if not domain:
        raise ValueError("unable to determine domain from URL")

    if not cfg.is_domain_allowed(domain):
        raise PermissionError(f"domain '{domain}' not in INTEL_ALLOWLIST")

    _check_rate_limit(domain)

    if not _robots_allows(url):
        raise PermissionError("fetch blocked by robots.txt policy")

    logger.info(
        "intel fetch approved",
        extra={
            "url": url,
            "domain": domain,
            "user": user or "unknown",
            "justification": justification or "unspecified",
        },
    )


def fetch_and_clean(url: str, *, user: str | None = None, justification: str | None = None) -> str:
    _enforce_guardrails(url, user=user, justification=justification)

    response = requests.get(
        url,
        timeout=_FETCH_TIMEOUT,
        headers={"User-Agent": _USER_AGENT},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text(separator=" ")
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def extract_iocs(text: str) -> Dict[str, list[str]]:
    return {kind: sorted(set(pattern.findall(text))) for kind, pattern in IOC_RE.items()}


def risk_score(label: int, probs: list[float]) -> float:
    weights = {0: 0.2, 1: 0.7, 2: 1.0}
    weight = weights.get(label, 0.2)
    return round(weight * max(probs or [0.0]), 3)


def classify_url(url: str, *, user: str | None = None, justification: str | None = None) -> Dict[str, object]:
    text = fetch_and_clean(url, user=user, justification=justification)
    result = classify_text(text, persist=False)
    iocs = extract_iocs(text)
    risk = risk_score(int(result["label"]), result["probs"])
    result.update({
        "iocs": iocs,
        "risk": risk,
        "source_url": url,
    })
    save_finding(result)
    return result


__all__ = [
    "IOC_RE",
    "allowed",
    "fetch_and_clean",
    "extract_iocs",
    "risk_score",
    "classify_url",
]
