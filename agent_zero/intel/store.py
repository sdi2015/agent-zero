"""Persistence helpers for intel classification results."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from pathlib import Path
from typing import Dict

DB_PATH = Path(os.environ.get("INTEL_DB_PATH", "intel.sqlite3"))

_init_lock = threading.Lock()
_initialised = False


def init() -> None:
    """Ensure the findings table exists."""

    global _initialised
    if _initialised:
        return

    with _init_lock:
        if _initialised:
            return
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS findings(
                    id INTEGER PRIMARY KEY,
                    ts INTEGER,
                    source_url TEXT,
                    label INTEGER,
                    probs TEXT,
                    iocs TEXT,
                    risk REAL
                )
                """
            )
        _initialised = True


def save_finding(data: Dict[str, object]) -> None:
    """Persist a single classification result."""

    init()
    probs = json.dumps(data.get("probs", []))
    iocs = json.dumps(data.get("iocs", {}))
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO findings(ts, source_url, label, probs, iocs, risk)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (
                int(time.time()),
                data.get("source_url"),
                int(data.get("label", 0)),
                probs,
                iocs,
                float(data.get("risk", 0.0)),
            ),
        )


# Ensure the schema exists as soon as the module is imported.
init()


__all__ = ["init", "save_finding", "DB_PATH"]
