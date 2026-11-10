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
from src.domain.enums import CommandType, ProjectStatus
from src.domain.exceptions import OperationUnresolvedError, ProjectNotFoundError
from src.domain.repositories.project_repository import ProjectRepository
from src.domain.value_objects.operation_result import ProjectSnapshot
from src.use_cases.dto.operation import UpdateProjectCommandDTO
from src.use_cases.services.canonicalization import CanonicalRequest
from src.use_cases.services.idempotency import IdempotencyCoordinator, IdempotentResult
from src.use_cases.services.monetary_precision import validate_command_amount


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

    def __init__(
        self,
        project_repo: ProjectRepository,
        *,
        coordinator: IdempotencyCoordinator | None = None,
    ) -> None:
        self._project_repo = project_repo
        self._coordinator = coordinator

    def execute_idempotent(
        self, command: UpdateProjectCommandDTO
    ) -> IdempotentResult[ProjectSnapshot]:
        if self._coordinator is None:
            raise OperationUnresolvedError("No idempotency coordinator configured.")
        dto = command.data
        validate_command_amount(dto.estimated_budget)
        return self._coordinator.execute(
            context=command.context,
            request=CanonicalRequest(
                command_type=CommandType.UPDATE_PROJECT,
                target_resource_id=dto.project_id,
                # None means no change in the existing PATCH contract. A future
                # nullable clear operation needs a new command version.
                content={
                    "name": dto.name,
                    "client": dto.client,
                    "estimated_budget": dto.estimated_budget,
                    "status": dto.status,
                    "description": dto.description,
                },
            ),
            execute_business=lambda: ProjectSnapshot.from_project(self.execute(dto)),
            result_type=ProjectSnapshot,
        )

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
