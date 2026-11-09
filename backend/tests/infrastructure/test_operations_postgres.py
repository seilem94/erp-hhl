"""Transaction ownership, immutable JSONB snapshots and real PostgreSQL races."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal, localcontext
from threading import Barrier, Event
from uuid import uuid4

import pytest
from sqlalchemy import func, inspect, select, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from alembic import command
from src.domain.entities.operation import (
    OperationKey,
    OperationRecord,
    RequestFingerprint,
)
from src.domain.enums import (
    CommandType,
    Currency,
    ExpenseCategory,
    OperationState,
    ProjectStatus,
)
from src.domain.exceptions import (
    IdempotencyConflictError,
    OperationReconciliationRequiredError,
    OperationUnresolvedError,
)
from src.domain.repositories.operation_repository import ReservationAcquired
from src.domain.value_objects.operation_result import ExpenseSnapshot, ProjectSnapshot
from src.infrastructure.database.models import OperationORM, ProjectORM
from src.infrastructure.database.repositories.sqlalchemy_operation_repository import (
    SQLAlchemyOperationRepository,
)
from tests.infrastructure.postgres import migration_config

NOW = datetime(2026, 11, 9, 12, 0, 0, 123456, tzinfo=UTC)


def reservation(command: CommandType = CommandType.CREATE_PROJECT) -> OperationRecord:
    return OperationRecord(
        key=OperationKey(actor_id=uuid4(), operation_id=uuid4()),
        command_type=command,
        request_fingerprint=RequestFingerprint(version=1, digest="a" * 64),
        command_version=1,
        created_at=NOW,
        target_resource_id=uuid4() if command is CommandType.UPDATE_PROJECT else None,
    )


def confirmation(operation: OperationRecord) -> OperationRecord:
    resource_id = operation.target_resource_id or uuid4()
    if operation.command_type is CommandType.REGISTER_EXPENSE:
        payload = ExpenseSnapshot(
            id=resource_id,
            amount=Decimal("1234567890.12"),
            date=date(2026, 11, 9),
            category=ExpenseCategory.MATERIALS,
            description="Cable y conectores",
            has_receipt=True,
            receipt_url="verified-file-reference",
            created_at=NOW,
            updated_at=NOW,
            currency=Currency.CLP,
            project_id=uuid4(),
        )
    else:
        payload = ProjectSnapshot(
            id=resource_id,
            name="Obra con presupuesto",
            client="Cliente",
            status=ProjectStatus.IN_PROGRESS,
            start_date=NOW.date(),
            created_at=NOW,
            updated_at=NOW,
            currency=Currency.CLP,
            budget=Decimal("12.30"),
            description="Primera línea\nSegunda línea",
            end_date=date(2026, 12, 31),
        )
    return replace(
        operation,
        state=OperationState.CONFIRMED,
        result_resource_id=resource_id,
        result_schema_version=1,
        result_payload=payload,
        completed_at=NOW + timedelta(seconds=1),
    )


def business_project(result: OperationRecord) -> ProjectORM:
    payload = result.recover_result()
    assert isinstance(payload, ProjectSnapshot)
    return ProjectORM(
        id=payload.id,
        name=payload.name,
        client=payload.client,
        status=payload.status.value,
        start_date=payload.start_date,
        created_at=payload.created_at,
        updated_at=payload.updated_at,
        budget=payload.budget,
    )


@pytest.mark.parametrize("commit", [False, True])
def test_business_and_confirmation_share_the_callers_commit_or_rollback(
    pg_engine: Engine, monkeypatch: pytest.MonkeyPatch, commit: bool
) -> None:
    operation = reservation()
    result = confirmation(operation)

    def forbidden_boundary() -> None:
        raise AssertionError("The repository must not commit or roll back.")

    with Session(pg_engine) as session:
        with monkeypatch.context() as guard:
            guard.setattr(session, "commit", forbidden_boundary)
            guard.setattr(session, "rollback", forbidden_boundary)
            repo = SQLAlchemyOperationRepository(session)
            assert isinstance(repo.reserve(operation), ReservationAcquired)
            # Load before confirmation too: reads must not retain a stale ORM state.
            assert repo.get_by_key(operation.key) == operation
            session.add(business_project(result))
            session.flush()
            repo.confirm(result)
            assert repo.get_by_key(operation.key) == result
            with Session(pg_engine) as observer:
                assert (
                    SQLAlchemyOperationRepository(observer).get_by_key(operation.key)
                    is None
                )
                assert observer.get(ProjectORM, result.result_resource_id) is None
        if commit:
            session.commit()
        else:
            session.rollback()
    with Session(pg_engine) as observer:
        stored = SQLAlchemyOperationRepository(observer).get_by_key(operation.key)
        assert stored == (result if commit else None)
        assert (
            observer.get(ProjectORM, result.result_resource_id) is not None
        ) is commit


@pytest.mark.parametrize("kind", list(CommandType))
def test_jsonb_roundtrip_preserves_typed_immutable_result(
    pg_engine: Engine, kind: CommandType
) -> None:
    operation = reservation(kind)
    result = confirmation(operation)
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        repo.confirm(result)
        session.commit()
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        assert repo.get_by_key(operation.key) == result
        assert (
            session.scalar(select(func.jsonb_typeof(OperationORM.result_payload)))
            == "object"
        )
        raw = session.scalar(select(OperationORM.result_payload))
        assert raw is not None
        amount_field = "amount" if kind is CommandType.REGISTER_EXPENSE else "budget"
        assert raw[amount_field] == (
            "1234567890.12" if amount_field == "amount" else "12.30"
        )
        assert isinstance(
            repo.reserve(replace(operation, created_at=NOW + timedelta(days=1))),
            OperationRecord,
        )


def test_snapshot_precision_is_independent_of_decimal_context(
    pg_engine: Engine,
) -> None:
    operation = reservation()
    result = confirmation(operation)
    payload = result.recover_result()
    assert isinstance(payload, ProjectSnapshot)
    exact = Decimal("123456789012345678901234567890.12")
    result = replace(result, result_payload=replace(payload, budget=exact))
    with Session(pg_engine) as session, localcontext() as context:
        context.prec = 3
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        repo.confirm(result)
        session.commit()
    with Session(pg_engine) as session:
        stored = SQLAlchemyOperationRepository(session).get_by_key(operation.key)
        assert stored == result


def test_recovery_and_replay_do_not_flush_pending_business_objects(
    pg_engine: Engine,
) -> None:
    operation = reservation()
    result = confirmation(operation)
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        repo.confirm(result)
        session.commit()
        # Deliberately incomplete: an implicit flush would fail before recovery.
        pending = ProjectORM(id=uuid4(), name="Objeto aún no ejecutado")
        session.add(pending)
        assert repo.get_by_key(operation.key) == result
        assert repo.reserve(operation) == result
        assert pending in session.new


def test_two_simultaneous_sessions_have_one_winner_and_one_recoverable_error(
    pg_engine: Engine,
) -> None:
    operation = reservation()
    result = confirmation(operation)
    start = Barrier(2)
    loser_finished = Event()
    release_winner = Event()

    def compete() -> str:
        with Session(pg_engine) as session:
            try:
                with session.begin():
                    start.wait(timeout=5)
                    repo = SQLAlchemyOperationRepository(session, lock_timeout_ms=150)
                    outcome = repo.reserve(operation)
                    assert isinstance(outcome, ReservationAcquired)
                    session.add(business_project(result))
                    session.flush()
                    repo.confirm(result)
                    assert release_winner.wait(timeout=5)
                return "confirmed"
            except OperationUnresolvedError as exc:
                assert isinstance(exc.__cause__, DBAPIError)
                loser_finished.set()
                return "unresolved"

    with ThreadPoolExecutor(max_workers=2) as workers:
        futures = [workers.submit(compete) for _ in range(2)]
        try:
            assert loser_finished.wait(timeout=5)
            # Neither business data nor the prepared confirmation is committed yet.
            with Session(pg_engine) as observer:
                assert (
                    SQLAlchemyOperationRepository(observer).get_by_key(operation.key)
                    is None
                )
                assert (
                    observer.scalar(select(func.count()).select_from(ProjectORM)) == 0
                )
        finally:
            release_winner.set()
        assert sorted(future.result(timeout=5) for future in futures) == [
            "confirmed",
            "unresolved",
        ]
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        assert repo.get_by_key(operation.key) == result
        assert repo.reserve(operation) == result
        assert session.scalar(select(func.count()).select_from(OperationORM)) == 1
        assert session.scalar(select(func.count()).select_from(ProjectORM)) == 1


def test_timeout_requires_caller_rollback_and_preserves_settings(
    pg_engine: Engine,
) -> None:
    operation = reservation()
    with Session(pg_engine) as winner, Session(pg_engine) as contender:
        previous = contender.scalar(select(func.current_setting("lock_timeout")))
        SQLAlchemyOperationRepository(winner).reserve(operation)
        repo = SQLAlchemyOperationRepository(contender, lock_timeout_ms=100)
        with pytest.raises(OperationUnresolvedError):
            repo.reserve(operation)
        # The adapter must not secretly repair/roll back the caller's transaction.
        with pytest.raises(DBAPIError):
            contender.execute(select(1))
        contender.rollback()
        assert (
            contender.scalar(select(func.current_setting("lock_timeout"))) == previous
        )
        winner.rollback()
        assert isinstance(repo.reserve(operation), ReservationAcquired)
        assert (
            contender.scalar(select(func.current_setting("lock_timeout"))) == previous
        )


def test_rolled_back_reservation_can_be_acquired_by_another_session(
    pg_engine: Engine,
) -> None:
    operation = reservation()
    with Session(pg_engine) as first:
        SQLAlchemyOperationRepository(first).reserve(operation)
        first.rollback()
    with Session(pg_engine) as second:
        repo = SQLAlchemyOperationRepository(second)
        assert isinstance(repo.reserve(operation), ReservationAcquired)
        result = confirmation(operation)
        repo.confirm(result)
        second.commit()
        assert repo.get_by_key(operation.key) == result


@pytest.mark.parametrize("altered", ["fingerprint", "version", "command", "target"])
def test_known_key_with_another_request_is_a_conflict(
    pg_engine: Engine, altered: str
) -> None:
    operation = reservation()
    result = confirmation(operation)
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        repo.confirm(result)
        session.commit()
    changed = {
        "fingerprint": replace(
            operation,
            request_fingerprint=RequestFingerprint(version=1, digest="b" * 64),
        ),
        "version": replace(operation, command_version=2),
        "command": replace(operation, command_type=CommandType.REGISTER_EXPENSE),
        "target": replace(operation, target_resource_id=uuid4()),
    }[altered]
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        with pytest.raises(IdempotencyConflictError):
            repo.reserve(changed)
        assert repo.get_by_key(operation.key) == result


def test_purged_payload_remains_sql_null_and_never_a_new_reservation(
    pg_engine: Engine,
) -> None:
    operation = reservation()
    result = confirmation(operation)
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        repo.confirm(result)
        session.commit()
        session.execute(update(OperationORM).values(result_payload=None))
        session.commit()
        assert session.scalar(select(OperationORM.result_payload.is_(None))) is True
        stored = repo.reserve(operation)
        assert isinstance(stored, OperationRecord)
        assert stored == replace(result, result_payload=None)
        with pytest.raises(OperationReconciliationRequiredError):
            stored.recover_result()


@pytest.mark.parametrize("corrupt", ["version", "payload"])
def test_unreadable_confirmation_requires_reconciliation_not_execution(
    pg_engine: Engine, corrupt: str
) -> None:
    operation = reservation()
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        repo.confirm(confirmation(operation))
        session.commit()
        if corrupt == "version":
            session.execute(update(OperationORM).values(result_schema_version=999))
        else:
            session.execute(
                update(OperationORM).values(result_payload={"invalid": True})
            )
        session.commit()
        with pytest.raises(OperationReconciliationRequiredError):
            repo.reserve(operation)
        assert session.scalar(select(func.count()).select_from(OperationORM)) == 1


def test_operation_identity_is_isolated_by_actor(pg_engine: Engine) -> None:
    original = reservation()
    another = replace(
        original,
        key=OperationKey(actor_id=uuid4(), operation_id=original.key.operation_id),
    )
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(original)
        repo.confirm(confirmation(original))
        session.commit()
        assert repo.get_by_key(another.key) is None
        assert isinstance(repo.reserve(another), ReservationAcquired)
        repo.confirm(confirmation(another))
        session.commit()
        assert session.scalar(select(func.count()).select_from(OperationORM)) == 2


def test_confirmation_cannot_be_taken_over_after_premature_reservation_commit(
    pg_engine: Engine,
) -> None:
    operation = reservation()
    with Session(pg_engine) as owner:
        SQLAlchemyOperationRepository(owner).reserve(operation)
        owner.commit()  # Deliberately violate the application protocol.
    with Session(pg_engine) as another:
        repo = SQLAlchemyOperationRepository(another)
        with pytest.raises(OperationUnresolvedError):
            repo.confirm(confirmation(operation))
        with pytest.raises(OperationUnresolvedError):
            repo.reserve(operation)


def test_confirmation_is_immutable_after_commit(pg_engine: Engine) -> None:
    operation = reservation()
    result = confirmation(operation)
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        repo.confirm(result)
        session.commit()
        payload = result.recover_result()
        assert isinstance(payload, ProjectSnapshot)
        with pytest.raises(OperationUnresolvedError):
            repo.confirm(
                replace(result, result_payload=replace(payload, name="Alterado"))
            )
        assert repo.get_by_key(operation.key) == result


def test_resource_deletion_cannot_remove_its_confirmation(pg_engine: Engine) -> None:
    operation = reservation()
    result = confirmation(operation)
    with Session(pg_engine) as session:
        repo = SQLAlchemyOperationRepository(session)
        repo.reserve(operation)
        project = business_project(result)
        session.add(project)
        session.flush()
        repo.confirm(result)
        session.commit()
        session.delete(project)
        session.commit()
        assert repo.reserve(operation) == result


def test_operations_schema_and_migration_are_reversible(pg_engine: Engine) -> None:
    with pg_engine.begin() as connection:
        inspector = inspect(connection)
        assert inspector.get_pk_constraint("operations")["constrained_columns"] == [
            "actor_id",
            "operation_id",
        ]
        payload = next(
            c
            for c in inspector.get_columns("operations")
            if c["name"] == "result_payload"
        )
        assert isinstance(payload["type"], JSONB) and payload["nullable"]
        assert not inspector.get_foreign_keys("operations")
        config = migration_config(connection)
        command.downgrade(config, "a417b6283c90")
        assert "operations" not in inspect(connection).get_table_names()
        assert {"projects", "expenses"} <= set(inspect(connection).get_table_names())
        command.upgrade(config, "head")
        assert "operations" in inspect(connection).get_table_names()


@pytest.mark.parametrize("invalid", ["state", "version", "result", "resource"])
def test_database_rejects_invalid_operation_metadata(
    pg_engine: Engine, invalid: str
) -> None:
    values: dict[str, object] = {
        "actor_id": uuid4(),
        "operation_id": uuid4(),
        "command_type": "create_project",
        "resource_type": "project",
        "fingerprint_version": 1,
        "command_version": 1,
        "request_fingerprint": "a" * 64,
        "state": "reserved",
        "reserved_in_transaction": 1,
        "created_at": NOW,
    }
    if invalid == "state":
        values["state"] = "unknown"
    elif invalid == "version":
        values["fingerprint_version"] = 0
    elif invalid == "result":
        values["state"] = "confirmed"
    else:
        values["resource_type"] = "expense"
    with pytest.raises(IntegrityError), pg_engine.begin() as connection:
        connection.execute(OperationORM.__table__.insert().values(**values))
