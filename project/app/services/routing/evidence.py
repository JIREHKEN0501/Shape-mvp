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
            The semantic name of the observation (e.g. "fatigue_risk").

        value:
            The interpreted value associated with the observation
            (e.g. "low", "stable", "deliberate").

        confidence:
            Confidence score associated with the observation.

        priority:
            Relative importance of the observation during routing.
    """

    kind: str
    value: str
    confidence: str
    priority: str


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
