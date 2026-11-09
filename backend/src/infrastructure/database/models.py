"""SQLAlchemy 2.0 ORM models for the persistence layer.

These models are infrastructure-only. They have no knowledge of domain
logic and must never be imported by the domain or use-case layers.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
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
    # Transitional storage only: historical classification must not default to False.
    # The final mandatory business classification is introduced with its write flow.
    has_iva: Mapped[bool | None] = mapped_column(nullable=True)


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


class OperationORM(Base):
    """Persistent operation identity; resource deletion cannot cascade into it."""

    __tablename__ = "operations"
    __table_args__ = (
        CheckConstraint(
            "state IN ('reserved', 'confirmed')", name="ck_operations_state"
        ),
        CheckConstraint(
            "(command_type = 'register_expense' AND resource_type = 'expense') OR "
            "(command_type IN ('create_project', 'update_project') "
            "AND resource_type = 'project')",
            name="ck_operations_command_resource",
        ),
        CheckConstraint(
            "fingerprint_version > 0 AND command_version > 0",
            name="ck_operations_versions",
        ),
        CheckConstraint(
            "length(request_fingerprint) = 64",
            name="ck_operations_fingerprint_length",
        ),
        CheckConstraint(
            "reserved_in_transaction > 0", name="ck_operations_owner_transaction"
        ),
        CheckConstraint(
            "command_type <> 'update_project' OR target_resource_id IS NOT NULL",
            name="ck_operations_update_target",
        ),
        CheckConstraint(
            "(state = 'reserved' AND result_resource_id IS NULL "
            "AND result_schema_version IS NULL AND result_payload IS NULL "
            "AND completed_at IS NULL) OR "
            "(state = 'confirmed' AND result_resource_id IS NOT NULL "
            "AND result_schema_version IS NOT NULL AND result_schema_version > 0 "
            "AND completed_at IS NOT NULL)",
            name="ck_operations_confirmation_shape",
        ),
        CheckConstraint(
            "state <> 'confirmed' OR target_resource_id IS NULL "
            "OR target_resource_id = result_resource_id",
            name="ck_operations_target_result",
        ),
    )

    actor_id: Mapped[UUID] = mapped_column(primary_key=True)
    operation_id: Mapped[UUID] = mapped_column(primary_key=True)
    command_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(24), nullable=False)
    target_resource_id: Mapped[UUID | None] = mapped_column(nullable=True)
    fingerprint_version: Mapped[int] = mapped_column(Integer, nullable=False)
    command_version: Mapped[int] = mapped_column(Integer, nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(16), nullable=False)
    # Infrastructure ownership only, assigned from txid_current() at reservation.
    reserved_in_transaction: Mapped[int] = mapped_column(BigInteger, nullable=False)
    result_resource_id: Mapped[UUID | None] = mapped_column(nullable=True)
    result_schema_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Native JSONB in PostgreSQL. SQLite supports only the pre-existing unit suite.
    result_payload: Mapped[dict[str, JsonValue] | None] = mapped_column(
        JSONB(none_as_null=True).with_variant(JSON(none_as_null=True), "sqlite"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
