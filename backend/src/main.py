"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.domain.exceptions import DomainException
from src.infrastructure.http.error_handlers import domain_exception_handler
from src.infrastructure.http.routers.expenses import router as expenses_router
from src.infrastructure.http.routers.projects import router as projects_router

app = FastAPI(
    title="ERP HHL API",
    description="Backend API for ERP HHL (electrical works and operations management).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(DomainException, domain_exception_handler)  # type: ignore[arg-type]

app.include_router(projects_router)
app.include_router(expenses_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Health check endpoint to verify API availability."""
    return {"status": "ok"}
