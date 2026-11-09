"""Read port for database aggregation, including tax filters from day one."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.read_models.financial_summary import (
    FinancialReadScope,
    FinancialSummary,
    FinancialSummaryFilters,
    ProjectFinancialSummary,
)


class FinancialSummaryRepository(ABC):
    @abstractmethod
    def get_general(
        self, filters: FinancialSummaryFilters, scope: FinancialReadScope
    ) -> FinancialSummary:
        """Aggregate the authorized snapshot in one statement.

        Apply filters.has_iva in SQL before aggregation; None means no tax
        predicate. Include cancelled-project expenses and return zero for empty
        sets. Propagate failures rather than inventing partial totals.
        """

    @abstractmethod
    def get_project(
        self,
        project_id: UUID,
        filters: FinancialSummaryFilters,
        scope: FinancialReadScope,
    ) -> ProjectFinancialSummary | None:
        """Return one snapshot or None for an absent, excluded or invisible work.

        A visible matching work without expenses returns zero, not None.
        Both date and has_iva predicates must run inside the aggregate statement.
        """
