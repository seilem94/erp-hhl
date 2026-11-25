"""Immutable operation results; JSONB serialization belongs to infrastructure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import TypeAlias
from uuid import UUID

from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.enums import Currency, ExpenseCategory, ProjectStatus

OPERATION_RESULT_SCHEMA_VERSION = 2


@dataclass(frozen=True, kw_only=True)
class ProjectSnapshot:
    id: UUID
    name: str
    client: str
    status: ProjectStatus
    start_date: date
    created_at: datetime
    updated_at: datetime
    currency: Currency
    description: str | None = None
    end_date: date | None = None
    budget: int | None = None

    @classmethod
    def from_project(cls, project: Project) -> ProjectSnapshot:
        return cls(
            id=project.id,
            name=project.name,
            client=project.client,
            status=project.status,
            start_date=project.start_date,
            created_at=project.created_at,
            updated_at=project.updated_at,
            currency=project.currency,
            description=project.description,
            end_date=project.end_date,
            budget=project.budget,
        )


@dataclass(frozen=True, kw_only=True)
class ExpenseSnapshot:
    id: UUID
    amount: int
    date: date
    category: ExpenseCategory
    title: str
    has_receipt: bool
    created_at: datetime
    updated_at: datetime
    currency: Currency
    project_id: UUID | None = None
    receipt_url: str | None = None
    detail: str | None = None

    @classmethod
    def from_expense(cls, expense: Expense) -> ExpenseSnapshot:
        return cls(
            id=expense.id,
            amount=expense.amount,
            date=expense.date,
            category=expense.category,
            title=expense.title,
            detail=expense.detail,
            has_receipt=expense.has_receipt,
            created_at=expense.created_at,
            updated_at=expense.updated_at,
            currency=expense.currency,
            project_id=expense.project_id,
            receipt_url=expense.receipt_url,
        )


OperationResult: TypeAlias = ProjectSnapshot | ExpenseSnapshot
