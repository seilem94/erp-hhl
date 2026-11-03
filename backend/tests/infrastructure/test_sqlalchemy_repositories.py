"""Integration tests for SQLAlchemy repository implementations.

These tests exercise the concrete persistence layer against an in-memory
SQLite database (StaticPool), verifying that:

- ``SQLAlchemyProjectRepository`` correctly persists, updates, deletes, and queries
  ``Project`` domain entities.
- ``SQLAlchemyExpenseRepository`` correctly persists, deletes, and queries ``Expense``
  entities both with a valid ``project_id`` (CapEx) and with ``project_id=None`` (OPEX).
- Every repository method returns pure ``@dataclass`` domain objects — no
  SQLAlchemy ORM models ever escape the infrastructure boundary.

Design rules:
- Each test function receives a fresh, isolated ``Session`` via the
  ``db_session`` fixture (transaction is rolled back after each test).
- No network I/O, no real PostgreSQL, no environment variables required.
- Strict typing: fully typed fixtures and helpers, no ``Any``.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Generator
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.enums import ExpenseCategory, ProjectStatus
from src.infrastructure.database.models import Base
from src.infrastructure.database.repositories.sqlalchemy_expense_repository import (
    SQLAlchemyExpenseRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    """Create a single in-memory SQLite engine reused across the session.

    ``StaticPool`` ensures all connections share the same in-memory DB so
    table DDL and test data are visible to every query in the same process.
    ``check_same_thread=False`` is required by SQLite when used outside the
    thread that created the connection.
    """
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(_engine)
    yield _engine
    _engine.dispose()


@pytest.fixture()
def db_session(engine: Engine) -> Generator[Session, None, None]:
    """Provide a transactional ``Session`` that rolls back after each test.

    The outermost ``connection.begin()`` starts a SAVEPOINT-based nested
    transaction; the ``session`` uses that connection directly. After each
    test the outer transaction is rolled back, leaving the DB pristine for
    the next test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session: Session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_project(
    *,
    name: str = "Instalación Tablero Principal",
    client: str = "Cliente Ejemplo S.A.",
    status: ProjectStatus = ProjectStatus.PLANNING,
    start_date: date = date(2026, 1, 1),
    budget: Decimal | None = None,
    description: str | None = None,
    end_date: date | None = None,
) -> Project:
    """Return a fresh ``Project`` dataclass with sensible defaults."""
    now = datetime.now(UTC)
    return Project(
        id=uuid4(),
        name=name,
        client=client,
        status=status,
        start_date=start_date,
        created_at=now,
        updated_at=now,
        description=description,
        end_date=end_date,
        budget=budget,
    )


def _make_expense(
    *,
    amount: Decimal = Decimal("1500.00"),
    expense_date: date = date(2026, 3, 15),
    category: ExpenseCategory = ExpenseCategory.MATERIALS,
    description: str = "Compra cable 2.5mm²",
    has_receipt: bool = True,
    project_id: UUID | None = None,
    receipt_url: str | None = None,
) -> Expense:
    """Return a fresh ``Expense`` dataclass with sensible defaults."""
    now = datetime.now(UTC)
    return Expense(
        id=uuid4(),
        amount=amount,
        date=expense_date,
        category=category,
        description=description,
        has_receipt=has_receipt,
        created_at=now,
        updated_at=now,
        project_id=project_id,
        receipt_url=receipt_url,
    )


# ---------------------------------------------------------------------------
# SQLAlchemyProjectRepository — integration tests
# ---------------------------------------------------------------------------


