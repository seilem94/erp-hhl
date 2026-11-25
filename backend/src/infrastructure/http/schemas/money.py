"""Validate whole CLP and serialize exact integers for JSON clients."""

import re
from typing import Annotated

from pydantic import BeforeValidator, Field, PlainSerializer

from src.use_cases.services.monetary_precision import MAX_CLP


def _whole_clp(value: object) -> int:
    if type(value) is int:
        return value
    if isinstance(value, str):
        amount = value.strip()
        if re.fullmatch(r"[+-]?[0-9]+(?:\.0+)?", amount):
            # Support existing clients that serialize whole values with .00.
            return int(amount.split(".", 1)[0])
    raise ValueError("Ingresa un monto entero en pesos chilenos.")


def _serialize_clp(value: int) -> str:
    return str(value)


ClpInput = Annotated[int, BeforeValidator(_whole_clp, json_schema_input_type=int | str)]
ExpenseAmount = Annotated[ClpInput, Field(gt=0, le=MAX_CLP)]
ProjectBudget = Annotated[ClpInput, Field(ge=0, le=MAX_CLP)]
ClpResponse = Annotated[
    int, PlainSerializer(_serialize_clp, return_type=str, when_used="json")
]
