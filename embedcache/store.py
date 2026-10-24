"""A small SQLite-backed cache for text embeddings."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable, Optional


class _Expired:
    def __repr__(self) -> str:
        return "<ttl-expired>"


TTL_EXPIRED = _Expired()


class EmbeddingCache:
    """Persistent, disk-backed cache mapping text to embedding vectors."""

    def __init__(self, path: str | Path, ttl: Optional[float] = None) -> None:
        self.path = Path(path)
        self.ttl = ttl
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute("PRAGMA journal_mode = WAL")
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                key TEXT PRIMARY KEY,
                vector TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        self._conn.commit()

    @staticmethod
    def _key(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def set(self, text: str, vector: Iterable[float]) -> None:
        payload = json.dumps([float(v) for v in vector])
        self._conn.execute(
            "INSERT OR REPLACE INTO embeddings (key, vector, created_at) VALUES (?, ?, ?)",
            (self._key(text), payload, time.time()),
        )
        self._conn.commit()

    def get(self, text: str) -> Optional[list[float]]:
        row = self._conn.execute(
            "SELECT vector, created_at FROM embeddings WHERE key = ?",
            (self._key(text),),
        ).fetchone()
        if row is None:
            return None
        vector, created_at = row
        if self.ttl is not None and (time.time() - created_at) > self.ttl:
            return TTL_EXPIRED
        return json.loads(vector)

    def contains(self, text: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM embeddings WHERE key = ?", (self._key(text),)
        ).fetchone()
        return row is not None

    def delete(self, text: str) -> None:
        self._conn.execute("DELETE FROM embeddings WHERE key = ?", (self._key(text),))
        self._conn.commit()

    def clear(self) -> None:
        self._conn.execute("DELETE FROM embeddings")
        self._conn.commit()

    def __len__(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "EmbeddingCache":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()