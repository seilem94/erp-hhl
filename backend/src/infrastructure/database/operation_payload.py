"""Versioned JSON representation of pure snapshots, independent of HTTP schemas."""

from decimal import Decimal, InvalidOperation

from pydantic import JsonValue, TypeAdapter

from src.domain.enums import ResourceType
from src.domain.exceptions import OperationReconciliationRequiredError
from src.domain.value_objects.operation_result import (
    OPERATION_RESULT_SCHEMA_VERSION,
    ExpenseSnapshot,
    OperationResult,
    ProjectSnapshot,
)
from src.use_cases.services.monetary_precision import round_legacy_clp

SNAPSHOT_SCHEMA_VERSION = OPERATION_RESULT_SCHEMA_VERSION
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
    # UUID, date and datetime become strings. CLP stays an exact JSONB integer.
    return _json_adapter.validate_json(encoded)


def decode_result(
    payload: dict[str, JsonValue], resource_type: ResourceType, schema_version: int
) -> OperationResult:
    try:
        if schema_version == 1:
            payload = _upgrade_v1(payload, resource_type)
        else:
            _check_version(schema_version)
        if resource_type is ResourceType.PROJECT:
            return _project_adapter.validate_python(payload)
        return _expense_adapter.validate_python(payload)
    except (InvalidOperation, OverflowError, ValueError) as exc:
        raise OperationReconciliationRequiredError(
            "Stored operation result cannot be decoded; reconciliation is required."
        ) from exc


def _upgrade_v1(
    payload: dict[str, JsonValue], resource_type: ResourceType
) -> dict[str, JsonValue]:
    """Read a legacy confirmation without modifying the original JSONB payload."""
    upgraded = dict(payload)
    money_field = "budget" if resource_type is ResourceType.PROJECT else "amount"
    value = upgraded.get(money_field)
    if isinstance(value, str):
        upgraded[money_field] = round_legacy_clp(Decimal(value))
    elif value is not None and type(value) is not int:
        raise ValueError("Invalid legacy CLP amount.")
    if resource_type is ResourceType.EXPENSE:
        upgraded["title"] = upgraded.pop("description", None)
    return upgraded


def _check_version(schema_version: int) -> None:
    if schema_version != SNAPSHOT_SCHEMA_VERSION:
        raise OperationReconciliationRequiredError(
            "Unsupported operation result version; reconciliation is required."
        )