class TestSQLAlchemyProjectRepositorySave:
    """Tests for ``SQLAlchemyProjectRepository.save``."""

    def test_save_returns_pure_dataclass(self, db_session: Session) -> None:
        """``save`` must return a pure domain dataclass, not an ORM model."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project()

        result = repo.save(project)

        assert dataclasses.is_dataclass(result)
        assert not hasattr(result, "_sa_instance_state"), (
            "save() must not return an ORM model"
        )

    def test_save_persists_and_returns_same_id(self, db_session: Session) -> None:
        """The returned entity must preserve the original UUID."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project(name="Obra Norte")

        result = repo.save(project)

        assert result.id == project.id

    def test_save_persists_scalar_fields(self, db_session: Session) -> None:
        """All scalar fields survive the ORM round-trip unchanged."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project(
            name="Obra Sur",
            client="Empresa XYZ",
            status=ProjectStatus.IN_PROGRESS,
            budget=Decimal("250000.50"),
            description="Descripción de prueba",
            end_date=date(2026, 12, 31),
        )

        result = repo.save(project)

        assert result.name == project.name
        assert result.client == project.client
        assert result.status == project.status
        assert result.budget == project.budget
        assert result.description == project.description
        assert result.end_date == project.end_date
        assert result.start_date == project.start_date

    def test_saved_project_retrievable_by_id(self, db_session: Session) -> None:
        """A project saved via ``save`` can be fetched back with ``get_by_id``."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project(name="Obra Recuperable")

        repo.save(project)
        fetched = repo.get_by_id(project.id)

        assert fetched is not None
        assert fetched.id == project.id
        assert fetched.name == project.name
        assert dataclasses.is_dataclass(fetched)
        assert not hasattr(fetched, "_sa_instance_state")

    def test_get_by_id_nonexistent_returns_none(self, db_session: Session) -> None:
        """``get_by_id`` returns None when the project UUID is not in database."""
        repo = SQLAlchemyProjectRepository(db_session)

        result = repo.get_by_id(uuid4())

        assert result is None


