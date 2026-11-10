"""Use case: Create a new project (obra eléctrica).

This module contains:
- ``CreateProjectDTO``     – immutable input contract from the interface layer.
- ``CreateProjectUseCase`` – orchestrates entity construction and persistence.

Design constraints:
- Pure Python 3.11+; zero dependencies on FastAPI, SQLAlchemy, or Pydantic.
- Strict typing: no ``Any``.
- UTC timestamps are server generated; resource identity may be preassigned.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.entities.project import Project
from src.domain.enums import CommandType, Currency, ProjectStatus
from src.domain.exceptions import OperationUnresolvedError
from src.domain.repositories.project_repository import ProjectRepository
from src.domain.value_objects.operation_result import ProjectSnapshot
from src.use_cases.dto.operation import CreateProjectCommandDTO
from src.use_cases.services.canonicalization import CanonicalRequest
from src.use_cases.services.idempotency import IdempotencyCoordinator, IdempotentResult
from src.use_cases.services.monetary_precision import validate_command_amount


@dataclass(frozen=True)
class CreateProjectDTO:
    """Immutable input contract for ``CreateProjectUseCase``.

    The interface layer (FastAPI schema, CLI, test fixture …) constructs this
    object from raw user input after basic format/type validation.  Business
    rule validation is the responsibility of the use case.

    Attributes:
        name: Human-readable name of the obra
              (e.g. "Instalación Tablero General Edificio Central").
        client: Name of the contracting client or company.
        estimated_budget: Optional agreed or estimated budget in local currency.
        description: Optional scope or technical notes for the obra.
        id: Optional preassigned resource UUID, separate from the operation key.
    """

    name: str
    client: str
    estimated_budget: Decimal | None = None
    description: str | None = None
    id: UUID | None = None


class CreateProjectUseCase:
    """Create and persist a new project with initial PLANNING status.

    The use case is responsible for:
    1. Preserving a supplied resource UUID or generating a UUIDv4.
    2. Setting the initial status to ``PLANNING``.
    3. Recording ``start_date`` as today's UTC date and both
       ``created_at`` / ``updated_at`` as the current UTC datetime.
    4. Persisting the entity via ``project_repo.save()``.

    Args:
        project_repo: Persistence adapter for ``Project`` entities.
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        *,
        coordinator: IdempotencyCoordinator | None = None,
    ) -> None:
        self._project_repo = project_repo
        self._coordinator = coordinator

    def execute_idempotent(
        self, command: CreateProjectCommandDTO
    ) -> IdempotentResult[ProjectSnapshot]:
        if self._coordinator is None:
            raise OperationUnresolvedError("No idempotency coordinator configured.")
        dto = command.data
        validate_command_amount(dto.estimated_budget)
        return self._coordinator.execute(
            context=command.context,
            request=CanonicalRequest(
                command_type=CommandType.CREATE_PROJECT,
                target_resource_id=dto.id,
                content={
                    "name": dto.name,
                    "client": dto.client,
                    "estimated_budget": dto.estimated_budget,
                    "description": dto.description,
                    "currency": Currency.CLP,
                },
            ),
            execute_business=lambda: ProjectSnapshot.from_project(self.execute(dto)),
            result_type=ProjectSnapshot,
        )

    def execute(self, dto: CreateProjectDTO) -> Project:
        """Build, persist and return a new ``Project`` entity.

        Args:
            dto: Immutable input data from the interface layer.

        Returns:
            The persisted entity with the supplied or generated resource UUID
            and server-generated status, start date and UTC timestamps.
        """
        now: datetime = datetime.now(UTC)

        project = Project(
            id=dto.id if dto.id is not None else uuid4(),
            name=dto.name,
            client=dto.client,
            status=ProjectStatus.PLANNING,
            start_date=date(now.year, now.month, now.day),
            created_at=now,
            updated_at=now,
            budget=dto.estimated_budget,
            description=dto.description,
        )

        return self._project_repo.save(project)
