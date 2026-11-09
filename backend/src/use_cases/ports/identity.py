"""Server-resolved identities; development identity is explicitly marked."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, kw_only=True)
class ActorIdentity:
    actor_id: UUID
    is_development: bool = False


class IdentityProvider(Protocol):
    def get_actor(self) -> ActorIdentity:
        """Resolve a stable actor or raise IdentityProviderUnavailableError."""
        ...
