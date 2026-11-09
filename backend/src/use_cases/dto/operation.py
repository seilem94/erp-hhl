"""Command envelopes leave legacy use cases unchanged until their integration."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.operation import OperationKey
from src.use_cases.create_project import CreateProjectDTO
from src.use_cases.ports.identity import ActorIdentity
from src.use_cases.register_daily_expense import RegisterDailyExpenseDTO
from src.use_cases.update_project import UpdateProjectDTO


@dataclass(frozen=True, kw_only=True)
class OperationContextDTO:
    actor: ActorIdentity
    operation_id: UUID

    def __post_init__(self) -> None:
        OperationKey(actor_id=self.actor.actor_id, operation_id=self.operation_id)

    @property
    def key(self) -> OperationKey:
        return OperationKey(
            actor_id=self.actor.actor_id, operation_id=self.operation_id
        )


@dataclass(frozen=True, kw_only=True)
class GetOperationResultDTO:
    context: OperationContextDTO


@dataclass(frozen=True, kw_only=True)
class CreateProjectCommandDTO:
    context: OperationContextDTO
    data: CreateProjectDTO
    resource_id: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class RegisterExpenseCommandDTO:
    context: OperationContextDTO
    data: RegisterDailyExpenseDTO
    resource_id: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class UpdateProjectCommandDTO:
    context: OperationContextDTO
    data: UpdateProjectDTO
