"""HTTP router for project management endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.domain.enums import ProjectStatus
from src.infrastructure.http.dependencies import (
    get_create_project_uc,
    get_list_projects_uc,
)
from src.infrastructure.http.schemas.project import (
    CreateProjectRequest,
    ProjectResponse,
)
from src.use_cases.create_project import CreateProjectDTO, CreateProjectUseCase
from src.use_cases.list_projects import ListProjectsUseCase

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


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
    summary="Create a new project",
)
def create_project(
    request: CreateProjectRequest,
    use_case: Annotated[CreateProjectUseCase, Depends(get_create_project_uc)],
) -> ProjectResponse:
    """Create a new electrical project in PLANNING status."""
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
    summary="List all projects",
)
def list_projects(
    use_case: Annotated[ListProjectsUseCase, Depends(get_list_projects_uc)],
    status: Annotated[
        ProjectStatus | None,
        Query(description="Filter projects by lifecycle status"),
    ] = None,
) -> list[ProjectResponse]:
    """Retrieve all projects, optionally filtered by status."""
    projects = use_case.execute(status=status)
    return [ProjectResponse.model_validate(p) for p in projects]
