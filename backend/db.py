from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pathlib import Path

from config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
# Ensure directory exists
if settings.database_url.startswith("sqlite"):
    db_path_str = settings.database_url.split("sqlite:///")[-1]
    db_path = Path(db_path_str)
    db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)