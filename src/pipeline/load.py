from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

import pandas as pd

from pipeline.config import ensure_parent

PRIMARY_KEYS = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "returns": "return_id",
}


def load_sqlite(
    database_path: Path, schema_path: Path, tables: dict[str, pd.DataFrame], mode: str = "full"
) -> dict[str, int]:
    if mode not in {"full", "incremental"}:
        raise ValueError("mode must be 'full' or 'incremental'")
    ensure_parent(database_path)
    with closing(sqlite3.connect(database_path)) as connection:
        if mode == "full" or not _table_exists(connection, "orders"):
            connection.executescript(schema_path.read_text(encoding="utf-8"))

        loaded_counts = {}
        for table_name, frame in tables.items():
            frame_to_load = frame if mode == "full" else _new_rows(connection, table_name, frame)
            frame_to_load.to_sql(table_name, connection, if_exists="append", index=False)
            loaded_counts[table_name] = len(frame_to_load)
        connection.commit()
        return loaded_counts


def record_pipeline_run(database_path: Path, summary: dict[str, Any]) -> None:
    with closing(sqlite3.connect(database_path)) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                mode TEXT NOT NULL,
                started_at_utc TEXT NOT NULL,
                finished_at_utc TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                status TEXT NOT NULL,
                rows_read INTEGER NOT NULL,
                rows_cleaned INTEGER NOT NULL,
                rows_rejected INTEGER NOT NULL,
                validation_issues INTEGER NOT NULL,
                loaded_rows INTEGER NOT NULL,
                exports_directory TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO pipeline_runs (
                run_id,
                mode,
                started_at_utc,
                finished_at_utc,
                duration_seconds,
                status,
                rows_read,
                rows_cleaned,
                rows_rejected,
                validation_issues,
                loaded_rows,
                exports_directory
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                summary["run_id"],
                summary["mode"],
                summary["started_at_utc"],
                summary["finished_at_utc"],
                summary["duration_seconds"],
                summary["status"],
                summary["rows_read"],
                summary["rows_cleaned"],
                summary["rows_rejected"],
                summary["validation_issues"],
                summary["loaded_rows"],
                summary["exports_directory"],
            ),
        )
        connection.commit()


def read_sql(database_path: Path, query: str) -> pd.DataFrame:
    with closing(sqlite3.connect(database_path)) as connection:
        return pd.read_sql_query(query, connection)


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    result = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return result is not None


def _new_rows(connection: sqlite3.Connection, table_name: str, frame: pd.DataFrame) -> pd.DataFrame:
    key = PRIMARY_KEYS[table_name]
    if frame.empty:
        return frame
    existing = pd.read_sql_query(f"SELECT {key} FROM {table_name}", connection)
    existing_keys = set(existing[key].astype(str))
    return frame[~frame[key].astype(str).isin(existing_keys)]
