"""Transaction-bound operation port; no commits and no process-local locks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeAlias

from src.domain.entities.operation import OperationKey, OperationRecord


@dataclass(frozen=True)
class ReservationAcquired:
    """The current transaction owns the reservation and may execute the command."""


ReservationResult: TypeAlias = ReservationAcquired | OperationRecord


class OperationRepository(ABC):
    @abstractmethod
    def reserve(self, operation: OperationRecord) -> ReservationResult:
        """Arbitrate by UNIQUE(actor_id, operation_id) before any business effect.

        Return an existing confirmation even when result_payload is None after
        purging. A known key must never be reported as a new reservation.
        Contention/uncertainty raises OperationUnresolvedError. Implementations
        share the business session and may flush but must not commit.
        """

    @abstractmethod
    def confirm(self, operation: OperationRecord) -> None:
        """Flush the owned reservation's result within the business transaction."""

    @abstractmethod
    def get_by_key(self, key: OperationKey) -> OperationRecord | None:
        """Read a confirmation/tombstone visible to this transaction.

        None does not establish absence of a concurrent uncommitted request.
        Authorization must precede disclosure of any result.
        """
