from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from inventario.config import DATABASE_FILE


DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
