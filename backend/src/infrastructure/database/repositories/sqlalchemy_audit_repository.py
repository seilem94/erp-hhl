"""Read and append audit logs within the caller's transaction."""

from datetime import UTC

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from src.domain.entities.audit_log import (
    AuditAction,
    AuditEntity,
    AuditFilters,
    AuditLog,
)
from src.infrastructure.database.models import AuditLogORM, ProjectORM


class SQLAlchemyAuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, log: AuditLog) -> None:
        self._session.add(
            AuditLogORM(
                id=log.id,
                created_at=log.created_at,
                actor_email=log.actor_email,
                accion=str(log.accion),
                entidad=str(log.entidad),
                entidad_id=log.entidad_id,
                proyecto_id=log.proyecto_id,
                resumen=log.resumen,
                detalles=log.detalles,
            )
        )
        self._session.flush()

    def list(self, filters: AuditFilters) -> list[AuditLog]:
        stmt = select(AuditLogORM, ProjectORM.name).outerjoin(
            ProjectORM, ProjectORM.id == AuditLogORM.proyecto_id
        )
        if filters.proyecto_id is not None:
            project_id = str(filters.proyecto_id)
            # A moved expense belongs in the history of both accounts.
            stmt = stmt.where(
                or_(
                    AuditLogORM.proyecto_id == filters.proyecto_id,
                    and_(
                        AuditLogORM.entidad == AuditEntity.PROJECT,
                        AuditLogORM.entidad_id == project_id,
                    ),
                    AuditLogORM.detalles["antes"]["project_id"].as_string()
                    == project_id,
                    AuditLogORM.detalles["despues"]["project_id"].as_string()
                    == project_id,
                )
            )
        if filters.entidad is not None:
            stmt = stmt.where(AuditLogORM.entidad == filters.entidad)
        if filters.accion is not None:
            stmt = stmt.where(AuditLogORM.accion == filters.accion)
        stmt = (
            stmt.order_by(AuditLogORM.created_at.desc(), AuditLogORM.id.desc())
            .offset(filters.offset)
            .limit(filters.limit)
        )
        return [
            AuditLog(
                id=row.id,
                created_at=row.created_at.astimezone(UTC),
                actor_email=row.actor_email,
                accion=AuditAction(row.accion),
                entidad=AuditEntity(row.entidad),
                entidad_id=row.entidad_id,
                proyecto_id=row.proyecto_id,
                resumen=row.resumen,
                detalles=row.detalles,
                proyecto_nombre=project_name,
            )
            for row, project_name in self._session.execute(stmt)
        ]
