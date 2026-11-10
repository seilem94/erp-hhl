"""Historical snapshots and payload-free confirmations retain their identity."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from src.domain.entities.expense import Expense
from src.domain.entities.operation import (
    OperationKey,
    OperationRecord,
    RequestFingerprint,
)
from src.domain.entities.project import Project
from src.domain.enums import CommandType, ExpenseCategory, OperationState, ProjectStatus
from src.domain.exceptions import (
    InvalidOperationIdError,
    OperationReconciliationRequiredError,
    OperationUnresolvedError,
)
from src.domain.value_objects.operation_result import ExpenseSnapshot, ProjectSnapshot
from src.use_cases.dto.operation import CreateProjectCommandDTO, OperationContextDTO
from src.use_cases.ports.identity import ActorIdentity

NOW = datetime(2026, 11, 9, tzinfo=UTC)


def make_confirmation() -> OperationRecord:
    project = Project(
        id=uuid4(),
        name="Obra",
        client="Cliente",
        status=ProjectStatus.IN_PROGRESS,
        start_date=NOW.date(),
        created_at=NOW,
        updated_at=NOW,
    )
    return OperationRecord(
        key=OperationKey(actor_id=uuid4(), operation_id=uuid4()),
        command_type=CommandType.CREATE_PROJECT,
        request_fingerprint=RequestFingerprint(version=1, digest="a" * 64),
        command_version=1,
        created_at=NOW,
        state=OperationState.CONFIRMED,
        result_resource_id=project.id,
        result_schema_version=1,
        result_payload=ProjectSnapshot.from_project(project),
        completed_at=NOW,
    )


def test_project_snapshot_does_not_follow_later_business_mutation() -> None:
    confirmation = make_confirmation()
    snapshot = confirmation.recover_result()
    assert isinstance(snapshot, ProjectSnapshot)
    project = Project(
        id=snapshot.id,
        name=snapshot.name,
        client=snapshot.client,
        status=snapshot.status,
        start_date=snapshot.start_date,
        created_at=snapshot.created_at,
        updated_at=snapshot.updated_at,
    )
    original = ProjectSnapshot.from_project(project)
    project.status = ProjectStatus.COMPLETED
    project.name = "Nombre posterior"
    assert original.status is ProjectStatus.IN_PROGRESS
    assert original.name == snapshot.name
    with pytest.raises(FrozenInstanceError):
        original.status = ProjectStatus.COMPLETED  # type: ignore[misc]


def test_expense_snapshot_preserves_original_amount_and_receipt() -> None:
    expense = Expense(
        id=uuid4(),
        amount=Decimal("1234.56"),
        date=date(2026, 11, 9),
        category=ExpenseCategory.MATERIALS,
        description="Cable",
        has_receipt=True,
        receipt_url="receipt-reference",
        created_at=NOW,
        updated_at=NOW,
    )
    snapshot = ExpenseSnapshot.from_expense(expense)
    expense.amount = Decimal("9999.99")
    expense.receipt_url = None
    assert snapshot.amount == Decimal("1234.56")
    assert snapshot.receipt_url == "receipt-reference"


def test_payload_purge_preserves_a_known_confirmation_and_requires_reconciliation() -> (
    None
):
    original = make_confirmation()
    purged = replace(original, result_payload=None)
    assert purged.state is OperationState.CONFIRMED
    assert purged.key == original.key
    assert purged.request_fingerprint == original.request_fingerprint
    assert purged.result_resource_id == original.result_resource_id
    assert purged.result_schema_version == original.result_schema_version
    assert purged.completed_at == original.completed_at
    with pytest.raises(OperationReconciliationRequiredError):
        purged.recover_result()


def test_reservation_cannot_be_recovered_or_contain_confirmation_data() -> None:
    confirmed = make_confirmation()
    reservation = OperationRecord(
        key=confirmed.key,
        command_type=confirmed.command_type,
        request_fingerprint=confirmed.request_fingerprint,
        command_version=1,
        created_at=NOW,
    )
    with pytest.raises(OperationUnresolvedError):
        reservation.recover_result()
    with pytest.raises(ValueError, match="reservation"):
        replace(reservation, result_resource_id=uuid4())


def test_confirmation_requires_metadata_even_after_purge() -> None:
    with pytest.raises(ValueError, match="metadata"):
        replace(make_confirmation(), result_payload=None, result_resource_id=None)


def test_result_must_match_requested_resource() -> None:
    with pytest.raises(ValueError, match="requested resource"):
        replace(make_confirmation(), target_resource_id=uuid4())


def test_context_rejects_non_v4_operation_identifiers() -> None:
    with pytest.raises(InvalidOperationIdError):
        OperationContextDTO(
            actor=ActorIdentity(actor_id=uuid4()), operation_id=UUID(int=1)
        )


def test_command_envelope_keeps_operation_and_resource_identity_separate() -> None:
    from src.use_cases.create_project import CreateProjectDTO

    operation_id, resource_id = uuid4(), uuid4()
    envelope = CreateProjectCommandDTO(
        context=OperationContextDTO(
            actor=ActorIdentity(actor_id=uuid4()), operation_id=operation_id
        ),
        data=CreateProjectDTO(name="Obra", client="Cliente", id=resource_id),
    )
    assert envelope.context.key.operation_id == operation_id
    assert envelope.resource_id == resource_id
