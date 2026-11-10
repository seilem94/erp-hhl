"""Real HTTP command transactions, using the production yield dependency.

Only SessionLocal is replaced with an isolated PostgreSQL factory. In particular,
the commit-failure tests must not replace get_db or bypass its dependency scope.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, date, datetime, timedelta
from threading import Event
from typing import Literal
from uuid import UUID, uuid1, uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import func, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core.config import Environment, settings
from src.domain.entities.operation import OperationRecord
from src.domain.entities.project import Project
from src.domain.enums import CommandType, ProjectStatus
from src.domain.exceptions import AuthorizationDeniedError
from src.domain.repositories.operation_repository import OperationRepository
from src.infrastructure.database import session as database
from src.infrastructure.database.models import ExpenseORM, OperationORM, ProjectORM
from src.infrastructure.database.repositories.sqlalchemy_operation_repository import (
    SQLAlchemyOperationRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from src.infrastructure.http.dependencies import (
    SessionDep,
    get_authorization,
    get_identity_provider,
    get_operation_repo,
)
from src.infrastructure.http.schemas.project import ProjectResponse
from src.infrastructure.identity.providers import (
    DEVELOPMENT_ACTOR_ID,
    DevelopmentAuthorization,
    UnavailableIdentityProvider,
)
from src.main import app
from src.use_cases.ports.identity import ActorIdentity

Kind = Literal["project", "expense", "update"]
KINDS = ("project", "expense", "update")


def seed_project(engine: Engine) -> UUID:
    project_id = uuid4()
    now = datetime.now(UTC)
    with Session(engine) as session:
        session.add(
            ProjectORM(
                id=project_id,
                name="Obra original",
                client="Cliente",
                status=ProjectStatus.PLANNING.value,
                start_date=now.date(),
                created_at=now,
                updated_at=now,
                has_iva=True,
            )
        )
        session.commit()
    return project_id


def payload(kind: Kind, project_id: UUID) -> dict[str, str | None]:
    if kind == "project":
        return {"name": "Obra nueva", "client": "Cliente", "estimated_budget": "0.10"}
    if kind == "expense":
        return {
            "amount": "0.10",
            "date": date.today().isoformat(),
            "category": "materials",
            "description": "Cable",
            "project_id": str(project_id),
        }
    return {"name": "Nombre editado", "status": "in_progress"}


def send_command(
    client: TestClient,
    kind: Kind,
    project_id: UUID,
    data: dict[str, str | None],
    key: str | None,
    *,
    slash: bool = False,
) -> Response:
    headers = {} if key is None else {"Idempotency-Key": key}
    if kind == "update":
        return client.patch(
            f"/api/v1/projects/{project_id}", json=data, headers=headers
        )
    path = "/api/v1/projects" if kind == "project" else "/api/v1/expenses"
    return client.post(path + ("/" if slash else ""), json=data, headers=headers)


def counts(engine: Engine) -> tuple[int, int, int]:
    with Session(engine) as session:
        return (
            session.execute(select(func.count()).select_from(ProjectORM)).scalar_one(),
            session.execute(select(func.count()).select_from(ExpenseORM)).scalar_one(),
            session.execute(
                select(func.count()).select_from(OperationORM)
            ).scalar_one(),
        )


@pytest.fixture
def client(pg_client: TestClient) -> TestClient:
    return pg_client


@pytest.mark.parametrize("kind", KINDS)
def test_command_replays_original_response_and_commits_both_records(
    client: TestClient, pg_engine: Engine, kind: Kind
) -> None:
    project_id, key = seed_project(pg_engine), str(uuid4())
    data = payload(kind, project_id)
    first = send_command(client, kind, project_id, data, key)
    replay = send_command(
        client, kind, project_id, dict(reversed(data.items())), key, slash=True
    )
    assert first.status_code == replay.status_code == (200 if kind == "update" else 201)
    assert first.headers["Idempotency-Replayed"] == "false"
    assert replay.headers["Idempotency-Replayed"] == "true"
    assert replay.json() == first.json()
    with Session(pg_engine) as session:
        record = session.get(OperationORM, (DEVELOPMENT_ACTOR_ID, UUID(key)))
        assert record is not None and record.state == "confirmed"
        assert str(record.result_resource_id) == first.json()["id"]
        assert record.result_payload is not None
        assert record.result_payload["updated_at"] == first.json()["updated_at"]
        if kind == "update":
            # The transitional tax classification survives the existing mapper.
            assert session.get(ProjectORM, project_id).has_iva is True
    assert counts(pg_engine) == (
        2 if kind == "project" else 1,
        1 if kind == "expense" else 0,
        1,
    )


@pytest.mark.parametrize("kind", ("project", "expense"))
def test_preassigned_resource_identity_is_distinct_and_replayed(
    client: TestClient, pg_engine: Engine, kind: Kind
) -> None:
    project_id, resource_id, key = seed_project(pg_engine), uuid4(), str(uuid4())
    data = {**payload(kind, project_id), "id": str(resource_id)}
    first = send_command(client, kind, project_id, data, key)
    second = send_command(client, kind, project_id, data, key)
    assert first.status_code == second.status_code == 201
    assert first.json() == second.json()
    assert first.json()["id"] == str(resource_id) != key
    with Session(pg_engine) as session:
        operation = session.get(OperationORM, (DEVELOPMENT_ACTOR_ID, UUID(key)))
        assert (
            operation.target_resource_id == operation.result_resource_id == resource_id
        )


@pytest.mark.parametrize("kind", ("project", "expense"))
def test_different_operation_cannot_overwrite_occupied_resource_identity(
    client: TestClient, pg_engine: Engine, kind: Kind
) -> None:
    project_id = seed_project(pg_engine)
    data = {**payload(kind, project_id), "id": str(uuid4())}
    first = send_command(client, kind, project_id, data, str(uuid4()))
    second_key = str(uuid4())
    conflict = send_command(client, kind, project_id, data, second_key)
    assert first.status_code == 201
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "resource_identity_conflict"
    with Session(pg_engine) as session:
        assert (
            session.get(OperationORM, (DEVELOPMENT_ACTOR_ID, UUID(second_key))) is None
        )
    assert counts(pg_engine)[2] == 1


@pytest.mark.parametrize("kind", KINDS)
def test_legacy_without_key_does_not_resolve_identity_or_reserve(
    client: TestClient, pg_engine: Engine, monkeypatch: pytest.MonkeyPatch, kind: Kind
) -> None:
    monkeypatch.setattr(settings, "ENV", Environment.PRODUCTION)

    def unexpected_identity(self: UnavailableIdentityProvider) -> ActorIdentity:
        raise AssertionError("A legacy write must not resolve an identity")

    monkeypatch.setattr(UnavailableIdentityProvider, "get_actor", unexpected_identity)
    project_id = seed_project(pg_engine)
    data = payload(kind, project_id)
    first = send_command(client, kind, project_id, data, None)
    second = send_command(client, kind, project_id, data, None)
    assert first.status_code == second.status_code == (200 if kind == "update" else 201)
    assert "Idempotency-Replayed" not in first.headers
    if kind != "update":
        assert first.json()["id"] != second.json()["id"]
    assert counts(pg_engine)[2] == 0


@pytest.mark.parametrize("kind", KINDS)
def test_valid_key_without_identity_uses_legacy_without_deduplication(
    client: TestClient, pg_engine: Engine, monkeypatch: pytest.MonkeyPatch, kind: Kind
) -> None:
    monkeypatch.setattr(settings, "ENV", Environment.PRODUCTION)
    project_id, key = seed_project(pg_engine), str(uuid4())
    data = payload(kind, project_id)
    first = send_command(client, kind, project_id, data, key)
    second = send_command(client, kind, project_id, data, key)
    assert first.status_code == second.status_code == (200 if kind == "update" else 201)
    assert "Idempotency-Replayed" not in first.headers
    assert "Idempotency-Replayed" not in second.headers
    if kind != "update":
        assert first.json()["id"] != second.json()["id"]
    assert counts(pg_engine)[2] == 0


@pytest.mark.parametrize("with_key", (False, True))
def test_resource_id_is_not_honored_when_using_legacy_compatibility(
    client: TestClient,
    pg_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
    with_key: bool,
) -> None:
    monkeypatch.setattr(settings, "ENV", Environment.PRODUCTION)
    resource_id = uuid4()
    response = client.post(
        "/api/v1/projects",
        json={"id": str(resource_id), "name": "Obra", "client": "Cliente"},
        headers={"Idempotency-Key": str(uuid4())} if with_key else {},
    )
    assert response.status_code == 201
    assert response.json()["id"] != str(resource_id)
    assert counts(pg_engine) == (1, 0, 0)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("key", ("invalid", "", str(uuid1())))
def test_invalid_idempotency_keys_are_rejected_before_any_write(
    client: TestClient, pg_engine: Engine, kind: Kind, key: str
) -> None:
    project_id = seed_project(pg_engine)
    response = send_command(client, kind, project_id, payload(kind, project_id), key)
    assert response.status_code == 422
    assert counts(pg_engine) == (1, 0, 0)


@pytest.mark.parametrize("change", ("body", "resource", "command", "target"))
def test_same_key_with_different_intent_returns_conflict_without_an_effect(
    client: TestClient, pg_engine: Engine, change: str
) -> None:
    project_id, other_id, key = (
        seed_project(pg_engine),
        seed_project(pg_engine),
        str(uuid4()),
    )
    kind: Kind = "update" if change == "target" else "project"
    data = payload(kind, project_id)
    original = send_command(client, kind, project_id, data, key)
    expected_counts = counts(pg_engine)
    if change == "body":
        data["name"] = "Otra intención"
    elif change == "resource":
        data["id"] = str(uuid4())
    elif change == "command":
        kind, data = "expense", payload("expense", project_id)
    else:
        project_id = other_id
    conflict = send_command(client, kind, project_id, data, key)
    assert original.status_code in (200, 201)
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "idempotency_conflict"
    assert counts(pg_engine) == expected_counts


def test_creation_replay_returns_snapshot_after_update_and_resource_deletion(
    client: TestClient, pg_engine: Engine
) -> None:
    data, key = {"name": "Obra", "client": "Cliente"}, str(uuid4())
    original = client.post(
        "/api/v1/projects", json=data, headers={"Idempotency-Key": key}
    )
    project_id = UUID(original.json()["id"])
    assert (
        client.patch(
            f"/api/v1/projects/{project_id}", json={"name": "Posterior"}
        ).status_code
        == 200
    )
    replay = client.post(
        "/api/v1/projects/", json=data, headers={"Idempotency-Key": key}
    )
    assert replay.json() == original.json()
    with Session(pg_engine) as session:
        assert session.get(ProjectORM, project_id).name == "Posterior"
        assert SQLAlchemyProjectRepository(session).delete(project_id)
        session.commit()
    after_delete = client.post(
        "/api/v1/projects", json=data, headers={"Idempotency-Key": key}
    )
    assert after_delete.status_code == 201
    assert after_delete.json() == original.json()
    assert counts(pg_engine) == (0, 0, 1)


def test_patch_replay_does_not_reapply_an_old_status_or_timestamp(
    client: TestClient, pg_engine: Engine
) -> None:
    project_id, key = seed_project(pg_engine), str(uuid4())
    data = payload("update", project_id)
    original = send_command(client, "update", project_id, data, key)
    newer = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"status": "completed"},
        headers={"Idempotency-Key": str(uuid4())},
    )
    replay = send_command(client, "update", project_id, data, key)
    assert newer.status_code == replay.status_code == 200
    assert replay.json() == original.json()
    with Session(pg_engine) as session:
        current = session.get(ProjectORM, project_id)
        assert current.status == "completed"
        assert (
            current.updated_at.isoformat().replace("+00:00", "Z")
            == newer.json()["updated_at"]
        )


def test_expense_replay_does_not_revalidate_changed_business_state(
    client: TestClient, pg_engine: Engine
) -> None:
    project_id, key = seed_project(pg_engine), str(uuid4())
    data = payload("expense", project_id)
    original = send_command(client, "expense", project_id, data, key)
    assert (
        client.patch(
            f"/api/v1/projects/{project_id}", json={"status": "cancelled"}
        ).status_code
        == 200
    )
    replay = send_command(client, "expense", project_id, data, key)
    assert original.status_code == replay.status_code == 201
    assert original.json() == replay.json()
    assert counts(pg_engine) == (1, 1, 1)


@pytest.mark.parametrize("kind", KINDS)
def test_decimal_scale_and_optional_nulls_keep_the_same_intent(
    client: TestClient, pg_engine: Engine, kind: Kind
) -> None:
    project_id, key = seed_project(pg_engine), str(uuid4())
    data = payload(kind, project_id)
    money = "amount" if kind == "expense" else "estimated_budget"
    data[money] = "1500.50"
    original = send_command(client, kind, project_id, data, key)
    data[money] = "1500.5000"
    data["receipt_url" if kind == "expense" else "description"] = None
    replay = send_command(client, kind, project_id, data, key)
    assert (
        replay.status_code == original.status_code == (200 if kind == "update" else 201)
    )
    assert replay.json() == original.json()
    assert replay.headers["Idempotency-Replayed"] == "true"


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("amount", ("0.001", "10000000000", "NaN"))
def test_idempotent_money_is_rejected_instead_of_rounded_or_overflowed(
    client: TestClient, pg_engine: Engine, kind: Kind, amount: str
) -> None:
    project_id = seed_project(pg_engine)
    data = payload(kind, project_id)
    data["amount" if kind == "expense" else "estimated_budget"] = amount
    response = send_command(client, kind, project_id, data, str(uuid4()))
    assert response.status_code == 422
    assert counts(pg_engine) == (1, 0, 0)


@pytest.mark.parametrize("failure", ("amount", "date", "missing", "cancelled"))
def test_business_failure_rolls_back_reservation_and_allows_a_corrected_request(
    client: TestClient, pg_engine: Engine, failure: str
) -> None:
    project_id, key = seed_project(pg_engine), str(uuid4())
    valid = payload("expense", project_id)
    invalid = valid.copy()
    if failure == "amount":
        invalid["amount"] = "-1.00"
    elif failure == "date":
        invalid["date"] = (date.today() + timedelta(days=1)).isoformat()
    elif failure == "missing":
        invalid["project_id"] = str(uuid4())
    else:
        client.patch(f"/api/v1/projects/{project_id}", json={"status": "cancelled"})
    failed = send_command(client, "expense", project_id, invalid, key)
    assert failed.status_code == (404 if failure == "missing" else 422)
    assert counts(pg_engine) == (1, 0, 0)
    if failure == "cancelled":
        client.patch(f"/api/v1/projects/{project_id}", json={"status": "in_progress"})
    fixed = send_command(client, "expense", project_id, valid, key)
    assert fixed.status_code == 201
    assert fixed.headers["Idempotency-Replayed"] == "false"
    assert counts(pg_engine) == (1, 1, 1)


@pytest.mark.parametrize("mutation", ("purged", "schema", "fingerprint", "corrupt"))
def test_unrecoverable_known_operation_never_executes_again(
    client: TestClient, pg_engine: Engine, mutation: str
) -> None:
    key, project_id = str(uuid4()), uuid4()
    data = payload("project", project_id)
    assert send_command(client, "project", project_id, data, key).status_code == 201
    values: dict[str, object] = {
        "purged": {"result_payload": None},
        "schema": {"result_schema_version": 99},
        "fingerprint": {"fingerprint_version": 99},
        "corrupt": {"result_payload": {"invalid": "snapshot"}},
    }[mutation]
    with Session(pg_engine) as session:
        session.execute(update(OperationORM).values(**values))
        session.commit()
    response = send_command(client, "project", project_id, data, key)
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "operation_reconciliation_required"
    assert counts(pg_engine) == (1, 0, 1)


class CommandPolicy(DevelopmentAuthorization):
    def __init__(self) -> None:
        self.allow_command = True
        self.allow_result = True
        self.project_id: UUID | None = None

    def authorize_command(
        self,
        actor: ActorIdentity,
        command_type: CommandType,
        target_resource_id: UUID | None,
        *,
        project_id: UUID | None = None,
    ) -> None:
        super().authorize_command(
            actor, command_type, target_resource_id, project_id=project_id
        )
        self.project_id = project_id
        if not self.allow_command:
            raise AuthorizationDeniedError("Current command access denied.")

    def authorize_operation_result(
        self, actor: ActorIdentity, operation: OperationRecord
    ) -> None:
        super().authorize_operation_result(actor, operation)
        if not self.allow_result:
            raise AuthorizationDeniedError("Current result access denied.")


@pytest.mark.parametrize("deny", ("command", "result"))
def test_authorization_denial_does_not_degrade_or_leave_a_successful_operation(
    client: TestClient, pg_engine: Engine, deny: str
) -> None:
    policy = CommandPolicy()
    app.dependency_overrides[get_authorization] = lambda: policy
    project_id, key = seed_project(pg_engine), str(uuid4())
    data = payload("expense", project_id)
    setattr(policy, "allow_" + deny, False)
    denied = send_command(client, "expense", project_id, data, key)
    assert denied.status_code == 403
    assert counts(pg_engine) == (1, 0, 0)
    assert policy.project_id == project_id
    policy.allow_command = policy.allow_result = True
    original = send_command(client, "expense", project_id, data, key)
    assert original.status_code == 201
    setattr(policy, "allow_" + deny, False)
    revoked = send_command(client, "expense", project_id, data, key)
    assert revoked.status_code == 403
    assert counts(pg_engine) == (1, 1, 1)


class CaptureResponseStart:
    def __init__(self, application: ASGIApp) -> None:
        self.app = application
        self.statuses: list[int] = []

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def capture(message: Message) -> None:
            if message["type"] == "http.response.start":
                self.statuses.append(message["status"])
            await send(message)

        await self.app(scope, receive, capture)


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("idempotent", (False, True))
def test_failed_dependency_commit_never_sends_http_success_and_rolls_back(
    client: TestClient,
    pg_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
    kind: Kind,
    idempotent: bool,
) -> None:
    project_id = seed_project(pg_engine)
    data = payload(kind, project_id)
    key = str(uuid4()) if idempotent else None
    lifecycle: list[str] = []

    class FailingCommitSession(Session):
        def commit(self) -> None:
            lifecycle.append("commit")
            raise RuntimeError("Forced dependency commit failure")

        def rollback(self) -> None:
            lifecycle.append("rollback")
            super().rollback()

    monkeypatch.setattr(
        database, "SessionLocal", sessionmaker(pg_engine, class_=FailingCommitSession)
    )
    captured = CaptureResponseStart(app)
    with TestClient(captured, raise_server_exceptions=False) as failing_client:
        response = send_command(failing_client, kind, project_id, data, key)
    assert response.status_code == 500
    assert captured.statuses == [500]  # No 200/201 was sent before teardown failed.
    assert lifecycle == ["commit", "rollback"]
    assert counts(pg_engine) == (1, 0, 0)
    with Session(pg_engine) as session:
        assert session.get(ProjectORM, project_id).name == "Obra original"
    monkeypatch.setattr(
        database, "SessionLocal", sessionmaker(pg_engine, autoflush=False)
    )
    retry = send_command(client, kind, project_id, data, key)
    assert retry.status_code == (200 if kind == "update" else 201)
    assert counts(pg_engine)[2] == (1 if idempotent else 0)


def test_lost_commit_ack_returns_error_and_retry_recovers_committed_snapshot(
    client: TestClient, pg_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    key, project_id = str(uuid4()), uuid4()
    data = payload("project", project_id)

    class LostCommitAcknowledgement(Session):
        def commit(self) -> None:
            super().commit()
            raise RuntimeError("Simulated loss after the database committed")

    monkeypatch.setattr(
        database,
        "SessionLocal",
        sessionmaker(pg_engine, class_=LostCommitAcknowledgement),
    )
    first = send_command(client, "project", project_id, data, key)
    assert first.status_code == 500
    assert counts(pg_engine) == (1, 0, 1)
    monkeypatch.setattr(
        database, "SessionLocal", sessionmaker(pg_engine, autoflush=False)
    )
    retry = send_command(client, "project", project_id, data, key)
    assert retry.status_code == 201
    assert retry.headers["Idempotency-Replayed"] == "true"
    assert counts(pg_engine) == (1, 0, 1)


def test_response_construction_failure_rolls_back_business_and_confirmation(
    client: TestClient, pg_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    def invalid_response(*args: object, **kwargs: object) -> ProjectResponse:
        raise ValueError("Forced response construction failure")

    monkeypatch.setattr(ProjectResponse, "model_validate", invalid_response)
    response = client.post(
        "/api/v1/projects",
        json={"name": "Obra", "client": "Cliente"},
        headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 500
    assert counts(pg_engine) == (0, 0, 0)


def test_operation_namespace_uses_server_identity_and_ignores_client_actor(
    client: TestClient, pg_engine: Engine
) -> None:
    class ServerIdentity:
        def __init__(self) -> None:
            self.actor = ActorIdentity(actor_id=uuid4())

        def get_actor(self) -> ActorIdentity:
            return self.actor

    class ActorPolicy(DevelopmentAuthorization):
        def _check_actor(self, actor: ActorIdentity) -> None:
            if actor != identity.actor:
                raise AuthorizationDeniedError("Not the current server actor.")

    identity = ServerIdentity()
    first_actor = identity.actor.actor_id
    app.dependency_overrides[get_identity_provider] = lambda: identity
    app.dependency_overrides[get_authorization] = ActorPolicy
    key = str(uuid4())
    data = {"name": "Obra", "client": "Cliente", "actor_id": str(uuid4())}
    first = client.post(
        "/api/v1/projects",
        json=data,
        headers={"Idempotency-Key": key, "X-Actor-Id": data["actor_id"]},
    )
    identity.actor = ActorIdentity(actor_id=uuid4())
    second = client.post(
        "/api/v1/projects", json=data, headers={"Idempotency-Key": key}
    )
    replay = client.post(
        "/api/v1/projects", json=data, headers={"Idempotency-Key": key}
    )
    assert first.status_code == second.status_code == replay.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    assert second.json() == replay.json()
    with Session(pg_engine) as session:
        actors = set(session.scalars(select(OperationORM.actor_id)))
        assert actors == {first_actor, identity.actor.actor_id}
    assert counts(pg_engine) == (2, 0, 2)


def test_openapi_keeps_headers_and_resource_identity_optional(
    client: TestClient,
) -> None:
    document = client.get("/openapi.json").json()
    operations = (
        document["paths"]["/api/v1/projects/"]["post"],
        document["paths"]["/api/v1/expenses/"]["post"],
        document["paths"]["/api/v1/projects/{project_id}"]["patch"],
    )
    for operation in operations:
        header = next(
            item
            for item in operation["parameters"]
            if item["name"] == "Idempotency-Key"
        )
        assert header["in"] == "header" and header["required"] is False
        assert any(item.get("format") == "uuid4" for item in header["schema"]["anyOf"])
        assert {"403", "409", "503"} <= operation["responses"].keys()
        success = operation["responses"].get("201", operation["responses"].get("200"))
        assert "Idempotency-Replayed" in success["headers"]
    for schema in ("CreateProjectRequest", "RegisterExpenseRequest"):
        assert "id" not in document["components"]["schemas"][schema]["required"]


def test_web_client_can_read_the_idempotency_indicator_via_cors(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/projects",
        json={"name": "Obra", "client": "Cliente"},
        headers={"Idempotency-Key": str(uuid4()), "Origin": "http://localhost:5173"},
    )
    assert response.status_code == 201
    assert response.headers["Idempotency-Replayed"] == "false"
    assert "Idempotency-Replayed" in response.headers["Access-Control-Expose-Headers"]


def test_concurrent_http_requests_have_one_effect_and_a_recoverable_loser(
    client: TestClient, pg_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    entered, release = Event(), Event()
    save = SQLAlchemyProjectRepository.save
    calls: list[UUID] = []

    def hold_winner(self: SQLAlchemyProjectRepository, project: Project) -> Project:
        saved = save(self, project)
        calls.append(saved.id)
        entered.set()
        assert release.wait(10), "Winner was not released"
        return saved

    def short_reservation(session: SessionDep) -> OperationRepository:
        return SQLAlchemyOperationRepository(session, lock_timeout_ms=150)

    monkeypatch.setattr(SQLAlchemyProjectRepository, "save", hold_winner)
    app.dependency_overrides[get_operation_repo] = short_reservation
    project_id, key = uuid4(), str(uuid4())
    data = payload("project", project_id)
    with ThreadPoolExecutor(max_workers=2) as executor:
        winner = executor.submit(send_command, client, "project", project_id, data, key)
        try:
            assert entered.wait(10), "Winner never reserved the operation"
            loser = executor.submit(
                send_command, client, "project", project_id, data, key
            ).result(timeout=10)
            assert loser.status_code == 503
            assert loser.json()["detail"]["code"] == "operation_unresolved"
            assert counts(pg_engine) == (0, 0, 0)
        finally:
            release.set()
        first = winner.result(timeout=10)
    assert first.status_code == 201
    replay = send_command(client, "project", project_id, data, key)
    assert (
        replay.status_code == 201 and replay.headers["Idempotency-Replayed"] == "true"
    )
    assert replay.json() == first.json()
    assert len(calls) == 1
    assert counts(pg_engine) == (1, 0, 1)
