"""Versioned request fingerprints, extensible to metadata-only multipart inputs.

File adapters must provide verified metadata and compute content checksums by
streaming outside this service. Never pass UploadFile, bytes, streams or binary
contents here. Metadata must include a digest: filename/size alone do not identify
content. This boundary keeps large files out of canonical JSON and server RAM.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum
from typing import Protocol, TypeAlias
from uuid import UUID

from src.domain.entities.operation import RequestFingerprint
from src.domain.enums import CommandType
from src.domain.exceptions import InvalidCanonicalContentError

CanonicalValue: TypeAlias = (
    None
    | bool
    | int
    | str
    | Decimal
    | UUID
    | date
    | Enum
    | tuple["CanonicalValue", ...]
    | Mapping[str, "CanonicalValue"]
)
JsonValue: TypeAlias = (
    None | bool | int | str | list["JsonValue"] | dict[str, "JsonValue"]
)


@dataclass(frozen=True, kw_only=True)
class AttachmentMetadata:
    file_id: UUID
    media_type: str
    size_bytes: int
    checksum_sha256: str

    def __post_init__(self) -> None:
        if self.size_bytes < 0:
            raise InvalidCanonicalContentError("Attachment size cannot be negative.")
        try:
            RequestFingerprint(version=1, digest=self.checksum_sha256)
        except ValueError as exc:
            raise InvalidCanonicalContentError(
                "Attachment metadata requires a verified SHA-256 checksum."
            ) from exc


@dataclass(frozen=True, kw_only=True)
class CanonicalRequest:
    command_type: CommandType
    content: Mapping[str, CanonicalValue]
    target_resource_id: UUID | None = None
    command_version: int = 1
    attachments: tuple[AttachmentMetadata, ...] = ()

    def __post_init__(self) -> None:
        if self.command_version < 1:
            raise InvalidCanonicalContentError("Command version must be positive.")


class RequestCanonicalizer(Protocol):
    def fingerprint(self, request: CanonicalRequest) -> RequestFingerprint:
        """Hash structured command values and attachment metadata, never files."""
        ...


class SHA256RequestCanonicalizer:
    """Version 1; retain this implementation when introducing future versions."""

    def fingerprint(self, request: CanonicalRequest) -> RequestFingerprint:
        document: Mapping[str, CanonicalValue] = {
            "fingerprint_version": 1,
            "command_type": request.command_type,
            "command_version": request.command_version,
            "target_resource_id": request.target_resource_id,
            "content": request.content,
            "attachments": tuple(
                {
                    "file_id": item.file_id,
                    "media_type": item.media_type,
                    "size_bytes": item.size_bytes,
                    "checksum_sha256": item.checksum_sha256,
                }
                for item in request.attachments
            ),
        }
        normalized = self._normalize(document)
        serialized = json.dumps(
            normalized,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return RequestFingerprint(
            version=1, digest=hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        )

    def _normalize(self, value: CanonicalValue) -> JsonValue:
        # Enums must precede str/int: StrEnum is also an instance of str.
        if isinstance(value, Enum):
            enum_value: object = value.value
            if not isinstance(enum_value, (str, int)):
                raise InvalidCanonicalContentError("Unsupported enum value.")
            return self._normalize(enum_value)
        if value is None or isinstance(value, (bool, int, str)):
            return value
        if isinstance(value, Decimal):
            if not value.is_finite():
                raise InvalidCanonicalContentError("Decimal values must be finite.")
            if value.is_zero():
                return "0"
            # Avoid normalize()/quantize(): the current Decimal context may round.
            text = format(value, "f")
            return text.rstrip("0").rstrip(".") if "." in text else text
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, datetime):
            if value.utcoffset() is None:
                raise InvalidCanonicalContentError("Datetime values must be aware.")
            return value.astimezone(UTC).isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, tuple):
            return [self._normalize(item) for item in value]
        if isinstance(value, Mapping):
            if not all(isinstance(key, str) for key in value):
                raise InvalidCanonicalContentError("Canonical keys must be strings.")
            return {key: self._normalize(item) for key, item in value.items()}
        raise InvalidCanonicalContentError(
            "Canonical content must be structured data; binaries/streams are excluded."
        )
