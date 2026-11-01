"""Abstract interface for the Expense repository.

Use-cases depend on this ABC; infrastructure provides the concrete
implementation (SQLAlchemy, in-memory, etc.).
Domain layer has zero knowledge of how or where data is stored.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.domain.entities.expense import Expense


class ExpenseRepository(ABC):
    """Contract for all Expense persistence adapters."""

    @abstractmethod
    def save(self, expense: Expense) -> Expense:
        """Persist a new expense (direct or operational) and return the entity.

        Args:
            expense: The Expense entity to create.

        Returns:
            The persisted Expense entity (may include DB-generated fields).
        """

    @abstractmethod
    def get_by_id(self, expense_id: UUID) -> Expense | None:
        """Fetch a single expense by its unique identifier.

        Args:
            expense_id: UUIDv4 of the expense.

        Returns:
            The Expense entity, or None if not found.
        """

    @abstractmethod
    def get_by_project(
        self,
        project_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Expense]:
        """Return all expenses charged directly to a specific project.

        Only returns records where ``expense.project_id == project_id``.
        An optional date range filter (inclusive on both ends) can be applied.

        Args:
            project_id: UUIDv4 of the target project.
            start_date: Lower bound (inclusive). None means no lower limit.
            end_date: Upper bound (inclusive). None means no upper limit.

        Returns:
            List of matching Expense entities (may be empty).
        """

    @abstractmethod
    def get_operational_expenses(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Expense]:
        """Return all OPEX expenses (those where project_id is None).

        These are general operational costs not tied to any particular obra
        (e.g. vehicle maintenance, workshop supplies, instrument calibration).
        An optional date range filter (inclusive on both ends) can be applied.

        Args:
            start_date: Lower bound (inclusive). None means no lower limit.
            end_date: Upper bound (inclusive). None means no upper limit.

        Returns:
            List of matching Expense entities (may be empty).
        """

    @abstractmethod
    def list_all(self) -> list[Expense]:
        """Return every expense in the system (direct + operational).

        Returns:
            List of all Expense entities (may be empty).
        """

    @abstractmethod
    def delete(self, expense_id: UUID) -> bool:
        """Remove an expense by its identifier.

        Args:
            expense_id: UUIDv4 of the expense to remove.

        Returns:
            True if the expense existed and was deleted; False otherwise.
        """
