"""Configuración del motor SQLAlchemy y fábrica de sesiones síncronas.

Expone:
- ``engine``    → motor configurado con pool_pre_ping para detectar conexiones caídas.
- ``SessionLocal`` → fábrica de sesiones (autocommit=False, autoflush=False).
- ``get_db``    → generador de dependencia compatible con FastAPI / inyección manual.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings

# --------------------------------------------------------------------------- #
# Motor                                                                         #
# --------------------------------------------------------------------------- #
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,  # verifica la conexión antes de usarla (evita "idle" colgadas)
)

# --------------------------------------------------------------------------- #
# Fábrica de sesiones                                                           #
# --------------------------------------------------------------------------- #
SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    class_=Session,
)


# --------------------------------------------------------------------------- #
# Generador de dependencia                                                      #
# --------------------------------------------------------------------------- #
def get_db() -> Generator[Session, None, None]:
    """Generador que entrega una sesión de base de datos y garantiza su cierre.

    Uso típico con FastAPI::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)) -> list[Item]:
            return db.query(Item).all()

    Uso manual::

        with contextlib.closing(next(get_db())) as db:
            ...
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
