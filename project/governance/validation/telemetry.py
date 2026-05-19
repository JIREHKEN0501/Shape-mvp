from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List


@dataclass
class GovernanceTelemetryEvent:
    """
    Canonical runtime governance telemetry event.
    """

    event_type: str
    payload: Dict[str, Any]

    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "created_at": self.created_at.isoformat(),
            "payload": self.payload,
        }


class GovernanceTelemetryBuffer:
    """
    Lightweight in-memory governance telemetry collector.

    Intended for:
    - validation engineering
    - replay support
    - runtime observability
    - invariant debugging
    """

    def __init__(self) -> None:
        self._events: List[GovernanceTelemetryEvent] = []

    def emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> GovernanceTelemetryEvent:
        """
        Emit governance telemetry event.
        """

        event = GovernanceTelemetryEvent(
            event_type=event_type,
            payload=payload,
        )

        self._events.append(event)

        return event

    def list_events(self) -> List[GovernanceTelemetryEvent]:
        """
        Return all buffered telemetry events.
        """

        return self._events.copy()

    def clear(self) -> None:
        """
        Clear telemetry buffer.
        """

        self._events.clear()


telemetry_buffer = GovernanceTelemetryBuffer()
