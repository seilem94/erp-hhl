"""Whole CLP for writes and conversion of historical decimal values."""

from decimal import ROUND_HALF_UP, Decimal

from src.domain.exceptions import InvalidMonetaryPrecisionError

MAX_CLP = 2**63 - 1


def validate_clp(value: int | None) -> None:
    if value is not None and (type(value) is not int or not 0 <= value <= MAX_CLP):
        raise InvalidMonetaryPrecisionError(
            f"El monto debe ser un entero entre 0 y {MAX_CLP} pesos chilenos."
        )


def round_legacy_clp(value: Decimal) -> int:
    """Match PostgreSQL ROUND(numeric) without changing the Decimal context."""
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))
