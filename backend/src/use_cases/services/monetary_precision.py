"""Validate the current NUMERIC(12,2) command contract without rounding.

Only the opt-in command path applies this stricter contract. Aggregated read
amounts are not subject to the per-row limit. No Decimal context is modified.
"""

from decimal import Decimal

from src.domain.exceptions import InvalidMonetaryPrecisionError


def validate_command_amount(value: Decimal | None) -> None:
    if value is None:
        return
    if not value.is_finite() or value.copy_abs() >= Decimal("10000000000"):
        raise InvalidMonetaryPrecisionError(
            "Amount must be finite and fit NUMERIC(12,2) without rounding."
        )
    # A finite Decimal always has an integer exponent. Trailing zeroes beyond
    # scale two are harmless; any nonzero digit there would change the intent.
    _, digits, exponent = value.as_tuple()
    if isinstance(exponent, int) and exponent < -2:
        if any(digits[exponent + 2 :]):
            raise InvalidMonetaryPrecisionError(
                "Amount must have at most two nonzero fractional decimal places."
            )
