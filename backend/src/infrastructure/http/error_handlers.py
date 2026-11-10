"""Global HTTP exception handlers for domain exceptions."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    AuthorizationDeniedError,
    DomainException,
    FinancialSummaryUnavailableError,
    IdempotencyConflictError,
    IdentityProviderUnavailableError,
    InvalidCanonicalContentError,
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
    InvalidMonetaryPrecisionError,
    InvalidOperationIdError,
    InvalidSummaryDateRangeError,
    OperationNotFoundError,
    OperationReconciliationRequiredError,
    OperationUnresolvedError,
    ProjectCancelledError,
    ProjectNotFoundError,
    ProjectSummaryUnavailableError,
    ResourceIdentityConflictError,
)


def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Map domain exceptions to standard JSON responses."""
    operation_code: str | None = None
    if isinstance(exc, IdempotencyConflictError):
        operation_code = "idempotency_conflict"
    elif isinstance(exc, ResourceIdentityConflictError):
        operation_code = "resource_identity_conflict"
    elif isinstance(exc, OperationReconciliationRequiredError):
        operation_code = "operation_reconciliation_required"
    elif isinstance(exc, OperationUnresolvedError):
        operation_code = "operation_unresolved"
    elif isinstance(exc, OperationNotFoundError):
        operation_code = "operation_unknown"
    if operation_code is not None:
        if isinstance(exc, OperationUnresolvedError):
            operation_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif isinstance(exc, OperationNotFoundError):
            operation_status = status.HTTP_404_NOT_FOUND
        else:
            operation_status = status.HTTP_409_CONFLICT
        return JSONResponse(
            status_code=operation_status,
            content={"detail": {"code": operation_code, "message": str(exc)}},
            headers={"Cache-Control": "no-store"},
        )
    if isinstance(exc, (ProjectNotFoundError, ProjectSummaryUnavailableError)):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, AuthorizationDeniedError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(
        exc, (IdentityProviderUnavailableError, FinancialSummaryUnavailableError)
    ):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(
        exc,
        (
            InvalidExpenseAmountError,
            InvalidExpenseDateError,
            InvalidCanonicalContentError,
            InvalidMonetaryPrecisionError,
            InvalidOperationIdError,
            InvalidSummaryDateRangeError,
            ProjectCancelledError,
        ),
    ):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc)},
        headers=(
            {"Cache-Control": "no-store"}
            if isinstance(exc, IdentityProviderUnavailableError)
            else None
        ),
    )
