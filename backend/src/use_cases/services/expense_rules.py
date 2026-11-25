"""Business validation shared by registration and editing."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.enums import ProjectStatus
from src.domain.exceptions import (
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
    ProjectCancelledError,
    ProjectNotFoundError,
)
from src.domain.repositories.project_repository import ProjectRepository


def validate_expense_amount(amount: Decimal) -> None:
    if not amount.is_finite() or amount <= 0:
        raise InvalidExpenseAmountError(amount)


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
