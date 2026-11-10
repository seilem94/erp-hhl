"""Errors for opt-in idempotent writes; legacy error bodies remain unchanged."""

from typing import Literal

from pydantic import BaseModel

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
    ]
    message: str


class OperationErrorResponse(BaseModel):
    detail: OperationErrorDetail
