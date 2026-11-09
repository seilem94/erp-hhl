"""Financial responses preserve exact amounts as decimal strings."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, PlainSerializer

from src.domain.enums import Currency, ProjectStatus
from src.domain.read_models.financial_summary import (
    FinancialSummary,
    ProjectFinancialSummary,
)


def _serialize_money(value: Decimal) -> str:
    return format(value, ".2f")


Money = Annotated[
    Decimal, PlainSerializer(_serialize_money, return_type=str, when_used="json")
]


class SummaryResponseBase(BaseModel):
    currency: Currency
    start_date: date | None
    end_date: date | None
    has_iva: bool | None
    as_of: datetime


class ProjectStatusCountsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    planning: int
    in_progress: int
    paused: int
    completed: int
    cancelled: int


class FinancialSummaryResponse(SummaryResponseBase):
    operational_expenses_total: Money
    project_expenses_total: Money
    expenses_total: Money
    expense_count: int
    project_count: int
    projects_by_status: ProjectStatusCountsResponse

    @classmethod
    def from_summary(cls, summary: FinancialSummary) -> FinancialSummaryResponse:
        return cls(
            currency=summary.currency,
            start_date=summary.filters.start_date,
            end_date=summary.filters.end_date,
            has_iva=summary.filters.has_iva,
            as_of=summary.as_of,
            operational_expenses_total=summary.operational_expenses_total,
            project_expenses_total=summary.project_expenses_total,
            expenses_total=summary.expenses_total,
            expense_count=summary.expense_count,
            project_count=summary.project_count,
            projects_by_status=ProjectStatusCountsResponse.model_validate(
                summary.projects_by_status
            ),
        )


class ProjectFinancialSummaryResponse(SummaryResponseBase):
    project_id: UUID
    project_status: ProjectStatus
    expenses_total: Money
    expense_count: int

    @classmethod
    def from_summary(
        cls, summary: ProjectFinancialSummary
    ) -> ProjectFinancialSummaryResponse:
        return cls(
            currency=summary.currency,
            start_date=summary.filters.start_date,
            end_date=summary.filters.end_date,
            has_iva=summary.filters.has_iva,
            as_of=summary.as_of,
            project_id=summary.project_id,
            project_status=summary.project_status,
            expenses_total=summary.expenses_total,
            expense_count=summary.expense_count,
        )
