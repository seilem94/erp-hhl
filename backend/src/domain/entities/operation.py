"""Pure operation identity and confirmation, including payload-free tombstones."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.enums import CommandType, OperationState, ResourceType
from src.domain.exceptions import (
    InvalidOperationIdError,
    OperationReconciliationRequiredError,
    OperationUnresolvedError,
)
from src.domain.value_objects.operation_result import (
    ExpenseSnapshot,
    OperationResult,
    ProjectSnapshot,
)


@dataclass(frozen=True, kw_only=True)
class OperationKey:
    actor_id: UUID
    operation_id: UUID

    def __post_init__(self) -> None:
        if self.operation_id.version != 4:
            raise InvalidOperationIdError("Operation identifiers must be UUIDv4.")


@dataclass(frozen=True, kw_only=True)
class RequestFingerprint:
    version: int
    digest: str

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("Fingerprint version must be positive.")
        if len(self.digest) != 64 or any(
            char not in "0123456789abcdef" for char in self.digest
        ):
            raise ValueError("Fingerprint must be a lowercase SHA-256 hex digest.")


@dataclass(frozen=True, kw_only=True)
class OperationRecord:
    key: OperationKey
    command_type: CommandType
    request_fingerprint: RequestFingerprint
    command_version: int
    created_at: datetime
    target_resource_id: UUID | None = None
    state: OperationState = OperationState.RESERVED
    result_resource_id: UUID | None = None
    result_schema_version: int | None = None
    result_payload: OperationResult | None = None
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.command_version < 1:
            raise ValueError("Command version must be positive.")
        if (
            self.command_type is CommandType.UPDATE_PROJECT
            and self.target_resource_id is None
        ):
            raise ValueError("An update must retain its requested target.")
        if self.state is OperationState.RESERVED:
            if any(
                value is not None
                for value in (
                    self.result_resource_id,
                    self.result_schema_version,
                    self.result_payload,
                    self.completed_at,
                )
            ):
                raise ValueError("A reservation cannot contain confirmation data.")
            return
        if (
            self.result_resource_id is None
            or self.result_schema_version is None
            or self.result_schema_version < 1
            or self.completed_at is None
        ):
            raise ValueError("A confirmation must retain its result metadata.")
        if (
            self.target_resource_id is not None
            and self.target_resource_id != self.result_resource_id
        ):
            raise ValueError("The result must identify the requested resource.")
        if self.result_payload is not None:
            if self.result_payload.id != self.result_resource_id:
                raise ValueError("Snapshot and result identifiers must agree.")
            expected = (
                ExpenseSnapshot
                if self.resource_type is ResourceType.EXPENSE
                else ProjectSnapshot
            )
            if not isinstance(self.result_payload, expected):
                raise ValueError("Snapshot type must match the command resource.")

    @property
    def resource_type(self) -> ResourceType:
        return self.command_type.resource_type

    def recover_result(self) -> OperationResult:
        """A purged confirmation remains known and can never be executed again."""
        if self.state is OperationState.RESERVED:
            raise OperationUnresolvedError("The operation is not confirmed.")
        if self.result_payload is None:
            raise OperationReconciliationRequiredError(
                "The confirmed result payload is unavailable; reconcile the operation."
            )
        return self.result_payload
