"""Simple scheduler helpers for processing OSINT feeds."""
from __future__ import annotations

from typing import List

from ..pipelines.osint import classify_url
from ..store import seen_urls
from .rss import dedupe_items, iter_items


def ingest_feed(
    feed_url: str,
    *,
    limit: int = 50,
    user: str | None = None,
    justification: str | None = None,
) -> List[dict[str, object]]:
    """Fetch a feed, classify unseen links, and return their findings."""

    items = list(iter_items(feed_url, limit=limit))
    if not items:
        return []

    already_seen = seen_urls(item["link"] for item in items)
    unseen_items = [item for item in items if item["link"] not in already_seen]
    deduped = dedupe_items(unseen_items, ())

    results: List[dict[str, object]] = []
    for item in deduped:
        result = classify_url(item["link"], user=user, justification=justification)
        results.append(result)
    return results


__all__ = ["ingest_feed"]
