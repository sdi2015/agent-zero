"""Persistence helpers for intel classification results."""
from __future__ import annotations

import json
import time
from typing import Dict, Iterable, List

from sqlalchemy import select

from .alerts import notify_slack
from .db import Finding, get_session, session_scope


def init() -> None:
    """Ensure the database schema exists."""

    session = get_session()
    session.close()


def save_finding(data: Dict[str, object]) -> None:
    """Persist a single classification result and emit alerts."""

    payload = {
        "ts": int(time.time()),
        "source_url": data.get("source_url"),
        "label": int(data.get("label", 0)),
        "probs": json.dumps(data.get("probs", [])),
        "iocs": json.dumps(data.get("iocs", {})),
        "risk": float(data.get("risk", 0.0)),
    }

    with session_scope() as session:
        record = None
        if payload["source_url"]:
            stmt = select(Finding).where(Finding.source_url == payload["source_url"]).limit(1)
            record = session.execute(stmt).scalar_one_or_none()
        if record is None:
            record = Finding(**payload)
        else:
            for key, value in payload.items():
                setattr(record, key, value)
        session.add(record)

    notify_slack({**data, "risk": payload["risk"], "source_url": payload["source_url"]})


def list_findings(limit: int = 50) -> List[Dict[str, object]]:
    """Return the most recent findings in descending timestamp order."""

    stmt = select(Finding).order_by(Finding.ts.desc()).limit(limit)
    results: List[Dict[str, object]] = []
    with session_scope() as session:
        for row in session.execute(stmt).scalars():
            results.append(
                {
                    "id": row.id,
                    "ts": row.ts,
                    "source_url": row.source_url,
                    "label": row.label,
                    "probs": json.loads(row.probs or "[]"),
                    "iocs": json.loads(row.iocs or "{}"),
                    "risk": row.risk,
                }
            )
    return results


def seen_urls(urls: Iterable[str]) -> set[str]:
    """Return the subset of URLs that already exist in the findings table."""

    cleaned = {url for url in urls if url}
    if not cleaned:
        return set()

    stmt = select(Finding.source_url).where(Finding.source_url.in_(cleaned))
    with session_scope() as session:
        return {row[0] for row in session.execute(stmt) if row[0]}


init()


__all__ = ["init", "save_finding", "list_findings", "seen_urls"]
