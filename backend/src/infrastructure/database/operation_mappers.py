"""Translate persisted confirmations into pure records, retaining purged identity."""

from src.domain.entities.operation import (
    OperationKey,
    OperationRecord,
    RequestFingerprint,
)
from src.domain.enums import CommandType, OperationState, ResourceType
from src.domain.exceptions import OperationReconciliationRequiredError
from src.domain.value_objects.operation_result import OperationResult
from src.infrastructure.database.models import OperationORM
from src.infrastructure.database.operation_payload import decode_result


def operation_to_domain(
    orm: OperationORM, *, include_payload: bool = True
) -> OperationRecord:
    try:
        command = CommandType(orm.command_type)
        resource_type = ResourceType(orm.resource_type)
        if resource_type is not command.resource_type:
            raise ValueError("Stored resource and command disagree.")
        payload: OperationResult | None = None
        if include_payload and orm.result_payload is not None:
            if orm.result_schema_version is None:
                raise ValueError("Missing result schema version.")
            payload = decode_result(
                orm.result_payload, resource_type, orm.result_schema_version
            )
        return OperationRecord(
            key=OperationKey(actor_id=orm.actor_id, operation_id=orm.operation_id),
            command_type=command,
            request_fingerprint=RequestFingerprint(
                version=orm.fingerprint_version, digest=orm.request_fingerprint
            ),
            command_version=orm.command_version,
            created_at=orm.created_at,
            target_resource_id=orm.target_resource_id,
            state=OperationState(orm.state),
            result_resource_id=orm.result_resource_id,
            result_schema_version=orm.result_schema_version,
            result_payload=payload,
            completed_at=orm.completed_at,
        )
    except (ValueError, TypeError) as exc:
        raise OperationReconciliationRequiredError(
            "Stored operation metadata is invalid; reconciliation is required."
        ) from exc
