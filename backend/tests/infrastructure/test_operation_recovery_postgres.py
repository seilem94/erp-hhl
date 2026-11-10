"""HTTP recovery with real PostgreSQL, authorization and concurrent transactions."""

from __future__ import annotations

from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from threading import Event
from uuid import UUID, uuid1, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, func, select, update
from sqlalchemy.engine import Connection, Engine, ExecutionContext
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import Environment, settings
from src.domain.entities.operation import (
    OperationKey,
    OperationRecord,
    RequestFingerprint,
)
from src.domain.enums import CommandType
from src.domain.exceptions import AuthorizationDeniedError
from src.domain.repositories.operation_repository import (
    OperationRepository,
    ReservationAcquired,
)
from src.infrastructure.database import session as database
from src.infrastructure.database.models import ExpenseORM, OperationORM, ProjectORM
from src.infrastructure.database.repositories.sqlalchemy_operation_repository import (
    SQLAlchemyOperationRepository,
)
from src.infrastructure.http.dependencies import (
    SessionDep,
    get_authorization,
    get_identity_provider,
    get_operation_repo,
)
from src.infrastructure.identity.providers import (
    DEVELOPMENT_ACTOR_ID,
    DevelopmentAuthorization,
)
from src.main import app
from src.use_cases.ports.identity import ActorIdentity


@dataclass(frozen=True)
class RecordedOperation:
    operation_id: UUID
    resource_id: UUID
    command: CommandType
    original_response: dict[str, object]

    @property
    def path(self) -> str:
        return f"/api/v1/operations/{self.operation_id}"


def create_operation(client: TestClient, command: CommandType) -> RecordedOperation:
    operation_id = uuid4()
    headers = {"Idempotency-Key": str(operation_id)}
    project_data = {
        "name": "Obra original",
        "client": "Cliente",
        "estimated_budget": "10.50",
    }
    if command is CommandType.CREATE_PROJECT:
        response = client.post("/api/v1/projects", json=project_data, headers=headers)
    else:
        project = client.post("/api/v1/projects", json=project_data)
        assert project.status_code == 201
        project_id = project.json()["id"]
        if command is CommandType.UPDATE_PROJECT:
            response = client.patch(
                f"/api/v1/projects/{project_id}",
                json={"name": "Primera edición", "status": "in_progress"},
                headers=headers,
            )
        else:
            response = client.post(
                "/api/v1/expenses",
                headers=headers,
                json={
                    "amount": "0.10",
                    "date": date.today().isoformat(),
                    "category": "materials",
                    "description": "Cable original",
                    "project_id": project_id,
                    "receipt_url": "receipt-reference",
                },
            )
    assert response.status_code == (
        200 if command is CommandType.UPDATE_PROJECT else 201
    )
    result: dict[str, object] = response.json()
    return RecordedOperation(operation_id, UUID(str(result["id"])), command, result)


def operation_count(engine: Engine) -> int:
    with Session(engine) as session:
        return session.execute(
            select(func.count()).select_from(OperationORM)
        ).scalar_one()


@pytest.fixture
def queries(pg_engine: Engine) -> Generator[list[str], None, None]:
    statements: list[str] = []

    def record(
        connection: Connection,
        cursor: object,
        statement: str,
        parameters: object,
        context: ExecutionContext,
        executemany: bool,
    ) -> None:
        statements.append(statement.lower())

    event.listen(pg_engine, "before_cursor_execute", record)
    try:
        yield statements
    finally:
        event.remove(pg_engine, "before_cursor_execute", record)


@pytest.mark.parametrize("command", tuple(CommandType))
def test_recovery_returns_original_snapshot_with_public_metadata(
    pg_client: TestClient, pg_engine: Engine, queries: list[str], command: CommandType
) -> None:
    operation = create_operation(pg_client, command)
    queries.clear()
    response = pg_client.get(operation.path)
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    body = response.json()
    assert body == {
        "operation_id": str(operation.operation_id),
        "state": "confirmed",
        "command_type": command.value,
        "resource_type": command.resource_type.value,
        "result_resource_id": str(operation.resource_id),
        "result_schema_version": 1,
        "created_at": body["created_at"],
        "completed_at": body["completed_at"],
        "result": operation.original_response,
    }
    assert datetime.fromisoformat(body["completed_at"]) >= datetime.fromisoformat(
        body["created_at"]
    )
    assert not any("from projects" in sql or "from expenses" in sql for sql in queries)
    assert operation_count(pg_engine) == 1


@pytest.mark.parametrize("command", tuple(CommandType))
@pytest.mark.parametrize("delete", (False, True))
def test_snapshot_survives_later_resource_edits_or_deletion(
    pg_client: TestClient, pg_engine: Engine, command: CommandType, delete: bool
) -> None:
    operation = create_operation(pg_client, command)
    with Session(pg_engine) as session:
        if command is CommandType.REGISTER_EXPENSE:
            resource = session.get(ExpenseORM, operation.resource_id)
            assert resource is not None
            resource.amount = Decimal("99.99")
            resource.description = "Modificación posterior"
        else:
            resource = session.get(ProjectORM, operation.resource_id)
            assert resource is not None
            resource.name = "Nombre posterior"
            resource.status = "completed"
        if delete:
            session.delete(resource)
        session.commit()
    response = pg_client.get(operation.path)
    assert response.status_code == 200
    assert response.json()["result"] == operation.original_response
    assert operation_count(pg_engine) == 1


