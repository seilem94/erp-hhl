"""FastAPI dependency injection factories for repositories and use cases."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.core.config import settings
from src.domain.repositories.expense_repository import ExpenseRepository
from src.domain.repositories.financial_summary_repository import (
    FinancialSummaryRepository,
)
from src.domain.repositories.project_repository import ProjectRepository
from src.infrastructure.database.repositories.sqlalchemy_expense_repository import (
    SQLAlchemyExpenseRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_financial_summary_repository import (  # noqa: E501
    SQLAlchemyFinancialSummaryRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from src.infrastructure.database.session import get_db
from src.infrastructure.identity.providers import (
    build_authorization,
    build_identity_provider,
)
from src.use_cases.create_project import CreateProjectUseCase
from src.use_cases.get_financial_summary import GetFinancialSummaryUseCase
from src.use_cases.get_operational_expenses import GetOperationalExpensesUseCase
from src.use_cases.get_project_expenses import GetProjectExpensesUseCase
from src.use_cases.get_project_financial_summary import (
    GetProjectFinancialSummaryUseCase,
)
from src.use_cases.list_projects import ListProjectsUseCase
from src.use_cases.ports.authorization import AuthorizationPort
from src.use_cases.ports.identity import ActorIdentity, IdentityProvider
from src.use_cases.register_daily_expense import RegisterDailyExpenseUseCase
from src.use_cases.update_project import UpdateProjectUseCase

SessionDep = Annotated[Session, Depends(get_db)]


def get_identity_provider() -> IdentityProvider:
    return build_identity_provider(settings.ENV)


def get_actor_identity(
    provider: Annotated[IdentityProvider, Depends(get_identity_provider)],
) -> ActorIdentity:
    return provider.get_actor()


def get_authorization() -> AuthorizationPort:
    return build_authorization(settings.ENV)


def get_financial_summary_repo(session: SessionDep) -> FinancialSummaryRepository:
    return SQLAlchemyFinancialSummaryRepository(session)


SummaryRepoDep = Annotated[
    FinancialSummaryRepository, Depends(get_financial_summary_repo)
]
AuthorizationDep = Annotated[AuthorizationPort, Depends(get_authorization)]
ActorDep = Annotated[ActorIdentity, Depends(get_actor_identity)]


def get_financial_summary_uc(
    summary_repo: SummaryRepoDep, authorization: AuthorizationDep, actor: ActorDep
) -> GetFinancialSummaryUseCase:
    return GetFinancialSummaryUseCase(summary_repo, authorization, actor)


def get_project_financial_summary_uc(
    summary_repo: SummaryRepoDep, authorization: AuthorizationDep, actor: ActorDep
) -> GetProjectFinancialSummaryUseCase:
    return GetProjectFinancialSummaryUseCase(summary_repo, authorization, actor)


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


def get_update_project_uc(
    project_repo: ProjectRepoDep,
) -> UpdateProjectUseCase:
    """Instantiate UpdateProjectUseCase with injected repository."""
    return UpdateProjectUseCase(project_repo)


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
