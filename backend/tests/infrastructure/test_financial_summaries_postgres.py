"""Real PostgreSQL + HTTP integration; every test migrates an isolated schema.

Set TEST_DATABASE_URL to an existing disposable PostgreSQL database. No business
tables are touched: generated schemas are created and dropped by these fixtures.
An explicitly configured but unreachable database fails rather than falling back
to SQLite or fakes.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, inspect, select
from sqlalchemy.engine import Connection, Engine, ExecutionContext
from sqlalchemy.orm import Session
from sqlalchemy.schema import DropTable

from alembic import command
from src.core.config import Environment, settings
from src.domain.entities.operation import OperationRecord
from src.domain.enums import CommandType, ProjectStatus
from src.domain.exceptions import AuthorizationDeniedError
from src.domain.read_models.financial_summary import (
    FinancialReadScope,
    FinancialSummaryFilters,
)
from src.infrastructure.database.models import ExpenseORM, ProjectORM
from src.infrastructure.database.repositories import (
    sqlalchemy_financial_summary_repository as summaries,
)
from src.infrastructure.database.session import get_db
from src.infrastructure.http.dependencies import get_actor_identity, get_authorization
from src.infrastructure.identity.providers import DenyAllAuthorization
from src.main import app
from src.use_cases.ports.identity import ActorIdentity
from tests.infrastructure.postgres import migration_config

NOW = datetime(2026, 11, 9, tzinfo=UTC)
GENERAL = "/api/v1/dashboard/summary"


@dataclass(frozen=True)
class Dataset:
    tax: UUID
    partner: UUID
    unknown: UUID
    empty: UUID


def project_record(
    project_id: UUID, status: ProjectStatus, has_iva: bool | None
) -> ProjectORM:
    return ProjectORM(
        id=project_id,
        name="Obra de prueba",
        client="Cliente de prueba",
        status=status.value,
        start_date=date(2020, 1, 1),
        created_at=NOW,
        updated_at=NOW,
        has_iva=has_iva,
    )


@pytest.fixture
def dataset(pg_engine: Engine) -> Dataset:
    data = Dataset(uuid4(), uuid4(), uuid4(), uuid4())
    rows = (
        (data.tax, "0.10", date(2026, 11, 1)),
        (data.tax, "0.20", date(2026, 11, 2)),
        (data.partner, "2.30", date(2026, 11, 2)),
        (data.partner, "4.40", date(2026, 11, 3)),
        (data.unknown, "8.80", date(2026, 11, 2)),
        (None, "0.05", date(2026, 11, 2)),
        (None, "0.15", date(2026, 11, 4)),
    )
    with Session(pg_engine) as session:
        session.add_all(
            [
                project_record(data.tax, ProjectStatus.IN_PROGRESS, True),
                project_record(data.partner, ProjectStatus.CANCELLED, False),
                project_record(data.unknown, ProjectStatus.PLANNING, None),
                project_record(data.empty, ProjectStatus.COMPLETED, True),
            ]
        )
        session.flush()
        session.add_all(
            ExpenseORM(
                id=uuid4(),
                project_id=project_id,
                amount=Decimal(amount),
                date=expense_date,
                category="materials",
                description="Gasto de prueba",
                has_receipt=False,
                created_at=NOW,
                updated_at=NOW,
            )
            for project_id, amount, expense_date in rows
        )
        session.commit()
    return data


class SummaryAuthorization:
    """Test policy only; requests cannot choose its actor or financial scope."""

    def __init__(self, data: Dataset) -> None:
        self.global_access = True
        self.allowed_projects = frozenset({data.tax, data.empty})
        self.actor = ActorIdentity(actor_id=uuid4())

    def authorize_summary(
        self, actor: ActorIdentity, project_id: UUID | None = None
    ) -> FinancialReadScope:
        if actor != self.actor:
            raise AuthorizationDeniedError("Different actor.")
        return FinancialReadScope(
            all_projects=self.global_access,
            project_ids=self.allowed_projects,
            include_operational=self.global_access,
        )

    def authorize_command(
        self,
        actor: ActorIdentity,
        command_type: CommandType,
        target_resource_id: UUID | None,
    ) -> None:
        raise AuthorizationDeniedError("Not provided by this test policy.")

    def authorize_operation_result(
        self, actor: ActorIdentity, operation: OperationRecord
    ) -> None:
        raise AuthorizationDeniedError("Not provided by this test policy.")


@pytest.fixture
def policy(dataset: Dataset) -> SummaryAuthorization:
    return SummaryAuthorization(dataset)


@pytest.fixture
def client(
    pg_engine: Engine, policy: SummaryAuthorization
) -> Generator[TestClient, None, None]:
    def database() -> Generator[Session, None, None]:
        with Session(pg_engine, autoflush=False) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = database
    app.dependency_overrides[get_authorization] = lambda: policy
    app.dependency_overrides[get_actor_identity] = lambda: policy.actor
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.fixture
def queries(pg_engine: Engine, dataset: Dataset) -> Generator[list[str], None, None]:
    statements: list[str] = []

    def count_query(
        connection: Connection,
        cursor: object,
        statement: str,
        parameters: object,
        context: ExecutionContext,
        executemany: bool,
    ) -> None:
        statements.append(statement)

    event.listen(pg_engine, "before_cursor_execute", count_query)
    try:
        yield statements
    finally:
        event.remove(pg_engine, "before_cursor_execute", count_query)


def test_http_exact_totals_include_cancelled_and_unclassified_projects(
    client: TestClient, queries: list[str]
) -> None:
    response = client.get(GENERAL)
    assert response.status_code == 200
    body = response.json()
    assert body["operational_expenses_total"] == "0.20"
    assert body["project_expenses_total"] == "15.80"
    assert body["expenses_total"] == "16.00"
    assert body["expense_count"] == 7
    assert body["project_count"] == 4
    assert body["projects_by_status"] == {
        "planning": 1,
        "in_progress": 1,
        "paused": 0,
        "completed": 1,
        "cancelled": 1,
    }
    assert body["has_iva"] is None
    cutoff = datetime.fromisoformat(body["as_of"].replace("Z", "+00:00"))
    assert cutoff.utcoffset() == timedelta(0)
    assert len(queries) == 1
    assert queries[0].lstrip().upper().startswith("WITH")
    assert "sum(" in queries[0].lower() and "count(" in queries[0].lower()


@pytest.mark.parametrize(
    ("has_iva", "total", "expense_count", "project_count"),
    [("true", "0.30", 2, 2), ("false", "6.70", 2, 1)],
)
def test_http_tax_filter_excludes_opex_and_unknowns_in_sql(
    client: TestClient,
    queries: list[str],
    has_iva: str,
    total: str,
    expense_count: int,
    project_count: int,
) -> None:
    response = client.get(GENERAL, params={"has_iva": has_iva})
    assert response.status_code == 200
    body = response.json()
    assert body["expenses_total"] == body["project_expenses_total"] == total
    assert body["operational_expenses_total"] == "0.00"
    assert body["expense_count"] == expense_count
    assert body["project_count"] == project_count
    assert len(queries) == 1
    assert ("IS TRUE" if has_iva == "true" else "IS FALSE") in queries[0].upper()


@pytest.mark.parametrize(
    ("params", "total", "count"),
    [
        ({"start_date": "2026-11-02", "end_date": "2026-11-02"}, "11.35", 4),
        ({"start_date": "2026-11-02", "end_date": "2026-11-03"}, "15.75", 5),
        ({"end_date": "2026-11-01"}, "0.10", 1),
        ({"start_date": "2026-11-03"}, "4.55", 2),
        ({"start_date": "2027-01-01"}, "0.00", 0),
    ],
)
def test_http_date_limits_are_inclusive_and_do_not_filter_project_counts(
    client: TestClient, params: dict[str, str], total: str, count: int
) -> None:
    response = client.get(GENERAL, params=params)
    assert response.status_code == 200
    assert response.json()["expenses_total"] == total
    assert response.json()["expense_count"] == count
    assert response.json()["project_count"] == 4


@pytest.mark.parametrize("per_project", [False, True])
@pytest.mark.parametrize(
    "params",
    [
        {"start_date": "2026-11-03", "end_date": "2026-11-01"},
        {"start_date": "not-a-date"},
        {"currency": "USD"},
        {"has_iva": "not-a-bool"},
    ],
)
def test_http_invalid_filters_fail_before_querying(
    client: TestClient,
    dataset: Dataset,
    queries: list[str],
    per_project: bool,
    params: dict[str, str],
) -> None:
    route = f"/api/v1/projects/{dataset.tax}/summary" if per_project else GENERAL
    assert client.get(route, params=params).status_code == 422
    assert not queries


def test_project_summary_reconciles_with_real_detail_in_same_period(
    client: TestClient, dataset: Dataset, queries: list[str]
) -> None:
    params = {"start_date": "2026-11-02", "end_date": "2026-11-03"}
    response = client.get(f"/api/v1/projects/{dataset.partner}/summary", params=params)
    assert response.status_code == 200
    assert response.json()["project_status"] == "cancelled"
    assert response.json()["expenses_total"] == "6.70"
    assert len(queries) == 1
    detail = client.get(f"/api/v1/expenses/project/{dataset.partner}", params=params)
    assert detail.status_code == 200
    independent = sum((Decimal(item["amount"]) for item in detail.json()), Decimal(0))
    assert independent == Decimal(response.json()["expenses_total"])
    assert response.json()["expense_count"] == len(detail.json())


def test_visible_project_without_expenses_has_zero_summary(
    client: TestClient, dataset: Dataset
) -> None:
    response = client.get(f"/api/v1/projects/{dataset.empty}/summary")
    assert response.status_code == 200
    assert response.json()["expenses_total"] == "0.00"
    assert response.json()["expense_count"] == 0


def test_global_permission_is_required_and_project_access_is_isolated(
    client: TestClient,
    dataset: Dataset,
    policy: SummaryAuthorization,
    queries: list[str],
) -> None:
    policy.global_access = False
    assert client.get(GENERAL).status_code == 403
    assert not queries
    allowed = client.get(f"/api/v1/projects/{dataset.tax}/summary")
    assert allowed.status_code == 200
    assert allowed.json()["expenses_total"] == "0.30"
    queries.clear()
    hidden = client.get(f"/api/v1/projects/{dataset.partner}/summary")
    assert hidden.status_code == 404
    assert not queries
    absent = client.get(f"/api/v1/projects/{uuid4()}/summary")
    assert absent.status_code == 404
    assert absent.json() == hidden.json()
    assert not queries


def test_excluded_missing_and_denied_project_responses_do_not_leak_existence(
    client: TestClient, dataset: Dataset
) -> None:
    excluded = client.get(
        f"/api/v1/projects/{dataset.unknown}/summary", params={"has_iva": "false"}
    )
    mismatch = client.get(
        f"/api/v1/projects/{dataset.tax}/summary", params={"has_iva": "false"}
    )
    absent = client.get(f"/api/v1/projects/{uuid4()}/summary")
    app.dependency_overrides[get_authorization] = lambda: DenyAllAuthorization()
    denied = client.get(f"/api/v1/projects/{dataset.tax}/summary")
    assert all(r.status_code == 404 for r in (excluded, mismatch, absent, denied))
    assert excluded.json() == mismatch.json() == absent.json() == denied.json()


def test_repository_enforces_server_scope_without_hydrating_entities(
    pg_engine: Engine, dataset: Dataset
) -> None:
    with Session(pg_engine) as session:
        repo = summaries.SQLAlchemyFinancialSummaryRepository(session)
        summary = repo.get_general(
            FinancialSummaryFilters(),
            FinancialReadScope(project_ids=frozenset({dataset.tax})),
        )
        assert summary.expenses_total == Decimal("0.30")
        assert isinstance(summary.expenses_total, Decimal)
        assert summary.project_count == 1
        assert not session.identity_map


def test_empty_database_returns_all_zeros(pg_engine: Engine) -> None:
    with Session(pg_engine) as session:
        result = summaries.SQLAlchemyFinancialSummaryRepository(session).get_general(
            FinancialSummaryFilters(),
            FinancialReadScope(all_projects=True, include_operational=True),
        )
        assert result.expenses_total == result.operational_expenses_total == Decimal(0)
        assert result.project_expenses_total == Decimal(0)
        assert result.expense_count == result.project_count == 0


def test_aggregate_may_exceed_individual_numeric_precision(
    client: TestClient, pg_engine: Engine
) -> None:
    with Session(pg_engine) as session:
        session.add_all(
            ExpenseORM(
                id=uuid4(),
                amount=Decimal("9999999999.99"),
                date=NOW.date(),
                category="other",
                description="Importe extremo",
                has_receipt=False,
                created_at=NOW,
                updated_at=NOW,
            )
            for _ in range(2)
        )
        session.commit()
    result = client.get(GENERAL)
    assert result.status_code == 200
    assert result.json()["operational_expenses_total"] == "20000000000.18"
    assert result.json()["expenses_total"] == "20000000015.98"


def test_query_count_does_not_grow_per_project(
    client: TestClient, pg_engine: Engine, queries: list[str]
) -> None:
    assert client.get(GENERAL).status_code == 200
    assert len(queries) == 1
    with Session(pg_engine) as session:
        session.add_all(
            project_record(uuid4(), ProjectStatus.PAUSED, None) for _ in range(30)
        )
        session.commit()
    queries.clear()
    result = client.get(GENERAL)
    assert result.json()["project_count"] == 34
    assert len(queries) == 1


def test_committed_expense_appears_in_next_summary(
    client: TestClient, dataset: Dataset
) -> None:
    before = client.get(GENERAL).json()
    write = client.post(
        "/api/v1/expenses/",
        json={
            "project_id": str(dataset.tax),
            "amount": "0.07",
            "date": "2026-11-01",
            "category": "materials",
            "description": "Nuevo gasto confirmado",
        },
    )
    assert write.status_code == 201
    after = client.get(GENERAL).json()
    assert Decimal(after["expenses_total"]) - Decimal(
        before["expenses_total"]
    ) == Decimal("0.07")
    assert after["expense_count"] == before["expense_count"] + 1


def test_legacy_project_edit_preserves_existing_tax_classification(
    client: TestClient, dataset: Dataset, pg_engine: Engine
) -> None:
    assert (
        client.patch(
            f"/api/v1/projects/{dataset.tax}", json={"name": "Nombre actualizado"}
        ).status_code
        == 200
    )
    with Session(pg_engine) as session:
        assert (
            session.scalar(
                select(ProjectORM.has_iva).where(ProjectORM.id == dataset.tax)
            )
            is True
        )


def test_database_failure_is_recoverable_and_never_partial(
    client: TestClient, pg_engine: Engine
) -> None:
    with pg_engine.begin() as connection:
        connection.execute(DropTable(ExpenseORM.__table__))
    response = client.get(GENERAL)
    assert response.status_code == 503
    assert response.json() == {
        "detail": "Financial summary is temporarily unavailable."
    }


def test_development_dummy_and_non_development_routes(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    app.dependency_overrides.pop(get_actor_identity)
    app.dependency_overrides.pop(get_authorization)
    monkeypatch.setattr(settings, "ENV", Environment.DEVELOPMENT)
    assert client.get(GENERAL, headers={"X-Actor-ID": str(uuid4())}).status_code == 200
    for environment in (Environment.PRODUCTION, Environment.TESTING):
        monkeypatch.setattr(settings, "ENV", environment)
        assert client.get(GENERAL).status_code == 503


def test_tax_migration_preserves_unknown_history_without_default(
    pg_engine: Engine,
) -> None:
    with pg_engine.begin() as connection:
        config = migration_config(connection)
        command.downgrade(config, "dd79d22101bf")
        project_id = uuid4()
        connection.execute(
            ProjectORM.__table__.insert().values(
                id=project_id,
                name="Histórico",
                client="Cliente",
                status="planning",
                start_date=NOW.date(),
                created_at=NOW,
                updated_at=NOW,
            )
        )
        command.upgrade(config, "head")
        row = connection.execute(
            select(ProjectORM.id, ProjectORM.name, ProjectORM.has_iva)
        ).one()
        assert row.id == project_id and row.name == "Histórico"
        assert row.has_iva is None
        column = next(
            c
            for c in inspect(connection).get_columns("projects")
            if c["name"] == "has_iva"
        )
        assert column["nullable"] and column["default"] is None
