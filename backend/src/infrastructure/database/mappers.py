"""Pure mapping functions between ORM models and domain dataclasses.

No business logic lives here — only structural translation.  Each
function is a plain module-level function (no class needed) so it can
be imported and tested without any ORM session.

Conversion direction naming convention
---------------------------------------
*_to_domain   : ORM model  → domain dataclass
domain_to_*   : domain dataclass → ORM model
"""

from __future__ import annotations

from src.domain.entities.expense import Expense
from src.domain.entities.project import Project
from src.domain.enums import ExpenseCategory, ProjectStatus
from src.infrastructure.database.models import ExpenseORM, ProjectORM

# ---------------------------------------------------------------------------
# Project mappers
# ---------------------------------------------------------------------------


def project_to_domain(orm: ProjectORM) -> Project:
    """Convert a :class:`ProjectORM` row into a :class:`Project` dataclass.

    Args:
        orm: A hydrated SQLAlchemy ORM instance fetched from the DB.

    Returns:
        An equivalent pure-Python domain object.
    """
    return Project(
        id=orm.id,
        name=orm.name,
        client=orm.client,
        status=ProjectStatus(orm.status),
        start_date=orm.start_date,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        description=orm.description,
        end_date=orm.end_date,
        budget=orm.budget,
    )


def domain_to_project_orm(project: Project) -> ProjectORM:
    """Convert a :class:`Project` domain dataclass into a :class:`ProjectORM`.

    The returned object is *detached* from any session; the caller is
    responsible for adding it to an active session before flushing.

    Args:
        project: A domain dataclass instance (may be newly created or
                 fetched from a repository).

    Returns:
        A :class:`ProjectORM` ready to be persisted.
    """
    return ProjectORM(
        id=project.id,
        name=project.name,
        client=project.client,
        # StrEnum values are plain strings; SQLAlchemy stores them as-is.
        status=str(project.status),
        start_date=project.start_date,
        created_at=project.created_at,
        updated_at=project.updated_at,
        description=project.description,
        end_date=project.end_date,
        budget=project.budget,
    )


# ---------------------------------------------------------------------------
# Expense mappers
# ---------------------------------------------------------------------------


def expense_to_domain(orm: ExpenseORM) -> Expense:
    """Convert an :class:`ExpenseORM` row into an :class:`Expense` dataclass.

    Args:
        orm: A hydrated SQLAlchemy ORM instance fetched from the DB.

    Returns:
        An equivalent pure-Python domain object.
    """
    return Expense(
        id=orm.id,
        amount=orm.amount,
        date=orm.date,
        category=ExpenseCategory(orm.category),
        description=orm.description,
        has_receipt=orm.has_receipt,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        project_id=orm.project_id,
        receipt_url=orm.receipt_url,
    )


def domain_to_expense_orm(expense: Expense) -> ExpenseORM:
    """Convert an :class:`Expense` domain dataclass into an :class:`ExpenseORM`.

    The returned object is *detached* from any session; the caller is
    responsible for adding it to an active session before flushing.

    Args:
        expense: A domain dataclass instance.

    Returns:
        An :class:`ExpenseORM` ready to be persisted.
    """
    return ExpenseORM(
        id=expense.id,
        amount=expense.amount,
        date=expense.date,
        # StrEnum values are plain strings; SQLAlchemy stores them as-is.
        category=str(expense.category),
        description=expense.description,
        has_receipt=expense.has_receipt,
        created_at=expense.created_at,
        updated_at=expense.updated_at,
        project_id=expense.project_id,
        receipt_url=expense.receipt_url,
    )
