"""Record business changes and expose a page of activity."""

from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.entities.audit_log import (
    AuditAction,
    AuditEntity,
    AuditFilters,
    AuditLog,
    AuditSnapshot,
    AuditValue,
)
from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.repositories.audit_repository import AuditRepository
from src.use_cases.services.monetary_precision import round_legacy_clp

LOCAL_AUDIT_ACTOR = "local@erp-hhl"

FIELD_LABELS = {
    "name": "nombre",
    "client": "cliente",
    "status": "estado",
    "start_date": "fecha de inicio",
    "end_date": "fecha de entrega",
    "budget": "presupuesto",
    "amount": "monto",
    "date": "fecha",
    "category": "categoría",
    "description": "descripción",
    "title": "título",
    "detail": "detalle",
    "project_id": "obra asociada",
    "has_receipt": "existencia de comprobante",
    "receipt_url": "enlace del comprobante",
}


def _project_values(project: Project) -> AuditSnapshot:
    return {
        "name": project.name,
        "client": project.client,
        "status": str(project.status),
        "start_date": project.start_date.isoformat(),
        "end_date": project.end_date.isoformat() if project.end_date else None,
        "budget": str(project.budget) if project.budget is not None else None,
        "description": project.description,
    }


def _expense_values(expense: Expense) -> AuditSnapshot:
    return {
        "amount": str(expense.amount),
        "date": expense.date.isoformat(),
        "category": str(expense.category),
        "title": expense.title,
        "detail": expense.detail,
        "project_id": str(expense.project_id) if expense.project_id else None,
        "has_receipt": expense.has_receipt,
        "receipt_url": expense.receipt_url,
    }


def _money(value: AuditValue) -> str:
    return (
        f"${int(value):,}".replace(",", ".") if isinstance(value, str) else "sin monto"
    )


def _legacy_money(value: AuditValue) -> str:
    if not isinstance(value, str):
        return "sin monto"
    whole, cents = f"{Decimal(value):,.2f}".split(".")
    return f"${whole.replace(',', '.')}" + (f",{cents}" if cents != "00" else "")


def _describe_change(field: str, old: AuditValue, new: AuditValue) -> str:
    label = FIELD_LABELS[field]
    if field in {"amount", "budget"}:
        return f"{label} {_money(old)} → {_money(new)}"
    if field == "project_id" and new is None:
        return "pasó a gasto operativo"
    return label


def _normalize_legacy_summary(log: AuditLog) -> AuditLog:
    """Display whole CLP while preserving the stored audit event and diff."""
    if log.accion is not AuditAction.UPDATE or log.detalles is None:
        return log
    before = log.detalles.get("antes") or {}
    after = log.detalles.get("despues") or {}
    field = "amount" if log.entidad is AuditEntity.EXPENSE else "budget"
    old, new = before.get(field), after.get(field)
    if not any(isinstance(value, str) and "." in value for value in (old, new)):
        return log
    clause = f"{FIELD_LABELS[field]} {_legacy_money(old)} → {_legacy_money(new)}"
    prefix, found, suffix = log.resumen.rpartition(clause)
    if not found:
        return log
    old_clp = str(round_legacy_clp(Decimal(old))) if isinstance(old, str) else old
    new_clp = str(round_legacy_clp(Decimal(new))) if isinstance(new, str) else new
    return replace(
        log, resumen=prefix + _describe_change(field, old_clp, new_clp) + suffix
    )


class AuditService:
    def __init__(
        self, repository: AuditRepository, *, actor_email: str = LOCAL_AUDIT_ACTOR
    ) -> None:
        self._repository = repository
        self._actor_email = actor_email

    def record_project(self, before: Project | None, after: Project | None) -> None:
        project = after or before
        if project is None:
            return
        self._record(
            entity=AuditEntity.PROJECT,
            entity_id=project.id,
            label=project.name,
            project_id=project.id,
            before=_project_values(before) if before else None,
            after=_project_values(after) if after else None,
        )

    def record_expense(self, before: Expense | None, after: Expense | None) -> None:
        expense = after or before
        if expense is None:
            return
        self._record(
            entity=AuditEntity.EXPENSE,
            entity_id=expense.id,
            label=expense.title,
            project_id=expense.project_id,
            before=_expense_values(before) if before else None,
            after=_expense_values(after) if after else None,
        )

    def _record(
        self,
        *,
        entity: AuditEntity,
        entity_id: UUID,
        label: str,
        project_id: UUID | None,
        before: AuditSnapshot | None,
        after: AuditSnapshot | None,
    ) -> None:
        subject = "proyecto" if entity is AuditEntity.PROJECT else "gasto"
        title = " ".join(label.split())
        if len(title) > 100:
            title = f"{title[:99]}…"
        subject = f"{subject} «{title}»" if title else subject
        if before is None:
            action = AuditAction.CREATE
            summary = f"Creó {subject}"
        elif after is None:
            action = AuditAction.DELETE
            summary = f"Eliminó {subject}"
        else:
            after = {
                field: value for field, value in after.items() if before[field] != value
            }
            if not after:
                return
            before = {field: before[field] for field in after}
            changes = ", ".join(
                _describe_change(field, before[field], value)
                for field, value in after.items()
            )
            action = AuditAction.UPDATE
            summary = f"Actualizó {subject} ({changes})"
        self._repository.add(
            AuditLog(
                id=uuid4(),
                created_at=datetime.now(UTC),
                actor_email=self._actor_email,
                accion=action,
                entidad=entity,
                entidad_id=str(entity_id),
                proyecto_id=project_id,
                resumen=summary,
                detalles={"antes": before, "despues": after},
            )
        )

    def list_page(self, filters: AuditFilters) -> tuple[list[AuditLog], bool]:
        rows = self._repository.list(replace(filters, limit=filters.limit + 1))
        return [_normalize_legacy_summary(log) for log in rows[: filters.limit]], len(
            rows
        ) > filters.limit
