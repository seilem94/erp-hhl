"""Command precision checks must never use rounding from the Decimal context."""

from decimal import Decimal, localcontext

import pytest

from src.domain.exceptions import InvalidMonetaryPrecisionError
from src.use_cases.services.monetary_precision import validate_command_amount


@pytest.mark.parametrize(
    "amount", (None, "0", "0.0100", "1.2300", "9999999999.99", "-9999999999.99")
)
def test_exact_representable_values_survive_low_precision_context(
    amount: str | None,
) -> None:
    value = None if amount is None else Decimal(amount)
    with localcontext() as context:
        context.prec = 3
        validate_command_amount(value)


@pytest.mark.parametrize(
    "amount", ("0.001", "1.2301", "9999999999.991", "10000000000", "NaN", "Infinity")
)
def test_nonrepresentable_values_are_rejected_without_rounding(amount: str) -> None:
    with localcontext() as context:
        context.prec = 3
        with pytest.raises(InvalidMonetaryPrecisionError):
            validate_command_amount(Decimal(amount))
