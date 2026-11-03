"""Abstract interface for the Project repository.

Use-cases depend on this ABC; infrastructure provides the concrete
implementation (SQLAlchemy, in-memory, etc.).
Domain layer has zero knowledge of how or where data is stored.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.project import Project
from src.domain.enums import ProjectStatus


class ProjectRepository(ABC):
    """Contract for all Project persistence adapters."""

    @abstractmethod
    def save(self, project: Project) -> Project:
        """Persist a new project and return the saved entity.

        Args:
            project: The Project entity to create.

        Returns:
            The persisted Project entity (may include DB-generated fields).
        """

    @abstractmethod
    def get_by_id(self, project_id: UUID) -> Project | None:
        """Fetch a single project by its unique identifier.

        Args:
            project_id: UUIDv4 of the project.

        Returns:
            The Project entity, or None if not found.
        """

    @abstractmethod
    def list_all(self) -> list[Project]:
        """Return all projects in the system, regardless of status.

        Returns:
            List of Project entities (may be empty).
        """

    @abstractmethod
    def list_by_status(self, status: ProjectStatus) -> list[Project]:
        """Return all projects that match the given status.

        Args:
            status: The lifecycle state to filter by.

        Returns:
            List of Project entities with the requested status (may be empty).
        """

    @abstractmethod
    def update(self, project: Project) -> Project:
        """Persist changes to an existing project.

        The caller is responsible for providing the full, mutated entity.

        Args:
            project: Project entity with updated field values.

        Returns:
            The updated Project entity as stored.
        """

    @abstractmethod
    def delete(self, project_id: UUID) -> bool:
        """Remove a project by its identifier.

        Args:
            project_id: UUIDv4 of the project to remove.

        Returns:
            True if the project existed and was deleted; False otherwise.
        """
