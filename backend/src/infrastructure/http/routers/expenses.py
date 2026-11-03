"""HTTP router for expense management endpoints."""

from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from src.infrastructure.http.dependencies import (
    get_operational_expenses_uc,
    get_project_expenses_uc,
    get_register_expense_uc,
)
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

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])


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
    summary="Register a new expense",
)
def register_expense(
    request: RegisterExpenseRequest,
    use_case: Annotated[RegisterDailyExpenseUseCase, Depends(get_register_expense_uc)],
) -> ExpenseResponse:
    """Register a daily expense, either project-tied or operational (OPEX)."""
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
    summary="List expenses for a specific project",
)
def list_project_expenses(
    project_id: UUID,
    use_case: Annotated[GetProjectExpensesUseCase, Depends(get_project_expenses_uc)],
    start_date: Annotated[
        date | None,
        Query(description="Filter expenses on or after this date"),
    ] = None,
    end_date: Annotated[
        date | None,
        Query(description="Filter expenses on or before this date"),
    ] = None,
) -> list[ExpenseResponse]:
    """Retrieve all expenses charged to a specific project."""
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
    summary="List operational (OPEX) expenses",
)
def list_operational_expenses(
    use_case: Annotated[
        GetOperationalExpensesUseCase, Depends(get_operational_expenses_uc)
    ],
    start_date: Annotated[
        date | None,
        Query(description="Filter expenses on or after this date"),
    ] = None,
    end_date: Annotated[
        date | None,
        Query(description="Filter expenses on or before this date"),
    ] = None,
) -> list[ExpenseResponse]:
    """Retrieve all operational (OPEX) expenses not tied to any project."""
    dto = GetOperationalExpensesDTO(
        start_date=start_date,
        end_date=end_date,
    )
    expenses = use_case.execute(dto)
    return [ExpenseResponse.model_validate(e) for e in expenses]
