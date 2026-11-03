"""Esquema de respuesta de error HTTP estándar."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Estructura uniforme para respuestas de error de la API."""

    detail: str = Field(
        ...,
        description="Mensaje descriptivo del motivo del error o validación.",
        examples=["Proyecto '123e4567-e89b-12d3-a456-426614174000' no encontrado."],
    )
