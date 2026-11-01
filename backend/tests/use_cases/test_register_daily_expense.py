"""Unit tests for RegisterDailyExpenseUseCase.

Test philosophy:
- Pure unit tests: zero I/O, zero network, zero database.
- Date is always fixed via the injected ``date_provider`` — no real clock.
- Each test exercises exactly one behaviour (one path through execute()).
- Fakes replace real repositories; no mocking frameworks needed.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.project import Project
from src.domain.enums import ExpenseCategory, ProjectStatus
from src.domain.exceptions import (
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
    ProjectCancelledError,
    ProjectNotFoundError,
)
from src.use_cases.register_daily_expense import (
    RegisterDailyExpenseDTO,
    RegisterDailyExpenseUseCase,
)
from tests.fakes import InMemoryExpenseRepository, InMemoryProjectRepository

# ── Shared fixtures ───────────────────────────────────────────────────────────

TODAY = date(2026, 11, 1)


def _fixed_today() -> date:
    """Deterministic date provider — always returns TODAY."""
    return TODAY


def _make_use_case(
    expense_repo: InMemoryExpenseRepository | None = None,
    project_repo: InMemoryProjectRepository | None = None,
) -> RegisterDailyExpenseUseCase:
    return RegisterDailyExpenseUseCase(
        expense_repo=expense_repo or InMemoryExpenseRepository(),
        project_repo=project_repo or InMemoryProjectRepository(),
        date_provider=_fixed_today,
    )


def _make_active_project(
    project_repo: InMemoryProjectRepository,
    status: ProjectStatus = ProjectStatus.IN_PROGRESS,
) -> Project:
    """Persist a project with the given status and return it."""
    project = Project(
        id=uuid4(),
        name="Instalación Tablero General",
        client="Cliente Ejemplo SpA",
        status=status,
        start_date=date(2026, 10, 1),
        created_at=__import__("datetime").datetime(2026, 10, 1, 12, 0, 0),
        updated_at=__import__("datetime").datetime(2026, 10, 1, 12, 0, 0),
    )
    project_repo.save(project)
    return project


# ── Happy-path tests ──────────────────────────────────────────────────────────


def test_registro_exitoso_gasto_proyecto_activo() -> None:
    """Un gasto válido asociado a un proyecto activo se persiste correctamente."""
    expense_repo = InMemoryExpenseRepository()
    project_repo = InMemoryProjectRepository()
    project = _make_active_project(project_repo)

    dto = RegisterDailyExpenseDTO(
        amount=Decimal("15000"),
        date=TODAY,
        category=ExpenseCategory.MATERIALS,
        description="Compra cable 2.5 mm²",
        project_id=project.id,
    )
    use_case = _make_use_case(expense_repo, project_repo)
    result = use_case.execute(dto)

    assert result.project_id == project.id
    assert result.amount == Decimal("15000")
    assert result.category == ExpenseCategory.MATERIALS
    assert result.description == "Compra cable 2.5 mm²"
    assert result.has_receipt is False
    assert result.receipt_url is None
    # El gasto debe haber sido persistido en el repositorio
    assert expense_repo.get_by_id(result.id) is not None


def test_registro_exitoso_gasto_operacional_sin_proyecto() -> None:
    """Un gasto OPEX (project_id=None) se registra sin consultar ProjectRepository."""
    expense_repo = InMemoryExpenseRepository()

    dto = RegisterDailyExpenseDTO(
        amount=Decimal("8500"),
        date=TODAY,
        category=ExpenseCategory.MAINTENANCE,
        description="Cambio de aceite camioneta",
        project_id=None,
    )
    use_case = _make_use_case(expense_repo)
    result = use_case.execute(dto)

    assert result.project_id is None
    assert result.is_project_expense is False
    assert expense_repo.get_by_id(result.id) is not None


def test_normalizacion_has_receipt_con_receipt_url() -> None:
    """Si se provee receipt_url, has_receipt debe ser True aunque el DTO diga False."""
    expense_repo = InMemoryExpenseRepository()

    dto = RegisterDailyExpenseDTO(
        amount=Decimal("3200"),
        date=TODAY,
        category=ExpenseCategory.FOOD,
        description="Colación cuadrilla terreno",
        has_receipt=False,  # Explícitamente False
        receipt_url="https://storage.example.com/boletas/factura-001.jpg",
    )
    use_case = _make_use_case(expense_repo)
    result = use_case.execute(dto)

    assert result.has_receipt is True
    assert result.receipt_url == "https://storage.example.com/boletas/factura-001.jpg"


# ── Error-path tests ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "amount",
    [Decimal("0"), Decimal("-1"), Decimal("-0.01")],
    ids=["cero", "negativo_entero", "negativo_decimal"],
)
def test_error_monto_invalido(amount: Decimal) -> None:
    """Se lanza InvalidExpenseAmountError para montos <= 0."""
    dto = RegisterDailyExpenseDTO(
        amount=amount,
        date=TODAY,
        category=ExpenseCategory.TRANSPORT,
        description="Peaje autopista",
    )
    use_case = _make_use_case()

    with pytest.raises(InvalidExpenseAmountError) as exc_info:
        use_case.execute(dto)

    assert exc_info.value.amount == amount


def test_error_fecha_futura() -> None:
    """Se lanza InvalidExpenseDateError si la fecha del gasto es posterior a hoy."""
    future_date = date(2026, 11, 2)  # un día después de TODAY
    dto = RegisterDailyExpenseDTO(
        amount=Decimal("5000"),
        date=future_date,
        category=ExpenseCategory.TOOLS,
        description="Compra brocas",
    )
    use_case = _make_use_case()

    with pytest.raises(InvalidExpenseDateError) as exc_info:
        use_case.execute(dto)

    assert exc_info.value.expense_date == future_date
    assert exc_info.value.today == TODAY


def test_error_proyecto_no_encontrado() -> None:
    """Se lanza ProjectNotFoundError si el project_id no existe en el repositorio."""
    nonexistent_id = uuid4()
    dto = RegisterDailyExpenseDTO(
        amount=Decimal("12000"),
        date=TODAY,
        category=ExpenseCategory.MATERIALS,
        description="Automáticos térmicos",
        project_id=nonexistent_id,
    )
    use_case = _make_use_case()  # project_repo vacío

    with pytest.raises(ProjectNotFoundError) as exc_info:
        use_case.execute(dto)

    assert exc_info.value.project_id == nonexistent_id


def test_error_proyecto_cancelado() -> None:
    """Se lanza ProjectCancelledError si el proyecto referenciado está CANCELLED."""
    expense_repo = InMemoryExpenseRepository()
    project_repo = InMemoryProjectRepository()
    cancelled_project = _make_active_project(
        project_repo, status=ProjectStatus.CANCELLED
    )

    dto = RegisterDailyExpenseDTO(
        amount=Decimal("7000"),
        date=TODAY,
        category=ExpenseCategory.SERVICES,
        description="Subcontrato andamios",
        project_id=cancelled_project.id,
    )
    use_case = _make_use_case(expense_repo, project_repo)

    with pytest.raises(ProjectCancelledError) as exc_info:
        use_case.execute(dto)

    assert exc_info.value.project_id == cancelled_project.id
    assert exc_info.value.current_status == ProjectStatus.CANCELLED
