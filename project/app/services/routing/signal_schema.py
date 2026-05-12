from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import time


@dataclass
class RoutingSignal:
    """
    Normalized routing signal.

    IMPORTANT:
    Signals describe session-level observations only.
    They are NOT permanent traits or diagnoses.
    """

    signal_type: str
    value: Any

    confidence: float = 0.5
    priority: int = 1

    source: str = "unknown"

    category: Optional[str] = None

    timestamp: float = 0.0

    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def make_signal(
    signal_type: str,
    value: Any,
    confidence: float = 0.5,
    priority: int = 1,
    source: str = "unknown",
    category: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> RoutingSignal:

    return RoutingSignal(
        signal_type=signal_type,
        value=value,
        confidence=confidence,
        priority=priority,
        source=source,
        category=category,
        timestamp=time.time(),
        metadata=metadata or {}
    )
