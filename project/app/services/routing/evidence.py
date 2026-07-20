"""
Immutable evidence domain models used by the routing pipeline.

Evidence objects represent structured observations derived from routing
signals. They form the stable contract between signal processing,
directive evaluation and conflict resolution.

This module intentionally contains only domain models. It does not perform
signal preparation, classification, or routing logic.
"""

from dataclasses import dataclass, field

@dataclass(frozen=True)
class EvidenceObservation:
    """
    A single immutable observation derived from one or more routing signals.

    Attributes:
        kind:
            The semantic kind of the observation
            (e.g. "fatigue_risk", "latency_trend").

        value:
            The interpreted value associated with the observation.

        confidence:
            Confidence score associated with the observation.

        priority:
            Relative importance of the observation during routing.

        source:
            Originating subsystem that produced the observation.

        evidence_class:
            The semantic role of the observation (e.g. observation,
            interpretation, prediction).

        dependencies:
            Other observations that contributed to this interpretation.

        independent_observations:
            Independent observations supporting this evidence.
    """

    kind: str
    value: Any
    confidence: float
    priority: int

    source: str

    evidence_class: str | None = None

    dependencies: tuple[str, ...] = field(default_factory=tuple)

    independent_observations: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TemporalEvidence:
    """
    Evidence derived from temporal behavioural analysis.
    """

    observations: tuple[EvidenceObservation, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PredictionEvidence:
    """
    Evidence derived from behavioural prediction models.
    """

    observations: tuple[EvidenceObservation, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PatternEvidence:
    """
    Evidence derived from behavioural pattern analysis.
    """

    observations: tuple[EvidenceObservation, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GovernanceEvidence:
    """
    Evidence derived from governance and orchestration constraints.
    """

    observations: tuple[EvidenceObservation, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EvidenceContext:
    """
    Immutable aggregation of all routing evidence.

    This object forms the primary evidence contract consumed by downstream
    directive evaluation and conflict resolution stages.
    """

    temporal: TemporalEvidence = field(default_factory=TemporalEvidence)
    prediction: PredictionEvidence = field(default_factory=PredictionEvidence)
    pattern: PatternEvidence = field(default_factory=PatternEvidence)
    governance: GovernanceEvidence = field(default_factory=GovernanceEvidence)
