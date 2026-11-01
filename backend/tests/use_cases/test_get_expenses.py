"""Unit tests for GetProjectExpensesUseCase and GetOperationalExpensesUseCase.

Test philosophy:
- Pure unit tests: zero I/O, zero network, zero database.
- Expenses are seeded directly into InMemoryExpenseRepository via save().
- Each test exercises exactly one behaviour (one path through execute()).
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.enums import ExpenseCategory, ProjectStatus
from src.domain.exceptions import ProjectNotFoundError
from src.use_cases.get_operational_expenses import (
    GetOperationalExpensesDTO,
    GetOperationalExpensesUseCase,
)
from src.use_cases.get_project_expenses import (
    GetProjectExpensesDTO,
    GetProjectExpensesUseCase,
)
from tests.fakes import InMemoryExpenseRepository, InMemoryProjectRepository

# ── Shared helpers ────────────────────────────────────────────────────────────

_NOW = datetime(2026, 11, 1, 12, 0, 0, tzinfo=UTC)
_TODAY = date(2026, 11, 1)


def _make_expense(
    *,
    expense_date: date = _TODAY,
    category: ExpenseCategory = ExpenseCategory.MATERIALS,
    project_id: None | type = None,  # sentinel: pass uuid directly when needed
    amount: Decimal = Decimal("1000"),
) -> Expense:
    """Build an Expense instance with sensible defaults for testing."""
    return Expense(
        id=uuid4(),
        amount=amount,
        date=expense_date,
        category=category,
        description="Gasto de prueba",
        has_receipt=False,
        created_at=_NOW,
        updated_at=_NOW,
        project_id=None if project_id is None else project_id,  # type: ignore[arg-type]
    )


def _make_expense_for_project(project_id: object, **kwargs: object) -> Expense:
    """Build an Expense tied to a specific project UUID."""
    from uuid import UUID

    assert isinstance(project_id, UUID)
    return Expense(
        id=uuid4(),
        amount=kwargs.get("amount", Decimal("1000")),  # type: ignore[arg-type]
        date=kwargs.get("expense_date", _TODAY),  # type: ignore[arg-type]
        category=kwargs.get("category", ExpenseCategory.MATERIALS),  # type: ignore[arg-type]
        description="Gasto de prueba en obra",
        has_receipt=False,
        created_at=_NOW,
        updated_at=_NOW,
        project_id=project_id,
    )


def _make_opex_expense(**kwargs: object) -> Expense:
    """Build an OPEX Expense (project_id is None)."""
    return Expense(
        id=uuid4(),
        amount=kwargs.get("amount", Decimal("500")),  # type: ignore[arg-type]
        date=kwargs.get("expense_date", _TODAY),  # type: ignore[arg-type]
        category=kwargs.get("category", ExpenseCategory.MAINTENANCE),  # type: ignore[arg-type]
        description="Gasto operacional de prueba",
        has_receipt=False,
        created_at=_NOW,
        updated_at=_NOW,
        project_id=None,
    )


def _make_project(
    project_repo: InMemoryProjectRepository,
    status: ProjectStatus = ProjectStatus.IN_PROGRESS,
) -> Project:
    """Persist and return a project with the given status."""
    project = Project(
        id=uuid4(),
        name="Obra de prueba",
        client="Cliente Ejemplo SpA",
        status=status,
        start_date=date(2026, 10, 1),
        created_at=_NOW,
        updated_at=_NOW,
    )
    project_repo.save(project)
    return project


# ── GetProjectExpensesUseCase tests ───────────────────────────────────────────


def test_get_project_expenses_lanza_error_si_proyecto_no_existe() -> None:
    """Se lanza ProjectNotFoundError cuando el project_id no existe en el repo."""
    nonexistent_id = uuid4()
    use_case = GetProjectExpensesUseCase(
        expense_repo=InMemoryExpenseRepository(),
        project_repo=InMemoryProjectRepository(),
    )
    dto = GetProjectExpensesDTO(project_id=nonexistent_id)

    with pytest.raises(ProjectNotFoundError) as exc_info:
        use_case.execute(dto)

    assert exc_info.value.project_id == nonexistent_id


def test_get_project_expenses_retorna_gastos_del_proyecto() -> None:
    """Retorna exactamente los gastos asociados al proyecto, sin incluir OPEX."""
    expense_repo = InMemoryExpenseRepository()
    project_repo = InMemoryProjectRepository()
    project = _make_project(project_repo)

    # Gasto propio del proyecto
    expense_a = _make_expense_for_project(project.id)
    expense_b = _make_expense_for_project(project.id)
    # Gasto OPEX que NO debe aparecer
    opex = _make_opex_expense()

    expense_repo.save(expense_a)
    expense_repo.save(expense_b)
    expense_repo.save(opex)

    use_case = GetProjectExpensesUseCase(expense_repo, project_repo)
    result = use_case.execute(GetProjectExpensesDTO(project_id=project.id))

    result_ids = {e.id for e in result}
    assert expense_a.id in result_ids
    assert expense_b.id in result_ids
    assert opex.id not in result_ids
    assert len(result) == 2


def test_get_project_expenses_retorna_lista_vacia_sin_gastos() -> None:
    """Retorna lista vacía cuando el proyecto existe pero no tiene gastos."""
    expense_repo = InMemoryExpenseRepository()
    project_repo = InMemoryProjectRepository()
    project = _make_project(project_repo)

    use_case = GetProjectExpensesUseCase(expense_repo, project_repo)
    result = use_case.execute(GetProjectExpensesDTO(project_id=project.id))

    assert result == []


# ── GetOperationalExpensesUseCase tests ───────────────────────────────────────


def test_get_operational_expenses_retorna_solo_opex() -> None:
    """Retorna únicamente gastos con project_id is None, excluyendo costos de obra."""
    expense_repo = InMemoryExpenseRepository()
    project_repo = InMemoryProjectRepository()
    project = _make_project(project_repo)

    opex_a = _make_opex_expense()
    opex_b = _make_opex_expense()
    project_expense = _make_expense_for_project(project.id)

    expense_repo.save(opex_a)
    expense_repo.save(opex_b)
    expense_repo.save(project_expense)

    use_case = GetOperationalExpensesUseCase(expense_repo)
    result = use_case.execute(GetOperationalExpensesDTO())

    result_ids = {e.id for e in result}
    assert opex_a.id in result_ids
    assert opex_b.id in result_ids
    assert project_expense.id not in result_ids
    assert len(result) == 2


def test_get_operational_expenses_retorna_lista_vacia_sin_opex() -> None:
    """Retorna lista vacía cuando no hay gastos operacionales registrados."""
    expense_repo = InMemoryExpenseRepository()
    project_repo = InMemoryProjectRepository()
    project = _make_project(project_repo)

    # Solo existe un gasto de proyecto, no OPEX
    expense_repo.save(_make_expense_for_project(project.id))

    use_case = GetOperationalExpensesUseCase(expense_repo)
    result = use_case.execute(GetOperationalExpensesDTO())

    assert result == []
