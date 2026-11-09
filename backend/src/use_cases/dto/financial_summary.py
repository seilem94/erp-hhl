"""Summary requests share the pure filter contract, including optional IVA."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.read_models.financial_summary import FinancialSummaryFilters


@dataclass(frozen=True, kw_only=True)
class FinancialSummaryQueryDTO(FinancialSummaryFilters):
    """General summary input: dates, Currency and has_iva: bool | None."""


@dataclass(frozen=True, kw_only=True)
class ProjectSummaryQueryDTO(FinancialSummaryFilters):
    project_id: UUID
