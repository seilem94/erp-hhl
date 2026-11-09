"""Versioned JSON representation of pure snapshots, independent of HTTP schemas."""

from pydantic import JsonValue, TypeAdapter, ValidationError

from src.domain.enums import ResourceType
from src.domain.exceptions import OperationReconciliationRequiredError
from src.domain.value_objects.operation_result import (
    ExpenseSnapshot,
    OperationResult,
    ProjectSnapshot,
)

SNAPSHOT_SCHEMA_VERSION = 1
# Preserve historical adapters when introducing an incompatible result version.
_project_adapter = TypeAdapter(ProjectSnapshot)
_expense_adapter = TypeAdapter(ExpenseSnapshot)
_json_adapter = TypeAdapter(dict[str, JsonValue])


def encode_result(result: OperationResult, schema_version: int) -> dict[str, JsonValue]:
    _check_version(schema_version)
    encoded = (
        _project_adapter.dump_json(result)
        if isinstance(result, ProjectSnapshot)
        else _expense_adapter.dump_json(result)
    )
    # Decimal, UUID, date and datetime become JSON strings, never float amounts.
    return _json_adapter.validate_json(encoded)


def decode_result(
    payload: dict[str, JsonValue], resource_type: ResourceType, schema_version: int
) -> OperationResult:
    _check_version(schema_version)
    try:
        if resource_type is ResourceType.PROJECT:
            return _project_adapter.validate_python(payload)
        return _expense_adapter.validate_python(payload)
    except ValidationError as exc:
        raise OperationReconciliationRequiredError(
            "Stored operation result cannot be decoded; reconciliation is required."
        ) from exc


def _check_version(schema_version: int) -> None:
    if schema_version != SNAPSHOT_SCHEMA_VERSION:
        raise OperationReconciliationRequiredError(
            "Unsupported operation result version; reconciliation is required."
        )
