"""Use case: Create a new project (obra eléctrica).

This module contains:
- ``CreateProjectDTO``     – immutable input contract from the interface layer.
- ``CreateProjectUseCase`` – orchestrates entity construction and persistence.

Design constraints:
- Pure Python 3.11+; zero dependencies on FastAPI, SQLAlchemy, or Pydantic.
- Strict typing: no ``Any``.
- ``id`` and UTC timestamps are generated here, not by the caller.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.project import Project
from src.domain.enums import ProjectStatus
from src.domain.repositories.project_repository import ProjectRepository


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
    """

    name: str
    client: str
    estimated_budget: Decimal | None = None
    description: str | None = None


class CreateProjectUseCase:
    """Create and persist a new project with initial PLANNING status.

    The use case is responsible for:
    1. Generating a UUIDv4 identifier.
    2. Setting the initial status to ``PLANNING``.
    3. Recording ``start_date`` as today's UTC date and both
       ``created_at`` / ``updated_at`` as the current UTC datetime.
    4. Persisting the entity via ``project_repo.save()``.

    Args:
        project_repo: Persistence adapter for ``Project`` entities.
    """

    def __init__(self, project_repo: ProjectRepository) -> None:
        self._project_repo = project_repo

    def execute(self, dto: CreateProjectDTO) -> Project:
        """Build, persist and return a new ``Project`` entity.

        Args:
            dto: Immutable input data from the interface layer.

        Returns:
            The persisted ``Project`` entity with server-generated fields
            (``id``, ``status``, ``start_date``, ``created_at``, ``updated_at``).
        """
        now: datetime = datetime.now(UTC)

        project = Project(
            id=uuid4(),
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
