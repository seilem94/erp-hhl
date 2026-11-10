"""Typed command envelopes, separate from transport and resource identity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from src.domain.entities.operation import OperationKey
from src.use_cases.ports.identity import ActorIdentity

if TYPE_CHECKING:
    from src.use_cases.create_project import CreateProjectDTO
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

    @property
    def resource_id(self) -> UUID | None:
        return self.data.id


@dataclass(frozen=True, kw_only=True)
class RegisterExpenseCommandDTO:
    context: OperationContextDTO
    data: RegisterDailyExpenseDTO

    @property
    def resource_id(self) -> UUID | None:
        return self.data.id


@dataclass(frozen=True, kw_only=True)
class UpdateProjectCommandDTO:
    context: OperationContextDTO
    data: UpdateProjectDTO
