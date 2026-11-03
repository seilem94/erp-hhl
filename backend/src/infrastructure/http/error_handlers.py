"""Global HTTP exception handlers for domain exceptions."""

from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    DomainException,
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
    ProjectCancelledError,
    ProjectNotFoundError,
)


def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Map domain exceptions to standard JSON responses."""
    if isinstance(exc, ProjectNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(
        exc,
        (
            InvalidExpenseAmountError,
            InvalidExpenseDateError,
            ProjectCancelledError,
        ),
    ):
        status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(
        status_code=status_code,
        content={"detail": str(exc)},
    )
