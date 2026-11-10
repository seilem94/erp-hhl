"""Esquemas HTTP para el registro y consulta de gastos (CapEx y OPEX)."""

from __future__ import annotations

from datetime import date as dt_date
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import UUID4, BaseModel, ConfigDict, Field

from src.domain.enums import ExpenseCategory


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

    amount: Decimal = Field(
        ...,
        description="Monto exacto del gasto en moneda local. Debe ser mayor a 0.",
        examples=[Decimal("45990.00")],
    )
    date: dt_date = Field(
        ...,
        description="Fecha en que se efectuó el gasto. No puede ser una fecha futura.",
        examples=["2026-11-03"],
    )
    category: ExpenseCategory = Field(
        ...,
        description="Categoría operativa del gasto.",
        examples=[ExpenseCategory.MATERIALS],
    )
    description: str = Field(
        ...,
        description=(
            "Detalle o concepto del gasto (ej. compra de materiales, combustible, "
            "colación de cuadrilla)."
        ),
        examples=["Compra cable libre de halógeno 2.5 mm² y terminales"],
    )
    project_id: UUID | None = Field(
        default=None,
        description=(
            "ID del proyecto si es un costo directo de obra (CapEx). "
            "Omitir si es un gasto operativo general (OPEX)."
        ),
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    receipt_url: str | None = Field(
        default=None,
        description="Enlace o ruta del comprobante/boleta escaneada (opcional).",
        examples=["https://almacenamiento.ejemplo.com/boletas/boleta_4021.jpg"],
    )


class ExpenseResponse(BaseModel):
    """Representación completa de un gasto registrado en el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="Identificador único universal (UUIDv4) del gasto.",
        examples=["890e1234-e89b-12d3-a456-426614174000"],
    )
    amount: Decimal = Field(
        ...,
        description="Monto exacto registrado para el gasto.",
        examples=[Decimal("45990.00")],
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
    description: str = Field(
        ...,
        description="Detalle o justificación del gasto.",
        examples=["Compra cable libre de halógeno 2.5 mm² y terminales"],
    )
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
