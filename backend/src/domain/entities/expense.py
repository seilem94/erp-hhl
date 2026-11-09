"""Domain entity: Expense.

Pure Python dataclass — no ORM decorators, no Pydantic, no FastAPI.
Supports both project-direct costs (CapEx) and general operational
expenses (OPEX) via the optional 'project_id' field.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from src.domain.enums import Currency, ExpenseCategory


@dataclass
class Expense:
    """A single expense record, either tied to an obra or operational (OPEX).

    Business rules (enforced at the use-case layer):
    - ``amount`` must be greater than zero.
    - ``date`` must not be in the future (date <= today).
    - When ``project_id`` is not None, the referenced project must exist
      and must not be in CANCELLED status.
    - When ``project_id`` is None the expense is classified as OPEX and
      no project validation is performed.

    Attributes:
        id: Unique identifier (UUIDv4).
        amount: Exact cost in local currency (Decimal avoids float errors).
        date: Date the expense was incurred.
        category: Business category of the expense.
        description: Free-text detail or concept (e.g. "Compra cable 2.5mm²").
        has_receipt: True when a boleta/factura/voucher exists as proof.
        created_at: UTC timestamp when the record was created.
        updated_at: UTC timestamp of the last modification.
        project_id: FK to Project. None → OPEX; not None → direct project cost.
        receipt_url: Optional path or URL to the scanned receipt image.
    """

    id: UUID
    amount: Decimal
    date: date
    category: ExpenseCategory
    description: str
    has_receipt: bool
    created_at: datetime
    updated_at: datetime
    project_id: UUID | None = None
    receipt_url: str | None = None
    currency: Currency = Currency.CLP

    @property
    def is_project_expense(self) -> bool:
        """Return True when this expense is directly charged to a project."""
        return self.project_id is not None
