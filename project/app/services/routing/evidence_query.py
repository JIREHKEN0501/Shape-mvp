"""
Read-only query interface for routing evidence.

EvidenceQuery provides retrieval helpers over an immutable
EvidenceContext. It encapsulates evidence traversal so that
consumers do not depend on the internal storage structure.
"""

from .evidence import (
    EvidenceContext,
    EvidenceObservation,
)


class EvidenceQuery:
    """
    Read-only adapter for querying routing evidence.
    """

    def __init__(
        self,
        evidence: EvidenceContext,
    ):
        self._evidence = evidence

    def _find(
        self,
        observations: tuple[EvidenceObservation, ...],
        kind: str,
    ) -> EvidenceObservation | None:
        """
        Return the first observation matching the requested kind.
        """

        for observation in observations:
            if observation.kind == kind:
                return observation

        return None

    def get_temporal(
        self,
        kind: str,
    ) -> EvidenceObservation | None:
        """
        Retrieve a temporal evidence observation.
        """

        return self._find(
            self._evidence.temporal.observations,
            kind,
        )
