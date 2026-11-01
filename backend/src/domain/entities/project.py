"""Domain entity: Project (obra eléctrica).

Pure Python dataclass — no ORM decorators, no Pydantic, no FastAPI.
Constraints are enforced at the use-case layer, not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from src.domain.enums import ProjectStatus


@dataclass
class Project:
    """Represents an electrical project or obra assigned to a client.

    Attributes:
        id: Unique identifier (UUIDv4).
        name: Human-readable name of the obra
              (e.g. "Instalación Tablero General Edificio Central").
        client: Name of the contracting client or company.
        status: Current lifecycle state of the project.
        start_date: Date on which fieldwork begins.
        created_at: UTC timestamp when the record was created.
        updated_at: UTC timestamp of the last modification.
        description: Optional scope or technical notes for the obra.
        end_date: Estimated or actual delivery date (None if not set yet).
        budget: Agreed or estimated budget in local currency (None if TBD).
    """

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
