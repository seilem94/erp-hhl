"""Read global financial totals only after verifying full financial permission."""

from src.domain.exceptions import AuthorizationDeniedError
from src.domain.read_models.financial_summary import FinancialSummary
from src.domain.repositories.financial_summary_repository import (
    FinancialSummaryRepository,
)
from src.use_cases.dto.financial_summary import FinancialSummaryQueryDTO
from src.use_cases.ports.authorization import AuthorizationPort
from src.use_cases.ports.identity import ActorIdentity


class GetFinancialSummaryUseCase:
    def __init__(
        self,
        summary_repo: FinancialSummaryRepository,
        authorization: AuthorizationPort,
        actor: ActorIdentity,
    ) -> None:
        self._summary_repo = summary_repo
        self._authorization = authorization
        self._actor = actor

    def execute(self, dto: FinancialSummaryQueryDTO) -> FinancialSummary:
        scope = self._authorization.authorize_summary(self._actor)
        if not scope.all_projects or not scope.include_operational:
            raise AuthorizationDeniedError("Global financial permission is required.")
        return self._summary_repo.get_general(dto, scope)
