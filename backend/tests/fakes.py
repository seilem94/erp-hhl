"""In-memory fakes for domain repository interfaces.

These fakes are for use in unit tests only — they must never be imported
from any production code path.

Design rules:
- Each fake stores entities in a plain ``dict[UUID, Entity]``.
- All ABC methods are implemented; behaviour mirrors a real repository
  without any persistence, transactions, or framework dependencies.
- No ``Any``. Strict typing throughout.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.repositories.expense_repository import ExpenseRepository
from src.domain.repositories.project_repository import ProjectRepository


class InMemoryExpenseRepository(ExpenseRepository):
    """Volatile, dict-backed implementation of ``ExpenseRepository``."""

    def __init__(self) -> None:
        self._store: dict[UUID, Expense] = {}

    # ── Write operations ──────────────────────────────────────────────────────

    def save(self, expense: Expense) -> Expense:
        self._store[expense.id] = expense
        return expense

    def delete(self, expense_id: UUID) -> bool:
        if expense_id not in self._store:
            return False
        del self._store[expense_id]
        return True

    # ── Read operations ───────────────────────────────────────────────────────

    def get_by_id(self, expense_id: UUID) -> Expense | None:
        return self._store.get(expense_id)

    def get_by_project(
        self,
        project_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Expense]:
        results = [e for e in self._store.values() if e.project_id == project_id]
        if start_date is not None:
            results = [e for e in results if e.date >= start_date]
        if end_date is not None:
            results = [e for e in results if e.date <= end_date]
        return results

    def get_operational_expenses(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Expense]:
        results = [e for e in self._store.values() if e.project_id is None]
        if start_date is not None:
            results = [e for e in results if e.date >= start_date]
        if end_date is not None:
            results = [e for e in results if e.date <= end_date]
        return results

    def list_all(self) -> list[Expense]:
        return list(self._store.values())


class InMemoryProjectRepository(ProjectRepository):
    """Volatile, dict-backed implementation of ``ProjectRepository``."""

    def __init__(self) -> None:
        self._store: dict[UUID, Project] = {}

    # ── Write operations ──────────────────────────────────────────────────────

    def save(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    def update(self, project: Project) -> Project:
        self._store[project.id] = project
        return project

    def delete(self, project_id: UUID) -> bool:
        if project_id not in self._store:
            return False
        del self._store[project_id]
        return True

    # ── Read operations ───────────────────────────────────────────────────────

    def get_by_id(self, project_id: UUID) -> Project | None:
        return self._store.get(project_id)

    def list_all(self) -> list[Project]:
        return list(self._store.values())
