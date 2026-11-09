"""Alembic environment configuration.

Loads the database URL dynamically from ``core.config.settings``
(pydantic-settings) instead of reading it from ``alembic.ini``, so the
single source of truth is always the ``.env`` file / environment variable.
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from alembic import context

# ── Alembic Config object ──────────────────────────────────────────────
config = context.config

# Python logging from the .ini file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Dynamic URL override ──────────────────────────────────────────────
# Import *after* prepend_sys_path is applied by Alembic so that "src" is
# already on sys.path.
from core.config import settings  # noqa: E402
from infrastructure.database.models import Base  # noqa: E402

config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

# ── Metadata for autogenerate support ─────────────────────────────────
target_metadata = Base.metadata


# ── Offline mode ──────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Emits SQL to stdout instead of executing it against the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ── Online mode ───────────────────────────────────────────────────────
def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    # Integration tests supply an isolated schema connection, never a business DB.
    supplied: object = config.attributes.get("connection")
    if supplied is not None:
        if not isinstance(supplied, Connection):
            raise TypeError("Alembic connection must be a SQLAlchemy Connection.")
        _run_on_connection(supplied)
        return

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        _run_on_connection(connection)


def _run_on_connection(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
