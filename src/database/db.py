from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from src.config import DATABASE_PATH


def get_connection(db_path: str | Path = DATABASE_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=OFF")
    connection.execute("PRAGMA synchronous=OFF")
    connection.execute("PRAGMA temp_store=MEMORY")
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: str | Path = DATABASE_PATH) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unit_id INTEGER NOT NULL,
                predicted_rul REAL NOT NULL,
                risk_level TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def insert_prediction(
    unit_id: int,
    predicted_rul: float,
    risk_level: str,
    recommendation: str,
    db_path: str | Path = DATABASE_PATH,
) -> None:
    init_db(db_path)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO prediction_history
                (unit_id, predicted_rul, risk_level, recommendation, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                unit_id,
                predicted_rul,
                risk_level,
                recommendation,
                datetime.now(UTC).isoformat(),
            ),
        )


def fetch_recent_predictions(limit: int = 25, db_path: str | Path = DATABASE_PATH) -> list[dict]:
    init_db(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, unit_id, predicted_rul, risk_level, recommendation, created_at
            FROM prediction_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]
