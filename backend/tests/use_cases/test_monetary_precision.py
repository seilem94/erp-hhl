"""Validate whole CLP and preserve the PostgreSQL rule for historical values."""

from decimal import Decimal, localcontext
from typing import cast

import pytest

from src.domain.exceptions import InvalidMonetaryPrecisionError
from src.use_cases.services.monetary_precision import (
    MAX_CLP,
    round_legacy_clp,
    validate_clp,
)


@pytest.mark.parametrize("amount", (None, 0, 1, 2_500_000_000, MAX_CLP))
def test_whole_clp_that_fits_bigint_is_valid(amount: int | None) -> None:
    validate_clp(amount)


@pytest.mark.parametrize("amount", (-1, MAX_CLP + 1, True, 125.5, Decimal("1.25")))
def test_invalid_new_clp_is_rejected_without_rounding(amount: object) -> None:
    with pytest.raises(InvalidMonetaryPrecisionError):
        validate_clp(cast(int, amount))


@pytest.mark.parametrize(
    ("amount", "rounded"),
    (("631809.50", 631810), ("9999999999.49", 9999999999), ("-0.50", -1)),
)
def test_legacy_rounding_matches_postgresql_even_with_low_decimal_precision(
    amount: str, rounded: int
) -> None:
    with localcontext() as context:
        context.prec = 3
        assert round_legacy_clp(Decimal(amount)) == rounded
