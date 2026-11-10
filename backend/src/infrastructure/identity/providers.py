"""Local development adapters; production never falls back to a dummy actor."""

from uuid import UUID

from src.core.config import Environment
from src.domain.entities.operation import OperationRecord
from src.domain.enums import CommandType
from src.domain.exceptions import (
    AuthorizationDeniedError,
    IdentityProviderUnavailableError,
)
from src.domain.read_models.financial_summary import FinancialReadScope
from src.use_cases.ports.authorization import AuthorizationPort
from src.use_cases.ports.identity import ActorIdentity, IdentityProvider

DEVELOPMENT_ACTOR_ID = UUID("00000000-0000-4000-8000-000000000001")


class DevelopmentIdentityProvider:
    """One stable local actor simulating a socio, with no authenticated session."""

    def get_actor(self) -> ActorIdentity:
        return ActorIdentity(actor_id=DEVELOPMENT_ACTOR_ID, is_development=True)


class UnavailableIdentityProvider:
    def get_actor(self) -> ActorIdentity:
        raise IdentityProviderUnavailableError(
            "No verified identity provider configured."
        )


class DevelopmentAuthorization:
    def _check_actor(self, actor: ActorIdentity) -> None:
        if not actor.is_development or actor.actor_id != DEVELOPMENT_ACTOR_ID:
            raise AuthorizationDeniedError(
                "Not the configured local development actor."
            )

    def authorize_summary(
        self, actor: ActorIdentity, project_id: UUID | None = None
    ) -> FinancialReadScope:
        self._check_actor(actor)
        if project_id is None:
            return FinancialReadScope(all_projects=True, include_operational=True)
        return FinancialReadScope(project_ids=frozenset({project_id}))

    def authorize_command(
        self,
        actor: ActorIdentity,
        command_type: CommandType,
        target_resource_id: UUID | None,
        *,
        project_id: UUID | None = None,
    ) -> None:
        self._check_actor(actor)

    def authorize_operation_result(
        self, actor: ActorIdentity, operation: OperationRecord
    ) -> None:
        self._check_actor(actor)
        if operation.key.actor_id != actor.actor_id:
            raise AuthorizationDeniedError("Cannot recover another actor's operation.")


class DenyAllAuthorization:
    def authorize_summary(
        self, actor: ActorIdentity, project_id: UUID | None = None
    ) -> FinancialReadScope:
        raise AuthorizationDeniedError("No authorization provider configured.")

    def authorize_command(
        self,
        actor: ActorIdentity,
        command_type: CommandType,
        target_resource_id: UUID | None,
        *,
        project_id: UUID | None = None,
    ) -> None:
        raise AuthorizationDeniedError("No authorization provider configured.")

    def authorize_operation_result(
        self, actor: ActorIdentity, operation: OperationRecord
    ) -> None:
        raise AuthorizationDeniedError("No authorization provider configured.")


def build_identity_provider(environment: Environment) -> IdentityProvider:
    if environment is Environment.DEVELOPMENT:
        return DevelopmentIdentityProvider()
    return UnavailableIdentityProvider()


def build_authorization(environment: Environment) -> AuthorizationPort:
    if environment is Environment.DEVELOPMENT:
        return DevelopmentAuthorization()
    return DenyAllAuthorization()
