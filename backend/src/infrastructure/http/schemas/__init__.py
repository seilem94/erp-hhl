"""Pydantic schemas for HTTP requests and responses."""

from src.infrastructure.http.schemas.error import ErrorResponse
from src.infrastructure.http.schemas.expense import (
    ExpenseResponse,
    RegisterExpenseRequest,
)
from src.infrastructure.http.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)

__all__ = [
    "CreateProjectRequest",
    "ErrorResponse",
    "ExpenseResponse",
    "ProjectResponse",
    "RegisterExpenseRequest",
    "UpdateProjectRequest",
]