class TestSQLAlchemyProjectRepositoryUpdate:
    """Tests for ``SQLAlchemyProjectRepository.update``."""

    def test_update_returns_pure_dataclass(self, db_session: Session) -> None:
        """``update`` must return a pure domain dataclass."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project()
        repo.save(project)

        updated_project = dataclasses.replace(project, status=ProjectStatus.IN_PROGRESS)
        result = repo.update(updated_project)

        assert dataclasses.is_dataclass(result)
        assert not hasattr(result, "_sa_instance_state"), (
            "update() must not return an ORM model"
        )

    def test_update_changes_status(self, db_session: Session) -> None:
        """Updating a project status is reflected when re-fetched."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project(status=ProjectStatus.PLANNING)
        repo.save(project)

        updated_project = dataclasses.replace(project, status=ProjectStatus.COMPLETED)
        repo.update(updated_project)

        fetched = repo.get_by_id(project.id)
        assert fetched is not None
        assert fetched.status == ProjectStatus.COMPLETED

    def test_update_changes_name_and_budget(self, db_session: Session) -> None:
        """Multiple fields can be updated in a single call."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project(name="Nombre Viejo", budget=None)
        repo.save(project)

        updated_project = dataclasses.replace(
            project, name="Nombre Nuevo", budget=Decimal("99999.99")
        )
        repo.update(updated_project)

        fetched = repo.get_by_id(project.id)
        assert fetched is not None
        assert fetched.name == "Nombre Nuevo"
        assert fetched.budget == Decimal("99999.99")


class TestSQLAlchemyProjectRepositoryDelete:
    """Tests for ``SQLAlchemyProjectRepository.delete``."""

    def test_delete_existing_project_returns_true(self, db_session: Session) -> None:
        """Deleting an existing project returns True and removes it from the DB."""
        repo = SQLAlchemyProjectRepository(db_session)
        project = _make_project(name="Proyecto a Eliminar")
        repo.save(project)

        deleted = repo.delete(project.id)

        assert deleted is True
        assert repo.get_by_id(project.id) is None

    def test_delete_nonexistent_project_returns_false(
        self, db_session: Session
    ) -> None:
        """Deleting a non-existent project returns False."""
        repo = SQLAlchemyProjectRepository(db_session)

        deleted = repo.delete(uuid4())

        assert deleted is False


class TestSQLAlchemyProjectRepositoryListAll:
    """Tests for ``SQLAlchemyProjectRepository.list_all`` and ``list_by_status``."""

    def test_list_all_empty_returns_empty_list(self, db_session: Session) -> None:
        """``list_all`` on a fresh DB returns an empty list."""
        repo = SQLAlchemyProjectRepository(db_session)

        result = repo.list_all()

        assert result == []

    def test_list_all_returns_all_saved_projects(self, db_session: Session) -> None:
        """``list_all`` returns every project that has been saved."""
        repo = SQLAlchemyProjectRepository(db_session)
        p1 = _make_project(name="Proyecto Alfa")
        p2 = _make_project(name="Proyecto Beta")

        repo.save(p1)
        repo.save(p2)

        results = repo.list_all()
        ids = {p.id for p in results}

        assert len(results) == 2
        assert p1.id in ids
        assert p2.id in ids

    def test_list_all_returns_pure_dataclasses(self, db_session: Session) -> None:
        """Every element returned by ``list_all`` must be a pure dataclass."""
        repo = SQLAlchemyProjectRepository(db_session)
        repo.save(_make_project(name="Solo Proyecto"))

        results = repo.list_all()

        for item in results:
            assert dataclasses.is_dataclass(item)
            assert not hasattr(item, "_sa_instance_state")

    def test_list_by_status_filters_correctly(self, db_session: Session) -> None:
        """``list_by_status`` only returns projects with the requested status."""
        repo = SQLAlchemyProjectRepository(db_session)
        planning = _make_project(name="En Planificación", status=ProjectStatus.PLANNING)
        in_progress = _make_project(
            name="En Ejecución", status=ProjectStatus.IN_PROGRESS
        )

        repo.save(planning)
        repo.save(in_progress)

        results = repo.list_by_status(ProjectStatus.PLANNING)

        assert len(results) == 1
        assert results[0].id == planning.id
        assert results[0].status == ProjectStatus.PLANNING
        assert dataclasses.is_dataclass(results[0])
        assert not hasattr(results[0], "_sa_instance_state")


# ---------------------------------------------------------------------------
# SQLAlchemyExpenseRepository — integration tests
# ---------------------------------------------------------------------------


class TestSQLAlchemyExpenseRepositoryCapEx:
    """Tests for expenses linked to a project (CapEx, ``project_id`` set)."""

    def test_save_capex_expense_returns_pure_dataclass(
        self, db_session: Session
    ) -> None:
        """``save`` must return a pure domain dataclass for CapEx expenses."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        project = _make_project()
        project_repo.save(project)

        expense = _make_expense(project_id=project.id)
        result = expense_repo.save(expense)

        assert dataclasses.is_dataclass(result)
        assert not hasattr(result, "_sa_instance_state"), (
            "save() must not return an ORM model"
        )

    def test_save_capex_expense_preserves_project_id(self, db_session: Session) -> None:
        """The ``project_id`` FK must survive the ORM round-trip."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        project = _make_project()
        project_repo.save(project)

        expense = _make_expense(project_id=project.id, amount=Decimal("750.00"))
        result = expense_repo.save(expense)

        assert result.project_id == project.id
        assert result.is_project_expense is True

    def test_save_capex_expense_scalar_fields(self, db_session: Session) -> None:
        """All scalar fields of a CapEx expense survive the round-trip."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        project = _make_project()
        project_repo.save(project)

        expense = _make_expense(
            amount=Decimal("3200.75"),
            expense_date=date(2026, 4, 10),
            category=ExpenseCategory.TRANSPORT,
            description="Flete materiales a obra",
            has_receipt=True,
            project_id=project.id,
            receipt_url="https://boletas.example.com/001.pdf",
        )
        result = expense_repo.save(expense)

        assert result.id == expense.id
        assert result.amount == expense.amount
        assert result.date == expense.date
        assert result.category == expense.category
        assert result.description == expense.description
        assert result.has_receipt == expense.has_receipt
        assert result.receipt_url == expense.receipt_url

    def test_get_by_project_returns_only_linked_expenses(
        self, db_session: Session
    ) -> None:
        """``get_by_project`` returns expenses tied to the requested project."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        proj_a = _make_project(name="Proyecto A")
        proj_b = _make_project(name="Proyecto B")
        project_repo.save(proj_a)
        project_repo.save(proj_b)

        exp_a1 = _make_expense(project_id=proj_a.id, description="Gasto A1")
        exp_a2 = _make_expense(project_id=proj_a.id, description="Gasto A2")
        exp_b1 = _make_expense(project_id=proj_b.id, description="Gasto B1")
        expense_repo.save(exp_a1)
        expense_repo.save(exp_a2)
        expense_repo.save(exp_b1)

        results = expense_repo.get_by_project(proj_a.id)

        assert len(results) == 2
        ids = {e.id for e in results}
        assert exp_a1.id in ids
        assert exp_a2.id in ids
        assert exp_b1.id not in ids

    def test_get_by_project_returns_pure_dataclasses(self, db_session: Session) -> None:
        """Every element returned by ``get_by_project`` is a pure dataclass."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        project = _make_project()
        project_repo.save(project)
        expense_repo.save(_make_expense(project_id=project.id))

        results = expense_repo.get_by_project(project.id)

        for item in results:
            assert dataclasses.is_dataclass(item)
            assert not hasattr(item, "_sa_instance_state")

    def test_get_by_project_with_date_range(self, db_session: Session) -> None:
        """``get_by_project`` respects start_date and end_date filters."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        project = _make_project()
        project_repo.save(project)

        exp1 = _make_expense(
            project_id=project.id, expense_date=date(2026, 1, 10), description="Enero"
        )
        exp2 = _make_expense(
            project_id=project.id, expense_date=date(2026, 2, 15), description="Febrero"
        )
        exp3 = _make_expense(
            project_id=project.id, expense_date=date(2026, 3, 20), description="Marzo"
        )
        expense_repo.save(exp1)
        expense_repo.save(exp2)
        expense_repo.save(exp3)

        results = expense_repo.get_by_project(
            project.id, start_date=date(2026, 2, 1), end_date=date(2026, 2, 28)
        )

        assert len(results) == 1
        assert results[0].id == exp2.id


class TestSQLAlchemyExpenseRepositoryOpEx:
    """Tests for OPEX expenses (``project_id = None``)."""

    def test_save_opex_expense_returns_pure_dataclass(
        self, db_session: Session
    ) -> None:
        """``save`` must return a pure domain dataclass for OPEX expenses."""
        repo = SQLAlchemyExpenseRepository(db_session)

        expense = _make_expense(project_id=None, description="Gasto OPEX")
        result = repo.save(expense)

        assert dataclasses.is_dataclass(result)
        assert not hasattr(result, "_sa_instance_state"), (
            "save() must not return an ORM model"
        )

    def test_save_opex_expense_project_id_is_none(self, db_session: Session) -> None:
        """``project_id`` must be ``None`` for OPEX expenses after round-trip."""
        repo = SQLAlchemyExpenseRepository(db_session)

        expense = _make_expense(project_id=None, description="Alquiler oficina")
        result = repo.save(expense)

        assert result.project_id is None
        assert result.is_project_expense is False

    def test_save_opex_expense_no_project_in_db_needed(
        self, db_session: Session
    ) -> None:
        """An OPEX expense can be saved without any project existing in the DB."""
        repo = SQLAlchemyExpenseRepository(db_session)

        expense = _make_expense(
            project_id=None,
            amount=Decimal("450.00"),
            category=ExpenseCategory.SERVICES,
            description="Suscripción software contabilidad",
        )
        result = repo.save(expense)

        assert result.id == expense.id
        assert result.project_id is None

    def test_get_operational_expenses_returns_only_opex(
        self, db_session: Session
    ) -> None:
        """``get_operational_expenses`` must exclude project-linked expenses."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        project = _make_project()
        project_repo.save(project)

        capex = _make_expense(project_id=project.id, description="CapEx")
        opex1 = _make_expense(project_id=None, description="OPEX 1")
        opex2 = _make_expense(project_id=None, description="OPEX 2")
        expense_repo.save(capex)
        expense_repo.save(opex1)
        expense_repo.save(opex2)

        results = expense_repo.get_operational_expenses()

        ids = {e.id for e in results}
        assert opex1.id in ids
        assert opex2.id in ids
        assert capex.id not in ids

    def test_get_operational_expenses_returns_pure_dataclasses(
        self, db_session: Session
    ) -> None:
        """Every element from ``get_operational_expenses`` is a pure dataclass."""
        repo = SQLAlchemyExpenseRepository(db_session)
        repo.save(_make_expense(project_id=None))

        results = repo.get_operational_expenses()

        for item in results:
            assert dataclasses.is_dataclass(item)
            assert not hasattr(item, "_sa_instance_state")

    def test_get_operational_expenses_empty_when_none_saved(
        self, db_session: Session
    ) -> None:
        """``get_operational_expenses`` returns [] when no OPEX expenses exist."""
        repo = SQLAlchemyExpenseRepository(db_session)

        result = repo.get_operational_expenses()

        assert result == []

    def test_get_operational_expenses_with_date_range(
        self, db_session: Session
    ) -> None:
        """``get_operational_expenses`` respects start_date and end_date filters."""
        repo = SQLAlchemyExpenseRepository(db_session)

        op1 = _make_expense(
            project_id=None, expense_date=date(2026, 1, 5), description="Enero"
        )
        op2 = _make_expense(
            project_id=None, expense_date=date(2026, 2, 10), description="Febrero"
        )
        repo.save(op1)
        repo.save(op2)

        results = repo.get_operational_expenses(start_date=date(2026, 2, 1))

        assert len(results) == 1
        assert results[0].id == op2.id


