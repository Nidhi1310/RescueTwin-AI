"""Thread-safe, in-memory record of which rescue teams are committed to incidents.

The decision engine is a *what-if* tool by default.  Only an explicit commit
reserves a team, after which every later allocation treats that team as
unavailable until the incident is released.  State is per-process; a real
deployment would back this with a shared store.
"""

from __future__ import annotations

import threading
from typing import Callable, TypeVar

T = TypeVar("T")


class DispatchLedger:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._assignments: dict[str, str] = {}  # team_id -> incident_zone_id

    def reserved_team_ids(self, *, excluding_incident: str | None = None) -> frozenset[str]:
        with self._lock:
            return frozenset(
                team for team, incident in self._assignments.items() if incident != excluding_incident
            )

    def snapshot(self) -> dict[str, str]:
        with self._lock:
            return dict(self._assignments)

    def release_incident(self, incident_zone_id: str) -> list[str]:
        with self._lock:
            released = [team for team, incident in self._assignments.items() if incident == incident_zone_id]
            for team in released:
                del self._assignments[team]
            return released

    def commit_allocation(
        self,
        incident_zone_id: str,
        allocate: Callable[[frozenset[str]], T],
        selected_team_id: Callable[[T], str | None],
    ) -> tuple[T, bool]:
        """Allocate and reserve atomically so two incidents can never win the same team."""

        with self._lock:
            result = allocate(self.reserved_team_ids(excluding_incident=incident_zone_id))
            team_id = selected_team_id(result)
            if team_id is None:
                return result, False
            self.release_incident(incident_zone_id)
            self._assignments[team_id] = incident_zone_id
            return result, True

    def clear(self) -> None:
        with self._lock:
            self._assignments.clear()


_ledger = DispatchLedger()


def get_ledger() -> DispatchLedger:
    return _ledger
