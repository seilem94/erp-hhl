"""HTTP API for the system and project activity logs."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response

from src.domain.entities.audit_log import AuditAction, AuditEntity, AuditFilters
from src.infrastructure.http.dependencies import AuditServiceDep
from src.infrastructure.http.schemas.audit import AuditLogPageResponse, AuditLogResponse

router = APIRouter(tags=["Auditoría"])


@router.get(
    "/api/auditoria", response_model=AuditLogPageResponse, include_in_schema=False
)
@router.get(
    "/api/v1/audit-logs",
    response_model=AuditLogPageResponse,
    summary="Consultar la bitácora de actividad",
)
def list_audit_logs(
    response: Response,
    audit: AuditServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0, le=2**63 - 1)] = 0,
    proyecto_id: UUID | None = None,
    entidad: AuditEntity | None = None,
    accion: AuditAction | None = None,
) -> AuditLogPageResponse:
    response.headers["Cache-Control"] = "no-store"
    logs, has_more = audit.list_page(
        AuditFilters(
            limit=limit,
            offset=offset,
            proyecto_id=proyecto_id,
            entidad=entidad,
            accion=accion,
        )
    )
    return AuditLogPageResponse(
        items=[AuditLogResponse.model_validate(log) for log in logs], has_more=has_more
    )
