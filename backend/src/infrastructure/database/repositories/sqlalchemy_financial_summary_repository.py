"""Exact PostgreSQL aggregates: one statement and no hydrated business entities."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Numeric, and_, func, literal, or_, select, true
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import CTE

from src.domain.enums import ProjectStatus
from src.domain.exceptions import FinancialSummaryUnavailableError
from src.domain.read_models.financial_summary import (
    FinancialReadScope,
    FinancialSummary,
    FinancialSummaryFilters,
    ProjectFinancialSummary,
    ProjectStatusCounts,
)
from src.domain.repositories.financial_summary_repository import (
    FinancialSummaryRepository,
)
from src.infrastructure.database.models import ExpenseORM, ProjectORM


class SQLAlchemyFinancialSummaryRepository(FinancialSummaryRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_general(
        self, filters: FinancialSummaryFilters, scope: FinancialReadScope
    ) -> FinancialSummary:
        projects = self._visible_projects(filters, scope)
        expenses = self._visible_expenses(
            projects, filters, include_operational=scope.include_operational
        )
        totals = self._expense_totals(expenses)
        counts = (
            select(
                *(
                    func.count()
                    .filter(projects.c.status == status.value)
                    .label(status.value)
                    for status in ProjectStatus
                )
            )
            .select_from(projects)
            .cte("project_counts")
        )
        statement = select(
            totals, counts, func.statement_timestamp().label("as_of")
        ).select_from(totals.join(counts, true()))
        try:
            row = self._session.execute(statement).mappings().one()
        except SQLAlchemyError as exc:
            raise FinancialSummaryUnavailableError(
                "Financial summary is temporarily unavailable."
            ) from exc
        return FinancialSummary(
            filters=filters,
            as_of=self._cutoff(row),
            operational_expenses_total=self._decimal(row, "operational_total"),
            project_expenses_total=self._decimal(row, "project_total"),
            expenses_total=self._decimal(row, "expenses_total"),
            expense_count=self._integer(row, "expense_count"),
            projects_by_status=ProjectStatusCounts(
                planning=self._integer(row, ProjectStatus.PLANNING.value),
                in_progress=self._integer(row, ProjectStatus.IN_PROGRESS.value),
                paused=self._integer(row, ProjectStatus.PAUSED.value),
                completed=self._integer(row, ProjectStatus.COMPLETED.value),
                cancelled=self._integer(row, ProjectStatus.CANCELLED.value),
            ),
        )

    def get_project(
        self,
        project_id: UUID,
        filters: FinancialSummaryFilters,
        scope: FinancialReadScope,
    ) -> ProjectFinancialSummary | None:
        projects = self._visible_projects(filters, scope, project_id)
        expenses = self._visible_expenses(projects, filters, include_operational=False)
        totals = self._expense_totals(expenses)
        statement = select(
            projects.c.status,
            totals.c.expenses_total,
            totals.c.expense_count,
            func.statement_timestamp().label("as_of"),
        ).select_from(projects.join(totals, true()))
        try:
            row = self._session.execute(statement).mappings().one_or_none()
        except SQLAlchemyError as exc:
            raise FinancialSummaryUnavailableError(
                "Financial summary is temporarily unavailable."
            ) from exc
        if row is None:
            return None
        status: object = row["status"]
        if not isinstance(status, str):
            raise TypeError("Unexpected project status in summary projection.")
        return ProjectFinancialSummary(
            project_id=project_id,
            project_status=ProjectStatus(status),
            filters=filters,
            as_of=self._cutoff(row),
            expenses_total=self._decimal(row, "expenses_total"),
            expense_count=self._integer(row, "expense_count"),
        )

    @staticmethod
    def _visible_projects(
        filters: FinancialSummaryFilters,
        scope: FinancialReadScope,
        project_id: UUID | None = None,
    ) -> CTE:
        statement = select(ProjectORM.id, ProjectORM.status)
        if not scope.all_projects:
            statement = statement.where(ProjectORM.id.in_(scope.project_ids))
        if project_id is not None:
            statement = statement.where(ProjectORM.id == project_id)
        if filters.has_iva is not None:
            # IS FALSE must not include NULL; no COALESCE/backfill classification.
            statement = statement.where(ProjectORM.has_iva.is_(filters.has_iva))
        return statement.cte("visible_projects")

    @staticmethod
    def _visible_expenses(
        projects: CTE,
        filters: FinancialSummaryFilters,
        *,
        include_operational: bool,
    ) -> CTE:
        statement = select(ExpenseORM.project_id, ExpenseORM.amount).where(
            or_(
                ExpenseORM.project_id.in_(select(projects.c.id)),
                and_(
                    ExpenseORM.project_id.is_(None),
                    literal(include_operational and filters.has_iva is None),
                ),
            )
        )
        if filters.start_date is not None:
            statement = statement.where(ExpenseORM.date >= filters.start_date)
        if filters.end_date is not None:
            statement = statement.where(ExpenseORM.date <= filters.end_date)
        return statement.cte("visible_expenses")

    @staticmethod
    def _expense_totals(expenses: CTE) -> CTE:
        # SUM(numeric) is unbounded in PostgreSQL: never cast totals to NUMERIC(12,2).
        zero = literal(Decimal("0.00"), type_=Numeric())
        return (
            select(
                func.coalesce(
                    func.sum(expenses.c.amount).filter(expenses.c.project_id.is_(None)),
                    zero,
                ).label("operational_total"),
                func.coalesce(
                    func.sum(expenses.c.amount).filter(
                        expenses.c.project_id.is_not(None)
                    ),
                    zero,
                ).label("project_total"),
                func.coalesce(func.sum(expenses.c.amount), zero).label(
                    "expenses_total"
                ),
                func.count().label("expense_count"),
            )
            .select_from(expenses)
            .cte("expense_totals")
        )

    @staticmethod
    def _decimal(row: RowMapping, name: str) -> Decimal:
        value: object = row[name]
        if not isinstance(value, Decimal):
            raise TypeError("Financial aggregates must be exact Decimal values.")
        return value

    @staticmethod
    def _integer(row: RowMapping, name: str) -> int:
        value: object = row[name]
        if not isinstance(value, int):
            raise TypeError("Unexpected financial counter type.")
        return value

    @staticmethod
    def _cutoff(row: RowMapping) -> datetime:
        value: object = row["as_of"]
        if not isinstance(value, datetime) or value.utcoffset() is None:
            raise TypeError("Summary cutoff must be a timezone-aware datetime.")
        return value.astimezone(UTC)
