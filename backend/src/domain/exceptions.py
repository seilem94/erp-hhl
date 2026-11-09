"""Domain-level exceptions.

All exceptions are pure Python — zero framework dependencies.
The infrastructure layer (FastAPI, etc.) is responsible for catching
these and mapping them to the appropriate HTTP status codes.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from src.domain.enums import ProjectStatus


class DomainException(Exception):
    """Base class for all domain exceptions.

    Catching this class covers every domain-level error; prefer the
    concrete subclasses when you need to react to a specific condition.
    """


class EntityNotFoundError(DomainException):
    """Base class for 'resource does not exist' errors (→ HTTP 404)."""


class ProjectNotFoundError(EntityNotFoundError):
    """Raised when a project_id is provided but no matching project exists.

    Args:
        project_id: The UUID that was looked up and not found.
    """

    def __init__(self, project_id: UUID) -> None:
        self.project_id = project_id
        super().__init__(f"Project '{project_id}' not found.")


class BusinessRuleViolationError(DomainException):
    """Base class for business-rule violations (→ HTTP 422)."""


class ProjectCancelledError(BusinessRuleViolationError):
    """Raised when an expense targets a project in CANCELLED status.

    Args:
        project_id: UUID of the cancelled project.
        current_status: The status that was found (always CANCELLED).
    """

    def __init__(self, project_id: UUID, current_status: ProjectStatus) -> None:
        self.project_id = project_id
        self.current_status = current_status
        super().__init__(
            f"Project '{project_id}' is in '{current_status}' status "
            "and cannot accept new expenses."
        )


class InvalidExpenseDateError(BusinessRuleViolationError):
    """Raised when the expense date is strictly in the future.

    Args:
        expense_date: The date supplied by the caller.
        today: The reference date used for validation.
    """

    def __init__(self, expense_date: date, today: date) -> None:
        self.expense_date = expense_date
        self.today = today
        super().__init__(
            f"Expense date '{expense_date}' is in the future (today is '{today}')."
        )


class InvalidExpenseAmountError(BusinessRuleViolationError):
    """Raised when the expense amount is zero or negative.

    Args:
        amount: The invalid amount that was supplied.
    """

    def __init__(self, amount: Decimal) -> None:
        self.amount = amount
        super().__init__(f"Expense amount must be greater than zero, got '{amount}'.")


class InvalidSummaryDateRangeError(BusinessRuleViolationError):
    """The inclusive summary interval is inverted."""

    def __init__(self, start_date: date, end_date: date) -> None:
        self.start_date = start_date
        self.end_date = end_date
        super().__init__("Summary start_date must not be after end_date.")


class InvalidOperationIdError(BusinessRuleViolationError):
    """The stable operation identifier is not a UUIDv4."""


class InvalidCanonicalContentError(BusinessRuleViolationError):
    """Canonical requests contain unsupported or non-finite content."""


class IdempotencyConflictError(DomainException):
    """A known operation key identifies another command or content."""


class OperationUnresolvedError(DomainException):
    """Resolution is uncertain; recovery must retain the same operation key."""


class OperationNotFoundError(EntityNotFoundError):
    """No operation is visible; this does not prove it is not in transit."""


class OperationReconciliationRequiredError(DomainException):
    """A known confirmation has no recoverable payload; never execute it again."""


class IdentityProviderUnavailableError(DomainException):
    """No verified identity provider is configured outside local development."""


class AuthorizationDeniedError(DomainException):
    """The current actor cannot perform the requested action."""


class ProjectSummaryUnavailableError(EntityNotFoundError):
    """Do not distinguish missing, excluded and unauthorized project summaries."""

    def __init__(self) -> None:
        super().__init__("Project summary is unavailable.")


class FinancialSummaryUnavailableError(DomainException):
    """Persistence failed; never replace missing aggregates with partial totals."""
