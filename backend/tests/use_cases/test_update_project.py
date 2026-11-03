"""Unit tests for UpdateProjectUseCase."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.project import Project
from src.domain.enums import ProjectStatus
from src.domain.exceptions import ProjectNotFoundError
from src.use_cases.update_project import UpdateProjectDTO, UpdateProjectUseCase
from tests.fakes import InMemoryProjectRepository


def test_actualizar_proyecto_exitoso() -> None:
    repo = InMemoryProjectRepository()
    use_case = UpdateProjectUseCase(repo)

    initial_time = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)
    project = Project(
        id=uuid4(),
        name="Obra Inicial",
        client="Cliente Original",
        status=ProjectStatus.PLANNING,
        start_date=date(2026, 1, 1),
        created_at=initial_time,
        updated_at=initial_time,
        budget=Decimal("100000.00"),
        description="Alcance inicial",
    )
    repo.save(project)

    dto = UpdateProjectDTO(
        project_id=project.id,
        name="Obra Modificada",
        status=ProjectStatus.IN_PROGRESS,
        estimated_budget=Decimal("150000.00"),
        description="Nuevo alcance ampliado",
    )
    updated = use_case.execute(dto)

    assert updated.name == "Obra Modificada"
    assert updated.client == "Cliente Original"  # Sin cambios
    assert updated.status == ProjectStatus.IN_PROGRESS
    assert updated.budget == Decimal("150000.00")
    assert updated.description == "Nuevo alcance ampliado"
    assert updated.updated_at > initial_time


def test_actualizar_proyecto_inexistente_lanza_error() -> None:
    repo = InMemoryProjectRepository()
    use_case = UpdateProjectUseCase(repo)

    dto = UpdateProjectDTO(
        project_id=uuid4(),
        name="Obra Fantasma",
    )

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(dto)


def test_actualizar_proyecto_campos_none_no_sobreescriben() -> None:
    repo = InMemoryProjectRepository()
    use_case = UpdateProjectUseCase(repo)

    project = Project(
        id=uuid4(),
        name="Obra Fija",
        client="Cliente Fijo",
        status=ProjectStatus.PLANNING,
        start_date=date(2026, 1, 1),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        budget=Decimal("500000.00"),
        description="Descripción fija",
    )
    repo.save(project)

    dto = UpdateProjectDTO(
        project_id=project.id,
        status=ProjectStatus.PAUSED,
    )
    updated = use_case.execute(dto)

    assert updated.status == ProjectStatus.PAUSED
    assert updated.name == "Obra Fija"
    assert updated.client == "Cliente Fijo"
    assert updated.budget == Decimal("500000.00")
    assert updated.description == "Descripción fija"
