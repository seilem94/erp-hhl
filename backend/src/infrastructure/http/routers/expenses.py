"""Enrutador HTTP para el registro y consulta de gastos."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from src.infrastructure.http.dependencies import (
    get_operational_expenses_uc,
    get_project_expenses_uc,
    get_register_expense_uc,
)
from src.infrastructure.http.schemas.error import ErrorResponse
from src.infrastructure.http.schemas.expense import (
    ExpenseResponse,
    RegisterExpenseRequest,
)
from src.use_cases.get_operational_expenses import (
    GetOperationalExpensesDTO,
    GetOperationalExpensesUseCase,
)
from src.use_cases.get_project_expenses import (
    GetProjectExpensesDTO,
    GetProjectExpensesUseCase,
)
from src.use_cases.register_daily_expense import (
    RegisterDailyExpenseDTO,
    RegisterDailyExpenseUseCase,
)

router = APIRouter(prefix="/api/v1/expenses", tags=["Gastos"])


@router.post(
    "",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo gasto",
    description=(
        "Registra un gasto incurrido en terreno o administrativo. "
        "Si se incluye 'project_id', el gasto se imputa a la obra (CapEx). "
        "Si se omite 'project_id', se clasifica como gasto operativo (OPEX). "
        "Valida monto mayor a 0, fecha no futura y obra no cancelada."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Gasto registrado y persistido exitosamente.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Error general o inconsistencia en la solicitud.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "La obra o proyecto especificado en 'project_id' no existe.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": (
                "Violación de regla de negocio (monto <= 0, fecha futura o "
                "proyecto cancelado) o error de validación de tipos."
            ),
        },
    },
)
def register_expense(
    request: RegisterExpenseRequest,
    use_case: Annotated[RegisterDailyExpenseUseCase, Depends(get_register_expense_uc)],
) -> ExpenseResponse:
    """Registra un gasto diario, ya sea directo a una obra o de operación general."""
    dto = RegisterDailyExpenseDTO(
        amount=request.amount,
        date=request.date,
        category=request.category,
        description=request.description,
        project_id=request.project_id,
        receipt_url=request.receipt_url,
    )
    expense = use_case.execute(dto)
    return ExpenseResponse.model_validate(expense)


@router.get(
    "/project/{project_id}",
    response_model=list[ExpenseResponse],
    summary="Consultar gastos directos de una obra",
    description=(
        "Obtiene todos los gastos directos imputados a un proyecto específico (CapEx), "
        "permitiendo opcionalmente filtrar por un rango de fechas de ejecución."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Listado de gastos de la obra obtenido exitosamente.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "La obra o proyecto indicado no fue encontrado.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Identificador UUID o fechas con formato incorrecto.",
        },
    },
)
def list_project_expenses(
    project_id: Annotated[
        UUID,
        Path(description="Identificador único universal (UUIDv4) de la obra"),
    ],
    use_case: Annotated[GetProjectExpensesUseCase, Depends(get_project_expenses_uc)],
    start_date: Annotated[
        date | None,
        Query(description="Fecha mínima de gasto (inclusive). Formato: YYYY-MM-DD"),
    ] = None,
    end_date: Annotated[
        date | None,
        Query(description="Fecha máxima de gasto (inclusive). Formato: YYYY-MM-DD"),
    ] = None,
) -> list[ExpenseResponse]:
    """Recupera los gastos imputados a la obra especificada."""
    dto = GetProjectExpensesDTO(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
    )
    expenses = use_case.execute(dto)
    return [ExpenseResponse.model_validate(e) for e in expenses]


@router.get(
    "/operational",
    response_model=list[ExpenseResponse],
    summary="Consultar gastos operacionales (OPEX)",
    description=(
        "Retorna todos los gastos operativos generales de la empresa "
        "(combustible, mantención vehicular, herramientas menores, etc.) "
        "no imputados a una obra, con filtro opcional por rango de fechas."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Listado de gastos operacionales obtenido exitosamente.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": (
                "Formato de fechas incorrecto en los parámetros de consulta."
            ),
        },
    },
)
def list_operational_expenses(
    use_case: Annotated[
        GetOperationalExpensesUseCase, Depends(get_operational_expenses_uc)
    ],
    start_date: Annotated[
        date | None,
        Query(description="Fecha mínima de gasto (inclusive). Formato: YYYY-MM-DD"),
    ] = None,
    end_date: Annotated[
        date | None,
        Query(description="Fecha máxima de gasto (inclusive). Formato: YYYY-MM-DD"),
    ] = None,
) -> list[ExpenseResponse]:
    """Recupera todos los gastos operativos no vinculados a ningún proyecto."""
    dto = GetOperationalExpensesDTO(
        start_date=start_date,
        end_date=end_date,
    )
    expenses = use_case.execute(dto)
    return [ExpenseResponse.model_validate(e) for e in expenses]
