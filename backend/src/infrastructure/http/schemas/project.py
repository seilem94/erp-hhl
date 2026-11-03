"""Esquemas HTTP para la gestión de proyectos y obras eléctricas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ProjectStatus


class CreateProjectRequest(BaseModel):
    """Cuerpo de la petición para crear o cotizar una nueva obra eléctrica."""

    name: str = Field(
        ...,
        description="Nombre descriptivo o identificación de la obra eléctrica.",
        examples=["Instalación Tablero General Edificio Central"],
    )
    client: str = Field(
        ...,
        description="Nombre de la empresa mandante o cliente particular.",
        examples=["Constructora Alerce S.A."],
    )
    estimated_budget: Decimal | None = Field(
        default=None,
        description=(
            "Presupuesto acordado o estimado para la obra en moneda local (opcional)."
        ),
        examples=[Decimal("5000000.00")],
    )
    description: str | None = Field(
        default=None,
        description="Alcance técnico o descripción detallada de la obra (opcional).",
        examples=["Instalación de tableros TDA y cableado subterráneo."],
    )


class UpdateProjectRequest(BaseModel):
    """Cuerpo de la petición para actualización parcial de una obra eléctrica."""

    name: str | None = Field(
        default=None,
        description="Nuevo nombre descriptivo de la obra eléctrica (opcional).",
        examples=["Instalación Tablero General Edificio Central - Fase 2"],
    )
    client: str | None = Field(
        default=None,
        description="Nuevo nombre de la empresa mandante o cliente (opcional).",
        examples=["Constructora Alerce S.A."],
    )
    estimated_budget: Decimal | None = Field(
        default=None,
        description="Nuevo presupuesto acordado o estimado para la obra (opcional).",
        examples=[Decimal("7500000.00")],
    )
    status: ProjectStatus | None = Field(
        default=None,
        description="Nuevo estado del ciclo de vida de la obra (opcional).",
        examples=[ProjectStatus.IN_PROGRESS],
    )
    description: str | None = Field(
        default=None,
        description="Nuevo alcance técnico o notas de la obra (opcional).",
        examples=["Ampliación de tablero de distribución y alimentadores."],
    )


class ProjectResponse(BaseModel):
    """Representación completa de una obra eléctrica en el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(
        ...,
        description="Identificador único universal (UUIDv4) del proyecto.",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    name: str = Field(
        ...,
        description="Nombre descriptivo de la obra eléctrica.",
        examples=["Instalación Tablero General Edificio Central"],
    )
    client: str = Field(
        ...,
        description="Cliente o empresa mandante de la obra.",
        examples=["Constructora Alerce S.A."],
    )
    status: ProjectStatus = Field(
        ...,
        description="Estado actual del ciclo de vida de la obra.",
        examples=[ProjectStatus.PLANNING],
    )
    start_date: date = Field(
        ...,
        description="Fecha de inicio programada o real de la obra.",
        examples=["2026-11-03"],
    )
    created_at: datetime = Field(
        ...,
        description="Marca temporal UTC de creación del registro.",
    )
    updated_at: datetime = Field(
        ...,
        description="Marca temporal UTC de la última actualización.",
    )
    description: str | None = Field(
        default=None,
        description="Alcance técnico o notas adicionales de la obra.",
        examples=["Montaje de tableros TDA y cableado subterráneo."],
    )
    end_date: date | None = Field(
        default=None,
        description="Fecha estimada o efectiva de entrega de la obra.",
        examples=["2026-12-15"],
    )
    budget: Decimal | None = Field(
        default=None,
        description="Presupuesto final o actual asignado a la obra.",
        examples=[Decimal("5000000.00")],
    )
