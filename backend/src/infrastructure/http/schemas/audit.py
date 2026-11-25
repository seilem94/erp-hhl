"""Public representations of activity events and paginated results."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.entities.audit_log import AuditAction, AuditDetails, AuditEntity


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    actor_email: str
    accion: AuditAction
    entidad: AuditEntity
    entidad_id: str
    proyecto_id: UUID | None
    proyecto_nombre: str | None
    resumen: str
    detalles: AuditDetails | None


class AuditLogPageResponse(BaseModel):
    items: list[AuditLogResponse]
    has_more: bool
