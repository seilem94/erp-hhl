"""Business validation shared by registration and editing."""

from datetime import date
from uuid import UUID

from src.domain.enums import ProjectStatus
from src.domain.exceptions import (
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
    InvalidExpenseTitleError,
    ProjectCancelledError,
    ProjectNotFoundError,
)
from src.domain.repositories.project_repository import ProjectRepository
from src.use_cases.services.monetary_precision import validate_clp


def validate_expense_amount(amount: int) -> None:
    if type(amount) is int and amount <= 0:
        raise InvalidExpenseAmountError(amount)
    validate_clp(amount)


def validate_expense_title(title: str) -> None:
    if not title.strip():
        raise InvalidExpenseTitleError


def validate_expense_date(expense_date: date, today: date) -> None:
    if expense_date > today:
        raise InvalidExpenseDateError(expense_date, today)


def validate_expense_project(
    project_repo: ProjectRepository, project_id: UUID | None
) -> None:
    if project_id is None:
        return
    project = project_repo.get_by_id(project_id)
    if project is None:
        raise ProjectNotFoundError(project_id)
    if project.status is ProjectStatus.CANCELLED:
        raise ProjectCancelledError(project_id, project.status)
