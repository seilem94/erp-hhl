"""Enrutador HTTP para la gestión de proyectos y obras eléctricas."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.domain.enums import ProjectStatus
from src.infrastructure.http.dependencies import (
    get_create_project_uc,
    get_list_projects_uc,
)
from src.infrastructure.http.schemas.error import ErrorResponse
from src.infrastructure.http.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
)
from src.use_cases.create_project import CreateProjectDTO, CreateProjectUseCase
from src.use_cases.list_projects import ListProjectsUseCase

router = APIRouter(prefix="/api/v1/projects", tags=["Proyectos"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo proyecto u obra",
    description=(
        "Registra un nuevo proyecto o cotización eléctrica con estado inicial de "
        "PLANIFICACIÓN (planning) y fecha de inicio automática fijada al día de hoy."
    ),
    responses={
        status.HTTP_201_CREATED: {
            "description": "Proyecto creado y persistido exitosamente.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorResponse,
            "description": "Solicitud inválida o violación de regla de negocio.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": (
                "Error en la validación de tipos o campos requeridos en el JSON."
            ),
        },
    },
)
def create_project(
    request: CreateProjectRequest,
    use_case: Annotated[CreateProjectUseCase, Depends(get_create_project_uc)],
) -> ProjectResponse:
    """Crea una nueva obra eléctrica en estado inicial de planificación."""
    dto = CreateProjectDTO(
        name=request.name,
        client=request.client,
        estimated_budget=request.estimated_budget,
    )
    project = use_case.execute(dto)
    return ProjectResponse.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    include_in_schema=False,
)
@router.get(
    "/",
    response_model=list[ProjectResponse],
    summary="Listar obras o proyectos",
    description=(
        "Obtiene el listado completo de obras eléctricas registradas. Permite "
        "filtrar opcionalmente por estado del ciclo de vida."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Listado de proyectos obtenido exitosamente.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Estado de proyecto inválido en el parámetro de consulta.",
        },
    },
)
def list_projects(
    use_case: Annotated[ListProjectsUseCase, Depends(get_list_projects_uc)],
    status: Annotated[
        ProjectStatus | None,
        Query(
            description=(
                "Filtro opcional por estado del proyecto: "
                "'planning', 'in_progress', 'paused', 'completed', 'cancelled'."
            )
        ),
    ] = None,
) -> list[ProjectResponse]:
    """Recupera todos los proyectos, aplicando filtro por estado si se especifica."""
    projects = use_case.execute(status=status)
    return [ProjectResponse.model_validate(p) for p in projects]
