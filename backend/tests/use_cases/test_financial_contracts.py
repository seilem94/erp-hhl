"""Core filter semantics, independent of the future SQL aggregation adapter."""

from dataclasses import FrozenInstanceError
from datetime import date
from uuid import uuid4

import pytest

from src.domain.enums import Currency
from src.domain.exceptions import InvalidSummaryDateRangeError
from src.domain.read_models.financial_summary import FinancialReadScope
from src.use_cases.dto.financial_summary import (
    FinancialSummaryQueryDTO,
    ProjectSummaryQueryDTO,
)


@pytest.mark.parametrize("has_iva", [None, True, False])
def test_tax_filter_is_preserved_without_coercing_unknown(has_iva: bool | None) -> None:
    query = FinancialSummaryQueryDTO(has_iva=has_iva)
    project_query = ProjectSummaryQueryDTO(project_id=uuid4(), has_iva=has_iva)
    assert query.has_iva is has_iva
    assert project_query.has_iva is has_iva
    assert query.currency is Currency.CLP


def test_summary_rejects_inverted_period_at_the_core_boundary() -> None:
    with pytest.raises(InvalidSummaryDateRangeError):
        FinancialSummaryQueryDTO(
            start_date=date(2026, 11, 9), end_date=date(2026, 11, 8)
        )


@pytest.mark.parametrize(
    ("start", "end"),
    [(None, None), (date(2026, 11, 9), None), (None, date(2026, 11, 9))],
)
def test_open_periods_keep_their_unbounded_limits(
    start: date | None, end: date | None
) -> None:
    query = FinancialSummaryQueryDTO(start_date=start, end_date=end)
    assert query.start_date == start
    assert query.end_date == end


def test_filters_are_immutable_and_default_scope_grants_nothing() -> None:
    query = FinancialSummaryQueryDTO()
    with pytest.raises(FrozenInstanceError):
        query.has_iva = False  # type: ignore[misc]  # Exercise the frozen guard.
    scope = FinancialReadScope()
    assert not scope.all_projects
    assert not scope.project_ids
    assert not scope.include_operational