def test_unknown_operation_is_not_created_by_querying_it(
    pg_client: TestClient, pg_engine: Engine
) -> None:
    path = f"/api/v1/operations/{uuid4()}"
    first, second = pg_client.get(path), pg_client.get(path)
    assert first.status_code == second.status_code == 404
    assert first.json() == second.json()
    assert first.json()["detail"]["code"] == "operation_unknown"
    assert first.headers["Cache-Control"] == "no-store"
    assert operation_count(pg_engine) == 0


def test_actor_isolation_returns_indistinguishable_unknown_and_own_snapshots(
    pg_client: TestClient, pg_engine: Engine
) -> None:
    class Identity:
        def __init__(self) -> None:
            self.actor = ActorIdentity(actor_id=uuid4())

        def get_actor(self) -> ActorIdentity:
            return self.actor

    class Policy(DevelopmentAuthorization):
        def _check_actor(self, actor: ActorIdentity) -> None:
            if actor != identity.actor:
                raise AuthorizationDeniedError("Not the current actor.")

    identity = Identity()
    app.dependency_overrides[get_identity_provider] = lambda: identity
    app.dependency_overrides[get_authorization] = Policy
    original_actor = identity.actor
    operation = create_operation(pg_client, CommandType.CREATE_PROJECT)
    identity.actor = ActorIdentity(actor_id=uuid4())
    unknown = pg_client.get(f"/api/v1/operations/{uuid4()}")
    foreign = pg_client.get(
        operation.path + f"?actor_id={original_actor.actor_id}",
        headers={"X-Actor-Id": str(original_actor.actor_id)},
    )
    assert unknown.status_code == foreign.status_code == 404
    assert unknown.json() == foreign.json()
    own = pg_client.post(
        "/api/v1/projects",
        json={"name": "Otra obra", "client": "Socio"},
        headers={"Idempotency-Key": str(operation.operation_id)},
    )
    assert own.status_code == 201
    assert pg_client.get(operation.path).json()["result"] == own.json()
    identity.actor = original_actor
    recovered = pg_client.get(operation.path)
    assert recovered.status_code == 200
    assert recovered.json()["result"] == operation.original_response
    assert operation_count(pg_engine) == 2


@pytest.mark.parametrize("mutation", ("purged", "schema", "corrupt"))
def test_unrecoverable_payload_returns_reconciliation_without_new_effects(
    pg_client: TestClient, pg_engine: Engine, mutation: str
) -> None:
    operation = create_operation(pg_client, CommandType.CREATE_PROJECT)
    values: dict[str, object] = {
        "purged": {"result_payload": None},
        "schema": {"result_schema_version": 99},
        "corrupt": {"result_payload": {"invalid": "snapshot"}},
    }[mutation]
    with Session(pg_engine) as session:
        session.execute(update(OperationORM).values(**values))
        session.commit()
    response = pg_client.get(operation.path)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "operation_reconciliation_required"
    assert response.headers["Cache-Control"] == "no-store"
    assert operation_count(pg_engine) == 1
    with Session(pg_engine) as session:
        record = session.get(
            OperationORM, (DEVELOPMENT_ACTOR_ID, operation.operation_id)
        )
        assert record.state == "confirmed"
        assert record.result_resource_id == operation.resource_id
        assert record.request_fingerprint is not None


@pytest.mark.parametrize("mutation", ("valid", "purged", "schema", "corrupt"))
def test_current_authorization_precedes_payload_read_or_reconciliation(
    pg_client: TestClient, pg_engine: Engine, queries: list[str], mutation: str
) -> None:
    recorded = create_operation(pg_client, CommandType.CREATE_PROJECT)
    if mutation != "valid":
        values: dict[str, object] = {
            "purged": {"result_payload": None},
            "schema": {"result_schema_version": 99},
            "corrupt": {"result_payload": {"invalid": "snapshot"}},
        }[mutation]
        with Session(pg_engine) as session:
            session.execute(update(OperationORM).values(**values))
            session.commit()

    class RevokedPolicy(DevelopmentAuthorization):
        def authorize_operation_result(
            self, actor: ActorIdentity, operation: OperationRecord
        ) -> None:
            assert operation.key.actor_id == actor.actor_id
            assert operation.result_resource_id == recorded.resource_id
            assert operation.result_payload is None
            raise AuthorizationDeniedError("Access revoked.")

    app.dependency_overrides[get_authorization] = RevokedPolicy
    queries.clear()
    denied = pg_client.get(recorded.path)
    assert denied.status_code == 404
    assert denied.json()["detail"]["code"] == "operation_unknown"
    operation_reads = [sql for sql in queries if "from operations" in sql]
    assert len(operation_reads) == 1
    assert "result_payload" not in operation_reads[0]
    unknown = pg_client.get(f"/api/v1/operations/{uuid4()}")
    assert unknown.json() == denied.json()


