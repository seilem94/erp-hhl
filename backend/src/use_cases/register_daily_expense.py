"""Use case: Register a daily expense (direct project cost or OPEX).

This module contains:
- ``RegisterDailyExpenseDTO``  – immutable input contract from the interface layer.
- ``RegisterDailyExpenseUseCase`` – orchestrates validation and persistence.

Design constraints:
- Pure Python 3.11+; zero dependencies on FastAPI, SQLAlchemy, or Pydantic.
- Strict typing: no ``Any``.
- Date provider is injected for deterministic unit testing.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from src.domain.entities.expense import Expense
from src.domain.enums import ExpenseCategory, ProjectStatus
from src.domain.exceptions import (
    InvalidExpenseAmountError,
    InvalidExpenseDateError,
    ProjectCancelledError,
    ProjectNotFoundError,
)
from src.domain.repositories.expense_repository import ExpenseRepository
from src.domain.repositories.project_repository import ProjectRepository


@dataclass(frozen=True)
class RegisterDailyExpenseDTO:
    """Immutable input contract for ``RegisterDailyExpenseUseCase``.

    The interface layer (FastAPI schema, CLI, test fixture …) constructs this
    object from raw user input after basic format/type validation.  Business
    rule validation is the responsibility of the use case.

    Attributes:
        amount: Cost amount in local currency.  Must be > 0.
        date: Date on which the expense was incurred.  Must be <= today.
        category: Business category of the expense.
        description: Free-text concept (e.g. "Compra cable 2.5 mm²").
        project_id: UUID of the target project.  None → OPEX expense.
        has_receipt: True when a physical receipt exists but is not yet
            uploaded.  Automatically forced to True when ``receipt_url``
            is provided.
        receipt_url: Optional path or URL of the scanned receipt image.
            Setting this implies ``has_receipt = True``; the use case
            enforces this invariant during execution.
    """

    amount: Decimal
    date: date
    category: ExpenseCategory
    description: str
    project_id: UUID | None = None
    has_receipt: bool = False
    receipt_url: str | None = None


class RegisterDailyExpenseUseCase:
    """Register a new expense — either a direct project cost or an OPEX entry.

    Validation pipeline (executed in order):
    1. ``amount`` must be strictly positive.
    2. ``date`` must not be in the future.
    3. If ``project_id`` is not None:
       a. The project must exist in the repository.
       b. The project must not be in ``CANCELLED`` status.
    4. Receipt coherence: ``has_receipt`` is normalised to ``True`` whenever
       ``receipt_url`` is present, regardless of the value in the DTO.
    5. A new ``Expense`` entity is built with a generated UUID and UTC
       timestamps, then persisted via the repository.

    Args:
        expense_repo: Persistence adapter for ``Expense`` entities.
        project_repo: Persistence adapter for ``Project`` entities.
        date_provider: Zero-argument callable that returns the current date.
            Defaults to ``date.today``; inject a fixed value in tests for
            deterministic behaviour.
    """

    def __init__(
        self,
        expense_repo: ExpenseRepository,
        project_repo: ProjectRepository,
        date_provider: Callable[[], date] = date.today,
    ) -> None:
        self._expense_repo = expense_repo
        self._project_repo = project_repo
        self._date_provider = date_provider

    def execute(self, dto: RegisterDailyExpenseDTO) -> Expense:
        """Validate, build, persist and return a new ``Expense`` entity.

        Args:
            dto: Immutable input data from the interface layer.

        Returns:
            The persisted ``Expense`` entity with server-generated fields
            (``id``, ``created_at``, ``updated_at``).

        Raises:
            InvalidExpenseAmountError: If ``dto.amount`` is zero or negative.
            InvalidExpenseDateError: If ``dto.date`` is strictly in the future.
            ProjectNotFoundError: If ``dto.project_id`` is set but the project
                does not exist.
            ProjectCancelledError: If the referenced project is CANCELLED.
        """
        # ── 1. Amount validation ──────────────────────────────────────────────
        if dto.amount <= Decimal("0"):
            raise InvalidExpenseAmountError(dto.amount)

        # ── 2. Date validation ────────────────────────────────────────────────
        today = self._date_provider()
        if dto.date > today:
            raise InvalidExpenseDateError(dto.date, today)

        # ── 3. Project validation (only when this is a project expense) ───────
        if dto.project_id is not None:
            project = self._project_repo.get_by_id(dto.project_id)
            if project is None:
                raise ProjectNotFoundError(dto.project_id)
            if project.status == ProjectStatus.CANCELLED:
                raise ProjectCancelledError(dto.project_id, project.status)

        # ── 4. Receipt coherence normalisation ────────────────────────────────
        has_receipt: bool = True if dto.receipt_url is not None else dto.has_receipt

        # ── 5. Build entity and persist ───────────────────────────────────────
        now = datetime.now(UTC)
        expense = Expense(
            id=uuid4(),
            amount=dto.amount,
            date=dto.date,
            category=dto.category,
            description=dto.description,
            has_receipt=has_receipt,
            receipt_url=dto.receipt_url,
            project_id=dto.project_id,
            created_at=now,
            updated_at=now,
        )

        return self._expense_repo.save(expense)
