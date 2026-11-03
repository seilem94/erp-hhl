"""HTTP request and response schemas for expenses."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.domain.enums import ExpenseCategory


class RegisterExpenseRequest(BaseModel):
    """Payload to register a new expense."""

    amount: Decimal
    date: date
    category: ExpenseCategory
    description: str
    project_id: UUID | None = None
    receipt_url: str | None = None


class ExpenseResponse(BaseModel):
    """Response payload representing an expense."""

    model_config = ConfigDict(from_attributes=True)

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
