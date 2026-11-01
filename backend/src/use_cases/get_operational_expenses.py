"""Use case: Get all operational (OPEX) expenses.

This module contains:
- ``GetOperationalExpensesDTO``    – immutable input contract from the interface layer.
- ``GetOperationalExpensesUseCase`` – delegates the OPEX query to the repository.

Design constraints:
- Pure Python 3.11+; zero dependencies on FastAPI, SQLAlchemy, or Pydantic.
- Strict typing: no ``Any``.
- No project validation is required: OPEX expenses are by definition not tied
  to any project (``Expense.project_id is None``).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.domain.entities.expense import Expense
from src.domain.repositories.expense_repository import ExpenseRepository


@dataclass(frozen=True)
class GetOperationalExpensesDTO:
    """Immutable input contract for ``GetOperationalExpensesUseCase``.

    Attributes:
        start_date: Lower bound filter (inclusive). None means no lower limit.
        end_date: Upper bound filter (inclusive). None means no upper limit.
    """

    start_date: date | None = None
    end_date: date | None = None


class GetOperationalExpensesUseCase:
    """Return all OPEX expenses (those not tied to any project).

    No business-rule validation is required beyond what the repository
    enforces: all returned expenses will have ``project_id is None``.

    Args:
        expense_repo: Persistence adapter for ``Expense`` entities.
    """

    def __init__(self, expense_repo: ExpenseRepository) -> None:
        self._expense_repo = expense_repo

    def execute(self, dto: GetOperationalExpensesDTO) -> list[Expense]:
        """Return all OPEX expenses, optionally filtered by date range.

        Args:
            dto: Immutable input data from the interface layer.

        Returns:
            List of ``Expense`` entities with ``project_id is None``,
            optionally filtered by the date range in the DTO (may be empty).
        """
        return self._expense_repo.get_operational_expenses(
            dto.start_date,
            dto.end_date,
        )
