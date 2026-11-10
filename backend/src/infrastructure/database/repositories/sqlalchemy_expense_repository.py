"""SQLAlchemy 2.0 implementation of ExpenseRepository.

Receives a synchronous ``Session`` at construction time so the caller
(e.g. a FastAPI dependency) controls the transaction lifecycle.
All public methods return pure-Python domain dataclasses — no ORM
objects ever leak beyond this module.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.entities.expense import Expense
from src.domain.exceptions import ResourceIdentityConflictError
from src.domain.repositories.expense_repository import ExpenseRepository
from src.infrastructure.database.mappers import (
    domain_to_expense_orm,
    expense_to_domain,
)
from src.infrastructure.database.models import ExpenseORM


class SQLAlchemyExpenseRepository(ExpenseRepository):
    """Concrete PostgreSQL-backed repository for :class:`Expense` entities.

    Args:
        session: An active SQLAlchemy :class:`~sqlalchemy.orm.Session`.
                 The caller is responsible for committing or rolling back
                 the transaction; this class never commits on its own.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def save(self, expense: Expense) -> Expense:
        """Persist a new expense row and return the saved domain entity.

        Args:
            expense: The :class:`Expense` domain dataclass to persist.

        Returns:
            The same entity as stored (identity-mapped through the ORM).
        """
        orm = domain_to_expense_orm(expense)
        self._session.add(orm)
        try:
            self._session.flush()
        except IntegrityError as exc:
            if (
                isinstance(exc.orig, UniqueViolation)
                and exc.orig.diag.constraint_name == "expenses_pkey"
            ):
                raise ResourceIdentityConflictError(
                    "The requested expense identifier is already in use."
                ) from exc
            raise
        return expense_to_domain(orm)

    def delete(self, expense_id: UUID) -> bool:
        """Delete an expense by its UUID.

        Args:
            expense_id: UUIDv4 of the expense to remove.

        Returns:
            ``True`` if a row was found and deleted; ``False`` otherwise.
        """
        orm = self._session.get(ExpenseORM, expense_id)
        if orm is None:
            return False
        self._session.delete(orm)
        self._session.flush()
        return True

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_by_id(self, expense_id: UUID) -> Expense | None:
        """Fetch a single expense by primary key.

        Args:
            expense_id: UUIDv4 of the expense.

        Returns:
            The :class:`Expense` domain entity, or ``None`` if not found.
        """
        orm = self._session.get(ExpenseORM, expense_id)
        if orm is None:
            return None
        return expense_to_domain(orm)

    def list_all(self) -> list[Expense]:
        """Return every expense in the system (direct + operational).

        Returns:
            List of all :class:`Expense` entities (may be empty).
        """
        stmt = select(ExpenseORM)
        rows = self._session.scalars(stmt).all()
        return [expense_to_domain(row) for row in rows]

    def get_by_project(
        self,
        project_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Expense]:
        """Return all expenses charged to a specific project.

        An optional inclusive date-range filter can be applied on the
        ``date`` column (the day the expense was incurred).

        Args:
            project_id: UUIDv4 of the target project.
            start_date: Lower-bound filter (inclusive). ``None`` = no limit.
            end_date: Upper-bound filter (inclusive). ``None`` = no limit.

        Returns:
            List of matching :class:`Expense` entities (may be empty).
        """
        stmt = select(ExpenseORM).where(ExpenseORM.project_id == project_id)
        if start_date is not None:
            stmt = stmt.where(ExpenseORM.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(ExpenseORM.date <= end_date)
        rows = self._session.scalars(stmt).all()
        return [expense_to_domain(row) for row in rows]

    def get_operational_expenses(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Expense]:
        """Return all OPEX expenses (those where ``project_id`` is ``None``).

        An optional inclusive date-range filter can be applied on the
        ``date`` column.

        Args:
            start_date: Lower-bound filter (inclusive). ``None`` = no limit.
            end_date: Upper-bound filter (inclusive). ``None`` = no limit.

        Returns:
            List of matching :class:`Expense` entities (may be empty).
        """
        stmt = select(ExpenseORM).where(ExpenseORM.project_id.is_(None))
        if start_date is not None:
            stmt = stmt.where(ExpenseORM.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(ExpenseORM.date <= end_date)
        rows = self._session.scalars(stmt).all()
        return [expense_to_domain(row) for row in rows]
