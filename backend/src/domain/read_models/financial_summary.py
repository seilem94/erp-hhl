"""Financial aggregation contracts; adapters must sum in a single SQL statement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from src.domain.enums import Currency, ProjectStatus
from src.domain.exceptions import InvalidSummaryDateRangeError


@dataclass(frozen=True, kw_only=True)
class FinancialSummaryFilters:
    """Filter expense dates inclusively and explicit project tax classification.

    None includes all authorized history, including OPEX and unclassified works.
    True/False match only explicitly classified works, never infer False for OPEX
    or historical unknowns. Tax filters also select project counters; date filters
    do not filter those counters. Future adapters must apply this before SUM.
    """

    start_date: date | None = None
    end_date: date | None = None
    currency: Currency = Currency.CLP
    has_iva: bool | None = None

    def __post_init__(self) -> None:
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise InvalidSummaryDateRangeError(self.start_date, self.end_date)


@dataclass(frozen=True, kw_only=True)
class FinancialReadScope:
    """Server-resolved scope; an empty default grants access to no records."""

    all_projects: bool = False
    project_ids: frozenset[UUID] = frozenset()
    include_operational: bool = False


@dataclass(frozen=True, kw_only=True)
class ProjectStatusCounts:
    planning: int = 0
    in_progress: int = 0
    paused: int = 0
    completed: int = 0
    cancelled: int = 0

    @property
    def total(self) -> int:
        return (
            self.planning
            + self.in_progress
            + self.paused
            + self.completed
            + self.cancelled
        )


@dataclass(frozen=True, kw_only=True)
class FinancialSummary:
    """Exact SQL totals for one current snapshot, not a historical time query."""

    filters: FinancialSummaryFilters
    as_of: datetime
    operational_expenses_total: Decimal
    project_expenses_total: Decimal
    expenses_total: Decimal
    expense_count: int
    projects_by_status: ProjectStatusCounts

    @property
    def currency(self) -> Currency:
        return self.filters.currency

    @property
    def project_count(self) -> int:
        return self.projects_by_status.total


@dataclass(frozen=True, kw_only=True)
class ProjectFinancialSummary:
    project_id: UUID
    project_status: ProjectStatus
    filters: FinancialSummaryFilters
    as_of: datetime
    expenses_total: Decimal
    expense_count: int

    @property
    def currency(self) -> Currency:
        return self.filters.currency
