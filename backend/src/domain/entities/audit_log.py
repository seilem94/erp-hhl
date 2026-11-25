"""Business activity recorded for projects and expenses."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TypeAlias
from uuid import UUID

ACTOR_EMAIL_MAX_LENGTH = 320


class AuditAction(StrEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditEntity(StrEnum):
    PROJECT = "PROYECTO"
    EXPENSE = "GASTO"


AuditValue: TypeAlias = str | bool | None
AuditSnapshot: TypeAlias = dict[str, AuditValue]
AuditDetails: TypeAlias = dict[str, AuditSnapshot | None]


@dataclass(frozen=True, kw_only=True)
class AuditLog:
    id: UUID
    created_at: datetime
    actor_email: str
    accion: AuditAction
    entidad: AuditEntity
    entidad_id: str
    proyecto_id: UUID | None
    resumen: str
    detalles: AuditDetails | None
    proyecto_nombre: str | None = None


@dataclass(frozen=True, kw_only=True)
class AuditFilters:
    limit: int
    offset: int
    proyecto_id: UUID | None = None
    entidad: AuditEntity | None = None
    accion: AuditAction | None = None
