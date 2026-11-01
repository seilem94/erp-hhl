"""Use case: List projects, optionally filtered by status.

This module contains:
- ``ListProjectsUseCase`` – queries all projects or filters by lifecycle state.

Design constraints:
- Pure Python 3.11+; zero dependencies on FastAPI, SQLAlchemy, or Pydantic.
- Strict typing: no ``Any``.
"""

from __future__ import annotations

from src.domain.entities.project import Project
from src.domain.enums import ProjectStatus
from src.domain.repositories.project_repository import ProjectRepository


class ListProjectsUseCase:
    """Return a list of projects, with optional status filtering.

    Behaviour:
    - If ``status`` is ``None``, all projects are returned via
      ``project_repo.list_all()``.
    - If ``status`` is provided, only projects in that state are returned
      via ``project_repo.list_by_status()``.

    Args:
        project_repo: Persistence adapter for ``Project`` entities.
    """

    def __init__(self, project_repo: ProjectRepository) -> None:
        self._project_repo = project_repo

    def execute(self, status: ProjectStatus | None = None) -> list[Project]:
        """Fetch and return the matching list of projects.

        Args:
            status: Optional lifecycle state to filter by.
                    Pass ``None`` (default) to retrieve all projects.

        Returns:
            A list of ``Project`` entities (may be empty).
        """
        if status is None:
            return self._project_repo.list_all()
        return self._project_repo.list_by_status(status)
