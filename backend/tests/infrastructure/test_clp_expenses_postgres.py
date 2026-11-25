"""Test the CLP migration and the published expense contracts on PostgreSQL."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from alembic import command
from src.domain.enums import CommandType, Currency, ExpenseCategory
from src.infrastructure.database.models import AuditLogORM, OperationORM
from src.use_cases.services.canonicalization import (
    CanonicalRequest,
    SHA256RequestCanonicalizer,
)
from src.use_cases.services.monetary_precision import MAX_CLP
from tests.infrastructure.postgres import migration_config


def test_clp_migration_preserves_rows_and_renames_the_expense_title(
    pg_engine: Engine,
) -> None:
    project_id, first_id, second_id = uuid4(), uuid4(), uuid4()
    title = " Cableado de la obra — anotación original "
    with pg_engine.begin() as connection:
        config = migration_config(connection)
        command.downgrade(config, "3845a60b9d12")
        connection.execute(
            text(
                "INSERT INTO projects (id, name, client, status, start_date, "
                "created_at, updated_at, budget) VALUES "
                "(:id, 'Obra', 'Cliente', 'planning', CURRENT_DATE, "
                "NOW(), NOW(), :budget)"
            ),
            {"id": project_id, "budget": Decimal("2300000000.50")},
        )
        connection.execute(
            text(
                "INSERT INTO expenses (id, amount, date, category, description, "
                "has_receipt, created_at, updated_at, project_id) VALUES "
                "(:id, :amount, CURRENT_DATE, 'materials', :title, "
                ":receipt, NOW(), NOW(), :project_id)"
            ),
            [
                {
                    "id": first_id,
                    "amount": Decimal("631809.50"),
                    "title": title,
                    "receipt": True,
                    "project_id": project_id,
                },
                {
                    "id": second_id,
                    "amount": Decimal("0.49"),
                    "title": "OPEX",
                    "receipt": False,
                    "project_id": None,
                },
            ],
        )

        command.upgrade(config, "head")
        rows = {
            row.id: (row.amount, row.title, row.detail, row.has_receipt, row.project_id)
            for row in connection.execute(
                text(
                    "SELECT id, amount, title, detail, has_receipt, project_id "
                    "FROM expenses"
                )
            )
        }
        assert rows == {
            first_id: (631810, title, None, True, project_id),
            second_id: (0, "OPEX", None, False, None),
        }
        assert connection.scalar(text("SELECT budget FROM projects")) == 2_300_000_001
        assert {
            column["name"] for column in inspect(connection).get_columns("expenses")
        } >= {"title", "detail"}
        command.downgrade(config, "3845a60b9d12")
        restored = connection.execute(
            text("SELECT description, amount FROM expenses WHERE id = :id"),
            {"id": first_id},
        ).one()
        assert restored.description == title
        assert restored.amount == Decimal("631810.00")
        command.upgrade(config, "head")


def test_spanish_routes_edit_title_detail_and_receipt_and_audit_whole_clp(
    pg_client: TestClient,
) -> None:
    created = pg_client.post(
        "/api/gastos",
        json={
            "monto": 1_250_000,
            "fecha": date.today().isoformat(),
            "categoria": "materials",
            "titulo": "Compra cable EVA",
            "detalle": " Incluye factura de materiales. ",
            "tiene_comprobante": True,
        },
    )
    assert created.status_code == 201, created.text
    expense = created.json()
    assert expense["monto"] == "1250000"
    assert expense["titulo"] == "Compra cable EVA"
    assert expense["detalle"] == "Incluye factura de materiales."
    assert expense["tiene_comprobante"] is True
    assert expense["receipt_url"] is None

    updated = pg_client.patch(
        f"/api/gastos/{expense['id']}",
        json={
            "monto": 2_500_000_000,
            "titulo": "Compra de materiales",
            "detalle": None,
        },
    )
    assert updated.status_code == 200, updated.text
    current = updated.json()
    assert current["monto"] == "2500000000"
    assert current["titulo"] == "Compra de materiales"
    assert current["detalle"] is None
    assert current["tiene_comprobante"] is True
    assert pg_client.get("/api/gastos").json() == [current]
    (canonical,) = pg_client.get("/api/v1/expenses/").json()
    assert canonical["title"] == canonical["description"] == current["titulo"]
    assert canonical["has_receipt"] is True

    logs = pg_client.get("/api/v1/audit-logs", params={"entidad": "GASTO"}).json()[
        "items"
    ]
    edited, registered = logs
    assert registered["detalles"]["despues"]["has_receipt"] is True
    assert edited["detalles"] == {
        "antes": {
            "amount": "1250000",
            "title": "Compra cable EVA",
            "detail": "Incluye factura de materiales.",
        },
        "despues": {
            "amount": "2500000000",
            "title": "Compra de materiales",
            "detail": None,
        },
    }
    assert (
        "«Compra de materiales» (monto $1.250.000 → $2.500.000.000" in edited["resumen"]
    )


@pytest.mark.parametrize("amount", ("2500000.01", 1.5, 1.0, True, 0, -1, MAX_CLP + 1))
def test_new_expenses_reject_fractional_invalid_and_out_of_range_clp(
    pg_client: TestClient, amount: object
) -> None:
    response = pg_client.post(
        "/api/v1/expenses/",
        json={
            "amount": amount,
            "date": date.today().isoformat(),
            "category": "materials",
            "title": "Cable",
        },
    )
    assert response.status_code == 422
    assert pg_client.get("/api/gastos").json() == []


def test_project_budgets_round_trip_as_exact_whole_pesos(pg_client: TestClient) -> None:
    created = pg_client.post(
        "/api/v1/projects/",
        json={"name": "Obra", "client": "Cliente", "presupuesto_estimado": MAX_CLP},
    )
    assert created.status_code == 201, created.text
    assert created.json()["budget"] == str(MAX_CLP)
    url = f"/api/v1/projects/{created.json()['id']}"
    assert (
        pg_client.patch(url, json={"estimated_budget": "2500000.10"}).status_code == 422
    )
    assert pg_client.patch(url, json={"estimated_budget": -1}).status_code == 422
    response = pg_client.patch(url, json={"estimated_budget": 0})
    assert response.status_code == 200
    assert response.json()["budget"] == "0"


def test_legacy_expense_confirmation_can_be_replayed_with_its_original_key(
    pg_client: TestClient, pg_engine: Engine
) -> None:
    operation_id = uuid4()
    headers = {"Idempotency-Key": str(operation_id)}
    today = date.today()
    request = {
        "amount": "1250000.00",
        "date": today.isoformat(),
        "category": "materials",
        "description": "Cable del historial",
    }
    original = pg_client.post("/api/v1/expenses/", headers=headers, json=request)
    assert original.status_code == 201
    assert original.json()["has_receipt"] is False
    expected = SHA256RequestCanonicalizer().fingerprint(
        CanonicalRequest(
            command_type=CommandType.REGISTER_EXPENSE,
            content={
                "amount": Decimal("1250000.00"),
                "date": today,
                "category": ExpenseCategory.MATERIALS,
                "description": "Cable del historial",
                "project_id": None,
                "has_receipt": False,
                "receipt_url": None,
                "currency": Currency.CLP,
            },
        )
    )
    with Session(pg_engine) as session, session.begin():
        record = session.scalars(select(OperationORM)).one()
        assert record.request_fingerprint == expected.digest
        assert record.result_payload is not None
        payload = dict(record.result_payload)
        payload["description"] = payload.pop("title")
        payload.pop("detail")
        payload["amount"] = "1250000.00"
        record.result_payload = payload
        record.result_schema_version = 1

    replay = pg_client.post("/api/v1/expenses/", headers=headers, json=request)
    assert replay.headers["Idempotency-Replayed"] == "true"
    assert replay.json() == original.json()
    different_detail = pg_client.post(
        "/api/v1/expenses/", headers=headers, json={**request, "detail": "Otro detalle"}
    )
    assert different_detail.status_code == 409
    assert len(pg_client.get("/api/gastos").json()) == 1
    with Session(pg_engine) as session:
        assert session.scalar(select(OperationORM.result_payload)) == payload


def test_legacy_audit_summaries_show_whole_pesos_without_rewriting_the_diff(
    pg_client: TestClient, pg_engine: Engine
) -> None:
    original = "Actualizó gasto «Cable $12,34» (monto $631.809,50 → $1.250.000,25)"
    changes = {"antes": {"amount": "631809.50"}, "despues": {"amount": "1250000.25"}}
    with Session(pg_engine) as session, session.begin():
        session.add(
            AuditLogORM(
                id=uuid4(),
                created_at=datetime.now(UTC),
                actor_email="local@erp-hhl",
                accion="UPDATE",
                entidad="GASTO",
                entidad_id=str(uuid4()),
                resumen=original,
                detalles=changes,
            )
        )
    (event,) = pg_client.get("/api/auditoria").json()["items"]
    assert (
        event["resumen"]
        == "Actualizó gasto «Cable $12,34» (monto $631.810 → $1.250.000)"
    )
    assert event["detalles"] == changes
    with Session(pg_engine) as session:
        assert session.scalar(select(AuditLogORM.resumen)) == original
