"""SQLAlchemy 2.0 implementation of ProjectRepository.

Receives a synchronous ``Session`` at construction time so the caller
(e.g. a FastAPI dependency) controls the transaction lifecycle.
All public methods return pure-Python domain dataclasses — no ORM
objects ever leak beyond this module.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.entities.project import Project
from src.domain.enums import ProjectStatus
from src.domain.repositories.project_repository import ProjectRepository
from src.infrastructure.database.mappers import (
    domain_to_project_orm,
    project_to_domain,
)
from src.infrastructure.database.models import ProjectORM


class SQLAlchemyProjectRepository(ProjectRepository):
    """Concrete PostgreSQL-backed repository for :class:`Project` entities.

    Args:
        session: An active SQLAlchemy :class:`~sqlalchemy.orm.Session`.
                 The caller is responsible for committing or rolling back
                 the transaction; this class never commits on its own.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def save(self, project: Project) -> Project:
        """Persist a new project row and return the saved domain entity.

        Args:
            project: The :class:`Project` domain dataclass to persist.

        Returns:
            The same entity as stored (identity-mapped through the ORM).
        """
        orm = domain_to_project_orm(project)
        self._session.add(orm)
        self._session.flush()  # populate DB-generated defaults without commit
        return project_to_domain(orm)

    def update(self, project: Project) -> Project:
        """Overwrite an existing project row with the provided entity state.

        Uses ``merge`` so the method works regardless of whether the ORM
        object is already tracked in the current session's identity map.

        Args:
            project: :class:`Project` entity with updated field values.

        Returns:
            The updated entity as reflected by the DB after flush.
        """
        orm = domain_to_project_orm(project)
        merged = self._session.merge(orm)
        self._session.flush()
        return project_to_domain(merged)

    def delete(self, project_id: UUID) -> bool:
        """Delete a project by its UUID.

        Args:
            project_id: UUIDv4 of the project to remove.

        Returns:
            ``True`` if a row was found and deleted; ``False`` otherwise.
        """
        orm = self._session.get(ProjectORM, project_id)
        if orm is None:
            return False
        self._session.delete(orm)
        self._session.flush()
        return True

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_by_id(self, project_id: UUID) -> Project | None:
        """Fetch a single project by primary key.

        Args:
            project_id: UUIDv4 of the project.

        Returns:
            The :class:`Project` domain entity, or ``None`` if not found.
        """
        orm = self._session.get(ProjectORM, project_id)
        if orm is None:
            return None
        return project_to_domain(orm)

    def list_all(self) -> list[Project]:
        """Return every project regardless of status.

        Returns:
            List of :class:`Project` domain entities (may be empty).
        """
        stmt = select(ProjectORM)
        rows = self._session.scalars(stmt).all()
        return [project_to_domain(row) for row in rows]

    def list_by_status(self, status: ProjectStatus) -> list[Project]:
        """Return projects filtered by lifecycle status.

        Args:
            status: The :class:`~src.domain.enums.ProjectStatus` to filter by.

        Returns:
            List of matching :class:`Project` entities (may be empty).
        """
        stmt = select(ProjectORM).where(ProjectORM.status == str(status))
        rows = self._session.scalars(stmt).all()
        return [project_to_domain(row) for row in rows]
