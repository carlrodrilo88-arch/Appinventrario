from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "database"
DATABASE_FILE = DATABASE_DIR / "inventario.db"
SCHEMA_FILE = DATABASE_DIR / "schema.sql"
OUTPUT_DIR = BASE_DIR / "output"
SALIDAS_PDF_DIR = OUTPUT_DIR / "salidas"
REPORTES_PDF_DIR = OUTPUT_DIR / "reportes"
