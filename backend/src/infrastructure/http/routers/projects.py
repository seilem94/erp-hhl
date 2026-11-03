"""Enrutador HTTP para la gestión de proyectos y obras eléctricas."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status

from src.domain.enums import ProjectStatus
from src.infrastructure.http.dependencies import (
    get_create_project_uc,
    get_list_projects_uc,
    get_update_project_uc,
)
from src.infrastructure.http.schemas.error import ErrorResponse
from src.infrastructure.http.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
    UpdateProjectRequest,
)
from src.use_cases.create_project import CreateProjectDTO, CreateProjectUseCase
from src.use_cases.list_projects import ListProjectsUseCase
from src.use_cases.update_project import UpdateProjectDTO, UpdateProjectUseCase

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
        description=request.description,
    )
    project = use_case.execute(dto)
    return ProjectResponse.model_validate(project)


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Actualizar parcialmente una obra o proyecto",
    description=(
        "Modifica uno o más campos de una obra existente (nombre, cliente, "
        "presupuesto, estado o descripción). Si el proyecto no existe, retorna 404."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Proyecto actualizado exitosamente.",
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "La obra o proyecto especificado no fue encontrado.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": (
                "Identificador UUID o datos en el JSON con formato incorrecto."
            ),
        },
    },
)
def update_project(
    project_id: Annotated[
        UUID,
        Path(description="Identificador único universal (UUIDv4) de la obra"),
    ],
    request: UpdateProjectRequest,
    use_case: Annotated[UpdateProjectUseCase, Depends(get_update_project_uc)],
) -> ProjectResponse:
    """Actualiza parcialmente los campos especificados de un proyecto existente."""
    dto = UpdateProjectDTO(
        project_id=project_id,
        name=request.name,
        client=request.client,
        estimated_budget=request.estimated_budget,
        status=request.status,
        description=request.description,
    )
    updated = use_case.execute(dto)
    return ProjectResponse.model_validate(updated)


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
