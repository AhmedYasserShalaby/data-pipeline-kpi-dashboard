from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from pipeline.config import ensure_parent


def load_sqlite(database_path: Path, schema_path: Path, tables: dict[str, pd.DataFrame]) -> None:
    ensure_parent(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
        for table_name, frame in tables.items():
            frame.to_sql(table_name, connection, if_exists="append", index=False)


def read_sql(database_path: Path, query: str) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(query, connection)

