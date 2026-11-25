"""Persistence contract for the activity log."""

from typing import Protocol

from src.domain.entities.audit_log import AuditFilters, AuditLog


class AuditRepository(Protocol):
    def add(self, log: AuditLog) -> None: ...

    def list(self, filters: AuditFilters) -> list[AuditLog]: ...
