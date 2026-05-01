from __future__ import annotations

import sqlite3
from pathlib import Path

from inventario.config import SCHEMA_FILE


def initialize_database(database_path: Path, schema_path: Path = SCHEMA_FILE) -> None:
    """Crea la base SQLite y aplica el esquema si hace falta."""
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        schema_sql = schema_path.read_text(encoding="utf-8")
        connection.executescript(schema_sql)
        connection.commit()
