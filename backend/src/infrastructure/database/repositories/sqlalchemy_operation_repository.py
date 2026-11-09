"""PostgreSQL arbitrates ownership; the request dependency owns commit/rollback."""

from __future__ import annotations

from psycopg import Error as PsycopgError
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from src.domain.entities.operation import OperationKey, OperationRecord
from src.domain.enums import OperationState
from src.domain.exceptions import IdempotencyConflictError, OperationUnresolvedError
from src.domain.repositories.operation_repository import (
    OperationRepository,
    ReservationAcquired,
    ReservationResult,
)
from src.infrastructure.database.models import OperationORM
from src.infrastructure.database.operation_mappers import operation_to_domain
from src.infrastructure.database.operation_payload import encode_result


class SQLAlchemyOperationRepository(OperationRepository):
    def __init__(self, session: Session, *, lock_timeout_ms: int = 2_000) -> None:
        if lock_timeout_ms < 1:
            raise ValueError("Reservation lock timeout must be positive.")
        self._session = session
        self._lock_timeout_ms = lock_timeout_ms

    def reserve(self, operation: OperationRecord) -> ReservationResult:
        if operation.state is not OperationState.RESERVED:
            raise ValueError("Only a new reservation may be acquired.")
        statement = (
            insert(OperationORM)
            .values(
                actor_id=operation.key.actor_id,
                operation_id=operation.key.operation_id,
                command_type=operation.command_type.value,
                resource_type=operation.resource_type.value,
                target_resource_id=operation.target_resource_id,
                fingerprint_version=operation.request_fingerprint.version,
                request_fingerprint=operation.request_fingerprint.digest,
                command_version=operation.command_version,
                state=OperationState.RESERVED.value,
                reserved_in_transaction=func.txid_current(),
                created_at=operation.created_at,
            )
            .on_conflict_do_nothing(
                index_elements=[OperationORM.actor_id, OperationORM.operation_id]
            )
            .returning(OperationORM.operation_id)
        )
        # Do not flush business objects before the operation has been acquired.
        with self._session.no_autoflush:
            try:
                previous = self._session.scalar(
                    select(func.current_setting("lock_timeout"))
                )
                if not isinstance(previous, str):
                    raise TypeError("Unexpected PostgreSQL lock timeout setting.")
                self._session.execute(
                    select(
                        func.set_config(
                            "lock_timeout", f"{self._lock_timeout_ms}ms", True
                        )
                    )
                )
                acquired = self._session.execute(statement).scalar_one_or_none()
                self._session.execute(
                    select(func.set_config("lock_timeout", previous, True))
                )
            except DBAPIError as exc:
                self._raise_if_transient(exc)
                raise
        # On a PostgreSQL timeout the transaction is aborted. Never try to restore
        # settings or recover it here: the dependency must roll back before retry.
        if acquired is not None:
            self._session.flush()
            return ReservationAcquired()
        existing = self.get_by_key(operation.key)
        if existing is None:
            raise OperationUnresolvedError(
                "The competing operation is not yet visible."
            )
        self._assert_same_request(existing, operation)
        if existing.state is not OperationState.CONFIRMED:
            raise OperationUnresolvedError(
                "A known reservation requires reconciliation."
            )
        return existing

    def confirm(self, operation: OperationRecord) -> None:
        if operation.state is not OperationState.CONFIRMED:
            raise ValueError("Confirmation requires a confirmed operation record.")
        if operation.result_payload is None or operation.result_schema_version is None:
            raise ValueError("A new confirmation requires a complete result payload.")
        payload = encode_result(
            operation.result_payload, operation.result_schema_version
        )
        statement = (
            update(OperationORM)
            .where(
                OperationORM.actor_id == operation.key.actor_id,
                OperationORM.operation_id == operation.key.operation_id,
                OperationORM.state == OperationState.RESERVED.value,
                OperationORM.reserved_in_transaction == func.txid_current(),
                OperationORM.command_type == operation.command_type.value,
                OperationORM.command_version == operation.command_version,
                OperationORM.target_resource_id.is_not_distinct_from(
                    operation.target_resource_id
                ),
                OperationORM.fingerprint_version
                == operation.request_fingerprint.version,
                OperationORM.request_fingerprint
                == operation.request_fingerprint.digest,
            )
            .values(
                state=OperationState.CONFIRMED.value,
                result_resource_id=operation.result_resource_id,
                result_schema_version=operation.result_schema_version,
                result_payload=payload,
                completed_at=operation.completed_at,
            )
            .returning(OperationORM.operation_id)
            .execution_options(synchronize_session=False)
        )
        try:
            with self._session.no_autoflush:
                confirmed = self._session.execute(statement).scalar_one_or_none()
        except DBAPIError as exc:
            self._raise_if_transient(exc)
            raise
        if confirmed is None:
            existing = self.get_by_key(operation.key)
            if existing is not None:
                self._assert_same_request(existing, operation)
            raise OperationUnresolvedError(
                "No reservation owned by this transaction can be confirmed."
            )
        self._session.flush()

    def get_by_key(self, key: OperationKey) -> OperationRecord | None:
        try:
            with self._session.no_autoflush:
                orm = self._session.get(
                    OperationORM,
                    (key.actor_id, key.operation_id),
                    populate_existing=True,
                )
        except DBAPIError as exc:
            self._raise_if_transient(exc)
            raise
        return None if orm is None else operation_to_domain(orm)

    @staticmethod
    def _assert_same_request(
        existing: OperationRecord, requested: OperationRecord
    ) -> None:
        # Server-generated timestamps and result UUIDs are not request identity.
        if (
            existing.command_type != requested.command_type
            or existing.command_version != requested.command_version
            or existing.target_resource_id != requested.target_resource_id
            or existing.request_fingerprint != requested.request_fingerprint
        ):
            raise IdempotencyConflictError(
                "The operation key identifies another request."
            )

    @staticmethod
    def _raise_if_transient(exc: DBAPIError) -> None:
        transient = {"55P03", "40P01", "40001", "57014"}
        if exc.connection_invalidated or (
            isinstance(exc.orig, PsycopgError) and exc.orig.sqlstate in transient
        ):
            raise OperationUnresolvedError(
                "Operation resolution is uncertain; roll back and retain the same key."
            ) from exc
