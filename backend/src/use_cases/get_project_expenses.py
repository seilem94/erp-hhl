"""Use case: Get all expenses charged directly to a specific project.

This module contains:
- ``GetProjectExpensesDTO``    – immutable input contract from the interface layer.
- ``GetProjectExpensesUseCase`` – validates project existence and delegates query.

Design constraints:
- Pure Python 3.11+; zero dependencies on FastAPI, SQLAlchemy, or Pydantic.
- Strict typing: no ``Any``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.domain.entities.expense import Expense
from src.domain.exceptions import ProjectNotFoundError
from src.domain.repositories.expense_repository import ExpenseRepository
from src.domain.repositories.project_repository import ProjectRepository


@dataclass(frozen=True)
class GetProjectExpensesDTO:
    """Immutable input contract for ``GetProjectExpensesUseCase``.

    Attributes:
        project_id: UUID of the project whose expenses are requested.
        start_date: Lower bound filter (inclusive). None means no lower limit.
        end_date: Upper bound filter (inclusive). None means no upper limit.
    """

    project_id: UUID
    start_date: date | None = None
    end_date: date | None = None


class GetProjectExpensesUseCase:
    """Return all expenses directly charged to a given project.

    Validation pipeline:
    1. Verify the project exists; raise ``ProjectNotFoundError`` otherwise.
    2. Delegate the filtered query to ``ExpenseRepository.get_by_project``.

    Args:
        expense_repo: Persistence adapter for ``Expense`` entities.
        project_repo: Persistence adapter for ``Project`` entities.
    """

    def __init__(
        self,
        expense_repo: ExpenseRepository,
        project_repo: ProjectRepository,
    ) -> None:
        self._expense_repo = expense_repo
        self._project_repo = project_repo

    def execute(self, dto: GetProjectExpensesDTO) -> list[Expense]:
        """Validate the project and return its associated expenses.

        Args:
            dto: Immutable input data from the interface layer.

        Returns:
            List of ``Expense`` entities charged to the project, optionally
            filtered by the date range supplied in the DTO (may be empty).

        Raises:
            ProjectNotFoundError: If no project with ``dto.project_id`` exists.
        """
        if self._project_repo.get_by_id(dto.project_id) is None:
            raise ProjectNotFoundError(dto.project_id)

        return self._expense_repo.get_by_project(
            dto.project_id,
            dto.start_date,
            dto.end_date,
        )
