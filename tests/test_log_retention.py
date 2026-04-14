from __future__ import annotations

import sqlite3
import time
from pathlib import Path

from zai2api.db import Database, LOG_RETENTION_DAYS_KEY


def test_delete_logs_before_prunes_entries_older_than_retention_window(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "state.db"), log_retention_days=7)
    db.initialize()

    now = int(time.time())
    with sqlite3.connect(db.path) as conn:
        conn.execute(
            "INSERT INTO logs(created_at, level, category, message, details) VALUES (?, ?, ?, ?, ?)",
            (now - 10 * 86400, "info", "tests", "old-log", None),
        )
        conn.execute(
            "INSERT INTO logs(created_at, level, category, message, details) VALUES (?, ?, ?, ?, ?)",
            (now, "info", "tests", "fresh-log", None),
        )

    cutoff = now - (7 * 86400)
    deleted = db.delete_logs_before(cutoff)
    assert deleted == 1

    logs = db.list_logs(limit=20)
    assert [item.message for item in logs] == ["fresh-log"]


def test_log_retention_days_from_database_setting(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "state.db"))
    db.initialize()
    db.set_setting(LOG_RETENTION_DAYS_KEY, "14")
    assert db._log_retention_days() == 14


def test_log_retention_days_override_takes_precedence(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "state.db"), log_retention_days=3)
    db.initialize()
    db.set_setting(LOG_RETENTION_DAYS_KEY, "14")
    assert db._log_retention_days() == 3
