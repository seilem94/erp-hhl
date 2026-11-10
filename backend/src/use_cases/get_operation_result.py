"""Read an actor's immutable confirmation without executing a command."""

from src.domain.entities.operation import OperationRecord
from src.domain.enums import OperationState
from src.domain.exceptions import (
    AuthorizationDeniedError,
    OperationNotFoundError,
    OperationUnresolvedError,
)
from src.domain.repositories.operation_repository import OperationRepository
from src.use_cases.dto.operation import GetOperationResultDTO
from src.use_cases.ports.authorization import AuthorizationPort


class GetOperationResultUseCase:
    def __init__(
        self, repository: OperationRepository, authorization: AuthorizationPort
    ) -> None:
        self._repository = repository
        self._authorization = authorization

    def execute(self, dto: GetOperationResultDTO) -> OperationRecord:
        # Authorize the stable references before fetching/decoding a potentially
        # purged, corrupt or unsupported payload. Never search by UUID alone.
        metadata = self._repository.get_by_key(dto.context.key, include_payload=False)
        self._authorize(dto, metadata)
        if metadata is not None and metadata.state is OperationState.RESERVED:
            raise OperationUnresolvedError(
                "The operation is not confirmed; retain the same operation key."
            )
        operation = self._repository.get_by_key(dto.context.key)
        if operation is None:
            raise OperationUnresolvedError(
                "The known operation is no longer visible; retain the same key."
            )
        # The two reads may straddle a concurrent state change. Recheck current
        # references before revealing the result, then validate recoverability.
        self._authorize(dto, operation)
        operation.recover_result()
        return operation

    def _authorize(
        self, dto: GetOperationResultDTO, operation: OperationRecord | None
    ) -> None:
        if operation is None or operation.key != dto.context.key:
            raise OperationNotFoundError()
        try:
            self._authorization.authorize_operation_result(dto.context.actor, operation)
        except AuthorizationDeniedError as exc:
            raise OperationNotFoundError() from exc
