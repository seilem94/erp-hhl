"""Authorization is independent of transport, sessions and role storage."""

from typing import Protocol
from uuid import UUID

from src.domain.entities.operation import OperationRecord
from src.domain.enums import CommandType
from src.domain.read_models.financial_summary import FinancialReadScope
from src.use_cases.ports.identity import ActorIdentity


class AuthorizationPort(Protocol):
    def authorize_summary(
        self, actor: ActorIdentity, project_id: UUID | None = None
    ) -> FinancialReadScope:
        """Resolve the visible scope or raise AuthorizationDeniedError."""
        ...

    def authorize_command(
        self,
        actor: ActorIdentity,
        command_type: CommandType,
        target_resource_id: UUID | None,
    ) -> None:
        """Check current permission before executing a command."""
        ...

    def authorize_operation_result(
        self, actor: ActorIdentity, operation: OperationRecord
    ) -> None:
        """Recheck current permissions and ownership before revealing a result."""
        ...
