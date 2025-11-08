"""RSS feed helpers for OSINT collection."""
from __future__ import annotations

import hashlib
from typing import Dict, Iterable, Iterator

import feedparser

from ..pipelines.osint import allowed


def _hash_url(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def iter_items(feed_url: str, limit: int = 50) -> Iterator[Dict[str, str]]:
    """Yield simplified feed entries for downstream processing."""

    if not allowed(feed_url):
        return

    parsed = feedparser.parse(feed_url)
    entries = getattr(parsed, "entries", [])
    if not entries and isinstance(parsed, dict):  # pragma: no cover - compatibility guard
        entries = parsed.get("entries", [])
    for entry in entries[:limit]:
        title = entry.get("title") if isinstance(entry, dict) else getattr(entry, "title", None)
        link = entry.get("link") if isinstance(entry, dict) else getattr(entry, "link", None)
        if not link:
            continue
        yield {
            "title": title or "",
            "link": link,
            "hash": _hash_url(link),
        }


def dedupe_items(items: Iterable[Dict[str, str]], seen_hashes: Iterable[str]) -> list[Dict[str, str]]:
    """Remove items whose hashes have already been processed."""

    seen = set(seen_hashes)
    result = []
    for item in items:
        if item["hash"] in seen:
            continue
        seen.add(item["hash"])
        result.append(item)
    return result


__all__ = ["iter_items", "dedupe_items"]