class TestSQLAlchemyExpenseRepositoryQueries:
    """Tests for ``get_by_id``, ``delete`` and ``list_all`` on expenses."""

    def test_get_by_id_retrieves_saved_expense(self, db_session: Session) -> None:
        """``get_by_id`` returns the saved domain dataclass."""
        repo = SQLAlchemyExpenseRepository(db_session)
        expense = _make_expense(project_id=None, description="Test get_by_id")
        repo.save(expense)

        fetched = repo.get_by_id(expense.id)

        assert fetched is not None
        assert fetched.id == expense.id
        assert fetched.description == "Test get_by_id"
        assert dataclasses.is_dataclass(fetched)
        assert not hasattr(fetched, "_sa_instance_state")

    def test_get_by_id_nonexistent_returns_none(self, db_session: Session) -> None:
        """``get_by_id`` returns None when UUID does not exist."""
        repo = SQLAlchemyExpenseRepository(db_session)

        assert repo.get_by_id(uuid4()) is None

    def test_delete_existing_expense_returns_true(self, db_session: Session) -> None:
        """``delete`` removes an existing expense and returns True."""
        repo = SQLAlchemyExpenseRepository(db_session)
        expense = _make_expense(project_id=None, description="A eliminar")
        repo.save(expense)

        deleted = repo.delete(expense.id)

        assert deleted is True
        assert repo.get_by_id(expense.id) is None

    def test_delete_nonexistent_expense_returns_false(
        self, db_session: Session
    ) -> None:
        """``delete`` returns False when UUID is not present."""
        repo = SQLAlchemyExpenseRepository(db_session)

        assert repo.delete(uuid4()) is False

    def test_list_all_returns_both_capex_and_opex(self, db_session: Session) -> None:
        """``list_all`` must include both project-linked and OPEX expenses."""
        project_repo = SQLAlchemyProjectRepository(db_session)
        expense_repo = SQLAlchemyExpenseRepository(db_session)

        project = _make_project()
        project_repo.save(project)

        capex = _make_expense(project_id=project.id, description="CapEx")
        opex = _make_expense(project_id=None, description="OPEX")
        expense_repo.save(capex)
        expense_repo.save(opex)

        results = expense_repo.list_all()
        ids = {e.id for e in results}

        assert capex.id in ids
        assert opex.id in ids

    def test_list_all_returns_pure_dataclasses(self, db_session: Session) -> None:
        """Every element returned by ``list_all`` must be a pure dataclass."""
        repo = SQLAlchemyExpenseRepository(db_session)
        repo.save(_make_expense(project_id=None))

        results = repo.list_all()

        for item in results:
            assert dataclasses.is_dataclass(item)
            assert not hasattr(item, "_sa_instance_state")
