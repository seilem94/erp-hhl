"""FastAPI dependency injection factories for repositories and use cases."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.domain.repositories.expense_repository import ExpenseRepository
from src.domain.repositories.project_repository import ProjectRepository
from src.infrastructure.database.repositories.sqlalchemy_expense_repository import (
    SQLAlchemyExpenseRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from src.infrastructure.database.session import get_db
from src.use_cases.create_project import CreateProjectUseCase
from src.use_cases.get_operational_expenses import GetOperationalExpensesUseCase
from src.use_cases.get_project_expenses import GetProjectExpensesUseCase
from src.use_cases.list_projects import ListProjectsUseCase
from src.use_cases.register_daily_expense import RegisterDailyExpenseUseCase

SessionDep = Annotated[Session, Depends(get_db)]


def get_project_repo(
    session: SessionDep,
) -> SQLAlchemyProjectRepository:
    """Provide a SQLAlchemyProjectRepository bound to the current database session."""
    return SQLAlchemyProjectRepository(session)


def get_expense_repo(
    session: SessionDep,
) -> SQLAlchemyExpenseRepository:
    """Provide a SQLAlchemyExpenseRepository bound to the current database session."""
    return SQLAlchemyExpenseRepository(session)


ProjectRepoDep = Annotated[ProjectRepository, Depends(get_project_repo)]
ExpenseRepoDep = Annotated[ExpenseRepository, Depends(get_expense_repo)]


def get_create_project_uc(
    project_repo: ProjectRepoDep,
) -> CreateProjectUseCase:
    """Instantiate CreateProjectUseCase with injected repository."""
    return CreateProjectUseCase(project_repo)


def get_list_projects_uc(
    project_repo: ProjectRepoDep,
) -> ListProjectsUseCase:
    """Instantiate ListProjectsUseCase with injected repository."""
    return ListProjectsUseCase(project_repo)


def get_register_expense_uc(
    expense_repo: ExpenseRepoDep,
    project_repo: ProjectRepoDep,
) -> RegisterDailyExpenseUseCase:
    """Instantiate RegisterDailyExpenseUseCase with injected repositories."""
    return RegisterDailyExpenseUseCase(expense_repo, project_repo)


def get_project_expenses_uc(
    expense_repo: ExpenseRepoDep,
    project_repo: ProjectRepoDep,
) -> GetProjectExpensesUseCase:
    """Instantiate GetProjectExpensesUseCase with injected repositories."""
    return GetProjectExpensesUseCase(expense_repo, project_repo)


def get_operational_expenses_uc(
    expense_repo: ExpenseRepoDep,
) -> GetOperationalExpensesUseCase:
    """Instantiate GetOperationalExpensesUseCase with injected repository."""
    return GetOperationalExpensesUseCase(expense_repo)
