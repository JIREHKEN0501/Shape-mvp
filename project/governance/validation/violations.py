from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, Optional

from .invariants import GovernanceInvariant, InvariantSeverity


class ViolationStatus(str, Enum):
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class GovernanceViolation:
    """
    Canonical runtime representation of a governance invariant violation.

    Violations represent operational governance integrity failures detected
    during orchestration execution.
    """

    invariant: GovernanceInvariant
    message: str

    status: ViolationStatus = ViolationStatus.DETECTED
    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    metadata: Dict[str, Any] = field(default_factory=dict)

    recommendation: Optional[str] = None

    @property
    def invariant_id(self) -> str:
        return self.invariant.invariant_id

    @property
    def severity(self) -> InvariantSeverity:
        return self.invariant.severity

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize violation into telemetry/audit-friendly structure.
        """

        return {
            "invariant_id": self.invariant_id,
            "invariant_name": self.invariant.name,
            "severity": self.severity.value,
            "message": self.message,
            "status": self.status.value,
            "detected_at": self.detected_at.isoformat(),
            "recommendation": self.recommendation,
            "metadata": self.metadata,
        }
