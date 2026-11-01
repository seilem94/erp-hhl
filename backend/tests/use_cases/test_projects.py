"""Unit tests for CreateProjectUseCase and ListProjectsUseCase.

Test philosophy:
- Pure unit tests: zero I/O, zero network, zero database.
- Each test exercises exactly one behaviour (one path through execute()).
- Fakes replace real repositories; no mocking frameworks needed.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from src.domain.enums import ProjectStatus
from src.use_cases.create_project import CreateProjectDTO, CreateProjectUseCase
from src.use_cases.list_projects import ListProjectsUseCase
from tests.fakes import InMemoryProjectRepository

# ── Helpers ───────────────────────────────────────────────────────────────────


def _make_create_use_case(
    repo: InMemoryProjectRepository | None = None,
) -> tuple[CreateProjectUseCase, InMemoryProjectRepository]:
    project_repo = repo or InMemoryProjectRepository()
    return CreateProjectUseCase(project_repo=project_repo), project_repo


def _make_list_use_case(
    repo: InMemoryProjectRepository | None = None,
) -> tuple[ListProjectsUseCase, InMemoryProjectRepository]:
    project_repo = repo or InMemoryProjectRepository()
    return ListProjectsUseCase(project_repo=project_repo), project_repo


# ── CreateProjectUseCase — happy-path tests ───────────────────────────────────


def test_crear_proyecto_retorna_entidad_persistida() -> None:
    """El proyecto devuelto por execute() debe estar guardado en el repositorio."""
    use_case, repo = _make_create_use_case()
    dto = CreateProjectDTO(name="Instalación Tablero General", client="Empresa ABC SpA")

    result = use_case.execute(dto)

    assert repo.get_by_id(result.id) is not None


def test_crear_proyecto_estado_inicial_es_planning() -> None:
    """El status inicial de todo proyecto creado debe ser PLANNING."""
    use_case, _ = _make_create_use_case()
    dto = CreateProjectDTO(name="Instalación Tablero General", client="Empresa ABC SpA")

    result = use_case.execute(dto)

    assert result.status == ProjectStatus.PLANNING


def test_crear_proyecto_campos_nombre_y_cliente_correctos() -> None:
    """name y client en la entidad deben coincidir con el DTO."""
    use_case, _ = _make_create_use_case()
    dto = CreateProjectDTO(
        name="Obra Eléctrica Industrial",
        client="Minera Los Andes SA",
    )

    result = use_case.execute(dto)

    assert result.name == "Obra Eléctrica Industrial"
    assert result.client == "Minera Los Andes SA"


def test_crear_proyecto_con_presupuesto_estimado() -> None:
    """El campo budget se mapea desde estimated_budget del DTO."""
    use_case, _ = _make_create_use_case()
    dto = CreateProjectDTO(
        name="Instalación Paneles Solares",
        client="Cliente Solar Ltda",
        estimated_budget=Decimal("5000000"),
    )

    result = use_case.execute(dto)

    assert result.budget == Decimal("5000000")


def test_crear_proyecto_sin_presupuesto_budget_es_none() -> None:
    """Cuando no se provee estimated_budget, el campo budget debe ser None."""
    use_case, _ = _make_create_use_case()
    dto = CreateProjectDTO(
        name="Mantención Preventiva", client="Cliente Sin Presupuesto"
    )

    result = use_case.execute(dto)

    assert result.budget is None


def test_crear_proyecto_genera_id_unico_por_instancia() -> None:
    """Cada llamada a execute() debe generar un UUID distinto."""
    use_case, _ = _make_create_use_case()
    dto = CreateProjectDTO(name="Proyecto Repetido", client="Cliente X")

    result_a = use_case.execute(dto)
    result_b = use_case.execute(dto)

    assert result_a.id != result_b.id


def test_crear_proyecto_timestamps_creados_con_zona_utc() -> None:
    """created_at y updated_at deben tener tzinfo UTC (timezone-aware)."""
    from datetime import UTC

    use_case, _ = _make_create_use_case()
    dto = CreateProjectDTO(name="Proyecto Zona Horaria", client="Cliente UTC")

    result = use_case.execute(dto)

    assert result.created_at.tzinfo is not None
    assert result.created_at.tzinfo == UTC
    assert result.updated_at.tzinfo is not None
    assert result.updated_at.tzinfo == UTC


def test_crear_proyecto_created_at_igual_a_updated_at() -> None:
    """En la creación, created_at y updated_at deben ser iguales (mismo instante)."""
    use_case, _ = _make_create_use_case()
    dto = CreateProjectDTO(name="Proyecto Timestamps Iguales", client="Cliente Y")

    result = use_case.execute(dto)

    assert result.created_at == result.updated_at


# ── ListProjectsUseCase — happy-path tests ────────────────────────────────────


def test_listar_proyectos_sin_filtro_devuelve_todos() -> None:
    """execute() sin argumento devuelve todos los proyectos sin importar su estado."""
    repo = InMemoryProjectRepository()
    create_uc, _ = _make_create_use_case(repo)
    list_uc, _ = _make_list_use_case(repo)

    create_uc.execute(CreateProjectDTO(name="Proyecto A", client="Cliente 1"))
    create_uc.execute(CreateProjectDTO(name="Proyecto B", client="Cliente 2"))

    result = list_uc.execute()

    assert len(result) == 2


def test_listar_proyectos_repositorio_vacio_devuelve_lista_vacia() -> None:
    """Con un repositorio vacío, execute() debe retornar una lista vacía."""
    list_uc, _ = _make_list_use_case()

    result = list_uc.execute()

    assert result == []


def test_listar_proyectos_filtrado_por_estado_planning() -> None:
    """Filtrar por PLANNING sólo debe devolver proyectos en ese estado."""
    repo = InMemoryProjectRepository()
    create_uc, _ = _make_create_use_case(repo)
    list_uc, _ = _make_list_use_case(repo)

    # Todos los proyectos creados parten en PLANNING
    create_uc.execute(CreateProjectDTO(name="Proyecto P1", client="Cliente 1"))
    create_uc.execute(CreateProjectDTO(name="Proyecto P2", client="Cliente 2"))

    result = list_uc.execute(status=ProjectStatus.PLANNING)

    assert len(result) == 2
    assert all(p.status == ProjectStatus.PLANNING for p in result)


def test_listar_proyectos_filtrado_por_estado_sin_coincidencias() -> None:
    """Si no hay proyectos en el estado solicitado, debe retornarse una lista vacía."""
    repo = InMemoryProjectRepository()
    create_uc, _ = _make_create_use_case(repo)
    list_uc, _ = _make_list_use_case(repo)

    # Creamos proyectos (estado PLANNING); no hay ninguno COMPLETED
    create_uc.execute(CreateProjectDTO(name="Proyecto X", client="Cliente X"))

    result = list_uc.execute(status=ProjectStatus.COMPLETED)

    assert result == []


def test_listar_proyectos_filtrado_excluye_otros_estados() -> None:
    """El filtro por un estado específico no debe incluir proyectos de otros estados."""
    repo = InMemoryProjectRepository()
    list_uc, _ = _make_list_use_case(repo)

    # Insertar manualmente proyectos con distintos estados
    from datetime import UTC, datetime
    from uuid import uuid4

    from src.domain.entities.project import Project

    now = datetime.now(UTC)
    planning_project = Project(
        id=uuid4(),
        name="En Planificación",
        client="Cliente A",
        status=ProjectStatus.PLANNING,
        start_date=now.date(),
        created_at=now,
        updated_at=now,
    )
    in_progress_project = Project(
        id=uuid4(),
        name="En Ejecución",
        client="Cliente B",
        status=ProjectStatus.IN_PROGRESS,
        start_date=now.date(),
        created_at=now,
        updated_at=now,
    )
    repo.save(planning_project)
    repo.save(in_progress_project)

    result = list_uc.execute(status=ProjectStatus.IN_PROGRESS)

    assert len(result) == 1
    assert result[0].status == ProjectStatus.IN_PROGRESS
    assert result[0].name == "En Ejecución"


@pytest.mark.parametrize(
    "status",
    [
        ProjectStatus.PLANNING,
        ProjectStatus.IN_PROGRESS,
        ProjectStatus.PAUSED,
        ProjectStatus.COMPLETED,
        ProjectStatus.CANCELLED,
    ],
    ids=["planning", "in_progress", "paused", "completed", "cancelled"],
)
def test_listar_proyectos_filtrado_por_cada_estado_valido(
    status: ProjectStatus,
) -> None:
    """list_by_status debe funcionar para cada valor del enum ProjectStatus."""
    from datetime import UTC, datetime
    from uuid import uuid4

    from src.domain.entities.project import Project

    repo = InMemoryProjectRepository()
    list_uc, _ = _make_list_use_case(repo)

    now = datetime.now(UTC)
    project = Project(
        id=uuid4(),
        name=f"Proyecto {status}",
        client="Cliente Test",
        status=status,
        start_date=now.date(),
        created_at=now,
        updated_at=now,
    )
    repo.save(project)

    result = list_uc.execute(status=status)

    assert len(result) == 1
    assert result[0].status == status
