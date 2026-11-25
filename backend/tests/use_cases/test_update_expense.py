"""Partial updates preserve untouched fields and enforce expense rules."""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from uuid import uuid4

import pytest

from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.enums import ExpenseCategory, ProjectStatus
from src.domain.exceptions import (
    ExpenseNotFoundError,
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
    InvalidMonetaryPrecisionError,
    ProjectCancelledError,
    ProjectNotFoundError,
)
from src.use_cases.update_expense import UpdateExpenseDTO, UpdateExpenseUseCase
from tests.fakes import InMemoryExpenseRepository, InMemoryProjectRepository

TODAY = date(2026, 11, 25)
REGISTERED_AT = datetime(2026, 11, 10, tzinfo=UTC)


@pytest.fixture
def setup() -> tuple[UpdateExpenseUseCase, Expense, InMemoryProjectRepository]:
    expenses = InMemoryExpenseRepository()
    projects = InMemoryProjectRepository()
    project = projects.save(
        Project(
            id=uuid4(),
            name="Obra",
            client="Cliente",
            status=ProjectStatus.CANCELLED,
            start_date=TODAY,
            created_at=REGISTERED_AT,
            updated_at=REGISTERED_AT,
        )
    )
    expense = expenses.save(
        Expense(
            id=uuid4(),
            amount=50,
            date=TODAY,
            category=ExpenseCategory.MATERIALS,
            title="Cable",
            project_id=project.id,
            has_receipt=True,
            receipt_url="boletas/50.pdf",
            created_at=REGISTERED_AT,
            updated_at=REGISTERED_AT,
        )
    )
    return UpdateExpenseUseCase(expenses, projects, lambda: TODAY), expense, projects


def test_patch_preserves_omitted_fields_and_accepts_explicit_clears(
    setup: tuple[UpdateExpenseUseCase, Expense, InMemoryProjectRepository],
) -> None:
    use_case, expense, _ = setup
    updated = use_case.execute(UpdateExpenseDTO(expense_id=expense.id, amount=7525))
    assert updated.amount == 7525
    assert updated.project_id == expense.project_id
    assert updated.receipt_url == expense.receipt_url
    assert updated.created_at == expense.created_at
    assert updated.updated_at > expense.updated_at

    cleared = use_case.execute(
        UpdateExpenseDTO(
            expense_id=expense.id, project_id=None, receipt_url=None, has_receipt=False
        )
    )
    assert cleared.project_id is cleared.receipt_url is None
    assert cleared.has_receipt is False


def test_patch_with_same_values_keeps_timestamp_and_receipt_invariant(
    setup: tuple[UpdateExpenseUseCase, Expense, InMemoryProjectRepository],
) -> None:
    use_case, expense, _ = setup
    updated = use_case.execute(
        UpdateExpenseDTO(expense_id=expense.id, amount=50, has_receipt=False)
    )
    assert updated is expense
    assert updated.has_receipt is True


def test_patch_rejects_missing_expense_and_invalid_fields(
    setup: tuple[UpdateExpenseUseCase, Expense, InMemoryProjectRepository],
) -> None:
    use_case, expense, projects = setup
    cancelled_id = uuid4()
    projects.save(replace(projects.list_all()[0], id=cancelled_id))

    with pytest.raises(ExpenseNotFoundError):
        use_case.execute(UpdateExpenseDTO(expense_id=uuid4()))
    dto = UpdateExpenseDTO(expense_id=expense.id)
    invalid = [
        (replace(dto, amount=0), InvalidExpenseAmountError),
        (replace(dto, amount=2**63), InvalidMonetaryPrecisionError),
        (replace(dto, date=TODAY + timedelta(days=1)), InvalidExpenseDateError),
        (replace(dto, project_id=uuid4()), ProjectNotFoundError),
        (replace(dto, project_id=cancelled_id), ProjectCancelledError),
    ]
    for change, error in invalid:
        with pytest.raises(error):
            use_case.execute(change)
    assert use_case.execute(dto) is expense
