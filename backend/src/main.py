"""Punto de entrada de la aplicación FastAPI para ERP HHL."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.domain.exceptions import DomainException
from src.infrastructure.http.error_handlers import domain_exception_handler
from src.infrastructure.http.routers.expenses import router as expenses_router
from src.infrastructure.http.routers.financial_summaries import (
    router as summaries_router,
)
from src.infrastructure.http.routers.projects import router as projects_router

tags_metadata = [
    {
        "name": "Proyectos",
        "description": (
            "Gestión integral de obras eléctricas: cotización, planificación, "
            "ejecución y seguimiento de estados."
        ),
    },
    {
        "name": "Gastos",
        "description": (
            "Control de gastos en terreno para obras (CapEx) y "
            "gastos operativos generales (OPEX)."
        ),
    },
    {
        "name": "Sistema",
        "description": (
            "Endpoints de monitoreo, estado y salud de la infraestructura de la API."
        ),
    },
]

app = FastAPI(
    title="ERP HHL — API de Gestión de Obras y Gastos",
    description=(
        "API REST modular diseñada bajo Clean Architecture para el control "
        "operativo en terreno, compras de insumos, control financiero por obra "
        "y administración de proyectos eléctricos de HHL."
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Idempotency-Replayed"],
)

app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]

app.include_router(projects_router)
app.include_router(expenses_router)
app.include_router(summaries_router)


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Verificación de estado de la API",
    description="Comprueba que la API esté activa y respondiendo peticiones.",
)
def health_check() -> dict[str, str]:
    """Retorna el estado de disponibilidad del servicio."""
    return {"status": "ok"}
