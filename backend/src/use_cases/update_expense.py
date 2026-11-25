"""Apply a partial update to an existing expense."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from enum import Enum, auto
from uuid import UUID

from src.domain.entities.expense import Expense
from src.domain.enums import ExpenseCategory
from src.domain.exceptions import ExpenseNotFoundError
from src.domain.repositories.expense_repository import ExpenseRepository
from src.domain.repositories.project_repository import ProjectRepository
from src.use_cases.services.expense_rules import (
    validate_expense_amount,
    validate_expense_date,
    validate_expense_project,
    validate_expense_title,
)


class _Unset(Enum):
    VALUE = auto()


UNSET = _Unset.VALUE


@dataclass(frozen=True, kw_only=True)
class UpdateExpenseDTO:
    expense_id: UUID
    amount: int | None = None
    date: date | None = None
    category: ExpenseCategory | None = None
    title: str | None = None
    detail: str | None | _Unset = UNSET
    project_id: UUID | None | _Unset = UNSET
    has_receipt: bool | None = None
    receipt_url: str | None | _Unset = UNSET


class UpdateExpenseUseCase:
    def __init__(
        self,
        expense_repo: ExpenseRepository,
        project_repo: ProjectRepository,
        date_provider: Callable[[], date] = date.today,
    ) -> None:
        self._expense_repo = expense_repo
        self._project_repo = project_repo
        self._date_provider = date_provider

    def execute(self, dto: UpdateExpenseDTO) -> Expense:
        expense = self._expense_repo.get_by_id(dto.expense_id, for_update=True)
        if expense is None:
            raise ExpenseNotFoundError(dto.expense_id)

        if dto.amount is not None:
            validate_expense_amount(dto.amount)
        if dto.date is not None:
            validate_expense_date(dto.date, self._date_provider())
        if dto.title is not None:
            validate_expense_title(dto.title)
        project_id = (
            expense.project_id if isinstance(dto.project_id, _Unset) else dto.project_id
        )
        if project_id != expense.project_id:
            validate_expense_project(self._project_repo, project_id)

        receipt_url = (
            expense.receipt_url
            if isinstance(dto.receipt_url, _Unset)
            else dto.receipt_url
        )
        has_receipt = (
            expense.has_receipt if dto.has_receipt is None else dto.has_receipt
        )
        updated = replace(
            expense,
            amount=expense.amount if dto.amount is None else dto.amount,
            date=expense.date if dto.date is None else dto.date,
            category=expense.category if dto.category is None else dto.category,
            title=expense.title if dto.title is None else dto.title,
            detail=expense.detail if isinstance(dto.detail, _Unset) else dto.detail,
            project_id=project_id,
            receipt_url=receipt_url,
            has_receipt=receipt_url is not None or has_receipt,
        )
        if updated == expense:
            return expense
        return self._expense_repo.update(replace(updated, updated_at=datetime.now(UTC)))
