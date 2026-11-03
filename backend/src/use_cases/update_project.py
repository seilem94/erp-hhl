"""Use case: Update an existing project (partial update).

This module contains:
- ``UpdateProjectDTO``     – input contract for updating project fields.
- ``UpdateProjectUseCase`` – orchestrates partial entity modification and persistence.

Design constraints:
- Pure Python 3.11+; zero dependencies on FastAPI, SQLAlchemy, or Pydantic.
- Strict typing: no ``Any``.
- Preserves unchanged fields and updates updated_at in UTC.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from src.domain.entities.project import Project
from src.domain.enums import ProjectStatus
from src.domain.exceptions import ProjectNotFoundError
from src.domain.repositories.project_repository import ProjectRepository


@dataclass(frozen=True)
class UpdateProjectDTO:
    """Input contract for ``UpdateProjectUseCase``.

    Attributes:
        project_id: UUID of the target project to update.
        name: New human-readable name of the obra (or None to leave unchanged).
        client: New client name (or None to leave unchanged).
        estimated_budget: New agreed budget (or None to leave unchanged).
        status: New lifecycle status (or None to leave unchanged).
        description: New technical description (or None to leave unchanged).
    """

    project_id: UUID
    name: str | None = None
    client: str | None = None
    estimated_budget: Decimal | None = None
    status: ProjectStatus | None = None
    description: str | None = None


class UpdateProjectUseCase:
    """Apply partial updates to an existing project entity."""

    def __init__(self, project_repo: ProjectRepository) -> None:
        self._project_repo = project_repo

    def execute(self, dto: UpdateProjectDTO) -> Project:
        """Fetch, mutate and persist changes to an existing Project.

        Args:
            dto: Data transfer object with fields to update.

        Returns:
            The updated Project entity.

        Raises:
            ProjectNotFoundError: If no project with ``dto.project_id`` exists.
        """
        project = self._project_repo.get_by_id(dto.project_id)
        if project is None:
            raise ProjectNotFoundError(dto.project_id)

        if dto.name is not None:
            project.name = dto.name
        if dto.client is not None:
            project.client = dto.client
        if dto.status is not None:
            project.status = dto.status
        if dto.estimated_budget is not None:
            project.budget = dto.estimated_budget
        if dto.description is not None:
            project.description = dto.description

        project.updated_at = datetime.now(UTC)

        return self._project_repo.update(project)