def test_visible_unconfirmed_reservation_returns_unresolved(
    pg_client: TestClient, pg_engine: Engine
) -> None:
    operation_id = uuid4()
    reservation = OperationRecord(
        key=OperationKey(actor_id=DEVELOPMENT_ACTOR_ID, operation_id=operation_id),
        command_type=CommandType.CREATE_PROJECT,
        command_version=1,
        request_fingerprint=RequestFingerprint(version=1, digest="a" * 64),
        created_at=datetime.now(UTC),
    )
    # Seed an orphaned reservation deliberately. Normal commands commit only
    # after confirmation; its continued visibility must never permit takeover.
    with Session(pg_engine) as session:
        assert isinstance(
            SQLAlchemyOperationRepository(session).reserve(reservation),
            ReservationAcquired,
        )
        session.commit()
    response = pg_client.get(f"/api/v1/operations/{operation_id}")
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "operation_unresolved"
    assert operation_count(pg_engine) == 1
    with Session(pg_engine) as session:
        record = session.get(OperationORM, (DEVELOPMENT_ACTOR_ID, operation_id))
        assert record.state == "reserved" and record.result_payload is None


def test_blocked_postgresql_read_returns_unresolved_then_recovers(
    pg_client: TestClient, pg_engine: Engine
) -> None:
    operation = create_operation(pg_client, CommandType.CREATE_PROJECT)

    def bounded_repo(session: SessionDep) -> OperationRepository:
        return SQLAlchemyOperationRepository(session, lock_timeout_ms=150)

    app.dependency_overrides[get_operation_repo] = bounded_repo
    with pg_engine.begin() as blocking:
        blocking.exec_driver_sql("LOCK TABLE operations IN ACCESS EXCLUSIVE MODE")
        response = pg_client.get(operation.path)
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "operation_unresolved"
    recovered = pg_client.get(operation.path)
    assert recovered.status_code == 200
    assert recovered.json()["result"] == operation.original_response


def test_in_flight_uncommitted_operation_is_unknown_until_commit(
    pg_client: TestClient, pg_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    committing, release = Event(), Event()

    class HeldCommitSession(Session):
        def commit(self) -> None:
            committing.set()
            assert release.wait(10), "Writer was not released"
            super().commit()

    monkeypatch.setattr(
        database, "SessionLocal", sessionmaker(pg_engine, class_=HeldCommitSession)
    )
    operation_id = uuid4()
    with ThreadPoolExecutor(max_workers=1) as executor:
        writer = executor.submit(
            pg_client.post,
            "/api/v1/projects",
            json={"name": "En tránsito", "client": "Cliente"},
            headers={"Idempotency-Key": str(operation_id)},
        )
        try:
            assert committing.wait(10), "Writer did not reach commit"
            monkeypatch.setattr(
                database, "SessionLocal", sessionmaker(pg_engine, autoflush=False)
            )
            unknown = pg_client.get(f"/api/v1/operations/{operation_id}")
            assert unknown.status_code == 404
            assert unknown.json()["detail"]["code"] == "operation_unknown"
            assert operation_count(pg_engine) == 0
        finally:
            release.set()
        written = writer.result(timeout=10)
    assert written.status_code == 201
    known = pg_client.get(f"/api/v1/operations/{operation_id}")
    assert known.status_code == 200
    assert known.json()["result"] == written.json()


@pytest.mark.parametrize("environment", (Environment.PRODUCTION, Environment.TESTING))
def test_recovery_requires_identity_without_legacy_fallback(
    pg_client: TestClient,
    queries: list[str],
    monkeypatch: pytest.MonkeyPatch,
    environment: Environment,
) -> None:
    monkeypatch.setattr(settings, "ENV", environment)
    queries.clear()
    response = pg_client.get(f"/api/v1/operations/{uuid4()}")
    assert response.status_code == 503
    assert response.headers["Cache-Control"] == "no-store"
    assert not queries


@pytest.mark.parametrize("operation_id", ("invalid", str(uuid1())))
def test_recovery_rejects_non_v4_identifiers_without_reading_database(
    pg_client: TestClient, queries: list[str], operation_id: str
) -> None:
    queries.clear()
    response = pg_client.get(f"/api/v1/operations/{operation_id}")
    assert response.status_code == 422
    assert not queries


def test_openapi_describes_recovery_and_all_requested_error_codes(
    pg_client: TestClient,
) -> None:
    document = pg_client.get("/openapi.json").json()
    route = document["paths"]["/api/v1/operations/{operation_id}"]["get"]
    assert {"200", "404", "409", "503"} <= route["responses"].keys()
    assert len(route["parameters"]) == 1
    parameter = route["parameters"][0]
    assert parameter["name"] == "operation_id" and parameter["in"] == "path"
    assert parameter["required"] is True
    assert parameter["schema"]["format"] == "uuid4"
