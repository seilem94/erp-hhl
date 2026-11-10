"""Recover an original result inside the server-resolved actor namespace."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status
from pydantic import UUID4

from src.infrastructure.http.dependencies import ActorDep, get_operation_result_uc
from src.infrastructure.http.schemas.error import ErrorResponse
from src.infrastructure.http.schemas.operation import (
    OperationErrorResponse,
    OperationResultResponse,
)
from src.use_cases.dto.operation import GetOperationResultDTO, OperationContextDTO
from src.use_cases.get_operation_result import GetOperationResultUseCase

router = APIRouter(prefix="/api/v1/operations", tags=["Operaciones"])


@router.get(
    "/{operation_id}",
    response_model=OperationResultResponse,
    summary="Recuperar el resultado original de una operación",
    description=(
        "Consulta autorizada por UUIDv4 dentro de la identidad del servidor. "
        "Devuelve el snapshot confirmado sin repetir el comando. Una operación "
        "desconocida puede seguir en tránsito o no ser visible antes del commit; "
        "un 404 no autoriza cambiar su clave."
    ),
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": OperationErrorResponse,
            "description": "Operación desconocida o sin acceso para este actor.",
        },
        status.HTTP_409_CONFLICT: {
            "model": OperationErrorResponse,
            "description": "Snapshot purgado, corrupto o con versión no soportada.",
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": OperationErrorResponse | ErrorResponse,
            "description": (
                "Operación sin confirmar, lectura bloqueada o identidad ausente."
            ),
        },
    },
)
def get_operation_result(
    operation_id: Annotated[UUID4, Path(description="UUIDv4 original del comando")],
    actor: ActorDep,
    use_case: Annotated[GetOperationResultUseCase, Depends(get_operation_result_uc)],
    response: Response,
) -> OperationResultResponse:
    dto = GetOperationResultDTO(
        context=OperationContextDTO(actor=actor, operation_id=operation_id)
    )
    operation = use_case.execute(dto)
    response.headers["Cache-Control"] = "no-store"
    return OperationResultResponse.from_operation(operation)
