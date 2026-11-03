"""HTTP request and response schemas for projects."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.enums import ProjectStatus


class CreateProjectRequest(BaseModel):
    """Payload to create a new project."""

    name: str
    client: str
    estimated_budget: Decimal | None = None


class ProjectResponse(BaseModel):
    """Response payload representing a project."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    client: str
    status: ProjectStatus
    start_date: date
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    end_date: date | None = None
    budget: Decimal | None = None
