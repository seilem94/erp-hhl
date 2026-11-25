"""SQLAlchemy 2.0 implementation of ExpenseRepository.

Receives a synchronous ``Session`` at construction time so the caller
(e.g. a FastAPI dependency) controls the transaction lifecycle.
All public methods return pure-Python domain dataclasses — no ORM
objects ever leak beyond this module.
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.domain.entities.expense import Expense
from src.domain.exceptions import (
    ExpenseNotFoundError,
    ProjectNotFoundError,
    ResourceIdentityConflictError,
)
from src.domain.repositories.expense_repository import ExpenseRepository
from src.infrastructure.database.mappers import (
    domain_to_expense_orm,
    expense_to_domain,
)
from src.infrastructure.database.models import ExpenseORM
from src.infrastructure.database.repositories.sqlalchemy_audit_repository import (
    SQLAlchemyAuditRepository,
)
from src.use_cases.services.audit_service import AuditService


class SQLAlchemyExpenseRepository(ExpenseRepository):
    """Concrete PostgreSQL-backed repository for :class:`Expense` entities.

    Args:
        session: An active SQLAlchemy :class:`~sqlalchemy.orm.Session`.
                 The caller is responsible for committing or rolling back
                 the transaction; this class never commits on its own.
    """

    def __init__(self, session: Session, *, audit: AuditService | None = None) -> None:
        self._session = session
        self._audit = audit or AuditService(SQLAlchemyAuditRepository(session))

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
        self._session.refresh(orm, ["amount"])
        saved = expense_to_domain(orm)
        self._audit.record_expense(None, saved)
        return saved

    def update(self, expense: Expense) -> Expense:
        """Persist changes and audit their effective values."""
        current = self._session.get(ExpenseORM, expense.id, with_for_update=True)
        if current is None:
            raise ExpenseNotFoundError(expense.id)
        before = expense_to_domain(current)
        updated = self._session.merge(domain_to_expense_orm(expense))
        try:
            self._session.flush()
        except IntegrityError as exc:
            if (
                expense.project_id is not None
                and isinstance(exc.orig, ForeignKeyViolation)
                and exc.orig.diag.constraint_name == "expenses_project_id_fkey"
            ):
                raise ProjectNotFoundError(expense.project_id) from exc
            raise
        self._session.refresh(updated, ["amount"])
        saved = expense_to_domain(updated)
        self._audit.record_expense(before, saved)
        return saved

    def delete(self, expense_id: UUID) -> bool:
        """Delete an expense by its UUID.

        Args:
            expense_id: UUIDv4 of the expense to remove.

        Returns:
            ``True`` if a row was found and deleted; ``False`` otherwise.
        """
        orm = self._session.get(ExpenseORM, expense_id, with_for_update=True)
        if orm is None:
            return False
        self._audit.record_expense(expense_to_domain(orm), None)
        self._session.delete(orm)
        self._session.flush()
        return True

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_by_id(
        self, expense_id: UUID, *, for_update: bool = False
    ) -> Expense | None:
        """Fetch a single expense by primary key.

        Args:
            expense_id: UUIDv4 of the expense.
            for_update: Lock the row for the caller's write transaction.

        Returns:
            The :class:`Expense` domain entity, or ``None`` if not found.
        """
        orm = self._session.get(
            ExpenseORM,
            expense_id,
            with_for_update=for_update,
            populate_existing=for_update,
        )
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
