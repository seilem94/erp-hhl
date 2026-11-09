"""Shared Alembic configuration for isolated PostgreSQL integration schemas."""

from pathlib import Path

from alembic.config import Config
from sqlalchemy.engine import Connection


def migration_config(connection: Connection) -> Config:
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    config.attributes["connection"] = connection
    return config
