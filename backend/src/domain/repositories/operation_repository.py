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
        """Flush a complete result in the transaction that acquired the reservation.

        A fresh confirmation requires a payload. A missing historical payload may
        be read for reconciliation, but must never become a new confirmation.
        """

    @abstractmethod
    def get_by_key(
        self, key: OperationKey, *, include_payload: bool = True
    ) -> OperationRecord | None:
        """Read a confirmation/tombstone visible to this transaction.

        None does not establish absence of a concurrent uncommitted request.
        With include_payload=False, return metadata for authorization without
        reading or decoding the snapshot. Its absent payload does not establish
        a purge: only a complete read may be recovered. The default preserves
        the existing command/replay contract.
        """
