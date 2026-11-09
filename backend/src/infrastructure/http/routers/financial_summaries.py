"""Summary transport only; authorization and aggregation live behind use cases."""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.domain.enums import Currency
from src.infrastructure.http.dependencies import (
    get_financial_summary_uc,
    get_project_financial_summary_uc,
)
from src.infrastructure.http.schemas.error import ErrorResponse
from src.infrastructure.http.schemas.financial_summary import (
    FinancialSummaryResponse,
    ProjectFinancialSummaryResponse,
)
from src.use_cases.dto.financial_summary import (
    FinancialSummaryQueryDTO,
    ProjectSummaryQueryDTO,
)
from src.use_cases.get_financial_summary import GetFinancialSummaryUseCase
from src.use_cases.get_project_financial_summary import (
    GetProjectFinancialSummaryUseCase,
)

router = APIRouter(prefix="/api/v1", tags=["Resúmenes financieros"])


def get_summary_query(
    start_date: Annotated[
        date | None, Query(description="Fecha mínima del gasto, inclusive.")
    ] = None,
    end_date: Annotated[
        date | None, Query(description="Fecha máxima del gasto, inclusive.")
    ] = None,
    currency: Currency = Currency.CLP,
    has_iva: Annotated[
        bool | None,
        Query(
            description=(
                "Clasificación fiscal explícita de la obra. Omitir incluye todo el "
                "historial autorizado; true/false excluyen OPEX y obras sin clasificar."
            )
        ),
    ] = None,
) -> FinancialSummaryQueryDTO:
    return FinancialSummaryQueryDTO(
        start_date=start_date, end_date=end_date, currency=currency, has_iva=has_iva
    )


SummaryQueryDep = Annotated[FinancialSummaryQueryDTO, Depends(get_summary_query)]


@router.get(
    "/dashboard/summary",
    response_model=FinancialSummaryResponse,
    summary="Consultar el resumen financiero general",
    description=(
        "Agrega gastos y cantidades de obras en un corte actual UTC. Las fechas "
        "filtran gastos; los contadores de obras siguen el alcance y filtro fiscal. "
        "Exige permiso financiero global. Los importes son cadenas decimales exactas."
    ),
    responses={
        403: {"model": ErrorResponse},
        422: {"description": "Filtros o intervalo de fechas inválidos."},
        503: {"model": ErrorResponse},
    },
)
def get_financial_summary(
    query: SummaryQueryDep,
    use_case: Annotated[GetFinancialSummaryUseCase, Depends(get_financial_summary_uc)],
) -> FinancialSummaryResponse:
    return FinancialSummaryResponse.from_summary(use_case.execute(query))


@router.get(
    "/projects/{project_id}/summary",
    response_model=ProjectFinancialSummaryResponse,
    summary="Consultar el resumen financiero de una obra",
    description=(
        "Devuelve el costo acumulado del período y cantidad de gastos, incluidas "
        "obras canceladas. Una obra visible sin gastos produce ceros. "
        "Una obra inexistente, excluida o no autorizada produce la misma respuesta 404."
    ),
    responses={
        404: {"model": ErrorResponse},
        422: {"description": "UUID, filtros o intervalo de fechas inválidos."},
        503: {"model": ErrorResponse},
    },
)
def get_project_financial_summary(
    project_id: UUID,
    query: SummaryQueryDep,
    use_case: Annotated[
        GetProjectFinancialSummaryUseCase, Depends(get_project_financial_summary_uc)
    ],
) -> ProjectFinancialSummaryResponse:
    dto = ProjectSummaryQueryDTO(
        project_id=project_id,
        start_date=query.start_date,
        end_date=query.end_date,
        currency=query.currency,
        has_iva=query.has_iva,
    )
    return ProjectFinancialSummaryResponse.from_summary(use_case.execute(dto))
