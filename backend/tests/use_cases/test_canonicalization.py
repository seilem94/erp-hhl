"""Fingerprint equivalence, precision and the binary exclusion boundary."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal, localcontext
from io import BytesIO
from typing import cast
from uuid import uuid4

import pytest

from src.domain.enums import CommandType, Currency
from src.domain.exceptions import InvalidCanonicalContentError
from src.use_cases.services.canonicalization import (
    AttachmentMetadata,
    CanonicalRequest,
    CanonicalValue,
    SHA256RequestCanonicalizer,
)


def test_key_order_decimal_scale_and_enum_representation_are_canonical() -> None:
    first = CanonicalRequest(
        command_type=CommandType.REGISTER_EXPENSE,
        content={"amount": Decimal("1500.50"), "currency": Currency.CLP},
    )
    second = replace(
        first, content={"currency": Currency.CLP.value, "amount": Decimal("1500.5")}
    )
    service = SHA256RequestCanonicalizer()
    assert service.fingerprint(first) == service.fingerprint(second)


def test_decimal_context_does_not_merge_distinct_exact_amounts() -> None:
    first = CanonicalRequest(
        command_type=CommandType.REGISTER_EXPENSE,
        content={"amount": Decimal("123456789012345678901234567890.12")},
    )
    second = replace(
        first, content={"amount": Decimal("123456789012345678901234567890.13")}
    )
    with localcontext() as context:
        context.prec = 3
        service = SHA256RequestCanonicalizer()
        assert service.fingerprint(first) != service.fingerprint(second)


def test_same_instant_has_same_fingerprint_across_timezones() -> None:
    instant = datetime(2026, 11, 9, 12, tzinfo=UTC)
    first = CanonicalRequest(
        command_type=CommandType.CREATE_PROJECT, content={"instant": instant}
    )
    second = replace(
        first, content={"instant": instant.astimezone(timezone(timedelta(hours=-3)))}
    )
    service = SHA256RequestCanonicalizer()
    assert service.fingerprint(first) == service.fingerprint(second)


def test_command_target_and_version_are_part_of_identity() -> None:
    original = CanonicalRequest(
        command_type=CommandType.CREATE_PROJECT, content={"name": "Obra"}
    )
    alternatives = (
        replace(original, command_type=CommandType.UPDATE_PROJECT),
        replace(original, target_resource_id=uuid4()),
        replace(original, command_version=2),
        replace(original, content={"name": "Obra "}),
    )
    service = SHA256RequestCanonicalizer()
    assert all(
        service.fingerprint(original) != service.fingerprint(candidate)
        for candidate in alternatives
    )


def test_metadata_only_attachment_digest_distinguishes_content() -> None:
    metadata = AttachmentMetadata(
        file_id=uuid4(),
        media_type="image/jpeg",
        size_bytes=10,
        checksum_sha256="a" * 64,
    )
    first = CanonicalRequest(
        command_type=CommandType.CREATE_PROJECT, content={}, attachments=(metadata,)
    )
    second = replace(first, attachments=(replace(metadata, checksum_sha256="b" * 64),))
    service = SHA256RequestCanonicalizer()
    assert service.fingerprint(first) != service.fingerprint(second)


class UnreadableStream(BytesIO):
    def read(self, size: int | None = -1) -> bytes:
        raise AssertionError("Canonicalization must not read binary streams.")


@pytest.mark.parametrize("binary", [b"large file", UnreadableStream()])
def test_binary_values_are_rejected_without_stream_reads(binary: object) -> None:
    request = CanonicalRequest(
        command_type=CommandType.CREATE_PROJECT,
        content={"nested": {"file": cast(CanonicalValue, binary)}},
    )
    with pytest.raises(InvalidCanonicalContentError, match="binaries/streams"):
        SHA256RequestCanonicalizer().fingerprint(request)


@pytest.mark.parametrize("amount", [Decimal("NaN"), Decimal("Infinity")])
def test_non_finite_amounts_cannot_be_fingerprinted(amount: Decimal) -> None:
    request = CanonicalRequest(
        command_type=CommandType.REGISTER_EXPENSE, content={"amount": amount}
    )
    with pytest.raises(InvalidCanonicalContentError, match="finite"):
        SHA256RequestCanonicalizer().fingerprint(request)


def test_naive_datetime_cannot_depend_on_host_timezone() -> None:
    request = CanonicalRequest(
        command_type=CommandType.CREATE_PROJECT,
        content={"instant": datetime(2026, 11, 9)},
    )
    with pytest.raises(InvalidCanonicalContentError, match="aware"):
        SHA256RequestCanonicalizer().fingerprint(request)
