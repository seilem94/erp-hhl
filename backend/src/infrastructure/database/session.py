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

from src.core.config import settings

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
        def list_items(db: Session = Depends(get_db, scope="function")) -> list[Item]:
            return db.query(Item).all()

    Uso manual (ejecuta también el finalizador transaccional)::

        with contextlib.contextmanager(get_db)() as db:
            ...

    La inyección HTTP usa scope="function" para confirmar o fallar antes de
    enviar http.response.start. No usar el scope por defecto para escrituras.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
