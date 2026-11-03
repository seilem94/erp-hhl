"""Integration tests for the HTTP presentation layer."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.enums import ExpenseCategory, ProjectStatus
from src.infrastructure.http.dependencies import get_expense_repo, get_project_repo
from src.main import app
from tests.fakes import InMemoryExpenseRepository, InMemoryProjectRepository


@pytest.fixture
def project_repo() -> InMemoryProjectRepository:
    return InMemoryProjectRepository()


@pytest.fixture
def expense_repo() -> InMemoryExpenseRepository:
    return InMemoryExpenseRepository()


@pytest.fixture
def client(
    project_repo: InMemoryProjectRepository,
    expense_repo: InMemoryExpenseRepository,
) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_project_repo] = lambda: project_repo
    app.dependency_overrides[get_expense_repo] = lambda: expense_repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_project_success(client: TestClient) -> None:
    payload = {
        "name": "Instalación Tablero Central",
        "client": "Constructora Alerce",
        "estimated_budget": "5000000.00",
        "description": "Montaje de tableros TDA",
    }
    response = client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["client"] == payload["client"]
    assert data["status"] == ProjectStatus.PLANNING.value
    assert data["budget"] == payload["estimated_budget"]
    assert data["description"] == payload["description"]
    assert "id" in data


def test_update_project_success(
    client: TestClient, project_repo: InMemoryProjectRepository
) -> None:
    p = Project(
        id=uuid4(),
        name="Obra Antigua",
        client="Cliente Antiguo",
        status=ProjectStatus.PLANNING,
        start_date=date.today(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        budget=Decimal("500000.00"),
        description="Alcance original",
    )
    project_repo.save(p)

    payload = {
        "name": "Obra Nueva",
        "status": ProjectStatus.IN_PROGRESS.value,
        "estimated_budget": "750000.00",
        "description": "Alcance modificado",
    }
    response = client.patch(f"/api/v1/projects/{p.id}", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(p.id)
    assert data["name"] == "Obra Nueva"
    assert data["client"] == "Cliente Antiguo"  # Inalterado
    assert data["status"] == ProjectStatus.IN_PROGRESS.value
    assert data["budget"] == "750000.00"
    assert data["description"] == "Alcance modificado"


def test_update_project_not_found(client: TestClient) -> None:
    random_id = uuid4()
    payload = {"name": "No existe"}
    response = client.patch(f"/api/v1/projects/{random_id}", json=payload)
    assert response.status_code == 404
    assert str(random_id) in response.json()["detail"]


def test_list_projects(
    client: TestClient, project_repo: InMemoryProjectRepository
) -> None:
    p1 = Project(
        id=uuid4(),
        name="Obra 1",
        client="Cliente 1",
        status=ProjectStatus.PLANNING,
        start_date=date.today(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    p2 = Project(
        id=uuid4(),
        name="Obra 2",
        client="Cliente 2",
        status=ProjectStatus.IN_PROGRESS,
        start_date=date.today(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    project_repo.save(p1)
    project_repo.save(p2)

    # List all
    res_all = client.get("/api/v1/projects")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 2

    # Filter by status
    res_filtered = client.get(
        f"/api/v1/projects?status={ProjectStatus.IN_PROGRESS.value}"
    )
    assert res_filtered.status_code == 200
    data = res_filtered.json()
    assert len(data) == 1
    assert data[0]["id"] == str(p2.id)


def test_register_expense_success(
    client: TestClient, project_repo: InMemoryProjectRepository
) -> None:
    project = Project(
        id=uuid4(),
        name="Obra Eléctrica",
        client="Minera Norte",
        status=ProjectStatus.IN_PROGRESS,
        start_date=date.today(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    project_repo.save(project)

    payload = {
        "amount": "15000.50",
        "date": str(date.today()),
        "category": ExpenseCategory.MATERIALS.value,
        "description": "Cables libres de halógeno 4mm",
        "project_id": str(project.id),
        "receipt_url": "https://storage.example.com/receipts/01.pdf",
    }

    response = client.post("/api/v1/expenses", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == payload["amount"]
    assert data["category"] == ExpenseCategory.MATERIALS.value
    assert data["has_receipt"] is True
    assert data["receipt_url"] == payload["receipt_url"]
    assert data["project_id"] == str(project.id)


def test_register_expense_invalid_amount_returns_422(
    client: TestClient,
) -> None:
    payload = {
        "amount": "-50.00",
        "date": str(date.today()),
        "category": ExpenseCategory.FOOD.value,
        "description": "Colaciones",
    }
    response = client.post("/api/v1/expenses", json=payload)
    assert response.status_code == 422
    assert "Expense amount must be greater than zero" in response.json()["detail"]


def test_register_expense_future_date_returns_422(
    client: TestClient,
) -> None:
    tomorrow = date.today() + timedelta(days=1)
    payload = {
        "amount": "100.00",
        "date": str(tomorrow),
        "category": ExpenseCategory.TOOLS.value,
        "description": "Destornillador",
    }
    response = client.post("/api/v1/expenses", json=payload)
    assert response.status_code == 422
    assert "in the future" in response.json()["detail"]


def test_register_expense_project_not_found_returns_404(
    client: TestClient,
) -> None:
    random_id = uuid4()
    payload = {
        "amount": "100.00",
        "date": str(date.today()),
        "category": ExpenseCategory.TOOLS.value,
        "description": "Brocas",
        "project_id": str(random_id),
    }
    response = client.post("/api/v1/expenses", json=payload)
    assert response.status_code == 404
    assert str(random_id) in response.json()["detail"]


def test_register_expense_cancelled_project_returns_422(
    client: TestClient, project_repo: InMemoryProjectRepository
) -> None:
    project = Project(
        id=uuid4(),
        name="Obra Cancelada",
        client="Cliente Cancelado",
        status=ProjectStatus.CANCELLED,
        start_date=date.today(),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    project_repo.save(project)

    payload = {
        "amount": "200.00",
        "date": str(date.today()),
        "category": ExpenseCategory.SERVICES.value,
        "description": "Servicio grúa",
        "project_id": str(project.id),
    }
    response = client.post("/api/v1/expenses", json=payload)
    assert response.status_code == 422
    assert "cancelled" in response.json()["detail"]


def test_list_project_expenses_not_found(client: TestClient) -> None:
    random_id = uuid4()
    response = client.get(f"/api/v1/expenses/project/{random_id}")
    assert response.status_code == 404
    assert str(random_id) in response.json()["detail"]


def test_list_operational_expenses(
    client: TestClient, expense_repo: InMemoryExpenseRepository
) -> None:
    exp = Expense(
        id=uuid4(),
        amount=Decimal("30000"),
        date=date.today(),
        category=ExpenseCategory.TRANSPORT,
        description="Combustible camioneta",
        has_receipt=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        project_id=None,
    )
    expense_repo.save(exp)

    response = client.get("/api/v1/expenses/operational")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Combustible camioneta"
