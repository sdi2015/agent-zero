"""SQLAlchemy models and session helpers for intel findings."""
from __future__ import annotations

import os
from contextlib import contextmanager
from functools import lru_cache
from typing import Iterator

from sqlalchemy import Column, Float, Integer, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    ts = Column(Integer, index=True)
    source_url = Column(Text, index=True, nullable=True)
    label = Column(Integer)
    probs = Column(Text)
    iocs = Column(Text)
    risk = Column(Float)


@lru_cache(maxsize=1)
def _engine(url: str | None = None):
    actual_url = url or os.environ.get("INTEL_DB_URL", "sqlite:///intel.sqlite3")
    return create_engine(actual_url, future=True)


@lru_cache(maxsize=1)
def _session_factory(url: str | None = None):
    engine = _engine(url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_session(url: str | None = None) -> Session:
    factory = _session_factory(url)
    return factory()


@contextmanager
def session_scope(url: str | None = None) -> Iterator[Session]:
    session = get_session(url)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["Finding", "get_session", "session_scope", "Base"]
