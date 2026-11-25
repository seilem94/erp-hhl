"""Esquemas HTTP para el registro y consulta de gastos (CapEx y OPEX)."""

from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import (
    UUID4,
    AliasChoices,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    computed_field,
    field_validator,
)
from pydantic.json_schema import SkipJsonSchema

from src.domain.enums import ExpenseCategory
from src.infrastructure.http.schemas.money import ClpResponse, ExpenseAmount

expense_title_aliases = AliasChoices("title", "titulo", "description", "descripcion")
ExpenseTitle = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def _trim_optional_text(value: object) -> object:
    return (value.strip() or None) if isinstance(value, str) else value


OptionalText = Annotated[str | None, BeforeValidator(_trim_optional_text)]


class RegisterExpenseRequest(BaseModel):
    """Cuerpo de la petición para registrar un gasto en terreno o administrativo."""

    id: UUID4 | None = Field(
        default=None,
        description=(
            "UUIDv4 opcional preasignado al gasto, distinto de Idempotency-Key. "
            "Solo se utiliza con clave e identidad válidas; el flujo antiguo "
            "genera su identificador en el servidor."
        ),
    )

    amount: ExpenseAmount = Field(
        ...,
        validation_alias=AliasChoices("amount", "monto"),
        description="Monto del gasto en pesos chilenos enteros.",
        examples=[45990],
    )
    date: dt_date = Field(
        ...,
        validation_alias=AliasChoices("date", "fecha"),
        description="Fecha en que se efectuó el gasto. No puede ser una fecha futura.",
        examples=["2026-11-03"],
    )
    category: ExpenseCategory = Field(
        ...,
        validation_alias=AliasChoices("category", "categoria"),
        description="Categoría operativa del gasto.",
        examples=[ExpenseCategory.MATERIALS],
    )
    title: ExpenseTitle = Field(
        ...,
        validation_alias=expense_title_aliases,
        description="Título breve del gasto.",
        examples=["Compra cable libre de halógeno 2.5 mm² y terminales"],
    )
    detail: OptionalText = Field(
        default=None, validation_alias=AliasChoices("detail", "detalle")
    )
    project_id: UUID | None = Field(
        default=None,
        validation_alias=AliasChoices("project_id", "proyecto_id"),
        description=(
            "ID del proyecto si es un costo directo de obra (CapEx). "
            "Omitir si es un gasto operativo general (OPEX)."
        ),
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    has_receipt: bool = Field(
        default=False, validation_alias=AliasChoices("has_receipt", "tiene_comprobante")
    )
    receipt_url: OptionalText = Field(
        default=None,
        description="Enlace o ruta del comprobante/boleta escaneada (opcional).",
        examples=["https://almacenamiento.ejemplo.com/boletas/boleta_4021.jpg"],
    )


class UpdateExpenseRequest(BaseModel):
    """Datos editables de un gasto. Los campos omitidos conservan su valor."""

    model_config = ConfigDict(extra="forbid")

    amount: ExpenseAmount | SkipJsonSchema[None] = Field(
        default=None, validation_alias=AliasChoices("amount", "monto")
    )
    date: dt_date | SkipJsonSchema[None] = Field(
        default=None, validation_alias=AliasChoices("date", "fecha")
    )
    category: ExpenseCategory | SkipJsonSchema[None] = Field(
        default=None, validation_alias=AliasChoices("category", "categoria")
    )
    title: ExpenseTitle | SkipJsonSchema[None] = Field(
        default=None, validation_alias=expense_title_aliases
    )
    detail: OptionalText = Field(
        default=None, validation_alias=AliasChoices("detail", "detalle")
    )
    project_id: UUID | None = Field(
        default=None,
        validation_alias=AliasChoices("project_id", "proyecto_id"),
        description="Enviar null para mover el gasto a OPEX.",
    )
    has_receipt: bool | SkipJsonSchema[None] = Field(
        default=None, validation_alias=AliasChoices("has_receipt", "tiene_comprobante")
    )
    receipt_url: OptionalText = Field(
        default=None, description="Enviar null para quitar el enlace del comprobante."
    )

    @field_validator("amount", "date", "category", "title", "has_receipt")
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("El campo debe tener un valor si se envía.")
        return value


class ExpenseRead(BaseModel):
    """Representación completa de un gasto registrado en el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="Identificador único universal (UUIDv4) del gasto.",
        examples=["890e1234-e89b-12d3-a456-426614174000"],
    )
    amount: ClpResponse = Field(
        ...,
        description="Monto en pesos chilenos enteros, serializado como cadena.",
        examples=["45990"],
    )
    date: dt_date = Field(
        ...,
        description="Fecha en que se incurrió el gasto.",
        examples=["2026-11-03"],
    )
    category: ExpenseCategory = Field(
        ...,
        description="Categoría operativa a la que pertenece el gasto.",
        examples=[ExpenseCategory.MATERIALS],
    )
    title: str = Field(
        ...,
        description="Título del gasto.",
        examples=["Compra cable libre de halógeno 2.5 mm² y terminales"],
    )
    detail: str | None = None
    has_receipt: bool = Field(
        ...,
        description=(
            "Indica si existe respaldo físico o digital (boleta, factura o voucher)."
        ),
        examples=[True],
    )
    created_at: datetime = Field(
        ...,
        description="Marca temporal UTC de registro del gasto.",
    )
    updated_at: datetime = Field(
        ...,
        description="Marca temporal UTC de la última modificación.",
    )
    project_id: UUID | None = Field(
        default=None,
        description="ID de la obra asociada (None indica que es un gasto OPEX).",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    receipt_url: str | None = Field(
        default=None,
        description="URL o ruta al archivo de la boleta o factura digitalizada.",
        examples=["https://almacenamiento.ejemplo.com/boletas/boleta_4021.jpg"],
    )


class ExpenseResponse(ExpenseRead):
    @computed_field(
        description="Alias de lectura para clientes anteriores. Usa title.",
        json_schema_extra={"deprecated": True},
    )
    def description(self) -> str:
        return self.title


class GastoResponse(ExpenseRead):
    amount: ClpResponse = Field(serialization_alias="monto")
    title: str = Field(serialization_alias="titulo")
    detail: str | None = Field(default=None, serialization_alias="detalle")
    has_receipt: bool = Field(serialization_alias="tiene_comprobante")
