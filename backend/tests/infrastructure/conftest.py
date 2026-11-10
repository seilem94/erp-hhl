"""Real PostgreSQL fixtures; no unconfigured test silently falls back to SQLite."""

import os
from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

from alembic import command
from src.core.config import Environment, settings
from src.infrastructure.database import session as database
from src.main import app
from tests.infrastructure.postgres import migration_config


@pytest.fixture
def pg_client(
    pg_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    """Keep the production get_db dependency and its function-scoped commit."""
    monkeypatch.setattr(
        database, "SessionLocal", sessionmaker(pg_engine, autoflush=False)
    )
    monkeypatch.setattr(settings, "ENV", Environment.DEVELOPMENT)
    previous = app.dependency_overrides.copy()
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.fixture
def pg_engine() -> Generator[Engine, None, None]:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for real PostgreSQL integration")
    admin = create_engine(url)
    if admin.dialect.name != "postgresql":
        admin.dispose()
        pytest.fail("TEST_DATABASE_URL must select PostgreSQL")
    schema = "hhl_test_" + uuid4().hex
    with admin.begin() as connection:
        connection.execute(CreateSchema(schema))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        with engine.begin() as connection:
            command.upgrade(migration_config(connection), "head")
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(DropSchema(schema, cascade=True))
        admin.dispose()
