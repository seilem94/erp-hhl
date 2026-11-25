"""Activity and expense edits through the HTTP and PostgreSQL transaction boundary."""

from datetime import date, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from src.infrastructure.database import session as database
from src.infrastructure.database.repositories.sqlalchemy_expense_repository import (
    SQLAlchemyExpenseRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from tests.infrastructure.postgres import migration_config

ACTOR_HEADER = "Cf-Access-Authenticated-User-Email"
AUDIT_PATH = "/api/v1/audit-logs"


def create_project(client: TestClient, name: str) -> str:
    response = client.post(
        "/api/v1/projects/", json={"name": name, "client": "Cliente"}
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def create_expense(client: TestClient, project_id: str | None = None) -> str:
    response = client.post(
        "/api/v1/expenses/",
        json={
            "project_id": project_id,
            "amount": "50000.00",
            "date": date.today().isoformat(),
            "category": "materials",
            "description": "Cableado",
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["id"])


def test_patch_moves_expense_updates_totals_and_audits_only_changed_fields(
    pg_client: TestClient,
) -> None:
    origin = create_project(pg_client, "Obra oriente")
    destination = create_project(pg_client, "Obra poniente")
    expense = create_expense(pg_client, origin)
    updated_date = (date.today() - timedelta(days=1)).isoformat()
    response = pg_client.patch(
        f"/api/gastos/{expense}",
        headers={ACTOR_HEADER: "terreno@example.test"},
        json={
            "amount": "65000.25",
            "date": updated_date,
            "description": "Cableado reforzado",
            "category": "services",
            "proyecto_id": destination,
            "receipt_url": "comprobantes/cableado.pdf",
        },
    )
    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated["project_id"] == destination
    assert updated["amount"] == "65000.25"
    assert updated["date"] == updated_date
    assert updated["has_receipt"] is True
    assert pg_client.get(f"/api/v1/expenses/project/{origin}").json() == []
    assert pg_client.get(f"/api/v1/expenses/project/{destination}").json() == [updated]
    for project_id, total in [(origin, "0.00"), (destination, "65000.25")]:
        summary = pg_client.get(f"/api/v1/projects/{project_id}/summary")
        assert summary.status_code == 200
        assert summary.json()["expenses_total"] == total
        activity = pg_client.get(
            "/api/auditoria",
            params={"proyecto_id": project_id, "entidad": "GASTO", "accion": "UPDATE"},
        )
        assert activity.status_code == 200, activity.text
        assert activity.headers["Cache-Control"] == "no-store"
        (log,) = activity.json()["items"]
        assert log["actor_email"] == "terreno@example.test"
        assert log["proyecto_nombre"] == "Obra poniente"
        assert log["entidad_id"] == expense
        assert datetime.fromisoformat(log["created_at"]).utcoffset() == timedelta(0)
        assert "monto $50.000 → $65.000,25" in log["resumen"]
        assert log["detalles"] == {
            "antes": {
                "amount": "50000.00",
                "date": date.today().isoformat(),
                "description": "Cableado",
                "category": "materials",
                "project_id": origin,
                "has_receipt": False,
                "receipt_url": None,
            },
            "despues": {
                "amount": "65000.25",
                "date": updated_date,
                "description": "Cableado reforzado",
                "category": "services",
                "project_id": destination,
                "has_receipt": True,
                "receipt_url": "comprobantes/cableado.pdf",
            },
        }

    to_opex = pg_client.patch(
        f"/api/v1/expenses/{expense}",
        json={"project_id": None, "receipt_url": None, "has_receipt": False},
    )
    assert to_opex.status_code == 200
    assert to_opex.json()["project_id"] is to_opex.json()["receipt_url"] is None
    assert to_opex.json()["has_receipt"] is False
    assert pg_client.get("/api/v1/expenses/operational").json() == [to_opex.json()]


def test_invalid_and_noop_patches_do_not_append_activity(pg_client: TestClient) -> None:
    expense = create_expense(pg_client)
    path = f"/api/v1/expenses/{expense}"
    (original,) = pg_client.get("/api/v1/expenses/operational").json()
    for body, status in (
        ({"amount": None}, 422),
        ({"amount": "25.123"}, 422),
        ({"description": "  "}, 422),
        ({"project_id": str(uuid4())}, 404),
    ):
        assert pg_client.patch(path, json=body).status_code == status
    assert pg_client.patch(f"/api/v1/expenses/{uuid4()}", json={}).status_code == 404
    assert pg_client.patch(path, json={"amount": "50000.0000"}).json() == original
    assert pg_client.get("/api/v1/expenses/operational").json() == [original]
    assert pg_client.get(AUDIT_PATH, params={"accion": "UPDATE"}).json()["items"] == []


def test_project_writes_keep_one_audit_event_per_effect_and_paginate(
    pg_client: TestClient,
) -> None:
    headers = {"Idempotency-Key": str(uuid4()), ACTOR_HEADER: "oficina@example.test"}
    body = {"name": "Obra", "client": "Cliente"}
    original = pg_client.post("/api/v1/projects/", headers=headers, json=body)
    assert original.status_code == 201
    project_id = original.json()["id"]
    replay = pg_client.post("/api/v1/projects/", headers=headers, json=body)
    assert replay.headers["Idempotency-Replayed"] == "true"

    patch_headers = {
        "Idempotency-Key": str(uuid4()),
        ACTOR_HEADER: "oficina@example.test",
    }
    payload = {"name": "Obra ampliada"}
    patch_path = f"/api/v1/projects/{project_id}"
    assert (
        pg_client.patch(patch_path, json=payload, headers=patch_headers).status_code
        == 200
    )
    replay = pg_client.patch(patch_path, json=payload, headers=patch_headers)
    assert replay.headers["Idempotency-Replayed"] == "true"
    assert pg_client.patch(patch_path, json=payload).status_code == 200

    params = {"proyecto_id": project_id, "limit": 1, "entidad": "PROYECTO"}
    first = pg_client.get(AUDIT_PATH, params=params).json()
    assert first["has_more"] is True
    (edited,) = first["items"]
    assert edited["accion"] == "UPDATE"
    assert edited["actor_email"] == "oficina@example.test"
    assert edited["detalles"] == {
        "antes": {"name": "Obra"},
        "despues": {"name": "Obra ampliada"},
    }
    second = pg_client.get(AUDIT_PATH, params={**params, "offset": 1}).json()
    assert second["has_more"] is False
    (created,) = second["items"]
    assert created["accion"] == "CREATE"
    assert created["detalles"]["antes"] is None
    assert (
        pg_client.get(AUDIT_PATH, params={"limit": 0, "offset": -1}).status_code == 422
    )


def test_repository_deletes_preserve_audit_history_after_project_is_removed(
    pg_client: TestClient,
    pg_engine: Engine,
) -> None:
    project_id = create_project(pg_client, "Obra retirada")
    expense_id = create_expense(pg_client, project_id)
    with Session(pg_engine) as session, session.begin():
        assert SQLAlchemyExpenseRepository(session).delete(UUID(expense_id))
        assert SQLAlchemyProjectRepository(session).delete(UUID(project_id))
    response = pg_client.get(AUDIT_PATH, params={"accion": "DELETE"})
    assert response.status_code == 200
    logs = {log["entidad_id"]: log for log in response.json()["items"]}
    assert logs.keys() == {project_id, expense_id}
    for event in logs.values():
        assert event["actor_email"] == "local@erp-hhl"
        assert event["proyecto_id"] is None
        assert event["detalles"]["despues"] is None
    assert logs[expense_id]["detalles"]["antes"]["project_id"] == project_id
    assert logs[project_id]["detalles"]["antes"]["name"] == "Obra retirada"


def test_failed_expense_commit_rolls_back_update_and_audit(
    pg_client: TestClient,
    pg_engine: Engine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expense = create_expense(pg_client)

    class FailingCommitSession(Session):
        def commit(self) -> None:
            raise RuntimeError("Forced commit failure")

    with monkeypatch.context() as context:
        context.setattr(
            database,
            "SessionLocal",
            sessionmaker(pg_engine, class_=FailingCommitSession),
        )
        response = pg_client.patch(
            f"/api/v1/expenses/{expense}", json={"amount": "25.00"}
        )
    assert response.status_code == 500
    (original,) = pg_client.get("/api/v1/expenses/operational").json()
    assert original["amount"] == "50000.00"
    assert pg_client.get(AUDIT_PATH, params={"accion": "UPDATE"}).json()["items"] == []


def test_audit_migration_reverses_without_removing_business_tables(
    pg_client: TestClient,
    pg_engine: Engine,
) -> None:
    project = create_project(pg_client, "Antigua")
    with pg_engine.begin() as connection:
        columns = inspect(connection)
        assert {index["name"] for index in columns.get_indexes("audit_logs")} == {
            "ix_audit_logs_actor_email",
            "ix_audit_logs_proyecto_id",
            "ix_audit_logs_entidad_id",
            "ix_audit_logs_created_at_id",
        }
        config = migration_config(connection)
        command.downgrade(config, "b528c7394d01")
        assert not inspect(connection).has_table("audit_logs")
        command.upgrade(config, "head")
        assert inspect(connection).has_table("audit_logs")
    assert pg_client.get("/api/v1/projects/").json()[0]["id"] == project
    assert pg_client.get(AUDIT_PATH).json() == {"items": [], "has_more": False}
