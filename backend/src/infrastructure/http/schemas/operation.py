"""Public recovery snapshots and errors, independent of the JSONB codec."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from src.domain.entities.operation import OperationRecord
from src.domain.enums import CommandType, OperationState, ResourceType
from src.domain.exceptions import OperationReconciliationRequiredError
from src.domain.value_objects.operation_result import ProjectSnapshot
from src.infrastructure.http.schemas.expense import ExpenseResponse
from src.infrastructure.http.schemas.project import ProjectResponse

IDEMPOTENCY_RESPONSE_HEADERS: dict[str, dict[str, object]] = {
    "Idempotency-Replayed": {
        "description": (
            "Presente solo con deduplicación: false para la primera ejecución, "
            "true para el snapshot recuperado. Su ausencia no ofrece esa garantía."
        ),
        "schema": {"type": "string", "enum": ["true", "false"]},
    }
}


class OperationErrorDetail(BaseModel):
    code: Literal[
        "idempotency_conflict",
        "resource_identity_conflict",
        "operation_unresolved",
        "operation_reconciliation_required",
        "operation_unknown",
    ]
    message: str


class OperationErrorResponse(BaseModel):
    detail: OperationErrorDetail


class OperationResultResponse(BaseModel):
    operation_id: UUID
    state: Literal[OperationState.CONFIRMED] = OperationState.CONFIRMED
    command_type: CommandType
    resource_type: ResourceType
    result_resource_id: UUID
    result_schema_version: int
    created_at: datetime
    completed_at: datetime
    result: ProjectResponse | ExpenseResponse

    @classmethod
    def from_operation(cls, operation: OperationRecord) -> OperationResultResponse:
        snapshot = operation.recover_result()
        version, completed_at = operation.result_schema_version, operation.completed_at
        if version is None or completed_at is None:
            raise OperationReconciliationRequiredError(
                "Confirmed operation metadata is incomplete."
            )
        result = (
            ProjectResponse.model_validate(snapshot)
            if isinstance(snapshot, ProjectSnapshot)
            else ExpenseResponse.model_validate(snapshot)
        )
        return cls(
            operation_id=operation.key.operation_id,
            command_type=operation.command_type,
            resource_type=operation.resource_type,
            result_resource_id=snapshot.id,
            result_schema_version=version,
            created_at=operation.created_at,
            completed_at=completed_at,
            result=result,
        )
