"""
PERSISTENT_EXTERNAL_MEMORY_FABRIC

Mémoire externe persistante fondée sur SQLite avec configuration
robuste inspirée des recommandations officielles :
- PRAGMA journal_mode = WAL
- PRAGMA auto_vacuum = INCREMENTAL
- PRAGMA incremental_vacuum
- gestion de quotas
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path


class PersistentExternalMemoryFabric:
    MIN_EFFECTIVE_QUOTA_BYTES = 100_000

    def __init__(self, db_path: str | None = None, quota_bytes: int = 500_000_000):
        root = Path.home() / "open-cognitive-ecology"
        memory_dir = root / "external_memory"
        memory_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path(db_path) if db_path else (memory_dir / "memory.db")
        self.quota_bytes = max(int(quota_bytes), self.MIN_EFFECTIVE_QUOTA_BYTES)

        initialize_new_db = not self.db_path.exists()

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL")

        if initialize_new_db:
            self.conn.execute("PRAGMA auto_vacuum=INCREMENTAL")
            self.conn.execute("VACUUM")

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        self.conn.commit()

    def _db_size(self) -> int:
        total = 0
        for suffix in ("", "-wal", "-shm"):
            path = Path(str(self.db_path) + suffix)
            if path.exists():
                total += path.stat().st_size
        return total

    def _entry_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM memory").fetchone()
        return int(row[0])

    def _incremental_vacuum(self) -> None:
        try:
            self.conn.execute("PRAGMA incremental_vacuum")
            self.conn.commit()
        except Exception:
            pass

    def _enforce_quota(self) -> None:
        while self._db_size() > self.quota_bytes and self._entry_count() > 1:
            row = self.conn.execute(
                "SELECT key FROM memory ORDER BY updated_at ASC LIMIT 1"
            ).fetchone()
            if not row:
                break
            self.conn.execute("DELETE FROM memory WHERE key = ?", (row[0],))
            self.conn.commit()
            self._incremental_vacuum()

    def store(self, key: str, value) -> None:
        payload = json.dumps(value, ensure_ascii=False)
        self.conn.execute(
            """
            INSERT INTO memory(key, value_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value_json = excluded.value_json,
                updated_at = excluded.updated_at
            """,
            (key, payload, time.time()),
        )
        self.conn.commit()
        self._enforce_quota()

    def recall(self, key: str, default=None):
        row = self.conn.execute(
            "SELECT value_json FROM memory WHERE key = ?",
            (key,),
        ).fetchone()
        if not row:
            return default
        return json.loads(row[0])

    def delete(self, key: str) -> None:
        self.conn.execute("DELETE FROM memory WHERE key = ?", (key,))
        self.conn.commit()
        self._incremental_vacuum()

    def list_keys(self):
        rows = self.conn.execute(
            "SELECT key FROM memory ORDER BY updated_at DESC"
        ).fetchall()
        return [r[0] for r in rows]

    def close(self) -> None:
        self.conn.close()
