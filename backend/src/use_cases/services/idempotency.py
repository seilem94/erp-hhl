"""Coordinate one database effect and its immutable confirmation.

Transaction ownership stays with the outer dependency. Exceptions propagate;
neither contention nor failed business validation may enter the legacy path.
"""

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Generic, TypeVar
from uuid import UUID

from src.domain.entities.operation import OperationRecord
from src.domain.enums import OperationState
from src.domain.exceptions import OperationReconciliationRequiredError
from src.domain.repositories.operation_repository import OperationRepository
from src.domain.value_objects.operation_result import (
    OPERATION_RESULT_SCHEMA_VERSION,
    OperationResult,
)
from src.use_cases.dto.operation import OperationContextDTO
from src.use_cases.ports.authorization import AuthorizationPort
from src.use_cases.services.canonicalization import (
    FINGERPRINT_VERSION,
    CanonicalRequest,
    RequestCanonicalizer,
)

ResultT = TypeVar("ResultT", bound=OperationResult)


@dataclass(frozen=True, kw_only=True)
class IdempotentResult(Generic[ResultT]):
    result: ResultT
    replayed: bool


def utc_now() -> datetime:
    return datetime.now(UTC)


class IdempotencyCoordinator:
    def __init__(
        self,
        repository: OperationRepository,
        canonicalizer: RequestCanonicalizer,
        authorization: AuthorizationPort,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._canonicalizer = canonicalizer
        self._authorization = authorization
        self._clock = clock

    def execute(
        self,
        *,
        context: OperationContextDTO,
        request: CanonicalRequest,
        execute_business: Callable[[], ResultT],
        result_type: type[ResultT],
        project_id: UUID | None = None,
    ) -> IdempotentResult[ResultT]:
        self._authorization.authorize_command(
            context.actor,
            request.command_type,
            request.target_resource_id,
            project_id=project_id,
        )
        # Select the stored normalizer for known keys. Preserve v1 when adding
        # future versions; a missing decoder must reconcile, never execute anew.
        known = self._repository.get_by_key(context.key)
        version = (
            FINGERPRINT_VERSION if known is None else known.request_fingerprint.version
        )
        reservation = OperationRecord(
            key=context.key,
            command_type=request.command_type,
            command_version=request.command_version,
            target_resource_id=request.target_resource_id,
            request_fingerprint=self._canonicalizer.fingerprint(
                request, version=version
            ),
            created_at=self._clock(),
        )
        outcome = self._repository.reserve(reservation)
        if isinstance(outcome, OperationRecord):
            self._authorization.authorize_operation_result(context.actor, outcome)
            result = outcome.recover_result()
            if not isinstance(result, result_type):
                raise OperationReconciliationRequiredError(
                    "The stored result does not match this command's result type."
                )
            return IdempotentResult(result=result, replayed=True)

        result = execute_business()
        confirmation = replace(
            reservation,
            state=OperationState.CONFIRMED,
            result_resource_id=result.id,
            result_schema_version=OPERATION_RESULT_SCHEMA_VERSION,
            result_payload=result,
            completed_at=self._clock(),
        )
        self._authorization.authorize_operation_result(context.actor, confirmation)
        self._repository.confirm(confirmation)
        return IdempotentResult(result=result, replayed=False)
