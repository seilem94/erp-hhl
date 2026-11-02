"""SQLAlchemy 2.0 ORM models for the persistence layer.

These models are infrastructure-only. They have no knowledge of domain
logic and must never be imported by the domain or use-case layers.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


class ProjectORM(Base):
    """Persistence model for the 'projects' table.

    Maps 1-to-1 with the :class:`~src.domain.entities.project.Project`
    domain dataclass via the mapper layer.
    """

    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    client: Mapped[str] = mapped_column(String(255), nullable=False)
    # ProjectStatus values are stored as plain strings (StrEnum → str).
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # NUMERIC(12, 2) gives 10 integer digits + 2 decimal places, enough for
    # local-currency budgets up to 9 999 999 999.99.
    budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)


class ExpenseORM(Base):
    """Persistence model for the 'expenses' table.

    Maps 1-to-1 with the :class:`~src.domain.entities.expense.Expense`
    domain dataclass via the mapper layer.

    ``project_id`` is nullable to support OPEX expenses that are not
    tied to any specific project.
    """

    __tablename__ = "expenses"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    # NUMERIC(12, 2): same reasoning as ProjectORM.budget.
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    # ExpenseCategory values stored as plain strings (StrEnum → str).
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    has_receipt: Mapped[bool] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # nullable=True → OPEX expense (no project assigned).
    project_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    receipt_url: Mapped[str | None] = mapped_column(Text, nullable=True)
