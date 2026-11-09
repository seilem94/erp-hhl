"""Automatic local identity selection and strict separation from other environments."""

from typing import Annotated
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.core.config import Environment, Settings, settings
from src.domain.exceptions import (
    AuthorizationDeniedError,
    IdentityProviderUnavailableError,
)
from src.infrastructure.http.dependencies import get_actor_identity
from src.infrastructure.identity.providers import (
    DEVELOPMENT_ACTOR_ID,
    build_authorization,
    build_identity_provider,
)
from src.use_cases.ports.identity import ActorIdentity


def test_development_dependency_injects_stable_actor_without_request_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ENV", Environment.DEVELOPMENT)
    app = FastAPI()

    @app.get("/actor")
    def actor_route(
        actor: Annotated[ActorIdentity, Depends(get_actor_identity)],
    ) -> dict[str, str]:
        assert actor.is_development
        return {"actor_id": str(actor.actor_id)}

    with TestClient(app) as client:
        first = client.get("/actor")
        second = client.get("/actor", headers={"X-Actor-ID": str(uuid4())})
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json() == {"actor_id": str(DEVELOPMENT_ACTOR_ID)}


@pytest.mark.parametrize("environment", [Environment.PRODUCTION, Environment.TESTING])
def test_non_development_environments_never_fall_back_to_dummy(
    environment: Environment,
) -> None:
    with pytest.raises(IdentityProviderUnavailableError):
        build_identity_provider(environment).get_actor()
    with pytest.raises(AuthorizationDeniedError):
        build_authorization(environment).authorize_summary(
            ActorIdentity(actor_id=DEVELOPMENT_ACTOR_ID, is_development=True)
        )


def test_environment_default_does_not_enable_dummy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ENV", raising=False)
    configured = Settings(
        _env_file=None,
        DATABASE_URL="postgresql+psycopg://test:test@localhost/hhl_contracts",
    )
    assert configured.ENV is Environment.PRODUCTION
    with pytest.raises(IdentityProviderUnavailableError):
        build_identity_provider(configured.ENV).get_actor()


def test_development_scope_is_explicit_and_rejects_foreign_actors() -> None:
    identity = build_identity_provider(Environment.DEVELOPMENT).get_actor()
    authorization = build_authorization(Environment.DEVELOPMENT)
    general = authorization.authorize_summary(identity)
    project_id = uuid4()
    project = authorization.authorize_summary(identity, project_id)
    assert general.all_projects and general.include_operational
    assert project.project_ids == frozenset({project_id})
    assert not project.include_operational
    with pytest.raises(AuthorizationDeniedError):
        authorization.authorize_summary(
            ActorIdentity(actor_id=uuid4(), is_development=True)
        )
