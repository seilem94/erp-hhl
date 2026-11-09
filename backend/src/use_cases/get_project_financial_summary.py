"""Read project totals without leaking resource existence through permission errors."""

from src.domain.exceptions import (
    AuthorizationDeniedError,
    ProjectSummaryUnavailableError,
)
from src.domain.read_models.financial_summary import ProjectFinancialSummary
from src.domain.repositories.financial_summary_repository import (
    FinancialSummaryRepository,
)
from src.use_cases.dto.financial_summary import ProjectSummaryQueryDTO
from src.use_cases.ports.authorization import AuthorizationPort
from src.use_cases.ports.identity import ActorIdentity


class GetProjectFinancialSummaryUseCase:
    def __init__(
        self,
        summary_repo: FinancialSummaryRepository,
        authorization: AuthorizationPort,
        actor: ActorIdentity,
    ) -> None:
        self._summary_repo = summary_repo
        self._authorization = authorization
        self._actor = actor

    def execute(self, dto: ProjectSummaryQueryDTO) -> ProjectFinancialSummary:
        try:
            scope = self._authorization.authorize_summary(self._actor, dto.project_id)
        except AuthorizationDeniedError as exc:
            raise ProjectSummaryUnavailableError() from exc
        if not scope.all_projects and dto.project_id not in scope.project_ids:
            raise ProjectSummaryUnavailableError()
        summary = self._summary_repo.get_project(dto.project_id, dto, scope)
        if summary is None:
            raise ProjectSummaryUnavailableError()
        return summary
